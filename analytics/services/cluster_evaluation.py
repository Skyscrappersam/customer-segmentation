from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from analytics.services.ml_segmentation import prepare_ml_data


def evaluate_clusters(
    min_clusters=2,
    max_clusters=10,
):
    """
    Evaluate different K values using:
    - Inertia (Elbow Method)
    - Silhouette Score
    """

    df = prepare_ml_data()

    if df.empty:
        return []

    features = [
        "recency",
        "frequency",
        "monetary",
    ]

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        df[features]
    )

    results = []

    for k in range(
        min_clusters,
        max_clusters + 1
    ):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        labels = model.fit_predict(
            scaled_features
        )

        silhouette = silhouette_score(
            scaled_features,
            labels,
        )

        results.append(
            {
                "k": k,
                "inertia": round(
                    model.inertia_,
                    2,
                ),
                "silhouette_score": round(
                    silhouette,
                    4,
                ),
            }
        )

    return results