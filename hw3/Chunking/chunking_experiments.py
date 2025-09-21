#!/usr/bin/env python3
"""
Compare three chunking techniques on Tiny Shakespeare using sentence-transformers
and simple retrieval based on cosine similarity.

Usage:
    python chunking_experiments.py [--full-size]

This script downloads the Tiny Shakespeare dataset if necessary.
"""
import argparse
from pathlib import Path
import requests
from tqdm import tqdm
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DATA_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
DATA_FILE = Path(__file__).parent / "tiny_shakespeare.txt"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def download_file(url, dest: Path):
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


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def token_based_chunking(text: str, chunk_size: int = 512, overlap: int = 64):
    """Simulate TokenTextSplitter - split by tokens/words with overlap"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks[:500]  # Limit to avoid memory issues


def semantic_chunking(text: str, chunk_size: int = 512):
    """Simulate SemanticSplitterNodeParser - split by semantic boundaries (paragraphs/scenes)"""
    # Split by double newlines (paragraph breaks) or scene markers
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed chunk_size, start new chunk
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks[:500]  # Limit to avoid memory issues


def sentence_window_chunking(text: str, window_size: int = 3):
    """Simulate SentenceWindowNodeParser - sliding window of sentences"""
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    for i in range(0, len(sentences), window_size - 1):  # overlap of 1 sentence
        window_sentences = sentences[i:i + window_size]
        chunk_text = '. '.join(window_sentences) + '.'
        if chunk_text.strip() != '.':
            chunks.append(chunk_text)

    return chunks[:500]  # Limit to avoid memory issues


def create_embeddings(chunks, model):
    """Create embeddings for chunks"""
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings


def retrieve_similar(query, chunks, embeddings, model, top_k=3):
    """Retrieve most similar chunks to query"""
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Get top_k most similar chunks
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            'chunk_id': idx,
            'similarity': similarities[idx],
            'text': chunks[idx][:200] + "..." if len(chunks[idx]) > 200 else chunks[idx]
        })

    return results


def main(full_size=False):
    download_file(DATA_URL, DATA_FILE)
    text = load_text(DATA_FILE)

    if not full_size:
        text = text[:50000]
        print(f"Using sample of {len(text)} characters (use --full-size for complete dataset)")
    else:
        print(f"Using full dataset with {len(text)} characters")

    print("\nLoading sentence transformer model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    # Apply three chunking techniques
    print("\n=== 1. Token-based Chunking ===")
    token_chunks = token_based_chunking(text)
    print(f"Created {len(token_chunks)} token-based chunks")
    print(f"Sample chunk: {token_chunks[0][:100]}...")

    print("\n=== 2. Semantic Chunking ===")
    semantic_chunks = semantic_chunking(text)
    print(f"Created {len(semantic_chunks)} semantic chunks")
    print(f"Sample chunk: {semantic_chunks[0][:100]}...")

    print("\n=== 3. Sentence Window Chunking ===")
    sentence_chunks = sentence_window_chunking(text)
    print(f"Created {len(sentence_chunks)} sentence window chunks")
    print(f"Sample chunk: {sentence_chunks[0][:100]}...")

    # Create embeddings for each chunking method
    print("\nCreating embeddings...")
    token_embeddings = create_embeddings(token_chunks, model)
    semantic_embeddings = create_embeddings(semantic_chunks, model)
    sentence_embeddings = create_embeddings(sentence_chunks, model)

    print(f"Token embeddings shape: {token_embeddings.shape}")
    print(f"Semantic embeddings shape: {semantic_embeddings.shape}")
    print(f"Sentence embeddings shape: {sentence_embeddings.shape}")

    # Sample embeddings (first few dimensions)
    print("\nSample embeddings (first 6 dimensions):")
    print("Token chunk 0:", token_embeddings[0][:6])
    print("Semantic chunk 0:", semantic_embeddings[0][:6])
    print("Sentence chunk 0:", sentence_embeddings[0][:6])

    # Test retrieval with shared query
    query = "To be or not to be"
    print(f"\n=== Retrieval Results for Query: '{query}' ===")

    print("\n--- Token-based Retrieval ---")
    token_results = retrieve_similar(query, token_chunks, token_embeddings, model)
    for i, result in enumerate(token_results):
        print(f"Rank {i + 1} (similarity: {result['similarity']:.4f}):")
        print(f"  {result['text']}")
        print()

    print("\n--- Semantic Retrieval ---")
    semantic_results = retrieve_similar(query, semantic_chunks, semantic_embeddings, model)
    for i, result in enumerate(semantic_results):
        print(f"Rank {i + 1} (similarity: {result['similarity']:.4f}):")
        print(f"  {result['text']}")
        print()

    print("\n--- Sentence Window Retrieval ---")
    sentence_results = retrieve_similar(query, sentence_chunks, sentence_embeddings, model)
    for i, result in enumerate(sentence_results):
        print(f"Rank {i + 1} (similarity: {result['similarity']:.4f}):")
        print(f"  {result['text']}")
        print()

    # Analysis
    print("\n=== ANALYSIS ===")
    print("Comparing the three chunking techniques:")
    print(
        f"1. Token-based: {len(token_chunks)} chunks, avg length: {np.mean([len(c) for c in token_chunks]):.0f} chars")
    print(
        f"2. Semantic: {len(semantic_chunks)} chunks, avg length: {np.mean([len(c) for c in semantic_chunks]):.0f} chars")
    print(
        f"3. Sentence window: {len(sentence_chunks)} chunks, avg length: {np.mean([len(c) for c in sentence_chunks]):.0f} chars")

    print(f"\nHighest similarity scores:")
    print(f"Token-based: {max([r['similarity'] for r in token_results]):.4f}")
    print(f"Semantic: {max([r['similarity'] for r in semantic_results]):.4f}")
    print(f"Sentence window: {max([r['similarity'] for r in sentence_results]):.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare chunking techniques on Tiny Shakespeare")
    parser.add_argument("--full-size", action="store_true",
                        help="Use full dataset instead of 50k character sample")
    args = parser.parse_args()

    main(full_size=args.full_size)
