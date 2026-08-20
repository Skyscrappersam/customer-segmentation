import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError

from analytics.models import Customer


class Command(BaseCommand):
    help = "Import customer data from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the customer CSV file.",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        try:
            with open(
                csv_file,
                "r",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.DictReader(file)

                required_columns = {
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
                }

                if not reader.fieldnames:
                    raise CommandError(
                        "The CSV file has no header row."
                    )

                missing_columns = (
                    required_columns - set(reader.fieldnames)
                )

                if missing_columns:
                    raise CommandError(
                        "Missing columns: "
                        + ", ".join(sorted(missing_columns))
                    )

                imported = 0
                updated = 0
                skipped = 0

                for row_number, row in enumerate(reader, start=2):

                    try:
                        customer_id = row["Customer ID"].strip()

                        if not customer_id:
                            raise ValueError(
                                "Customer ID is empty."
                            )

                        # -------------------------------
                        # Basic customer information
                        # -------------------------------

                        name = row["Name"].strip()

                        age = int(row["Age"])

                        gender = row["Gender"].strip()

                        annual_income = Decimal(
                            row["Annual Income"]
                        )

                        total_spending = Decimal(
                            row["Total Spending"]
                        )

                        purchase_frequency = int(
                            row["Purchase Frequency"]
                        )

                        # -------------------------------
                        # Last purchase date
                        # -------------------------------

                        last_purchase_date = None

                        if row["Last Purchase Date"].strip():

                            last_purchase_date = datetime.strptime(
                                row["Last Purchase Date"].strip(),
                                "%Y-%m-%d"
                            ).date()

                        # -------------------------------
                        # Average order value
                        # -------------------------------

                        average_order_value = None

                        if row["Average Order Value"].strip():

                            average_order_value = Decimal(
                                row["Average Order Value"]
                            )

                        # -------------------------------
                        # Discount usage
                        # -------------------------------

                        discount_usage = None

                        if row["Discount Usage"].strip():

                            discount_usage = Decimal(
                                row["Discount Usage"]
                            )

                        # -------------------------------
                        # Preferred category
                        # -------------------------------

                        preferred_category = (
                            row["Preferred Category"].strip()
                            or None
                        )

                        # -------------------------------
                        # Customer satisfaction
                        # -------------------------------

                        customer_satisfaction = None

                        if row["Customer Satisfaction"].strip():

                            customer_satisfaction = int(
                                float(
                                    row["Customer Satisfaction"]
                                )
                            )

                        # -------------------------------
                        # Save customer
                        # -------------------------------

                        defaults = {
                            "name": name,
                            "age": age,
                            "gender": gender,
                            "annual_income": annual_income,
                            "total_spending": total_spending,
                            "purchase_frequency": purchase_frequency,
                            "last_purchase_date": last_purchase_date,
                            "average_order_value": average_order_value,
                            "discount_usage": discount_usage,
                            "preferred_category": preferred_category,
                            "customer_satisfaction": customer_satisfaction,
                        }

                        customer, created = (
                            Customer.objects.update_or_create(
                                customer_id=customer_id,
                                defaults=defaults,
                            )
                        )

                        if created:
                            imported += 1
                        else:
                            updated += 1

                    except (
                        ValueError,
                        TypeError,
                        ArithmeticError,
                        InvalidOperation,
                    ) as error:

                        skipped += 1

                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipped row {row_number}: {error}"
                            )
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    "\nImport completed successfully!\n"
                    f"New customers : {imported}\n"
                    f"Updated        : {updated}\n"
                    f"Skipped        : {skipped}"
                )
            )

        except FileNotFoundError:

            raise CommandError(
                f"CSV file not found: {csv_file}"
            )