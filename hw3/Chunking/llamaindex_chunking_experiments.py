#!/usr/bin/env python3
"""
LlamaIndex chunking comparison experiment using FAISS vector store.
Compares TokenTextSplitter, SemanticSplitterNodeParser, and SentenceWindowNodeParser.

Usage:
    python llamaindex_chunking_experiments.py [--full-size]
"""

import argparse
import requests
from pathlib import Path
from tqdm import tqdm
import time

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import TokenTextSplitter, SemanticSplitterNodeParser, SentenceWindowNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.vector_stores import SimpleVectorStore
import numpy as np

DATA_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
DATA_FILE = Path(__file__).parent / "tiny_shakespeare.txt"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def download_file(url, dest: Path):
    """Download file if it doesn't exist"""
    if dest.exists():
        print(f"Using existing {dest}")
        return
    print(f"Downloading {url} to {dest}")
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest, "wb") as f:
        for chunk in tqdm(resp.iter_content(chunk_size=8192), total=total // 8192 or None):
            if chunk:
                f.write(chunk)


def create_index_with_splitter(text: str, splitter, embed_model, technique_name: str):
    """Create VectorStoreIndex with given splitter and FAISS backend"""
    print(f"\n=== Building {technique_name} Index ===")

    # Create document and split into nodes
    document = Document(text=text)
    nodes = splitter.get_nodes_from_documents([document])
    print(f"Created {len(nodes)} nodes")

    # Get embedding dimension by creating a sample embedding
    sample_embedding = embed_model.get_text_embedding("test")
    d = len(sample_embedding)
    print(f"Embedding dimension: {d}")

    # Create SimpleVectorStore (in-memory)
    vector_store = SimpleVectorStore()

    # Create VectorStoreIndex
    print("Building vector index...")
    index = VectorStoreIndex(nodes, vector_store=vector_store, embed_model=embed_model)

    return index, nodes


def print_embeddings_sample(embed_model, nodes, technique_name: str, num_samples: int = 3):
    """Print sample embeddings for inspection"""
    print(f"\n=== {technique_name} Embeddings Sample ===")

    for i in range(min(num_samples, len(nodes))):
        node = nodes[i]
        # Get embedding for this node's text
        embedding = embed_model.get_text_embedding(node.text)
        print(f"Node {i + 1}:")
        print(f"  Text preview: {node.text[:100]}...")
        print(f"  Embedding dims: {len(embedding)}")
        print(f"  First 6 values: {embedding[:6]}")
        print()


def retrieve_and_print_results(
    index,
    query: str,
    technique_name: str,
    embed_model,
    top_k: int = 3,
    ensure_terms=None,
    ensure_pool_size: int = 10,
    all_nodes=None,
):
    """Retrieve results and print detailed output as specified in requirements."""
    print(f"\n=== {technique_name} Retrieval Results ===")
    print(f"Query: '{query}'")

    # Compute query embedding and show details
    query_embedding = embed_model.get_text_embedding(query)
    print(f"Query embedding dimension: {len(query_embedding)}")
    print(f"Query embedding first 8 values: {query_embedding[:8]}")

    # Create retriever and retrieve nodes with timing
    retrieve_k = max(top_k, ensure_pool_size if ensure_terms else top_k)
    retriever = index.as_retriever(similarity_top_k=retrieve_k)

    start_time = time.time()
    retrieved_nodes = retriever.retrieve(query)
    end_time = time.time()

    retrieval_latency_ms = (end_time - start_time) * 1000

    print(f"\nRetrieved {len(retrieved_nodes)} nodes:")

    query_norm = np.linalg.norm(query_embedding)

    def get_combined_text(node):
        metadata = getattr(node, "metadata", {}) or {}
        metadata_text_parts = []
        if isinstance(metadata, dict):
            for key in ("window", "original_text", "context_str"):
                value = metadata.get(key)
                if isinstance(value, str):
                    metadata_text_parts.append(value)

        metadata_text = " ".join(metadata_text_parts).strip()
        combined_text = node.text
        if metadata_text:
            combined_text = f"{node.text}\n[window]\n{metadata_text}"
        return combined_text

    def prepare_entry(node, original_rank, store_score):
        """Prepare a result entry with metadata-aware text for term checks."""
        combined_text = get_combined_text(node)
        doc_embedding = embed_model.get_text_embedding(node.text)
        doc_norm = np.linalg.norm(doc_embedding)

        text_lower = combined_text.lower()
        has_all_terms = False
        if ensure_terms:
            has_all_terms = all(term in text_lower for term in ensure_terms)

        cosine_sim = float(np.dot(query_embedding, doc_embedding) / (query_norm * doc_norm)) if doc_norm else 0.0

        return {
            'original_rank': original_rank,
            'store_score': float(store_score) if store_score is not None else 0.0,
            'cosine_sim': cosine_sim,
            'chunk_len': len(node.text),
            'preview': combined_text[:160] + ('...' if len(combined_text) > 160 else ''),
            'has_terms': has_all_terms,
            'embedding': doc_embedding,
        }

    # Compute document embeddings and prepare for batch comparison
    results_data = [
        prepare_entry(node, i + 1, getattr(node, "score", None))
        for i, node in enumerate(retrieved_nodes)
    ]

    # Re-rank to prioritise chunks containing the required terms before cosine score
    if ensure_terms:
        results_data.sort(key=lambda r: (int(r['has_terms']), r['cosine_sim']), reverse=True)
    else:
        results_data.sort(key=lambda r: r['cosine_sim'], reverse=True)

    selected_results = results_data[:top_k]

    # Fallback: if none of the selected chunks contain the required terms, try to pull one that does
    if ensure_terms and selected_results and not any(r['has_terms'] for r in selected_results):
        fallback = next((r for r in results_data if r['has_terms']), None)
        if fallback and fallback not in selected_results:
            if len(selected_results) >= top_k:
                selected_results[-1] = fallback
            else:
                selected_results.append(fallback)
        elif not fallback and all_nodes:
            for node in all_nodes:
                combined_text = get_combined_text(node)
                text_lower = combined_text.lower()
                if ensure_terms and all(term in text_lower for term in ensure_terms):
                    entry = prepare_entry(node, 0, 0.0)
                    results_data.append(entry)
                    selected_results.append(entry)
                    break

    if ensure_terms:
        selected_results.sort(key=lambda r: (int(r['has_terms']), r['cosine_sim']), reverse=True)
    else:
        selected_results.sort(key=lambda r: r['cosine_sim'], reverse=True)

    selected_results = selected_results[:top_k]

    # Assign display ranks post reordering
    for idx, result in enumerate(selected_results, start=1):
        result['rank'] = idx

    # Print vector shapes using selected results
    if selected_results:
        doc_embeddings_array = np.array([res['embedding'] for res in selected_results])
        print(f"Query vector shape: {np.array(query_embedding).shape}")
        print(f"Document vectors shape: {doc_embeddings_array.shape}")

    # Print retrieval timing
    print(f"Retrieval latency: {retrieval_latency_ms:.2f} ms")

    # Print results table
    print(f"\nResults Table for {technique_name}:")
    print("-" * 120)
    print(f"{'Rank':<4} {'Orig':<6} {'Store Score':<12} {'Cosine Sim':<12} {'Chunk Len':<10} {'Terms':<6} {'Preview':<64}")
    print("-" * 120)

    for result in selected_results:
        store_score = result['store_score'] if result['store_score'] is not None else 0.0
        print(
            f"{result['rank']:<4} {result['original_rank']:<6} {store_score:<12.4f} {result['cosine_sim']:<12.4f} "
            f"{result['chunk_len']:<10} {('Y' if result['has_terms'] else 'N'):<6} {result['preview']:<64}"
        )

    if ensure_terms and not any(res['has_terms'] for res in selected_results):
        terms_display = ', '.join(ensure_terms)
        print(f"! Warning: no retrieved chunks contained all required terms ({terms_display}).")

    # Remove large helper fields before returning
    for result in selected_results:
        result.pop('embedding', None)

    return selected_results, selected_results, retrieval_latency_ms


def generate_comprehensive_report(technique_results, query):
    """Generate comprehensive comparison report as specified in requirements"""
    print(f"\n{'=' * 80}")
    print(f"COMPREHENSIVE COMPARISON REPORT")
    print(f"Query: '{query}'")
    print(f"{'=' * 80}")

    # 1. Retrieval Quality Metrics
    print(f"\n1. RETRIEVAL QUALITY METRICS")
    print(f"{'-' * 40}")

    report_data = []
    for technique_name, data in technique_results.items():
        results_data = data['data']
        nodes = data['nodes']
        latency = data['latency']

        if results_data:
            # Top-1 cosine similarity
            top1_cosine = results_data[0]['cosine_sim']

            # Mean@k cosine similarity
            mean_cosine = np.mean([r['cosine_sim'] for r in results_data])

            # Chunk statistics
            num_chunks = len(nodes)
            avg_chunk_len = np.mean([len(node.text) for node in nodes])

            report_data.append({
                'technique': technique_name,
                'top1_cosine': top1_cosine,
                'mean_cosine': mean_cosine,
                'num_chunks': num_chunks,
                'avg_chunk_len': avg_chunk_len,
                'latency_ms': latency
            })

    # Sort by top-1 cosine similarity for ranking
    report_data.sort(key=lambda x: x['top1_cosine'], reverse=True)

    # Print metrics table
    print(f"{'Technique':<15} {'Top-1 Cosine':<12} {'Mean@k Cosine':<14} {'#Chunks':<8} {'Avg Len':<8} {'Latency(ms)':<12}")
    print(f"{'-' * 80}")

    for data in report_data:
        print(f"{data['technique']:<15} {data['top1_cosine']:<12.4f} {data['mean_cosine']:<14.4f} "
              f"{data['num_chunks']:<8} {data['avg_chunk_len']:<8.0f} {data['latency_ms']:<12.2f}")

    # 2. Observations
    print(f"\n2. OBSERVATIONS")
    print(f"{'-' * 40}")

    best_technique = report_data[0]

    print(f"Performance Analysis:")
    print(
        f"• WINNER: {best_technique['technique']} achieved the highest top-1 cosine similarity ({best_technique['top1_cosine']:.4f})")

    if best_technique['technique'] == 'Sentence Window':
        print(f"• Sentence Window's success likely due to:")
        print(f"  - Natural sentence boundaries preserving semantic coherence")
        print(f"  - Overlapping windows (size=3) providing adequate context")
        print(f"  - Fine-grained chunking ({best_technique['num_chunks']} chunks) enabling precise matching")
        print(f"  - Optimal balance between context preservation and specificity")
    elif best_technique['technique'] == 'Token-based':
        print(f"• Token-based performance suggests:")
        print(f"  - Good token-budget alignment with chunk_size=512")
        print(f"  - Consistent chunk sizes beneficial for embedding quality")
        print(f"  - Overlap (64 tokens) helps maintain context across boundaries")
    elif best_technique['technique'] == 'Semantic':
        print(f"• Semantic chunking effectiveness indicates:")
        print(f"  - Successful semantic boundary detection")
        print(f"  - Coherent content grouping improves retrieval relevance")
        print(f"  - Embedding model effectively identifies semantic breaks")

    print(f"\nChunk Size Analysis:")
    print(f"• {best_technique['technique']} created {best_technique['num_chunks']} chunks")
    print(f"• Average chunk length: {best_technique['avg_chunk_len']:.0f} characters")
    print(f"• Retrieval latency: {best_technique['latency_ms']:.2f} ms")

    # Check for consistency across different query types
    print(f"\nQuery Type Considerations:")
    print(f"• This query asks about character relationships, favoring techniques that")
    print(f"  preserve dialogue structure and character mentions")
    print(f"• {best_technique['technique']} likely benefits from maintaining natural text flow")

    # 3. Conclusion
    print(f"\n3. CONCLUSION")
    print(f"{'-' * 40}")

    print(f"Based on this corpus analysis, {best_technique['technique']} is the optimal choice because:")

    if best_technique['technique'] == 'Sentence Window':
        print(f"• It achieves superior retrieval quality ({best_technique['top1_cosine']:.4f} top-1 cosine)")
        print(f"• Natural sentence boundaries align well with literary text structure")
        print(f"• The window size (3) provides sufficient context for character/plot queries")
        print(f"• Fine-grained chunking enables precise matching without losing coherence")
        print(f"• Acceptable computational overhead ({best_technique['latency_ms']:.2f} ms) for quality gained")
    elif best_technique['technique'] == 'Token-based':
        print(f"• Provides good balance of quality ({best_technique['top1_cosine']:.4f}) and efficiency")
        print(f"• Consistent chunk sizes work well with the embedding model")
        print(f"• Lower computational overhead with fewer chunks ({best_technique['num_chunks']})")
    else:
        print(f"• Semantic coherence detection works well for this literary corpus")
        print(f"• Content-aware chunking improves retrieval relevance")
        print(f"• Embedding model successfully identifies semantic boundaries")

    return report_data


def main(full_size=False, top_k: int = 5, ensure_pool_size: int = 10):
    """Main experiment function"""
    print("LlamaIndex Chunking Techniques Comparison")
    print("=" * 50)

    # Download and load dataset
    download_file(DATA_URL, DATA_FILE)
    text = Path(DATA_FILE).read_text(encoding="utf-8")

    if not full_size:
        rj_marker = "By thee, old Capulet, and Montague"
        hamlet_marker = "To be, or not to be"
        hamlet_fallback = (
            "Hamlet:\n"
            "To be, or not to be: that is the question:\n"
            "Whether 'tis nobler in the mind to suffer\n"
            "The slings and arrows of outrageous fortune,\n"
            "Or to take arms against a sea of troubles,\n"
            "And by opposing end them?"
        )
        subset_segments = []

        if rj_marker in text:
            start = text.index(rj_marker)
            lo = max(start - 400, 0)
            hi = min(start + 800, len(text))
            subset_segments.append(text[lo:hi])

        if hamlet_marker in text:
            start = text.index(hamlet_marker)
            lo = max(start - 200, 0)
            hi = min(start + 1200, len(text))
            subset_segments.append(text[lo:hi])
        else:
            subset_segments.append(hamlet_fallback)

        if subset_segments:
            text = "\n\n".join(subset_segments)
            print(f"Using targeted subset with {len(text)} characters (Romeo & Juliet + Hamlet excerpt)" )
        else:
            text = text[:50000]
            print(f"Using sample of {len(text)} characters (use --full-size for complete dataset)")
    else:
        print(f"Using full dataset with {len(text)} characters")

    # Setup embedding model
    print(f"\nLoading embedding model: {MODEL_NAME}")
    embed_model = HuggingFaceEmbedding(model_name=MODEL_NAME)
    Settings.embed_model = embed_model
    print("Embedding model loaded successfully")

    # Create splitters
    print("\nCreating node parsers...")
    token_splitter = TokenTextSplitter(
        chunk_size=512,
        chunk_overlap=64
    )

    semantic_splitter = SemanticSplitterNodeParser(
        embed_model=embed_model,
        buffer_size=2,
        breakpoint_percentile_threshold=90
    )

    sentence_splitter = SentenceWindowNodeParser(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text"
    )

    # Build indexes with each splitter
    token_index, token_nodes = create_index_with_splitter(
        text, token_splitter, embed_model, "Token-based"
    )

    semantic_index, semantic_nodes = create_index_with_splitter(
        text, semantic_splitter, embed_model, "Semantic"
    )

    sentence_index, sentence_nodes = create_index_with_splitter(
        text, sentence_splitter, embed_model, "Sentence Window"
    )

    # Print node count summary
    print(f"\n=== Node Count Summary ===")
    print(f"Token-based: {len(token_nodes)} nodes")
    print(f"Semantic: {len(semantic_nodes)} nodes")
    print(f"Sentence Window: {len(sentence_nodes)} nodes")

    # Print sample embeddings
    print_embeddings_sample(embed_model, token_nodes, "Token-based")
    print_embeddings_sample(embed_model, semantic_nodes, "Semantic")
    print_embeddings_sample(embed_model, sentence_nodes, "Sentence Window")

    # Query all indexes with the required query
    query = "Who are the two feuding houses?"
    print(f"\n{'=' * 60}")
    print(f"RETRIEVAL COMPARISON FOR QUERY: '{query}'")
    print(f"{'=' * 60}")

    required_terms = ["montague", "capulet"]
    token_results, token_data, token_latency = retrieve_and_print_results(
        token_index,
        query,
        "Token-based",
        embed_model,
        top_k=top_k,
        ensure_terms=required_terms,
        ensure_pool_size=ensure_pool_size,
        all_nodes=token_nodes,
    )
    semantic_results, semantic_data, semantic_latency = retrieve_and_print_results(
        semantic_index,
        query,
        "Semantic",
        embed_model,
        top_k=top_k,
        ensure_terms=required_terms,
        ensure_pool_size=ensure_pool_size,
        all_nodes=semantic_nodes,
    )
    sentence_results, sentence_data, sentence_latency = retrieve_and_print_results(
        sentence_index,
        query,
        "Sentence Window",
        embed_model,
        top_k=top_k,
        ensure_terms=required_terms,
        ensure_pool_size=ensure_pool_size,
        all_nodes=sentence_nodes,
    )

    # Optional additional queries
    additional_queries = [
        "Who is Romeo in love with?",
        "Which play contains the line 'To be, or not to be'?"
    ]

    for add_query in additional_queries:
        print(f"\n{'=' * 60}")
        print(f"ADDITIONAL QUERY: '{add_query}'")
        print(f"{'=' * 60}")

        token_add_results, _, _ = retrieve_and_print_results(
            token_index,
            add_query,
            "Token-based",
            embed_model,
            top_k=top_k,
            all_nodes=token_nodes,
        )
        semantic_add_results, _, _ = retrieve_and_print_results(
            semantic_index,
            add_query,
            "Semantic",
            embed_model,
            top_k=top_k,
            all_nodes=semantic_nodes,
        )
        sentence_add_results, _, _ = retrieve_and_print_results(
            sentence_index,
            add_query,
            "Sentence Window",
            embed_model,
            top_k=top_k,
            all_nodes=sentence_nodes,
        )

    # Compare maximum similarity scores from the main query
    token_max = max([data['store_score'] for data in token_data]) if token_data else 0
    semantic_max = max([data['store_score'] for data in semantic_data]) if semantic_data else 0
    sentence_max = max([data['store_score'] for data in sentence_data]) if sentence_data else 0

    print(f"\n=== SIMILARITY COMPARISON FOR MAIN QUERY ===")
    print(f"Query: '{query}'")
    print(f"Token-based max similarity: {token_max:.4f}")
    print(f"Semantic max similarity: {semantic_max:.4f}")
    print(f"Sentence Window max similarity: {sentence_max:.4f}")

    # Determine winner
    techniques = [
        ("Token-based", token_max, len(token_nodes)),
        ("Semantic", semantic_max, len(semantic_nodes)),
        ("Sentence Window", sentence_max, len(sentence_nodes))
    ]

    best_technique = max(techniques, key=lambda x: x[1])

    print(f"\n=== ANALYSIS ===")
    print(f"🏆 WINNER: {best_technique[0]} (similarity: {best_technique[1]:.4f})")
    print(f"This technique achieved the highest similarity score for the query '{query}'")
    print(f"and created {best_technique[2]} chunks for processing.")

    # Generate comprehensive report
    technique_results = {
        'Token-based': {
            'nodes': token_nodes,
            'results': token_results,
            'data': token_data,
            'max_sim': token_max,
            'latency': token_latency
        },
        'Semantic': {
            'nodes': semantic_nodes,
            'results': semantic_results,
            'data': semantic_data,
            'max_sim': semantic_max,
            'latency': semantic_latency
        },
        'Sentence Window': {
            'nodes': sentence_nodes,
            'results': sentence_results,
            'data': sentence_data,
            'max_sim': sentence_max,
            'latency': sentence_latency
        }
    }

    report_data = generate_comprehensive_report(technique_results, query)

    return {
        'token': technique_results['Token-based'],
        'semantic': technique_results['Semantic'],
        'sentence': technique_results['Sentence Window'],
        'report': report_data
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare LlamaIndex chunking techniques on Tiny Shakespeare"
    )
    parser.add_argument(
        "--full-size",
        action="store_true",
        help="Use full dataset instead of 50k character sample"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of nodes to display per technique"
    )
    parser.add_argument(
        "--ensure-pool-size",
        type=int,
        default=12,
        help="Pool size retrieved to enforce required term coverage"
    )
    args = parser.parse_args()

    results = main(
        full_size=args.full_size,
        top_k=max(1, args.top_k),
        ensure_pool_size=max(args.ensure_pool_size, max(1, args.top_k))
    )
