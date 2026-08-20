import json
from datetime import date, datetime
from io import BytesIO
import csv

import numpy as np
import pandas as pd
import plotly.express as px

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from analytics.models import Customer

from analytics.services.segmentation import generate_segments
from analytics.services.ml_segmentation import (
    run_kmeans,
    profile_clusters,
)
from analytics.services.cluster_labeling import (
    apply_cluster_labels,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_customer_queryset():
    """
    Return all customers with calculated RFM and ML
    segments attached dynamically.
    """

    customers = list(
        Customer.objects.all()
    )

    if not customers:
        return customers

    # -----------------------------------------------------
    # RFM SEGMENTATION
    # -----------------------------------------------------

    try:

        rfm_df = generate_segments()

        if (
            rfm_df is not None
            and not rfm_df.empty
            and "customer_id" in rfm_df.columns
        ):

            rfm_lookup = {}

            for _, row in rfm_df.iterrows():

                customer_id = str(
                    row["customer_id"]
                )

                rfm_lookup[customer_id] = {
                    "rfm_segment": (
                        str(
                            row.get(
                                "segment",
                                ""
                            )
                        )
                        if pd.notna(
                            row.get(
                                "segment",
                                None
                            )
                        )
                        else ""
                    ),

                    "recency": row.get(
                        "recency",
                        None
                    ),

                    "frequency": row.get(
                        "frequency",
                        None
                    ),

                    "monetary": row.get(
                        "monetary",
                        None
                    ),

                    "R_score": row.get(
                        "R_score",
                        None
                    ),

                    "F_score": row.get(
                        "F_score",
                        None
                    ),

                    "M_score": row.get(
                        "M_score",
                        None
                    ),

                    "RFM_score": row.get(
                        "RFM_score",
                        None
                    ),

                    "RFM_total": row.get(
                        "RFM_total",
                        None
                    ),
                }

            for customer in customers:

                data = rfm_lookup.get(
                    str(
                        customer.customer_id
                    ),
                    {}
                )

                customer.rfm_segment = data.get(
                    "rfm_segment",
                    ""
                )

                customer.recency = data.get(
                    "recency"
                )

                customer.frequency = data.get(
                    "frequency"
                )

                customer.monetary = data.get(
                    "monetary"
                )

                customer.R_score = data.get(
                    "R_score"
                )

                customer.F_score = data.get(
                    "F_score"
                )

                customer.M_score = data.get(
                    "M_score"
                )

                customer.RFM_score = data.get(
                    "RFM_score"
                )

                customer.RFM_total = data.get(
                    "RFM_total"
                )

    except Exception as error:

        print(
            "RFM LOOKUP ERROR:",
            error
        )

        for customer in customers:

            customer.rfm_segment = ""

            customer.recency = None
            customer.frequency = None
            customer.monetary = None

            customer.R_score = None
            customer.F_score = None
            customer.M_score = None

            customer.RFM_score = None
            customer.RFM_total = None

    # -----------------------------------------------------
    # MACHINE LEARNING SEGMENTATION
    # -----------------------------------------------------

    try:

        ml_df, ml_model = run_kmeans(
            n_clusters=3
        )

        if (
            ml_df is not None
            and not ml_df.empty
        ):

            profile = profile_clusters(
                ml_df
            )

            ml_df = apply_cluster_labels(
                ml_df,
                profile
            )

            if (
                "customer_id" in ml_df.columns
                and "ml_segment" in ml_df.columns
            ):

                ml_lookup = {}

                for _, row in ml_df.iterrows():

                    customer_id = str(
                        row["customer_id"]
                    )

                    ml_segment = row.get(
                        "ml_segment",
                        ""
                    )

                    ml_lookup[
                        customer_id
                    ] = (
                        str(
                            ml_segment
                        )
                        if pd.notna(
                            ml_segment
                        )
                        else ""
                    )

                for customer in customers:

                    customer.ml_segment = (
                        ml_lookup.get(
                            str(
                                customer.customer_id
                            ),
                            ""
                        )
                    )

    except Exception as error:

        print(
            "ML LOOKUP ERROR:",
            error
        )

        for customer in customers:
            customer.ml_segment = ""

    return customers


# =========================================================
# FILTERS
# =========================================================

def apply_customer_filters(
    request,
    customers,
):

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:

        search_lower = search.lower()

        customers = [
            customer
            for customer in customers
            if (
                search_lower
                in str(
                    customer.customer_id
                    or ""
                ).lower()
                or
                search_lower
                in str(
                    customer.name
                    or ""
                ).lower()
            )
        ]

    # -----------------------------------------------------
    # GENDER
    # -----------------------------------------------------

    gender = request.GET.get(
        "gender",
        "",
    ).strip()

    if gender:

        customers = [
            customer
            for customer in customers
            if str(
                customer.gender
                or ""
            ).strip().lower()
            == gender.lower()
        ]

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category = request.GET.get(
        "preferred_category",
        "",
    ).strip()

    if category:

        customers = [
            customer
            for customer in customers
            if str(
                customer.preferred_category
                or ""
            ).strip()
            == category
        ]

    # -----------------------------------------------------
    # MIN SPENDING
    # -----------------------------------------------------

    min_spending = request.GET.get(
        "min_spending",
        "",
    ).strip()

    if min_spending:

        try:

            minimum = float(
                min_spending
            )

            customers = [
                customer
                for customer in customers
                if float(
                    customer.total_spending
                    or 0
                ) >= minimum
            ]

        except (
            ValueError,
            TypeError,
        ):
            pass

    # -----------------------------------------------------
    # MAX SPENDING
    # -----------------------------------------------------

    max_spending = request.GET.get(
        "max_spending",
        "",
    ).strip()

    if max_spending:

        try:

            maximum = float(
                max_spending
            )

            customers = [
                customer
                for customer in customers
                if float(
                    customer.total_spending
                    or 0
                ) <= maximum
            ]

        except (
            ValueError,
            TypeError,
        ):
            pass

    # -----------------------------------------------------
    # MIN FREQUENCY
    # -----------------------------------------------------

    min_frequency = request.GET.get(
        "min_frequency",
        "",
    ).strip()

    if min_frequency:

        try:

            minimum = float(
                min_frequency
            )

            customers = [
                customer
                for customer in customers
                if float(
                    customer.purchase_frequency
                    or 0
                ) >= minimum
            ]

        except (
            ValueError,
            TypeError,
        ):
            pass

    # -----------------------------------------------------
    # MAX FREQUENCY
    # -----------------------------------------------------

    max_frequency = request.GET.get(
        "max_frequency",
        "",
    ).strip()

    if max_frequency:

        try:

            maximum = float(
                max_frequency
            )

            customers = [
                customer
                for customer in customers
                if float(
                    customer.purchase_frequency
                    or 0
                ) <= maximum
            ]

        except (
            ValueError,
            TypeError,
        ):
            pass

    # -----------------------------------------------------
    # SATISFACTION
    # -----------------------------------------------------

    satisfaction = request.GET.get(
        "satisfaction",
        "",
    ).strip()

    if satisfaction:

        try:

            selected = float(
                satisfaction
            )

            customers = [
                customer
                for customer in customers
                if (
                    customer.customer_satisfaction
                    is not None
                    and float(
                        customer.customer_satisfaction
                    ) == selected
                )
            ]

        except (
            ValueError,
            TypeError,
        ):
            pass

    # -----------------------------------------------------
    # RFM SEGMENT
    # -----------------------------------------------------

    rfm_segment = request.GET.get(
        "rfm_segment",
        "",
    ).strip()

    if rfm_segment:

        customers = [
            customer
            for customer in customers
            if str(
                getattr(
                    customer,
                    "rfm_segment",
                    "",
                )
            ) == rfm_segment
        ]

    # -----------------------------------------------------
    # ML SEGMENT
    # -----------------------------------------------------

    ml_segment = request.GET.get(
        "ml_segment",
        "",
    ).strip()

    if ml_segment:

        customers = [
            customer
            for customer in customers
            if str(
                getattr(
                    customer,
                    "ml_segment",
                    "",
                )
            ) == ml_segment
        ]

    return customers


# =========================================================
# SORTING
# =========================================================

def sort_customers(
    customers,
    sort,
    direction,
):

    allowed_fields = {
        "customer_id",
        "-customer_id",
        "name",
        "-name",
        "gender",
        "-gender",
        "preferred_category",
        "-preferred_category",
        "rfm_segment",
        "-rfm_segment",
        "ml_segment",
        "-ml_segment",
        "total_spending",
        "-total_spending",
        "purchase_frequency",
        "-purchase_frequency",
        "customer_satisfaction",
        "-customer_satisfaction",
    }

    field = sort

    if direction == "desc":

        if not field.startswith("-"):
            field = "-" + field

    else:

        field = field.lstrip("-")

    if field not in allowed_fields:

        field = "customer_id"

    reverse = field.startswith("-")

    field_name = field.lstrip("-")

    def sort_key(customer):

        value = getattr(
            customer,
            field_name,
            None
        )

        if value is None:
            return 0

        if field_name in {
            "total_spending",
            "purchase_frequency",
            "customer_satisfaction",
        }:

            try:
                return float(value)

            except (
                ValueError,
                TypeError,
            ):
                return 0

        return str(value).lower()

    return sorted(
        customers,
        key=sort_key,
        reverse=reverse,
    )


# =========================================================
# STATISTICS
# =========================================================

def get_customer_statistics(
    customers=None,
):

    if customers is None:

        customers = Customer.objects.all()

    customers = list(
        customers
    )

    spending = []
    frequency = []
    satisfaction = []
    income = []

    for customer in customers:

        try:

            if customer.total_spending is not None:
                spending.append(
                    float(
                        customer.total_spending
                    )
                )

        except (
            ValueError,
            TypeError,
        ):
            pass

        try:

            if customer.purchase_frequency is not None:
                frequency.append(
                    float(
                        customer.purchase_frequency
                    )
                )

        except (
            ValueError,
            TypeError,
        ):
            pass

        try:

            if customer.customer_satisfaction is not None:
                satisfaction.append(
                    float(
                        customer.customer_satisfaction
                    )
                )

        except (
            ValueError,
            TypeError,
        ):
            pass

        try:

            if customer.annual_income is not None:
                income.append(
                    float(
                        customer.annual_income
                    )
                )

        except (
            ValueError,
            TypeError,
        ):
            pass

    return {

        "total_customers":
            len(customers),

        "total_spending":
            sum(spending)
            if spending
            else 0,

        "average_spending":
            (
                sum(spending)
                / len(spending)
                if spending
                else 0
            ),

        "average_income":
            (
                sum(income)
                / len(income)
                if income
                else 0
            ),

        "average_frequency":
            (
                sum(frequency)
                / len(frequency)
                if frequency
                else 0
            ),

        "average_satisfaction":
            (
                sum(satisfaction)
                / len(satisfaction)
                if satisfaction
                else 0
            ),

        "maximum_spending":
            max(spending)
            if spending
            else 0,

        "minimum_spending":
            min(spending)
            if spending
            else 0,
    }


# =========================================================
# FILTER OPTIONS
# =========================================================

def get_filter_options():

    genders = list(
        Customer.objects
        .values_list(
            "gender",
            flat=True,
        )
        .distinct()
        .exclude(
            gender__isnull=True
        )
        .exclude(
            gender=""
        )
        .order_by(
            "gender"
        )
    )

    categories = list(
        Customer.objects
        .values_list(
            "preferred_category",
            flat=True,
        )
        .distinct()
        .exclude(
            preferred_category__isnull=True
        )
        .exclude(
            preferred_category=""
        )
        .order_by(
            "preferred_category"
        )
    )

    satisfaction_values = list(
        Customer.objects
        .values_list(
            "customer_satisfaction",
            flat=True,
        )
        .distinct()
        .exclude(
            customer_satisfaction__isnull=True
        )
        .order_by(
            "customer_satisfaction"
        )
    )

    return (
        genders,
        categories,
        satisfaction_values,
    )


# =========================================================
# SEGMENT OPTIONS
# =========================================================

def get_segment_options(
    customers=None,
):

    if customers is None:
        customers = get_customer_queryset()

    rfm_segments = sorted(
        {
            str(
                getattr(
                    customer,
                    "rfm_segment",
                    ""
                )
            )
            for customer in customers
            if getattr(
                customer,
                "rfm_segment",
                ""
            )
        }
    )

    ml_segments = sorted(
        {
            str(
                getattr(
                    customer,
                    "ml_segment",
                    ""
                )
            )
            for customer in customers
            if getattr(
                customer,
                "ml_segment",
                ""
            )
        }
    )

    return (
        rfm_segments,
        ml_segments,
    )


# =========================================================
# DATAFRAME
# =========================================================

def get_customer_dataframe(
    customers=None,
):

    if customers is None:

        customers = Customer.objects.all()

    if hasattr(
        customers,
        "values",
    ):

        data = list(
            customers.values(
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
        )

    else:

        data = []

        for customer in customers:

            data.append({

                "customer_id":
                    customer.customer_id,

                "name":
                    customer.name,

                "age":
                    customer.age,

                "gender":
                    customer.gender,

                "annual_income":
                    customer.annual_income,

                "total_spending":
                    customer.total_spending,

                "purchase_frequency":
                    customer.purchase_frequency,

                "last_purchase_date":
                    customer.last_purchase_date,

                "average_order_value":
                    customer.average_order_value,

                "discount_usage":
                    customer.discount_usage,

                "preferred_category":
                    customer.preferred_category,

                "customer_satisfaction":
                    customer.customer_satisfaction,
            })

    return pd.DataFrame(
        data
    )


# =========================================================
# RFM / ML DATA
# =========================================================

def get_rfm_dataframe():

    try:

        df = generate_segments()

        if df is None:
            return None

        return df

    except Exception as error:

        print(
            "RFM ERROR:",
            error
        )

        return None


def get_ml_dataframe():

    try:

        df, model = run_kmeans(
            n_clusters=3
        )

        if (
            df is None
            or df.empty
        ):
            return None

        profile = profile_clusters(
            df
        )

        df = apply_cluster_labels(
            df,
            profile
        )

        return df

    except Exception as error:

        print(
            "ML ERROR:",
            error
        )

        return None


# =========================================================
# PLOTLY JSON
# =========================================================

def make_json_safe(
    value
):

    if isinstance(
        value,
        dict
    ):

        return {
            str(key):
                make_json_safe(
                    val
                )
            for key, val in value.items()
        }

    if isinstance(
        value,
        (list, tuple)
    ):

        return [
            make_json_safe(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        np.ndarray
    ):

        return [
            make_json_safe(
                item
            )
            for item in value.tolist()
        ]

    if isinstance(
        value,
        np.generic
    ):

        return value.item()

    if isinstance(
        value,
        pd.Timestamp
    ):

        return value.isoformat()

    if isinstance(
        value,
        (datetime, date)
    ):

        return value.isoformat()

    try:

        if pd.isna(value):
            return None

    except (
        TypeError,
        ValueError,
    ):
        pass

    return value


def figure_json(
    figure
):

    if figure is None:
        return "{}"

    try:

        return json.dumps(
            make_json_safe(
                figure.to_plotly_json()
            )
        )

    except Exception as error:

        print(
            "FIGURE JSON ERROR:",
            error
        )

        return "{}"


# =========================================================
# MAIN DASHBOARD
# =========================================================

def dashboard(request):

    customers = Customer.objects.all()

    df = get_customer_dataframe(
        customers
    )

    statistics = get_customer_statistics(
        customers
    )

    total_customers = statistics[
        "total_customers"
    ]

    total_spending = statistics[
        "total_spending"
    ]

    average_spending = statistics[
        "average_spending"
    ]

    # -----------------------------------------------------
    # RFM
    # -----------------------------------------------------

    rfm_df = get_rfm_dataframe()

    rfm_counts = {}

    if (
        rfm_df is not None
        and not rfm_df.empty
        and "segment" in rfm_df.columns
    ):

        rfm_counts = (
            rfm_df[
                "segment"
            ]
            .value_counts()
            .to_dict()
        )

    # -----------------------------------------------------
    # ML
    # -----------------------------------------------------

    ml_df = get_ml_dataframe()

    ml_counts = {}

    if (
        ml_df is not None
        and not ml_df.empty
        and "ml_segment" in ml_df.columns
    ):

        ml_counts = (
            ml_df[
                "ml_segment"
            ]
            .value_counts()
            .to_dict()
        )

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    at_risk_customers = (
        rfm_counts.get(
            "At Risk",
            0,
        )
        +
        rfm_counts.get(
            "Lost Customers",
            0,
        )
    )

    high_value_customers = (
        rfm_counts.get(
            "Champions",
            0,
        )
        +
        rfm_counts.get(
            "Loyal Customers",
            0,
        )
        +
        rfm_counts.get(
            "Big Spenders",
            0,
        )
    )

    active_customers = max(
        total_customers
        - at_risk_customers,
        0,
    )

    # -----------------------------------------------------
    # RFM CHART
    # -----------------------------------------------------

    rfm_fig = px.bar(
        x=list(
            rfm_counts.keys()
        ),
        y=list(
            rfm_counts.values()
        ),
        labels={
            "x": "RFM Segment",
            "y": "Customers",
        },
        title="RFM Customer Segmentation",
    )

    rfm_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=60,
        ),
    )

    # -----------------------------------------------------
    # ML CHART
    # -----------------------------------------------------

    ml_fig = px.bar(
        x=list(
            ml_counts.keys()
        ),
        y=list(
            ml_counts.values()
        ),
        labels={
            "x": "ML Segment",
            "y": "Customers",
        },
        title="Machine Learning Customer Segmentation",
    )

    ml_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=60,
        ),
    )

    # -----------------------------------------------------
    # CATEGORY CHART
    # -----------------------------------------------------

    category_df = (
        df[
            [
                "preferred_category",
                "total_spending",
            ]
        ]
        .copy()
    )

    category_df[
        "preferred_category"
    ] = (
        category_df[
            "preferred_category"
        ]
        .fillna("Unknown")
        .astype(str)
    )

    category_df[
        "total_spending"
    ] = pd.to_numeric(
        category_df[
            "total_spending"
        ],
        errors="coerce",
    ).fillna(0)

    category_df = (
        category_df
        .groupby(
            "preferred_category",
            as_index=False,
        )[
            "total_spending"
        ]
        .sum()
    )

    category_fig = px.bar(
        category_df,
        x="preferred_category",
        y="total_spending",
        labels={
            "preferred_category":
                "Category",
            "total_spending":
                "Total Spending",
        },
        title="Spending by Category",
    )

    category_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=60,
        ),
        yaxis=dict(
            tickprefix="₹",
            separatethousands=True,
        ),
    )

    # -----------------------------------------------------
    # FREQUENCY CHART
    # -----------------------------------------------------

    frequency_df = pd.to_numeric(
        df[
            "purchase_frequency"
        ],
        errors="coerce",
    )

    frequency_df = (
        frequency_df
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
        .astype(float)
    )

    frequency_fig = px.histogram(
        x=frequency_df,
        nbins=15,
        labels={
            "x":
                "Purchase Frequency",
            "y":
                "Customers",
        },
        title="Purchase Frequency Distribution",
    )

    frequency_fig.update_layout(
        template="plotly_white",
        bargap=0.15,
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=60,
        ),
    )

    # -----------------------------------------------------
    # SATISFACTION CHART
    # -----------------------------------------------------

    satisfaction_series = pd.to_numeric(
        df[
            "customer_satisfaction"
        ],
        errors="coerce",
    )

    satisfaction_df = (
        satisfaction_series
        .dropna()
        .round()
        .astype(int)
        .value_counts()
        .sort_index()
        .reindex(
            range(1, 11),
            fill_value=0,
        )
        .reset_index()
    )

    satisfaction_df.columns = [
        "satisfaction",
        "customers",
    ]

    satisfaction_fig = px.bar(
        satisfaction_df,
        x="satisfaction",
        y="customers",
        labels={
            "satisfaction":
                "Satisfaction Score",
            "customers":
                "Customers",
        },
        title="Customer Satisfaction Distribution",
    )

    satisfaction_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=60,
        ),
        xaxis=dict(
            tickmode="linear",
            dtick=1,
        ),
    )

    # -----------------------------------------------------
    # GENDER CHART
    # -----------------------------------------------------

    gender_series = (
        df[
            "gender"
        ]
        .fillna("Unknown")
        .astype(str)
    )

    gender_df = (
        gender_series
        .value_counts()
        .reset_index()
    )

    gender_df.columns = [
        "gender",
        "customers",
    ]

    gender_fig = px.pie(
        gender_df,
        names="gender",
        values="customers",
        title="Customer Gender Distribution",
    )

    gender_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=30,
            r=30,
            t=70,
            b=30,
        ),
    )

    context = {

        "total_customers":
            total_customers,

        "total_spending":
            total_spending,

        "average_spending":
            average_spending,

        "at_risk_customers":
            at_risk_customers,

        "high_value_customers":
            high_value_customers,

        "active_customers":
            active_customers,

        "ml_at_risk_count":
            ml_counts.get(
                "At Risk Customers",
                0,
            ),

        "ml_high_value_count":
            ml_counts.get(
                "High-Value Customers",
                0,
            ),

        "ml_regular_active_count":
            ml_counts.get(
                "Regular Active Customers",
                0,
            ),

        "rfm_counts":
            rfm_counts,

        "rfm_chart":
            figure_json(
                rfm_fig
            ),

        "ml_chart":
            figure_json(
                ml_fig
            ),

        "category_chart":
            figure_json(
                category_fig
            ),

        "frequency_chart":
            figure_json(
                frequency_fig
            ),

        "satisfaction_chart":
            figure_json(
                satisfaction_fig
            ),

        "gender_chart":
            figure_json(
                gender_fig
            ),
    }

    return render(
        request,
        "analytics/dashboard.html",
        context,
    )


