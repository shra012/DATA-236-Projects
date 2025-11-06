import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import openai
import redis
import requests
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer


@dataclass
class CacheResult:
    response: str
    is_cached: bool
    similarity: float
    total_latency_ms: float
    backend_latency_ms: float
    start_timestamp: str
    end_timestamp: str


class SemanticCache:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_name: str = "llm-cache",
        key_prefix: str = "llm:query:",
        similarity_threshold: float = 0.85,
        openai_model: str = "gpt-4o-mini",
        ollama_model: str = "phi3:mini",
        llm_provider: str = "openai",
    ):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
        self.index_name = index_name
        self.key_prefix = key_prefix
        self.similarity_threshold = similarity_threshold
        self.llm_provider = llm_provider.lower()
        if self.llm_provider not in {"openai", "ollama"}:
            raise ValueError("llm_provider must be either 'openai' or 'ollama'")
        self.openai_model = openai_model
        self.ollama_model = ollama_model
        self.llm_model = self.openai_model if self.llm_provider == "openai" else self.ollama_model
        self.embedder = SentenceTransformer(model_name)
        self.embedder.max_seq_length = 512
        self.embedder_kwargs = {"normalize_embeddings": True, "convert_to_numpy": True}
        self.vector_dims = int(self.embedder.get_sentence_embedding_dimension())
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set")
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
        self._ensure_index()

    def _ensure_index(self):
        try:
            self.redis.ft(self.index_name).info()
            return
        except redis.exceptions.ResponseError:
            pass

        definition = IndexDefinition(prefix=[self.key_prefix], index_type=IndexType.HASH)
        fields = [
            TextField("query"),
            TextField("response"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.vector_dims,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 1000,
                    "M": 16,
                    "EF_CONSTRUCTION": 200,
                },
            ),
        ]

        self.redis.ft(self.index_name).create_index(fields=fields, definition=definition)

    def _encode(self, text: str) -> np.ndarray:
        embedding = self.embedder.encode(text, **self.embedder_kwargs)
        return np.asarray(embedding, dtype=np.float32)

    def _embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        return embedding.astype(np.float32).tobytes()

    def _search_cache(self, embedding: np.ndarray):
        query_vector = self._embedding_to_bytes(embedding)
        knn_query = (
            Query("*=>[KNN 1 @embedding $vector AS score]")
            .return_fields("query", "response", "score")
            .sort_by("score")
            .dialect(2)
        )

        try:
            results = self.redis.ft(self.index_name).search(knn_query, query_params={"vector": query_vector})
        except redis.exceptions.ResponseError:
            return None

        if results.total == 0:
            return None

        doc = results.docs[0]
        distance = float(doc.score)
        similarity = 1.0 - distance
        if similarity >= self.similarity_threshold:
            response = doc.response.decode("utf-8") if isinstance(doc.response, bytes) else doc.response
            return response, similarity
        return None

    def _store_response(self, prompt: str, embedding: np.ndarray, response: str, latency_ms: float):
        key = f"{self.key_prefix}{uuid.uuid4().hex}"
        self.redis.hset(
            key,
            mapping={
                "query": prompt,
                "response": response,
                "embedding": self._embedding_to_bytes(embedding),
                "model": self.llm_model,
                "latency_ms": f"{latency_ms:.3f}",
                "timestamp": f"{time.time():.0f}",
            },
        )

    def _call_openai(self, prompt: str) -> str:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")
        completion = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        if not completion.choices:
            raise ValueError("No choices returned from OpenAI API")
        message = completion.choices[0].message
        if not message or not message.content:
            raise ValueError("Empty message content from OpenAI API")
        return message.content.strip()

    def _call_ollama(self, prompt: str) -> str:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        payload = {"model": self.ollama_model, "prompt": prompt}
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        if "response" not in data:
            raise ValueError("Unexpected response shape from Ollama API")
        return data["response"].strip()

    def handle_query(self, prompt: str) -> CacheResult:
        start_time = time.perf_counter()
        start_stamp = datetime.now().isoformat()
        embedding = self._encode(prompt)

        cached = self._search_cache(embedding)
        if cached:
            response, similarity = cached
            total_latency = (time.perf_counter() - start_time) * 1000
            end_stamp = datetime.now().isoformat()
            print(
                f"✓ Cache hit (similarity={similarity:.3f}, latency={total_latency:.2f}ms, "
                f"start={start_stamp}, end={end_stamp})"
            )
            return CacheResult(
                response=response,
                is_cached=True,
                similarity=similarity,
                total_latency_ms=total_latency,
                backend_latency_ms=0.0,
                start_timestamp=start_stamp,
                end_timestamp=end_stamp,
            )

        miss_time = time.perf_counter()
        if self.llm_provider == "openai":
            llm_response = self._call_openai(prompt)
        else:
            llm_response = self._call_ollama(prompt)
        backend_latency = (time.perf_counter() - miss_time) * 1000
        self._store_response(prompt, embedding, llm_response, backend_latency)
        total_latency = (time.perf_counter() - start_time) * 1000
        end_stamp = datetime.now().isoformat()
        print(
            f"✗ Cache miss ({self.llm_provider.upper()} latency={backend_latency:.2f}ms, total={total_latency:.2f}ms, "
            f"start={start_stamp}, end={end_stamp})"
        )
        return CacheResult(
            response=llm_response,
            is_cached=False,
            similarity=0.0,
            total_latency_ms=total_latency,
            backend_latency_ms=backend_latency,
            start_timestamp=start_stamp,
            end_timestamp=end_stamp,
        )


