"""
CustomerSeg - Customer Insights & Recommendations

This module generates business-oriented insights and
recommendations for individual customers.

The logic is rule-based and uses:
    - RFM segment
    - Machine-learning segment
    - Total spending
    - Purchase frequency
    - Customer satisfaction
    - Annual income
    - Preferred category
"""


# =========================================================
# SAFE HELPERS
# =========================================================

def _safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """
    Safely convert a value to integer.
    """

    try:
        if value is None:
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


def _clean_text(value, default="Not specified"):
    """
    Safely convert a value to readable text.
    """

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


# =========================================================
# CUSTOMER VALUE
# =========================================================

def determine_customer_value(
    total_spending,
    purchase_frequency,
    satisfaction,
):
    """
    Determine an overall customer value level.
    """

    spending = _safe_float(total_spending)
    frequency = _safe_int(purchase_frequency)
    satisfaction = _safe_float(satisfaction)

    if (
        spending >= 50000
        and frequency >= 15
        and satisfaction >= 8
    ):
        return "Very High Value"

    if (
        spending >= 30000
        and frequency >= 10
    ):
        return "High Value"

    if (
        spending >= 15000
        or frequency >= 8
    ):
        return "Medium Value"

    return "Low Value"


# =========================================================
# CUSTOMER RISK
# =========================================================

def determine_risk_level(
    ml_segment=None,
    rfm_segment=None,
    satisfaction=None,
    purchase_frequency=None,
):
    """
    Determine customer risk level.
    """

    ml = _clean_text(
        ml_segment,
        "",
    ).lower()

    rfm = _clean_text(
        rfm_segment,
        "",
    ).lower()

    satisfaction_value = _safe_float(
        satisfaction
    )

    frequency = _safe_int(
        purchase_frequency
    )

    # Strong ML signal
    if "at risk" in ml:
        return "High Risk"

    # RFM signal
    if (
        "at risk" in rfm
        or "hibernating" in rfm
        or "lost" in rfm
    ):
        return "High Risk"

    # Behavioural signals
    if (
        satisfaction_value > 0
        and satisfaction_value <= 4
    ):
        return "High Risk"

    if frequency <= 3:
        return "Medium Risk"

    if (
        satisfaction_value > 0
        and satisfaction_value <= 6
    ):
        return "Medium Risk"

    return "Low Risk"


# =========================================================
# RECOMMENDED ACTION
# =========================================================

def determine_recommended_action(
    ml_segment=None,
    rfm_segment=None,
    total_spending=None,
    purchase_frequency=None,
    satisfaction=None,
):
    """
    Generate the primary recommended business action.
    """

    ml = _clean_text(
        ml_segment,
        "",
    ).lower()

    rfm = _clean_text(
        rfm_segment,
        "",
    ).lower()

    spending = _safe_float(
        total_spending
    )

    frequency = _safe_int(
        purchase_frequency
    )

    satisfaction_value = _safe_float(
        satisfaction
    )

    # -----------------------------------------------------
    # At Risk
    # -----------------------------------------------------

    if "at risk" in ml or "at risk" in rfm:

        return (
            "Launch a targeted retention campaign "
            "with a personalized offer to encourage "
            "the customer to return."
        )

    # -----------------------------------------------------
    # High Value
    # -----------------------------------------------------

    if "high-value" in ml:

        return (
            "Prioritize this customer for premium "
            "offers, loyalty benefits and personalized "
            "upselling opportunities."
        )

    # -----------------------------------------------------
    # Very high spending
    # -----------------------------------------------------

    if spending >= 50000:

        return (
            "Treat this customer as a high-value account "
            "and focus on loyalty, premium products and "
            "relationship building."
        )

    # -----------------------------------------------------
    # Low satisfaction
    # -----------------------------------------------------

    if (
        satisfaction_value > 0
        and satisfaction_value <= 5
    ):

        return (
            "Investigate the customer's experience and "
            "provide targeted support or service recovery "
            "before attempting aggressive upselling."
        )

    # -----------------------------------------------------
    # Frequent customer
    # -----------------------------------------------------

    if frequency >= 15:

        return (
            "Encourage repeat purchases through loyalty "
            "rewards, personalized recommendations and "
            "cross-selling."
        )

    # -----------------------------------------------------
    # Low activity
    # -----------------------------------------------------

    if frequency <= 3:

        return (
            "Use a re-engagement campaign to increase "
            "purchase frequency and bring the customer "
            "back into the buying cycle."
        )

    # -----------------------------------------------------
    # Default
    # -----------------------------------------------------

    return (
        "Maintain regular engagement and use personalized "
        "offers to gradually increase customer value."
    )


