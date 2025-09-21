# Installation

Both experiments rely on CPU-only builds of PyTorch/FAISS plus LlamaIndex and
Jupyter for the notebook. Follow the steps below from the `Chunking/` folder.

## 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

The requirements file pins the CPU wheels for PyTorch (`--index-url` is embedded),
LlamaIndex, FAISS, sentence-transformers, and Jupyter utilities.

## 3. (Optional) Register the kernel for notebooks

```bash
python -m ipykernel install --user --name chunking-venv --display-name "Chunking (.venv)"
```

## 4. Verify the setup

```bash
python chunking_experiments.py --help
python llamaindex_chunking_experiments.py --help
```

Both commands should print usage information without errors. You can now run the
experiments or start Jupyter with:

```bash
Chunking/.venv/bin/jupyter notebook --notebook-dir=Chunking --ip=0.0.0.0 --port=8002
```