def run_demo():
    provider = os.getenv("LLM_PROVIDER", "openai")
    try:
        cache = SemanticCache(llm_provider=provider)
    except RuntimeError as exc:
        print("Configuration error:", exc)
        return
    print(f"Using LLM provider: {cache.llm_provider} (model={cache.llm_model})")
    queries = [
        "Explain the concept of semantic caching in simple terms.",
        "What is semantic caching?",
        "Give me a short summary of Redis vector similarity search.",
        "How does Redis handle vector similarity?",
        "Outline the benefits of caching LLM responses.",
        "Explain the concept of semantic caching in simple terms.",
        "What are HNSW indexes used for?",
        "Describe how cosine similarity works in embeddings.",
        "Give me a short summary of Redis vector similarity search.",
        "Explain how to cache AI responses semantically.",
    ]

    hit_count = 0
    total_cached_latency = 0.0
    total_uncached_latency = 0.0
    total_miss_backend_latency = 0.0
    miss_count = 0

    for idx, prompt in enumerate(queries, start=1):
        print(f"\nQuery #{idx}: {prompt}")
        try:
            result = cache.handle_query(prompt)
        except openai.OpenAIError as exc:
            print("OpenAI request failed:", exc)
            break
        except requests.RequestException as exc:
            print("Ollama request failed:", exc)
            break
        except RuntimeError as exc:
            print("Configuration error:", exc)
            break
        except Exception as exc:
            print("Error handling query:", exc)
            break

        if result.is_cached:
            hit_count += 1
            total_cached_latency += result.total_latency_ms
        else:
            miss_count += 1
            total_uncached_latency += result.total_latency_ms
            total_miss_backend_latency += result.backend_latency_ms
        print(f"Timestamps: start={result.start_timestamp}, end={result.end_timestamp}")
        print(f"Response snippet: {result.response[:120]}...")

    total_queries = hit_count + miss_count
    if total_queries:
        hit_rate = (hit_count / total_queries) * 100
        avg_hit_latency = total_cached_latency / hit_count if hit_count else 0.0
        avg_miss_latency = total_uncached_latency / miss_count if miss_count else 0.0
        avg_backend_latency = total_miss_backend_latency / miss_count if miss_count else 0.0
        speedup = (avg_miss_latency / avg_hit_latency) if hit_count and avg_hit_latency else 0.0
        print("\n=== Cache Metrics ===")
        print(f"Total queries: {total_queries}")
        print(f"Cache hits: {hit_count}")
        print(f"Cache misses: {miss_count}")
        print(f"Hit rate: {hit_rate:.1f}%")
        if hit_count:
            print(f"Avg cached latency: {avg_hit_latency:.2f}ms")
        if miss_count:
            provider_label = cache.llm_provider.upper()
            print(f"Avg {provider_label} total latency: {avg_miss_latency:.2f}ms")
            print(f"Avg {provider_label} backend latency: {avg_backend_latency:.2f}ms")
        if speedup:
            print(f"Speedup factor: {speedup:.2f}x")


if __name__ == "__main__":
    run_demo()
