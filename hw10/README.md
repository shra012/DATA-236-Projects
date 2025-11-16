# Customer Segmentation Project

This repository contains:

- `train_customer_model.py` – generates synthetic customer data, trains a KMeans model (k=5), and saves the model/metadata pickles.
- `ml_app.py` – Streamlit app that loads the pickles, predicts a customer's cluster, and visualizes the simulated dataset.

## Development Environment

The project is managed with [uv](https://docs.astral.sh/uv/) and targets Python 3.12.

```bash
uv sync --python 3.12
source .venv/bin/activate
uv run python train_customer_model.py
uv run streamlit run ml_app.py
```

The `pyproject.toml` declares all required dependencies (NumPy, pandas, scikit-learn, matplotlib, and Streamlit).
