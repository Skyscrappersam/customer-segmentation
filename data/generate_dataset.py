import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUM_CUSTOMERS = 2500
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ---------------------------------------------------------
# Customer data
# ---------------------------------------------------------

first_names = [
    "Aarav", "Aditi", "Aditya", "Akash", "Ananya",
    "Ankit", "Arjun", "Ayush", "Diya", "Isha",
    "Karan", "Kavya", "Krishna", "Manish", "Meera",
    "Neha", "Nikhil", "Pooja", "Rahul", "Riya",
    "Rohan", "Sakshi", "Sameer", "Shreya", "Sneha",
    "Suraj", "Tanvi", "Varun", "Vikas", "Yash"
]

last_names = [
    "Sharma", "Verma", "Singh", "Gupta", "Kumar",
    "Mishra", "Yadav", "Tiwari", "Pandey", "Sinha",
    "Agarwal", "Srivastava", "Jaiswal", "Chauhan",
    "Mehta", "Malhotra", "Rai", "Shukla"
]

genders = ["Male", "Female"]

categories = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Sports",
    "Books"
]


# ---------------------------------------------------------
# Generate customers
# ---------------------------------------------------------

customers = []

today = datetime.now().date()

for i in range(1, NUM_CUSTOMERS + 1):

    age = int(np.clip(np.random.normal(32, 9), 18, 65))

    gender = random.choice(genders)

    annual_income = round(
        np.clip(np.random.lognormal(mean=10.7, sigma=0.45), 18000, 250000),
        2
    )

    purchase_frequency = int(
        np.clip(np.random.poisson(8), 1, 40)
    )

    average_order_value = round(
        np.clip(
            np.random.normal(
                1800 + annual_income * 0.01,
                650
            ),
            300,
            15000
        ),
        2
    )

    total_spending = round(
        purchase_frequency * average_order_value * random.uniform(0.65, 1.35),
        2
    )

    discount_usage = round(
        np.clip(np.random.normal(35, 20), 0, 100),
        2
    )

    days_since_purchase = int(
        np.clip(np.random.exponential(45), 1, 365)
    )

    last_purchase_date = today - timedelta(
        days=days_since_purchase
    )

    satisfaction = int(
        np.clip(
            np.random.normal(
                7.5 - discount_usage * 0.005,
                1.3
            ),
            1,
            10
        )
    )

    customers.append(
        {
            "Customer ID": f"CUST{i:05d}",
            "Name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "Age": age,
            "Gender": gender,
            "Annual Income": annual_income,
            "Total Spending": round(total_spending, 2),
            "Purchase Frequency": purchase_frequency,
            "Last Purchase Date": last_purchase_date.isoformat(),
            "Average Order Value": average_order_value,
            "Discount Usage": discount_usage,
            "Preferred Category": random.choice(categories),
            "Customer Satisfaction": satisfaction,
        }
    )


# ---------------------------------------------------------
# Create DataFrame
# ---------------------------------------------------------

df = pd.DataFrame(customers)


# ---------------------------------------------------------
# Add a few realistic data-quality issues
# ---------------------------------------------------------

missing_indices = np.random.choice(
    df.index,
    size=25,
    replace=False
)

df.loc[missing_indices[:10], "Customer Satisfaction"] = np.nan
df.loc[missing_indices[10:20], "Discount Usage"] = np.nan
df.loc[missing_indices[20:], "Preferred Category"] = np.nan


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

output_file = "data/customers.csv"

df.to_csv(
    output_file,
    index=False
)

print("=" * 60)
print("Customer dataset generated successfully!")
print("=" * 60)
print(f"Customers generated : {len(df)}")
print(f"Columns             : {len(df.columns)}")
print(f"Output file         : {output_file}")
print("=" * 60)

print("\nDataset preview:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())