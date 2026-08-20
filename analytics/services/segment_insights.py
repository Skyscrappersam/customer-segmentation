from collections import defaultdict


def generate_segment_insights(
    rfm_df=None,
    ml_df=None,
):
    """
    Generate business insights for RFM and
    machine-learning customer segments.

    This service keeps advanced analytics logic
    separate from views.py.
    """

    insights = {
        "rfm": [],
        "ml": [],
        "summary": {},
    }

    # =====================================================
    # RFM SEGMENT INSIGHTS
    # =====================================================

    if (
        rfm_df is not None
        and not rfm_df.empty
        and "segment" in rfm_df.columns
    ):

        for segment_name, group in rfm_df.groupby(
            "segment"
        ):

            customer_count = len(group)

            # ---------------------------------------------
            # Spending
            # ---------------------------------------------

            average_spending = 0

            if "monetary" in group.columns:

                values = group["monetary"].dropna()

                if not values.empty:
                    average_spending = float(
                        values.mean()
                    )

            elif "total_spending" in group.columns:

                values = group[
                    "total_spending"
                ].dropna()

                if not values.empty:
                    average_spending = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Frequency
            # ---------------------------------------------

            average_frequency = 0

            if "frequency" in group.columns:

                values = group["frequency"].dropna()

                if not values.empty:
                    average_frequency = float(
                        values.mean()
                    )

            elif "purchase_frequency" in group.columns:

                values = group[
                    "purchase_frequency"
                ].dropna()

                if not values.empty:
                    average_frequency = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Satisfaction
            # ---------------------------------------------

            average_satisfaction = 0

            if "customer_satisfaction" in group.columns:

                values = group[
                    "customer_satisfaction"
                ].dropna()

                if not values.empty:
                    average_satisfaction = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Business Recommendation
            # ---------------------------------------------

            segment_lower = str(
                segment_name
            ).lower()

            if (
                "champion" in segment_lower
                or "loyal" in segment_lower
            ):

                recommendation = (
                    "Reward loyal customers with "
                    "exclusive offers, loyalty benefits "
                    "and personalized recommendations."
                )

            elif (
                "new" in segment_lower
                or "recent" in segment_lower
            ):

                recommendation = (
                    "Focus on onboarding, engagement "
                    "and encouraging the next purchase."
                )

            elif (
                "at risk" in segment_lower
                or "risk" in segment_lower
            ):

                recommendation = (
                    "Launch targeted retention campaigns "
                    "and personalized incentives."
                )

            elif (
                "lost" in segment_lower
                or "hibernating" in segment_lower
            ):

                recommendation = (
                    "Use reactivation campaigns and "
                    "limited-time offers to bring customers back."
                )

            elif "potential" in segment_lower:

                recommendation = (
                    "Encourage customers to increase "
                    "purchase frequency and spending."
                )

            else:

                recommendation = (
                    "Monitor customer behaviour and use "
                    "targeted offers to improve engagement."
                )

            insights["rfm"].append(
                {
                    "segment": str(segment_name),
                    "customer_count": customer_count,
                    "average_spending": round(
                        average_spending,
                        2
                    ),
                    "average_frequency": round(
                        average_frequency,
                        2
                    ),
                    "average_satisfaction": round(
                        average_satisfaction,
                        2
                    ),
                    "recommendation": recommendation,
                }
            )

    # =====================================================
    # MACHINE LEARNING SEGMENT INSIGHTS
    # =====================================================

    if (
        ml_df is not None
        and not ml_df.empty
        and "ml_segment" in ml_df.columns
    ):

        for segment_name, group in ml_df.groupby(
            "ml_segment"
        ):

            customer_count = len(group)

            # ---------------------------------------------
            # Average Spending
            # ---------------------------------------------

            average_spending = 0

            if "total_spending" in group.columns:

                values = group[
                    "total_spending"
                ].dropna()

                if not values.empty:

                    average_spending = float(
                        values.mean()
                    )

            elif "monetary" in group.columns:

                values = group[
                    "monetary"
                ].dropna()

                if not values.empty:

                    average_spending = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Average Frequency
            # ---------------------------------------------

            average_frequency = 0

            if "purchase_frequency" in group.columns:

                values = group[
                    "purchase_frequency"
                ].dropna()

                if not values.empty:

                    average_frequency = float(
                        values.mean()
                    )

            elif "frequency" in group.columns:

                values = group[
                    "frequency"
                ].dropna()

                if not values.empty:

                    average_frequency = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Satisfaction
            # ---------------------------------------------

            average_satisfaction = 0

            if "customer_satisfaction" in group.columns:

                values = group[
                    "customer_satisfaction"
                ].dropna()

                if not values.empty:

                    average_satisfaction = float(
                        values.mean()
                    )

            # ---------------------------------------------
            # Determine Segment Type
            # ---------------------------------------------

            if (
                average_spending >= 20000
                and average_frequency >= 10
            ):

                segment_type = "High Value"

                recommendation = (
                    "Prioritize retention, loyalty rewards "
                    "and premium customer experiences."
                )

            elif (
                average_spending >= 10000
                or average_frequency >= 8
            ):

                segment_type = "Potential Value"

                recommendation = (
                    "Encourage customers to increase "
                    "their spending and purchase frequency."
                )

            elif average_frequency <= 3:

                segment_type = "Low Engagement"

                recommendation = (
                    "Use personalized campaigns and "
                    "incentives to increase engagement."
                )

            else:

                segment_type = "Regular"

                recommendation = (
                    "Maintain engagement through "
                    "personalized offers and recommendations."
                )

            insights["ml"].append(
                {
                    "segment": str(segment_name),
                    "customer_count": customer_count,
                    "segment_type": segment_type,
                    "average_spending": round(
                        average_spending,
                        2
                    ),
                    "average_frequency": round(
                        average_frequency,
                        2
                    ),
                    "average_satisfaction": round(
                        average_satisfaction,
                        2
                    ),
                    "recommendation": recommendation,
                }
            )

    # =====================================================
    # SUMMARY
    # =====================================================

    total_rfm_segments = len(
        insights["rfm"]
    )

    total_ml_segments = len(
        insights["ml"]
    )

    insights["summary"] = {
        "total_rfm_segments":
            total_rfm_segments,

        "total_ml_segments":
            total_ml_segments,

        "rfm_available":
            total_rfm_segments > 0,

        "ml_available":
            total_ml_segments > 0,
    }

    return insights