# =========================================================
# CUSTOMER EXPLORER
# =========================================================

def customer_explorer(request):

    all_customers = get_customer_queryset()

    customers = apply_customer_filters(
        request,
        all_customers,
    )

    sort = request.GET.get(
        "sort",
        "customer_id",
    )

    direction = request.GET.get(
        "direction",
        "asc",
    )

    customers = sort_customers(
        customers,
        sort,
        direction,
    )

    summary = get_customer_statistics(
        customers
    )

    (
        genders,
        categories,
        satisfaction_values,
    ) = get_filter_options()

    (
        rfm_segments,
        ml_segments,
    ) = get_segment_options(
        all_customers
    )

    paginator = Paginator(
        customers,
        25,
    )

    page_obj = paginator.get_page(
        request.GET.get(
            "page"
        )
    )

    filter_params = request.GET.copy()

    filter_params.pop(
        "page",
        None,
    )

    filter_query = (
        filter_params.urlencode()
    )

    context = {

        "customers":
            page_obj,

        "page_obj":
            page_obj,

        "paginator":
            paginator,

        "total_customers":
            summary[
                "total_customers"
            ],

        "total_spending":
            summary[
                "total_spending"
            ],

        "average_spending":
            summary[
                "average_spending"
            ],

        "average_frequency":
            summary[
                "average_frequency"
            ],

        "average_satisfaction":
            summary[
                "average_satisfaction"
            ],

        "filtered_customer_count":
            summary[
                "total_customers"
            ],

        "filtered_total_spending":
            summary[
                "total_spending"
            ],

        "filtered_average_spending":
            summary[
                "average_spending"
            ],

        "filtered_average_purchase_frequency":
            summary[
                "average_frequency"
            ],

        "filtered_average_satisfaction":
            summary[
                "average_satisfaction"
            ],

        "genders":
            genders,

        "categories":
            categories,

        "satisfaction_values":
            satisfaction_values,

        "rfm_segments":
            rfm_segments,

        "ml_segments":
            ml_segments,

        "current_search":
            request.GET.get(
                "search",
                "",
            ),

        "current_gender":
            request.GET.get(
                "gender",
                "",
            ),

        "current_category":
            request.GET.get(
                "preferred_category",
                "",
            ),

        "current_min_spending":
            request.GET.get(
                "min_spending",
                "",
            ),

        "current_max_spending":
            request.GET.get(
                "max_spending",
                "",
            ),

        "current_min_frequency":
            request.GET.get(
                "min_frequency",
                "",
            ),

        "current_max_frequency":
            request.GET.get(
                "max_frequency",
                "",
            ),

        "current_satisfaction":
            request.GET.get(
                "satisfaction",
                "",
            ),

        "current_rfm_segment":
            request.GET.get(
                "rfm_segment",
                "",
            ),

        "current_ml_segment":
            request.GET.get(
                "ml_segment",
                "",
            ),

        "current_sort":
            sort,

        "current_direction":
            direction,

        "filter_query":
            filter_query,

        "search":
            request.GET.get(
                "search",
                "",
            ),

        "selected_gender":
            request.GET.get(
                "gender",
                "",
            ),

        "selected_category":
            request.GET.get(
                "preferred_category",
                "",
            ),

        "min_spending":
            request.GET.get(
                "min_spending",
                "",
            ),

        "max_spending":
            request.GET.get(
                "max_spending",
                "",
            ),

        "min_frequency":
            request.GET.get(
                "min_frequency",
                "",
            ),

        "max_frequency":
            request.GET.get(
                "max_frequency",
                "",
            ),

        "selected_satisfaction":
            request.GET.get(
                "satisfaction",
                "",
            ),

        "selected_rfm_segment":
            request.GET.get(
                "rfm_segment",
                "",
            ),

        "selected_ml_segment":
            request.GET.get(
                "ml_segment",
                "",
            ),

        "selected_sort":
            sort,

        "selected_direction":
            direction,

        "satisfaction_options":
            satisfaction_values,
    }

    return render(
        request,
        "analytics/customer_explorer.html",
        context,
    )


