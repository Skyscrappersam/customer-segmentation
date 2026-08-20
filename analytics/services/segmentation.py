from analytics.services.rfm_analysis import calculate_rfm


def classify_customer(row):
    """
    Assign a meaningful business segment
    based on RFM scores.
    """

    r = row["R_score"]
    f = row["F_score"]
    m = row["M_score"]

    total = row["RFM_total"]

    # ---------------------------------------------
    # Champions
    # ---------------------------------------------

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    # ---------------------------------------------
    # Loyal Customers
    # ---------------------------------------------

    if r >= 3 and f >= 4 and m >= 3:
        return "Loyal Customers"

    # ---------------------------------------------
    # Potential Loyalists
    # ---------------------------------------------

    if r >= 4 and f >= 2 and m >= 2:
        return "Potential Loyalists"

    # ---------------------------------------------
    # New / Active Customers
    # ---------------------------------------------

    if r >= 4 and f <= 2:
        return "New Customers"

    # ---------------------------------------------
    # Big Spenders
    # ---------------------------------------------

    if m >= 5 and r >= 2:
        return "Big Spenders"

    # ---------------------------------------------
    # At Risk
    # ---------------------------------------------

    if r <= 2 and f >= 3:
        return "At Risk"

    # ---------------------------------------------
    # Lost Customers
    # ---------------------------------------------

    if r <= 2 and f <= 2 and m <= 2:
        return "Lost Customers"

    # ---------------------------------------------
    # General customers
    # ---------------------------------------------

    if total >= 8:
        return "Promising Customers"

    return "Needs Attention"


def generate_segments():
    """
    Calculate RFM and assign business segments.
    """

    df = calculate_rfm()

    if df.empty:
        return df

    df["segment"] = df.apply(
        classify_customer,
        axis=1
    )

    return df