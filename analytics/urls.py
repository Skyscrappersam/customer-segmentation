from django.urls import path

from . import views


app_name = "analytics"


urlpatterns = [

    # =====================================================
    # MAIN DASHBOARD
    # =====================================================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    # =====================================================
    # CUSTOMER EXPLORER
    # =====================================================

    path(
        "customers/",
        views.customer_explorer,
        name="customer_explorer",
    ),

    # =====================================================
    # CUSTOMER PROFILE
    # IMPORTANT:
    # customer_id is STRING because IDs are like CUST00001
    # =====================================================

    path(
        "customers/<str:customer_id>/",
        views.customer_profile,
        name="customer_profile",
    ),

    # =====================================================
    # ADVANCED ANALYTICS
    # =====================================================

    path(
        "analytics/",
        views.analytics_dashboard,
        name="analytics_dashboard",
    ),

    # =====================================================
    # EXPORTS
    # =====================================================

    path(
        "export/csv/",
        views.export_customers_csv,
        name="export_customers_csv",
    ),

    path(
        "export/pdf/",
        views.export_customers_pdf,
        name="export_customers_pdf",
    ),

    path(
        "export/",
        views.export_customers,
        name="export_customers",
    ),
]