# =========================================================
# CUSTOMER PROFILE
# =========================================================

def customer_profile(
    request,
    customer_id,
):

    customer = get_object_or_404(
        Customer,
        customer_id=customer_id
    )

    # =====================================================
    # DEFAULT RFM VALUES
    # =====================================================

    rfm_segment = ""
    recency = None
    frequency = None
    monetary = None

    r_score = None
    f_score = None
    m_score = None

    rfm_score = None
    rfm_total = None

    # =====================================================
    # GET COMPLETE RFM DATA
    # =====================================================

    try:

        rfm_df = get_rfm_dataframe()

        if (
            rfm_df is not None
            and not rfm_df.empty
            and "customer_id" in rfm_df.columns
        ):

            matching = rfm_df[
                rfm_df[
                    "customer_id"
                ].astype(str)
                == str(customer_id)
            ]

            if not matching.empty:

                row = matching.iloc[0]

                # -------------------------------------------------
                # SEGMENT
                # -------------------------------------------------

                rfm_segment = row.get(
                    "segment",
                    ""
                )

                if pd.isna(
                    rfm_segment
                ):
                    rfm_segment = ""

                # -------------------------------------------------
                # RFM RAW VALUES
                # -------------------------------------------------

                recency = row.get(
                    "recency",
                    None
                )

                frequency = row.get(
                    "frequency",
                    None
                )

                monetary = row.get(
                    "monetary",
                    None
                )

                # -------------------------------------------------
                # RFM SCORES
                # -------------------------------------------------

                r_score = row.get(
                    "R_score",
                    None
                )

                f_score = row.get(
                    "F_score",
                    None
                )

                m_score = row.get(
                    "M_score",
                    None
                )

                rfm_score = row.get(
                    "RFM_score",
                    None
                )

                rfm_total = row.get(
                    "RFM_total",
                    None
                )

                # -------------------------------------------------
                # CONVERT NUMPY/PANDAS VALUES
                # -------------------------------------------------

                if pd.isna(recency):
                    recency = None

                if pd.isna(frequency):
                    frequency = None

                if pd.isna(monetary):
                    monetary = None

                if pd.isna(r_score):
                    r_score = None

                if pd.isna(f_score):
                    f_score = None

                if pd.isna(m_score):
                    m_score = None

                if pd.isna(rfm_score):
                    rfm_score = None

                if pd.isna(rfm_total):
                    rfm_total = None

                # -------------------------------------------------
                # CLEAN TYPES
                # -------------------------------------------------

                if recency is not None:
                    recency = int(
                        recency
                    )

                if frequency is not None:
                    frequency = int(
                        frequency
                    )

                if monetary is not None:
                    monetary = float(
                        monetary
                    )

                if r_score is not None:
                    r_score = int(
                        r_score
                    )

                if f_score is not None:
                    f_score = int(
                        f_score
                    )

                if m_score is not None:
                    m_score = int(
                        m_score
                    )

                if rfm_total is not None:
                    rfm_total = int(
                        rfm_total
                    )

                if rfm_score is not None:
                    rfm_score = str(
                        rfm_score
                    )

                rfm_segment = str(
                    rfm_segment
                )

    except Exception as error:

        print(
            "CUSTOMER PROFILE RFM ERROR:",
            error
        )

    # =====================================================
    # MACHINE LEARNING
    # =====================================================

    ml_segment = ""
    ml_cluster = None

    try:

        ml_df = get_ml_dataframe()

        if (
            ml_df is not None
            and not ml_df.empty
            and "customer_id" in ml_df.columns
        ):

            matching = ml_df[
                ml_df[
                    "customer_id"
                ].astype(str)
                == str(customer_id)
            ]

            if not matching.empty:

                row = matching.iloc[0]

                # -------------------------------------------------
                # ML SEGMENT
                # -------------------------------------------------

                if "ml_segment" in ml_df.columns:

                    ml_segment = row.get(
                        "ml_segment",
                        ""
                    )

                    if pd.isna(
                        ml_segment
                    ):
                        ml_segment = ""

                    ml_segment = str(
                        ml_segment
                    )

                # -------------------------------------------------
                # ML CLUSTER
                # -------------------------------------------------

                possible_cluster_columns = [
                    "cluster",
                    "cluster_label",
                    "Cluster",
                    "Cluster_Label",
                    "ml_cluster",
                ]

                for column in possible_cluster_columns:

                    if column in ml_df.columns:

                        value = row.get(
                            column,
                            None
                        )

                        if not pd.isna(
                            value
                        ):

                            ml_cluster = value

                        break

    except Exception as error:

        print(
            "CUSTOMER PROFILE ML ERROR:",
            error
        )

    # =====================================================
    # FALLBACK ML SEGMENT
    # =====================================================

    if not ml_segment:

        ml_segment = ""

    # =====================================================
    # INSIGHTS
    # =====================================================

    insights = []

    try:

        spending = float(
            customer.total_spending or 0
        )

    except (
        ValueError,
        TypeError,
    ):

        spending = 0

    if spending >= 30000:

        insights.append(
            "This customer is a high-value spender."
        )

    elif spending >= 10000:

        insights.append(
            "This customer has a moderate spending level."
        )

    else:

        insights.append(
            "This customer has relatively low spending."
        )

    try:

        customer_frequency = int(
            customer.purchase_frequency or 0
        )

    except (
        ValueError,
        TypeError,
    ):

        customer_frequency = 0

    if customer_frequency >= 20:

        insights.append(
            "The customer purchases frequently."
        )

    elif customer_frequency >= 10:

        insights.append(
            "The customer shows regular purchasing behaviour."
        )

    else:

        insights.append(
            "Purchase frequency is relatively low."
        )

    satisfaction = (
        customer.customer_satisfaction
    )

    if satisfaction is not None:

        try:

            satisfaction_value = float(
                satisfaction
            )

            if satisfaction_value >= 8:

                insights.append(
                    "Customer satisfaction is high."
                )

            elif satisfaction_value >= 5:

                insights.append(
                    "Customer satisfaction is moderate."
                )

            else:

                insights.append(
                    "Customer satisfaction requires attention."
                )

        except (
            ValueError,
            TypeError,
        ):

            pass

    else:

        insights.append(
            "Customer satisfaction data is not available."
        )

    if rfm_segment:

        insights.append(
            f"RFM segment: {rfm_segment}."
        )

    if ml_segment:

        insights.append(
            f"Machine-learning segment: {ml_segment}."
        )

    # =====================================================
    # CUSTOMER PROFILE CONTEXT
    # =====================================================

    context = {

        "customer":
            customer,

        # -------------------------------------------------
        # SEGMENTS
        # -------------------------------------------------

        "rfm_segment":
            rfm_segment,

        "ml_segment":
            ml_segment,

        "ml_cluster":
            ml_cluster,

        # -------------------------------------------------
        # RFM VALUES
        # -------------------------------------------------

        "recency":
            recency,

        "frequency":
            frequency,

        "monetary":
            monetary,

        "R_score":
            r_score,

        "F_score":
            f_score,

        "M_score":
            m_score,

        "RFM_score":
            rfm_score,

        "RFM_total":
            rfm_total,

        # -------------------------------------------------
        # LOWERCASE ALIASES
        # -------------------------------------------------

        "r_score":
            r_score,

        "f_score":
            f_score,

        "m_score":
            m_score,

        "rfm_score":
            rfm_score,

        "rfm_total":
            rfm_total,

        # -------------------------------------------------
        # INSIGHTS
        # -------------------------------------------------

        "insights":
            insights,

        "customer_insights":
            insights,
    }

    return render(
        request,
        "analytics/customer_profile.html",
        context,
    )


