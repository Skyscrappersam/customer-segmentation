import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from analytics.services.rfm_analysis import calculate_rfm


# =========================================================
# PREPARE ML DATA
# =========================================================

def prepare_ml_data():
    """
    Prepare customer RFM data for machine learning.

    The clustering model uses:
        - Recency
        - Frequency
        - Monetary

    Returns a DataFrame containing customer information
    and the three ML features.
    """

    df = calculate_rfm()

    if df is None or df.empty:
        return pd.DataFrame()

    features = [
        "recency",
        "frequency",
        "monetary",
    ]

    required_columns = [
        "customer_id",
        "name",
        "recency",
        "frequency",
        "monetary",
    ]

    # -----------------------------------------------------
    # Check required columns
    # -----------------------------------------------------

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return pd.DataFrame()

    ml_data = df[
        required_columns
    ].copy()

    # -----------------------------------------------------
    # Convert ML features to numeric values
    # -----------------------------------------------------

    for column in features:

        ml_data[column] = pd.to_numeric(
            ml_data[column],
            errors="coerce",
        )

    # -----------------------------------------------------
    # Replace infinite values
    # -----------------------------------------------------

    ml_data[features] = ml_data[
        features
    ].replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    # -----------------------------------------------------
    # Fill missing values
    # -----------------------------------------------------

    for column in features:

        median_value = ml_data[
            column
        ].median()

        if pd.isna(median_value):
            median_value = 0

        ml_data[column] = (
            ml_data[column]
            .fillna(median_value)
        )

    return ml_data


# =========================================================
# RUN K-MEANS
# =========================================================

def run_kmeans(n_clusters=3):
    """
    Run K-Means clustering on customer RFM data.

    Default:
        3 clusters

    The three clusters are later converted into:
        - High-Value Customers
        - At Risk Customers
        - Regular Active Customers
    """

    df = prepare_ml_data()

    if df.empty:
        return df, None

    features = [
        "recency",
        "frequency",
        "monetary",
    ]

    # -----------------------------------------------------
    # Make sure requested cluster count is valid
    # -----------------------------------------------------

    if len(df) < 2:
        return df, None

    n_clusters = int(n_clusters)

    n_clusters = max(
        2,
        min(
            n_clusters,
            len(df),
        ),
    )

    # -----------------------------------------------------
    # Feature scaling
    # -----------------------------------------------------

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        df[features]
    )

    # -----------------------------------------------------
    # K-Means model
    # -----------------------------------------------------

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
    )

    df["cluster"] = model.fit_predict(
        scaled_features
    )

    return df, model


# =========================================================
# PROFILE CLUSTERS
# =========================================================

def profile_clusters(df):
    """
    Create a statistical profile for each
    machine-learning cluster.

    The profile contains:
        - Number of customers
        - Average recency
        - Average frequency
        - Average monetary value
    """

    if (
        df is None
        or df.empty
        or "cluster" not in df.columns
    ):
        return pd.DataFrame()

    profile = (
        df.groupby("cluster")
        .agg(
            customers=(
                "customer_id",
                "count",
            ),

            avg_recency=(
                "recency",
                "mean",
            ),

            avg_frequency=(
                "frequency",
                "mean",
            ),

            avg_monetary=(
                "monetary",
                "mean",
            ),
        )
        .round(2)
    )

    return profile