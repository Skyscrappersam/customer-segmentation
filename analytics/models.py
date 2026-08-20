from django.db import models


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)

    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_spending = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    purchase_frequency = models.PositiveIntegerField(default=0)

    last_purchase_date = models.DateField(
        null=True,
        blank=True
    )

    average_order_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    discount_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    preferred_category = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    customer_satisfaction = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.customer_id} - {self.name}"