# =========================================================
# COMPATIBILITY VIEW
# =========================================================

def customer_analytics(
    request,
    customer_id,
):

    return customer_profile(
        request,
        customer_id,
    )


# =========================================================
# ADVANCED ANALYTICS
# =========================================================

def analytics_dashboard(request):

    df = get_customer_dataframe()

    if df is None:
        df = pd.DataFrame()

    # -----------------------------------------------------
    # EMPTY DATASET
    # -----------------------------------------------------

    if df.empty:

        empty_fig = px.bar(
            x=[],
            y=[],
            title="No customer data available",
        )

        empty_json = figure_json(
            empty_fig
        )

        context = {

            "spending_distribution_chart":
                empty_json,

            "income_spending_chart":
                empty_json,

            "category_spending_chart":
                empty_json,

            "purchase_frequency_chart":
                empty_json,

            "satisfaction_chart":
                empty_json,

            "gender_chart":
                empty_json,

            "age_chart":
                empty_json,

            "discount_usage_chart":
                empty_json,

            "total_customers":
                0,

            "total_spending":
                0,

            "average_spending":
                0,

            "average_income":
                0,

            "average_frequency":
                0,

            "average_satisfaction":
                0,
        }

        return render(
            request,
            "analytics/analytics.html",
            context,
        )

    # -----------------------------------------------------
    # CLEAN NUMERIC DATA
    # -----------------------------------------------------

    numeric_columns = [

        "age",

        "annual_income",

        "total_spending",

        "purchase_frequency",

        "average_order_value",

        "discount_usage",

        "customer_satisfaction",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Remove infinite values

    df = df.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    # -----------------------------------------------------
    # CLEAN CATEGORY
    # -----------------------------------------------------

    df[
        "preferred_category"
    ] = (
        df[
            "preferred_category"
        ]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # CLEAN GENDER
    # -----------------------------------------------------

    df[
        "gender"
    ] = (
        df[
            "gender"
        ]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # =====================================================
    # CHART 1
    # SPENDING DISTRIBUTION
    # =====================================================

    spending_df = df.copy()

    spending_df[
        "spending_bucket"
    ] = pd.cut(

        spending_df[
            "total_spending"
        ],

        bins=[
            -1,
            5000,
            10000,
            20000,
            30000,
            float("inf"),
        ],

        labels=[
            "₹0 - ₹5K",
            "₹5K - ₹10K",
            "₹10K - ₹20K",
            "₹20K - ₹30K",
            "₹30K+",
        ],
    )

    spending_counts = (
        spending_df[
            "spending_bucket"
        ]
        .value_counts(
            sort=False
        )
        .reset_index()
    )

    spending_counts.columns = [
        "spending_range",
        "customers",
    ]

    spending_fig = px.bar(
        spending_counts,
        x="spending_range",
        y="customers",
        labels={
            "spending_range":
                "Spending Range",
            "customers":
                "Customers",
        },
        title="Customer Spending Distribution",
    )

    spending_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=55,
            r=25,
            t=75,
            b=60,
        ),
    )

    # =====================================================
    # CHART 2
    # ANNUAL INCOME VS TOTAL SPENDING
    # =====================================================

    income_df = df[
        [
            "customer_id",
            "name",
            "annual_income",
            "total_spending",
            "purchase_frequency",
            "customer_satisfaction",
            "preferred_category",
        ]
    ].copy()

    income_df = income_df.dropna(
        subset=[
            "annual_income",
            "total_spending",
        ]
    )

    income_df[
        "purchase_frequency"
    ] = pd.to_numeric(
        income_df[
            "purchase_frequency"
        ],
        errors="coerce",
    ).fillna(0)

    income_df[
        "customer_satisfaction"
    ] = pd.to_numeric(
        income_df[
            "customer_satisfaction"
        ],
        errors="coerce",
    )

    income_df[
        "bubble_frequency"
    ] = income_df[
        "purchase_frequency"
    ].clip(
        lower=1
    )

    income_fig = px.scatter(

        income_df,

        x="annual_income",

        y="total_spending",

        size="bubble_frequency",

        color="customer_satisfaction",

        hover_name="name",

        hover_data={
            "customer_id":
                True,

            "name":
                False,

            "preferred_category":
                True,

            "annual_income":
                ":,.2f",

            "total_spending":
                ":,.2f",

            "purchase_frequency":
                ":.0f",

            "customer_satisfaction":
                ":.1f",

            "bubble_frequency":
                False,
        },

        size_max=28,

        opacity=0.72,

        labels={

            "annual_income":
                "Annual Income",

            "total_spending":
                "Total Spending",

            "customer_satisfaction":
                "Satisfaction",

            "preferred_category":
                "Category",

            "purchase_frequency":
                "Purchase Frequency",
        },

        title="Annual Income vs Total Spending",

    )

    median_income = (
        income_df[
            "annual_income"
        ].median()
    )

    median_spending = (
        income_df[
            "total_spending"
        ].median()
    )

    if pd.notna(median_income):

        income_fig.add_vline(
            x=median_income,
            line_dash="dash",
            annotation_text="Median Income",
            annotation_position="top",
        )

    if pd.notna(median_spending):

        income_fig.add_hline(
            y=median_spending,
            line_dash="dash",
            annotation_text="Median Spending",
            annotation_position="bottom right",
        )

    income_fig.update_layout(

        template="plotly_white",

        margin=dict(
            l=70,
            r=30,
            t=80,
            b=70,
        ),

        hovermode="closest",

        legend=dict(
            title="Customer Satisfaction",
        ),

        xaxis=dict(
            title="Annual Income (₹)",
            tickprefix="₹",
            separatethousands=True,
            tickformat=",.0f",
        ),

        yaxis=dict(
            title="Total Spending (₹)",
            tickprefix="₹",
            separatethousands=True,
            tickformat=",.0f",
        ),

    )

    # =====================================================
    # CHART 3
    # CATEGORY SPENDING
    # =====================================================

    category_df = (
    df[
        [
            "preferred_category",
            "total_spending",
        ]
    ]
    .dropna(
        subset=[
            "total_spending"
        ]
    )
    .groupby(
        "preferred_category",
        as_index=False,
    )[
        "total_spending"
    ]
    .sum()
    .sort_values(
        "total_spending",
        ascending=False,
    )
)

    category_fig = px.bar(
        category_df,
        x="preferred_category",
        y="total_spending",
        labels={
            "preferred_category":
                "Category",
            "total_spending":
                "Total Spending",
        },
        title="Total Spending by Category",
    )

    category_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=65,
            r=25,
            t=75,
            b=70,
        ),
        yaxis=dict(
            tickprefix="₹",
            separatethousands=True,
            tickformat=",.0f",
        ),
    )

    # =====================================================
    # CHART 4
    # PURCHASE FREQUENCY
    # =====================================================

    frequency_series = pd.to_numeric(
        df[
            "purchase_frequency"
        ],
        errors="coerce",
    )

    frequency_series = (
        frequency_series
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
    )

    frequency_fig = px.histogram(
        x=frequency_series,
        nbins=15,
        labels={
            "x":
                "Purchase Frequency",
            "y":
                "Customers",
        },
        title="Purchase Frequency Distribution",
    )

    frequency_fig.update_layout(
        template="plotly_white",
        bargap=0.18,
        margin=dict(
            l=60,
            r=25,
            t=75,
            b=65,
        ),
    )

    # =====================================================
    # CHART 5
    # CUSTOMER SATISFACTION
    # =====================================================

    satisfaction_series = pd.to_numeric(
        df[
            "customer_satisfaction"
        ],
        errors="coerce",
    )

    satisfaction_series = (
        satisfaction_series
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
    )

    satisfaction_series = (
        satisfaction_series
        .round()
        .astype(int)
    )

    satisfaction_df = (
        satisfaction_series
        .value_counts()
        .sort_index()
        .reindex(
            range(1, 11),
            fill_value=0,
        )
        .reset_index()
    )

    satisfaction_df.columns = [
        "satisfaction",
        "customers",
    ]

    satisfaction_fig = px.bar(
        satisfaction_df,
        x="satisfaction",
        y="customers",
        labels={
            "satisfaction":
                "Satisfaction Score",
            "customers":
                "Customers",
        },
        title="Customer Satisfaction Distribution",
    )

    satisfaction_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=60,
            r=25,
            t=75,
            b=65,
        ),
        xaxis=dict(
            tickmode="linear",
            dtick=1,
        ),
    )

    # =====================================================
    # CHART 6
    # GENDER
    # =====================================================

    gender_df = (
        df[
            "gender"
        ]
        .value_counts()
        .reset_index()
    )

    gender_df.columns = [
        "gender",
        "customers",
    ]

    gender_fig = px.pie(
        gender_df,
        names="gender",
        values="customers",
        title="Customer Gender Distribution",
    )

    gender_fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=30,
            r=30,
            t=75,
            b=30,
        ),
    )

    # =====================================================
    # CHART 7
    # AGE
    # =====================================================

    age_series = pd.to_numeric(
        df[
            "age"
        ],
        errors="coerce",
    )

    age_series = (
        age_series
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
    )

    age_fig = px.histogram(
        x=age_series,
        nbins=15,
        labels={
            "x":
                "Age",
            "y":
                "Customers",
        },
        title="Customer Age Distribution",
    )

    age_fig.update_layout(
        template="plotly_white",
        bargap=0.18,
        margin=dict(
            l=60,
            r=25,
            t=75,
            b=65,
        ),
    )

    # =====================================================
    # CHART 8
    # DISCOUNT USAGE
    # =====================================================

    discount_series = pd.to_numeric(
        df[
            "discount_usage"
        ],
        errors="coerce",
    )

    discount_series = (
        discount_series
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .dropna()
    )

    discount_fig = px.histogram(
        x=discount_series,
        nbins=10,
        labels={
            "x":
                "Discount Usage",
            "y":
                "Customers",
        },
        title="Discount Usage Distribution",
    )

    discount_fig.update_layout(
        template="plotly_white",
        bargap=0.18,
        margin=dict(
            l=60,
            r=25,
            t=75,
            b=65,
        ),
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    statistics = get_customer_statistics()

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "spending_distribution_chart":
            figure_json(
                spending_fig
            ),

        "income_spending_chart":
            figure_json(
                income_fig
            ),

        "category_spending_chart":
            figure_json(
                category_fig
            ),

        "purchase_frequency_chart":
            figure_json(
                frequency_fig
            ),

        "satisfaction_chart":
            figure_json(
                satisfaction_fig
            ),

        "gender_chart":
            figure_json(
                gender_fig
            ),

        "age_chart":
            figure_json(
                age_fig
            ),

        "discount_usage_chart":
            figure_json(
                discount_fig
            ),

        "total_customers":
            statistics[
                "total_customers"
            ],

        "total_spending":
            statistics[
                "total_spending"
            ],

        "average_spending":
            statistics[
                "average_spending"
            ],

        "average_income":
            statistics[
                "average_income"
            ],

        "average_frequency":
            statistics[
                "average_frequency"
            ],

        "average_satisfaction":
            statistics[
                "average_satisfaction"
            ],
    }

    return render(
        request,
        "analytics/analytics.html",
        context,
    )


