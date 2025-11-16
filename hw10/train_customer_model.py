"""Training script for the customer segmentation assignment.

This file simulates customer data, fits a K-Means model, and writes out the
trained artifact along with metadata so the Streamlit app can consume them.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


RANDOM_SEED = 42
N_SAMPLES = 200
N_CLUSTERS = 5

MODEL_PATH = Path("customer_kmeans_model_Shravankumar_Nagarajan.pkl")
METADATA_PATH = Path("customer_metadata.pkl")


def simulate_customer_data(random_state: int | None = None) -> pd.DataFrame:
    """Generate synthetic customer features.

    Annual income lives roughly between 15k and 150k, while spending scores are
    bounded between 1 and 100.
    """

    rng = np.random.default_rng(random_state)
    incomes = rng.uniform(15, 150, size=N_SAMPLES)
    spending_scores = rng.uniform(1, 100, size=N_SAMPLES)

    return pd.DataFrame(
        {
            "Annual Income (k$)": incomes,
            "Spending Score (1-100)": spending_scores,
        }
    )


def train_model(data: pd.DataFrame) -> KMeans:
    model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED)
    model.fit(data)
    return model


def save_pickle(obj, path: Path) -> None:
    with path.open("wb") as file:
        pickle.dump(obj, file)


def main() -> None:
    data = simulate_customer_data(random_state=RANDOM_SEED)
    model = train_model(data)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_pickle(model, MODEL_PATH)

    metadata = {
        "feature_names": list(data.columns),
        "cluster_centers": model.cluster_centers_.tolist(),
        "data": data.to_dict(orient="records"),
        "labels": model.labels_.tolist(),
    }
    save_pickle(metadata, METADATA_PATH)

    print(f"Saved KMeans model to {MODEL_PATH.resolve()}")
    print(f"Saved metadata to {METADATA_PATH.resolve()}")


if __name__ == "__main__":
    main()
