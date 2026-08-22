\# CustomerSeg - Customer Analytics \& Segmentation System



\## Project Overview



\*\*CustomerSeg\*\* is a Django-based customer analytics and segmentation web application developed to analyze customer behaviour, identify valuable and at-risk customers, and support data-driven business decisions.



The system combines traditional \*\*RFM (Recency, Frequency, Monetary) analysis\*\* with \*\*K-Means machine learning clustering\*\* to divide customers into meaningful segments.



The application provides an interactive analytics dashboard, customer exploration tools, individual customer profiles, segmentation insights, and data export functionality.



\---



\## Key Features



\* 📊 Interactive customer analytics dashboard

\* 👥 Customer Explorer with search and filtering

\* 🔎 Individual customer profile pages

\* 📈 RFM-based customer segmentation

\* 🤖 K-Means machine learning segmentation

\* 🏷️ Automatic customer segment labeling

\* 💰 Customer spending and purchasing behaviour analysis

\* ⭐ Customer satisfaction analysis

\* 🔄 Customer sorting and pagination

\* 📄 CSV export

\* 📑 PDF export

\* 🛠️ Django Admin integration

\* 🧹 Handling of missing customer data

\* 📱 Responsive web interface

\* 📊 Plotly-based analytics visualizations



\---



\## Customer Segmentation



\### RFM Analysis



Customer behaviour is analyzed using three important RFM dimensions:



\* \*\*Recency\*\* - How recently a customer made a purchase

\* \*\*Frequency\*\* - How frequently a customer makes purchases

\* \*\*Monetary\*\* - How much a customer spends



Based on these characteristics, customers are assigned meaningful RFM segments.



\### Machine Learning Segmentation



The project also uses \*\*K-Means clustering\*\* to discover customer groups based on behavioural characteristics.



The resulting clusters are profiled and assigned business-friendly labels such as:



\* \*\*High-Value Customers\*\*

\* \*\*At Risk Customers\*\*

\* \*\*Regular Active Customers\*\*



This combination of RFM analysis and machine learning provides both interpretable business segmentation and data-driven customer grouping.



\---



\## Analytics Dashboard



The main dashboard provides an overview of customer behaviour and segmentation.



It includes metrics such as:



\* Total Customers

\* Active Customers

\* At Risk Customers

\* High-Value Customers

\* Total Spending

\* Average Spending

\* RFM Segmentation

\* Machine Learning Segmentation



The dashboard also provides navigation to detailed customer and analytics pages.



\---



\## Customer Explorer



The Customer Explorer allows users to examine customers individually and collectively.



Available functionality includes:



\* Customer search

\* Segment filtering

\* Machine learning segment filtering

\* Spending-based sorting

\* Customer satisfaction filtering

\* Pagination

\* Customer profile navigation



\---



\## Customer Profiles



Each customer has a dedicated profile page containing relevant information such as:



\* Customer ID

\* Customer name

\* Total spending

\* Purchase frequency

\* Customer satisfaction

\* Preferred category

\* RFM segment

\* Machine learning segment



This allows individual customers to be investigated in greater detail.



\---



\## Data Export



The application supports exporting customer analytics data in:



\* \*\*CSV format\*\*

\* \*\*PDF format\*\*



This allows analysis results to be used outside the web application.



\---



\## Technologies Used



\### Backend



\* Python

\* Django



\### Data Analysis \& Machine Learning



\* Pandas

\* NumPy

\* Scikit-learn



\### Visualization



\* Plotly



\### Frontend



\* HTML

\* CSS

\* JavaScript



\### Database



\* SQLite



\### Development Tools



\* Git

\* GitHub

\* Python Virtual Environment



\---



\## Project Structure



```text

CustomerSeg/

│

├── analytics/

│   ├── management/

│   │   └── commands/

│   │       └── import\_customers.py

│   │

│   ├── migrations/

│   │

│   ├── services/

│   │   ├── cluster\_evaluation.py

│   │   ├── cluster\_labeling.py

│   │   ├── customer\_insights.py

│   │   ├── ml\_segmentation.py

│   │   ├── rfm\_analysis.py

│   │   ├── segmentation.py

│   │   └── segment\_insights.py

│   │

│   ├── templates/

│   │   └── analytics/

│   │       ├── analytics.html

│   │       ├── base.html

│   │       ├── customer\_explorer.html

│   │       ├── customer\_profile.html

│   │       └── dashboard.html

│   │

│   ├── models.py

│   ├── urls.py

│   └── views.py

│

├── config/

│   ├── settings.py

│   ├── urls.py

│   ├── asgi.py

│   └── wsgi.py

│

├── data/

│   ├── customers.csv

│   └── generate\_dataset.py

│

├── manage.py

├── README.md

├── requirements.txt

└── .gitignore

```



\---



\## Installation and Setup



\### 1. Clone the repository



```bash

git clone https://github.com/Skyscrappersam/customer-segmentation.git

cd customer-segmentation

```



\### 2. Create a virtual environment



On Windows:



```powershell

python -m venv .venv

```



Activate it:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

pip install -r requirements.txt

```



\### 4. Apply database migrations



```powershell

python manage.py migrate

```



\### 5. Import customer data



If the database needs to be populated from the included dataset:



```powershell

python manage.py import\_customers data/customers.csv

```



\### 6. Run the development server



```powershell

python manage.py runserver

```



Open the application in your browser:



```text

http://127.0.0.1:8000/analytics/

```



\---



\## Main Application Pages



| Page                                  | Purpose                     |

| ------------------------------------- | --------------------------- |

| `/analytics/`                         | Main analytics dashboard    |

| `/analytics/customers/`               | Customer Explorer           |

| `/analytics/customers/<customer\_id>/` | Individual customer profile |

| `/analytics/analytics/`               | Advanced Analytics          |



\---



\## Data Processing Workflow



The application follows this general workflow:



```text

Customer Dataset

&#x20;      ↓

Data Import

&#x20;      ↓

Data Cleaning \& Preparation

&#x20;      ↓

RFM Analysis

&#x20;      ↓

Customer Segmentation

&#x20;      ↓

K-Means Clustering

&#x20;      ↓

Cluster Profiling \& Labeling

&#x20;      ↓

Analytics Dashboard

&#x20;      ↓

Customer Explorer \& Profiles

&#x20;      ↓

CSV / PDF Export

```



\---



\## Project Purpose



This project was developed as an individual academic/internship project to demonstrate practical implementation of:



\* Web application development using Django

\* Data analysis using Pandas and NumPy

\* Customer segmentation using RFM analysis

\* Machine learning using K-Means clustering

\* Data visualization using Plotly

\* Database management using SQLite

\* Data export functionality

\* Git and GitHub based project management



\---



\## Author



\*\*Suraj Sharma\*\*



GitHub:

https://github.com/Skyscrappersam



\---



\## License



This project was developed for educational and academic purposes.



