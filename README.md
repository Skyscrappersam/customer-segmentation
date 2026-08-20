# CustomerSeg - Customer Analytics & Segmentation System

## Project Overview

CustomerSeg is a Django-based customer analytics and segmentation web application designed to analyze customer behaviour, identify valuable and at-risk customers, and support data-driven business decisions.

The system combines traditional RFM (Recency, Frequency, Monetary) analysis with machine-learning-based K-Means clustering to segment customers into meaningful groups.

## Key Features

- Customer analytics dashboard
- Customer Explorer with search and filters
- Individual customer profile pages
- RFM-based customer segmentation
- K-Means machine learning segmentation
- Customer segment labeling
- Spending and purchasing behaviour analysis
- Customer satisfaction analysis
- Customer sorting and pagination
- CSV export
- PDF export
- Django Admin integration
- Handling of missing customer data
- Responsive web interface

## Technologies Used

- Python
- Django
- SQLite
- Pandas
- NumPy
- Scikit-learn
- Plotly
- HTML
- CSS
- JavaScript

## Project Structure

`	ext
CustomerSeg/
|
+-- analytics/
¦   +-- management/
¦   ¦   +-- commands/
¦   ¦       +-- import_customers.py
¦   +-- migrations/
¦   +-- services/
¦   ¦   +-- cluster_evaluation.py
¦   ¦   +-- cluster_labeling.py
¦   ¦   +-- customer_insights.py
¦   ¦   +-- ml_segmentation.py
¦   ¦   +-- rfm_analysis.py
¦   ¦   +-- segmentation.py
¦   ¦   +-- segment_insights.py
¦   +-- templates/
¦   ¦   +-- analytics/
¦   ¦       +-- analytics.html
¦   ¦       +-- base.html
¦   ¦       +-- customer_explorer.html
¦   ¦       +-- customer_profile.html
¦   ¦       +-- dashboard.html
¦   +-- models.py
¦   +-- urls.py
¦   +-- views.py
|
+-- config/
¦   +-- settings.py
¦   +-- urls.py
¦   +-- asgi.py
¦   +-- wsgi.py
|
+-- data/
¦   +-- customers.csv
¦   +-- generate_dataset.py
|
+-- manage.py
+-- README.md
+-- .gitignore