# =========================================================
# MARKETING STRATEGY
# =========================================================

def determine_marketing_strategy(
    ml_segment=None,
    rfm_segment=None,
    total_spending=None,
    purchase_frequency=None,
    satisfaction=None,
):
    """
    Generate a suitable marketing strategy.
    """

    ml = _clean_text(
        ml_segment,
        "",
    ).lower()

    rfm = _clean_text(
        rfm_segment,
        "",
    ).lower()

    spending = _safe_float(
        total_spending
    )

    frequency = _safe_int(
        purchase_frequency
    )

    satisfaction_value = _safe_float(
        satisfaction
    )

    # At Risk
    if "at risk" in ml or "at risk" in rfm:

        return (
            "Retention marketing: personalized discounts, "
            "reminders, win-back campaigns and targeted "
            "re-engagement messages."
        )

    # High Value
    if "high-value" in ml or spending >= 50000:

        return (
            "Premium marketing: VIP benefits, exclusive "
            "products, early access, loyalty rewards and "
            "personalized recommendations."
        )

    # Frequent
    if frequency >= 15:

        return (
            "Loyalty marketing: reward repeat purchases "
            "and introduce cross-selling opportunities."
        )

    # Low satisfaction
    if (
        satisfaction_value > 0
        and satisfaction_value <= 5
    ):

        return (
            "Customer-experience marketing: collect feedback, "
            "resolve issues and rebuild trust before promoting "
            "additional products."
        )

    # Low activity
    if frequency <= 3:

        return (
            "Re-engagement marketing: personalized reminders, "
            "limited-time offers and product recommendations."
        )

    # Default
    return (
        "Personalized marketing: recommend relevant products "
        "and use targeted promotions to increase engagement."
    )


# =========================================================
# UPSELLING OPPORTUNITY
# =========================================================

def determine_upsell_opportunity(
    total_spending=None,
    purchase_frequency=None,
    satisfaction=None,
    ml_segment=None,
):
    """
    Determine the customer's upselling opportunity.
    """

    spending = _safe_float(
        total_spending
    )

    frequency = _safe_int(
        purchase_frequency
    )

    satisfaction_value = _safe_float(
        satisfaction
    )

    ml = _clean_text(
        ml_segment,
        "",
    ).lower()

    # Avoid aggressive upselling to risky customers
    if "at risk" in ml:

        return "Low — focus on retention first."

    if (
        satisfaction_value > 0
        and satisfaction_value <= 5
    ):

        return "Low — improve customer experience first."

    if (
        spending >= 50000
        and frequency >= 10
    ):

        return "Very High — strong premium and cross-sell potential."

    if (
        spending >= 30000
        or frequency >= 10
    ):

        return "High — suitable for premium products and cross-selling."

    if (
        spending >= 15000
        or frequency >= 6
    ):

        return "Medium — introduce relevant complementary products."

    return "Low — build engagement before aggressive upselling."


# =========================================================
# RETENTION RECOMMENDATION
# =========================================================

def determine_retention_recommendation(
    risk_level,
    satisfaction=None,
    purchase_frequency=None,
):
    """
    Generate a retention recommendation.
    """

    satisfaction_value = _safe_float(
        satisfaction
    )

    frequency = _safe_int(
        purchase_frequency
    )

    if risk_level == "High Risk":

        if (
            satisfaction_value > 0
            and satisfaction_value <= 4
        ):

            return (
                "Immediate attention recommended. "
                "Investigate dissatisfaction, resolve service "
                "issues and provide a personalized recovery offer."
            )

        return (
            "Run a win-back campaign with personalized offers "
            "and reminders. Monitor the customer's next purchase."
        )

    if risk_level == "Medium Risk":

        if frequency <= 3:

            return (
                "Increase engagement with personalized reminders "
                "and relevant product recommendations."
            )

        return (
            "Maintain regular communication and provide loyalty "
            "incentives to prevent the customer from becoming inactive."
        )

    return (
        "Continue loyalty-building activities and personalized "
        "engagement to maintain the customer's relationship."
    )


# =========================================================
# CUSTOMER SUMMARY
# =========================================================

