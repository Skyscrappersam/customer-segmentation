import pandas as pd


# =========================================================
# LABEL CLUSTERS
# =========================================================

def label_clusters(profile):
    """
    Automatically assign meaningful business labels
    to K-Means customer clusters.

    Labels:
        High-Value Customers
        At Risk Customers
        Regular Active Customers

    High-Value:
        Strong monetary value and purchase frequency.

    At Risk:
        Customers with the highest average recency.
        Higher recency means the customer has not
        purchased recently.

    Regular Active:
        Remaining customers after identifying the
        high-value and at-risk clusters.
    """

    # -----------------------------------------------------
    # Validate profile
    # -----------------------------------------------------

    if profile is None or profile.empty:
        return {}

    profile = profile.copy()

    required_columns = [
        "avg_recency",
        "avg_frequency",
        "avg_monetary",
    ]

    for column in required_columns:

        if column not in profile.columns:
            return {}

        profile[column] = pd.to_numeric(
            profile[column],
            errors="coerce",
        )

    profile = profile.dropna(
        subset=required_columns
    )

    if profile.empty:
        return {}

    labels = {}

    # =====================================================
    # HIGH-VALUE CUSTOMERS
    # =====================================================

    # High-value customers should have strong
    # spending and purchase frequency.

    monetary_rank = profile[
        "avg_monetary"
    ].rank(
        method="average",
        pct=True,
    )

    frequency_rank = profile[
        "avg_frequency"
    ].rank(
        method="average",
        pct=True,
    )

    high_value_score = (
        monetary_rank
        + frequency_rank
    )

    high_value_cluster = (
        high_value_score.idxmax()
    )

    labels[
        high_value_cluster
    ] = "High-Value Customers"

    # =====================================================
    # AT-RISK CUSTOMERS
    # =====================================================

    # Remove the high-value cluster.

    remaining = profile.drop(
        index=high_value_cluster
    )

    if not remaining.empty:

        # Recency is the PRIMARY signal.
        #
        # Higher recency = customer has been inactive
        # for a longer period.
        #
        # Therefore, the cluster with the highest
        # average recency is considered At Risk.

        at_risk_cluster = (
            remaining[
                "avg_recency"
            ].idxmax()
        )

        labels[
            at_risk_cluster
        ] = "At Risk Customers"

    # =====================================================
    # REGULAR ACTIVE CUSTOMERS
    # =====================================================

    for cluster_id in profile.index:

        if cluster_id not in labels:

            labels[
                cluster_id
            ] = "Regular Active Customers"

    return labels


# =========================================================
# APPLY CLUSTER LABELS
# =========================================================

def apply_cluster_labels(df, profile):
    """
    Add business-friendly machine-learning segment
    names to the customer dataframe.
    """

    if df is None or df.empty:
        return df

    labels = label_clusters(
        profile
    )

    df = df.copy()

    df["ml_segment"] = (
        df["cluster"].map(
            labels
        )
    )

    return df