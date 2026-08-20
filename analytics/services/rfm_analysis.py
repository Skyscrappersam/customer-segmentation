import pandas as pd

from django.utils import timezone

from analytics.models import Customer


# =========================================================
# CUSTOMER DATAFRAME
# =========================================================

def get_customer_dataframe():
    """
    Convert all Customer records into a Pandas DataFrame.

    This function only prepares the customer data.
    RFM calculations are handled by calculate_rfm().
    """

    customers = Customer.objects.all().values(
        "customer_id",
        "name",
        "age",
        "gender",
        "annual_income",
        "total_spending",
        "purchase_frequency",
        "last_purchase_date",
        "average_order_value",
        "discount_usage",
        "preferred_category",
        "customer_satisfaction",
    )

    df = pd.DataFrame(list(customers))

    return df


# =========================================================
# SAFE QUINTILE SCORING
# =========================================================

def _quintile_score(
    series,
    ascending=True,
):
    """
    Convert a numeric series into a 1-5 quintile score.

    ascending=True:
        Lower values receive lower scores,
        higher values receive higher scores.

    ascending=False:
        Higher values receive lower scores,
        lower values receive higher scores.

    The ranking step prevents qcut from failing when
    many customers have identical values.
    """

    numeric_series = pd.to_numeric(
        series,
        errors="coerce",
    ).fillna(0)

    ranked = numeric_series.rank(
        method="first",
        ascending=ascending,
    )

    if len(ranked) == 0:
        return pd.Series(
            dtype="int64",
            index=series.index,
        )

    try:

        score = pd.qcut(
            ranked,
            q=5,
            labels=[1, 2, 3, 4, 5],
        )

        return score.astype(int)

    except (
        ValueError,
        TypeError,
    ):

        # Fallback for very small datasets.
        minimum = ranked.min()
        maximum = ranked.max()

        if minimum == maximum:

            return pd.Series(
                3,
                index=series.index,
                dtype="int64",
            )

        normalized = (
            (ranked - minimum)
            / (maximum - minimum)
        )

        score = (
            normalized * 4
        ).round().astype(int) + 1

        return score.clip(
            lower=1,
            upper=5,
        )


# =========================================================
# RFM CALCULATION
# =========================================================

def calculate_rfm():
    """
    Calculate Recency, Frequency and Monetary
    values and their RFM scores for all customers.

    Returns a Pandas DataFrame containing:

        recency
        frequency
        monetary

        R_score
        F_score
        M_score

        RFM_score
        RFM_total
    """

    df = get_customer_dataframe()

    if df.empty:
        return df

    # -----------------------------------------------------
    # PREPARE DATE
    # -----------------------------------------------------

    df["last_purchase_date"] = pd.to_datetime(
        df["last_purchase_date"],
        errors="coerce",
    )

    today = pd.Timestamp(
        timezone.now().date()
    )

    # -----------------------------------------------------
    # RECENCY
    # -----------------------------------------------------

    df["recency"] = (
        today
        - df["last_purchase_date"]
    ).dt.days

    # If dates are missing, use the median.
    if df["recency"].notna().any():

        median_recency = df[
            "recency"
        ].median()

        df["recency"] = (
            df["recency"]
            .fillna(median_recency)
        )

    else:

        df["recency"] = (
            df["recency"]
            .fillna(0)
        )

    # Future dates should not create negative recency.
    df["recency"] = df[
        "recency"
    ].clip(
        lower=0
    )

    # -----------------------------------------------------
    # FREQUENCY
    # -----------------------------------------------------

    df["frequency"] = pd.to_numeric(
        df["purchase_frequency"],
        errors="coerce",
    ).fillna(0)

    df["frequency"] = df[
        "frequency"
    ].clip(
        lower=0
    )

    # -----------------------------------------------------
    # MONETARY
    # -----------------------------------------------------

    df["monetary"] = pd.to_numeric(
        df["total_spending"],
        errors="coerce",
    ).fillna(0)

    df["monetary"] = df[
        "monetary"
    ].clip(
        lower=0
    )

    # -----------------------------------------------------
    # RFM SCORING
    # -----------------------------------------------------

    # Recency:
    # Lower number of days = better.
    #
    # Therefore the lowest recency gets score 5
    # and the highest recency gets score 1.

    df["R_score"] = _quintile_score(
        df["recency"],
        ascending=True,
    )

    df["R_score"] = (
        6 - df["R_score"]
    )

    # Frequency:
    # Higher frequency = better.

    df["F_score"] = _quintile_score(
        df["frequency"],
        ascending=True,
    )

    # Monetary:
    # Higher spending = better.

    df["M_score"] = _quintile_score(
        df["monetary"],
        ascending=True,
    )

    # -----------------------------------------------------
    # COMBINED RFM SCORE
    # -----------------------------------------------------

    df["RFM_score"] = (
        df["R_score"].astype(str)
        + df["F_score"].astype(str)
        + df["M_score"].astype(str)
    )

    # -----------------------------------------------------
    # TOTAL RFM SCORE
    # -----------------------------------------------------

    df["RFM_total"] = (
        df["R_score"]
        + df["F_score"]
        + df["M_score"]
    )

    return df