# =========================================================
# CSV EXPORT
# =========================================================

def export_customers_csv(request):

    customers = get_customer_queryset()

    customers = apply_customer_filters(
        request,
        customers,
    )

    customers = sort_customers(
        customers,
        request.GET.get(
            "sort",
            "customer_id",
        ),
        request.GET.get(
            "direction",
            "asc",
        ),
    )

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="customer_export.csv"'
    )

    writer = csv.writer(
        response
    )

    writer.writerow([
        "Customer ID",
        "Name",
        "Age",
        "Gender",
        "Annual Income",
        "Total Spending",
        "Purchase Frequency",
        "Last Purchase Date",
        "Average Order Value",
        "Discount Usage",
        "Preferred Category",
        "Customer Satisfaction",
        "RFM Segment",
        "ML Segment",
    ])

    for customer in customers:

        writer.writerow([

            customer.customer_id,

            customer.name,

            customer.age,

            customer.gender,

            customer.annual_income,

            customer.total_spending,

            customer.purchase_frequency,

            customer.last_purchase_date,

            customer.average_order_value,

            customer.discount_usage,

            customer.preferred_category,

            customer.customer_satisfaction,

            getattr(
                customer,
                "rfm_segment",
                "",
            ),

            getattr(
                customer,
                "ml_segment",
                "",
            ),
        ])

    return response


