"""Streamlit dashboard for the customer segmentation model."""

from __future__ import annotations

import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


MODEL_FILE = "customer_kmeans_model_Shravankumar_Nagarajan.pkl"
METADATA_FILE = "customer_metadata.pkl"


@st.cache_resource
def load_resources(model_file: str, metadata_file: str):
    """Load the pickled model and metadata once per Streamlit session."""

    if not os.path.exists(model_file) or not os.path.exists(metadata_file):
        st.error(
            "Required model or metadata files are missing. Please run "
            "'train_customer_model.py' first."
        )
        return None, None

    with open(model_file, "rb") as model_file_obj:
        model = pickle.load(model_file_obj)

    with open(metadata_file, "rb") as metadata_file_obj:
        metadata = pickle.load(metadata_file_obj)

    return model, metadata


model, metadata = load_resources(MODEL_FILE, METADATA_FILE)

st.title("Customer Segmentation Explorer")
st.markdown(
    "Interact with the simulated mall customer dataset to predict which cluster "
    "a new customer belongs to."
)


if model and metadata:
    feature_names = metadata.get("feature_names", ["Annual Income (k$)", "Spending Score (1-100)"])
    income_col, spending_col = feature_names

    data_records = metadata.get("data", [])
    data_df = pd.DataFrame(data_records, columns=feature_names)

    if data_df.empty:
        st.warning("Training data is unavailable, so the scatter plot cannot be rendered.")

    labels = metadata.get("labels")
    if labels is not None and len(labels) == len(data_df):
        data_df = data_df.copy()
        data_df["Cluster ID"] = labels

    st.sidebar.header("Customer Profile")

    def slider_bounds(series: pd.Series, default_min: float, default_max: float) -> tuple[float, float]:
        if series.empty:
            return default_min, default_max
        lower = float(series.min())
        upper = float(series.max())
        if lower == upper:
            upper += 1.0
        return lower, upper

    income_min, income_max = slider_bounds(data_df.get(income_col, pd.Series(dtype=float)), 15.0, 150.0)
    spending_min, spending_max = slider_bounds(data_df.get(spending_col, pd.Series(dtype=float)), 1.0, 100.0)

    annual_income = st.sidebar.slider(income_col, float(income_min), float(income_max), float(np.mean([income_min, income_max])))
    spending_score = st.sidebar.slider(spending_col, float(spending_min), float(spending_max), float(np.mean([spending_min, spending_max])))

    customer_features = pd.DataFrame(
        [[annual_income, spending_score]],
        columns=feature_names,
    )
    predicted_cluster = int(model.predict(customer_features)[0])

    st.metric(label="Predicted Cluster ID", value=str(predicted_cluster))

    if not data_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        if "Cluster ID" in data_df:
            scatter = ax.scatter(
                data_df[income_col],
                data_df[spending_col],
                c=data_df["Cluster ID"],
                cmap="tab10",
                alpha=0.7,
                edgecolor="white",
                linewidth=0.5,
            )
            cbar = fig.colorbar(scatter, ax=ax, label="Cluster ID")
        else:
            ax.scatter(
                data_df[income_col],
                data_df[spending_col],
                alpha=0.7,
                edgecolor="white",
                linewidth=0.5,
            )

        ax.scatter(
            annual_income,
            spending_score,
            color="black",
            s=140,
            marker="*",
            label="Predicted Customer",
            edgecolor="white",
            linewidth=1.0,
        )

        ax.set_xlabel(income_col)
        ax.set_ylabel(spending_col)
        ax.set_title("Simulated Customer Segments")
        ax.legend(loc="upper right")
        st.pyplot(fig)
