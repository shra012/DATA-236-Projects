# Chunking Experiments

The `Chunking/` folder contains two complementary comparisons of chunking
strategies on the Tiny Shakespeare corpus:

- `chunking_experiments.py` reproduces the cosine-similarity experiment from class
  with `sentence-transformers` only.
- `llamaindex_chunking_experiments.py` builds three LlamaIndex vector stores
  (TokenTextSplitter, SemanticSplitterNodeParser, SentenceWindowNodeParser) and
  prints embeddings, retrieval diagnostics, and aggregate metrics.
- `llamaindex_chunking_experiments.ipynb` mirrors the LlamaIndex script for
  interactive tinkering; remember to select the `Chunking (.venv)` kernel.

## Quick start

1. Create and activate the virtual environment (from `Chunking/`):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the baseline experiment:

   ```bash
   python chunking_experiments.py          # add --full-size for the whole corpus
   ```

4. Run the LlamaIndex experiment (subset by default, full corpus with the flag):

   ```bash
   python llamaindex_chunking_experiments.py --top-k 5 --ensure-pool-size 20
   python llamaindex_chunking_experiments.py --full-size  # optional long run
   ```

5. Launch the notebook if you prefer an interactive workflow:

   ```bash
   Chunking/.venv/bin/jupyter notebook --notebook-dir=Chunking --ip=0.0.0.0 --port=8002
   ```

## Notes

- The requirements install CPU-only PyTorch, FAISS, LlamaIndex, Jupyter, and helpers.
- Tiny Shakespeare is downloaded automatically to `tiny_shakespeare.txt`.
- Both experiments are retrieval-only; no generation is performed.