# =========================================================
# PDF EXPORT
# =========================================================

def export_customers_pdf(request):

    customers = get_customer_queryset()

    customers = apply_customer_filters(
        request,
        customers,
    )

    customers = sort_customers(
        customers,
        request.GET.get(
            "sort",
            "customer_id",
        ),
        request.GET.get(
            "direction",
            "asc",
        ),
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="customer_export.pdf"'
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(

        buffer,

        pagesize=landscape(A4),

        rightMargin=10 * mm,

        leftMargin=10 * mm,

        topMargin=10 * mm,

        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        "CustomerExportTitle",

        parent=styles[
            "Title"
        ],

        alignment=TA_CENTER,

        fontSize=18,

        spaceAfter=12,
    )

    elements = []

    elements.append(
        Paragraph(
            "CustomerSeg Customer Export",
            title_style,
        )
    )

    elements.append(
        Spacer(
            1,
            5 * mm
        )
    )

    data = [[

        "Customer ID",
        "Name",
        "Age",
        "Gender",
        "Income",
        "Spending",
        "Frequency",
        "AOV",
        "Discount",
        "Category",
        "Satisfaction",
        "RFM",
        "ML",

    ]]

    for customer in customers:

        data.append([

            str(
                customer.customer_id
                or ""
            ),

            str(
                customer.name
                or ""
            ),

            str(
                customer.age
                or ""
            ),

            str(
                customer.gender
                or ""
            ),

            str(
                customer.annual_income
                or ""
            ),

            str(
                customer.total_spending
                or ""
            ),

            str(
                customer.purchase_frequency
                or ""
            ),

            str(
                customer.average_order_value
                or ""
            ),

            str(
                customer.discount_usage
                or ""
            ),

            str(
                customer.preferred_category
                or ""
            ),

            str(
                customer.customer_satisfaction
                or ""
            ),

            str(
                getattr(
                    customer,
                    "rfm_segment",
                    ""
                )
                or ""
            ),

            str(
                getattr(
                    customer,
                    "ml_segment",
                    ""
                )
                or ""
            ),
        ])

    table = Table(
        data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#111827"
                ),
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.grey,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor(
                        "#f8fafc"
                    ),
                ],
            ),

        ])
    )

    elements.append(
        table
    )

    document.build(
        elements
    )

    pdf = buffer.getvalue()

    buffer.close()

    response.write(
        pdf
    )

    return response


# =========================================================
# COMPATIBILITY EXPORT
# =========================================================

def export_customers(request):
    """
    Compatibility export endpoint.

    Keeps the existing analytics.urls.py working.
    Defaults to CSV and supports ?format=pdf.
    """

    export_format = (
        request.GET.get(
            "format",
            "csv",
        )
        .strip()
        .lower()
    )

    if export_format == "pdf":

        return export_customers_pdf(
            request
        )

    return export_customers_csv(
        request
    )