def generate_customer_insights(
    *,
    total_spending=None,
    purchase_frequency=None,
    satisfaction=None,
    annual_income=None,
    preferred_category=None,
    rfm_segment=None,
    ml_segment=None,
):
    """
    Generate a complete customer insight package.

    Returns a dictionary that can be passed directly
    to a Django template.
    """

    spending = _safe_float(
        total_spending
    )

    frequency = _safe_int(
        purchase_frequency
    )

    satisfaction_value = _safe_float(
        satisfaction
    )

    income = _safe_float(
        annual_income
    )

    category = _clean_text(
        preferred_category
    )

    rfm = _clean_text(
        rfm_segment
    )

    ml = _clean_text(
        ml_segment
    )

    # -----------------------------------------------------
    # Core analysis
    # -----------------------------------------------------

    customer_value = determine_customer_value(
        spending,
        frequency,
        satisfaction_value,
    )

    risk_level = determine_risk_level(
        ml_segment=ml,
        rfm_segment=rfm,
        satisfaction=satisfaction_value,
        purchase_frequency=frequency,
    )

    recommended_action = determine_recommended_action(
        ml_segment=ml,
        rfm_segment=rfm,
        total_spending=spending,
        purchase_frequency=frequency,
        satisfaction=satisfaction_value,
    )

    marketing_strategy = determine_marketing_strategy(
        ml_segment=ml,
        rfm_segment=rfm,
        total_spending=spending,
        purchase_frequency=frequency,
        satisfaction=satisfaction_value,
    )

    upsell_opportunity = determine_upsell_opportunity(
        total_spending=spending,
        purchase_frequency=frequency,
        satisfaction=satisfaction_value,
        ml_segment=ml,
    )

    retention_recommendation = (
        determine_retention_recommendation(
            risk_level=risk_level,
            satisfaction=satisfaction_value,
            purchase_frequency=frequency,
        )
    )

    # -----------------------------------------------------
    # Spending insight
    # -----------------------------------------------------

    if spending >= 50000:

        spending_insight = (
            "The customer demonstrates very strong spending "
            "behaviour and should be considered an important "
            "revenue opportunity."
        )

    elif spending >= 30000:

        spending_insight = (
            "The customer demonstrates strong spending behaviour "
            "and has meaningful commercial value."
        )

    elif spending >= 15000:

        spending_insight = (
            "The customer has a moderate spending level with "
            "potential for further value growth."
        )

    else:

        spending_insight = (
            "The customer's spending level is relatively low "
            "and may benefit from targeted engagement."
        )

    # -----------------------------------------------------
    # Purchase insight
    # -----------------------------------------------------

    if frequency >= 15:

        purchase_insight = (
            "The customer purchases frequently and demonstrates "
            "strong engagement with the business."
        )

    elif frequency >= 8:

        purchase_insight = (
            "The customer shows regular purchasing behaviour "
            "and provides opportunities for loyalty development."
        )

    elif frequency >= 4:

        purchase_insight = (
            "The customer shows moderate purchasing activity "
            "but could potentially increase purchase frequency."
        )

    else:

        purchase_insight = (
            "The customer's purchase activity is relatively low "
            "and re-engagement may be beneficial."
        )

    # -----------------------------------------------------
    # Satisfaction insight
    # -----------------------------------------------------

    if satisfaction_value >= 8:

        satisfaction_insight = (
            "The customer reports high satisfaction, indicating "
            "a positive customer experience."
        )

    elif satisfaction_value >= 6:

        satisfaction_insight = (
            "The customer reports moderate satisfaction and "
            "there may be opportunities to improve the experience."
        )

    elif satisfaction_value > 0:

        satisfaction_insight = (
            "The customer reports relatively low satisfaction "
            "and should receive additional attention."
        )

    else:

        satisfaction_insight = (
            "Customer satisfaction data is unavailable."
        )

    # -----------------------------------------------------
    # Income relationship
    # -----------------------------------------------------

    if income > 0 and spending > 0:

        spending_income_ratio = (
            spending / income * 100
        )

    else:

        spending_income_ratio = 0

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        # Core classification
        "customer_value": customer_value,
        "risk_level": risk_level,

        # Recommendations
        "recommended_action": recommended_action,
        "marketing_strategy": marketing_strategy,
        "upsell_opportunity": upsell_opportunity,
        "retention_recommendation": retention_recommendation,

        # Insights
        "spending_insight": spending_insight,
        "purchase_insight": purchase_insight,
        "satisfaction_insight": satisfaction_insight,

        # Customer context
        "category": category,
        "rfm_segment": rfm,
        "ml_segment": ml,

        # Calculated metric
        "spending_income_ratio": round(
            spending_income_ratio,
            2,
        ),

    }