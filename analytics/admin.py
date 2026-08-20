from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer_id",
        "name",
        "age",
        "gender",
        "annual_income",
        "total_spending",
        "purchase_frequency",
        "created_at",
    )

    search_fields = (
        "customer_id",
        "name",
    )

    list_filter = (
        "gender",
    )