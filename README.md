# Retail Analytics Pipeline

An end-to-end data engineering and analytics project built using 
Snowflake, Snowpark Python, and Streamlit — processing 500K+ 
retail transactions to surface actionable business insights.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Snowflake](https://img.shields.io/badge/Snowflake-Data_Warehouse-29B5E8)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![Apache Airflow](https://img.shields.io/badge/Apache-Airflow-017CEE)

---

## Project Overview

This project demonstrates a production-grade data pipeline that:
- Ingests 541,909 raw retail transactions into Snowflake
- Cleans and transforms data using Snowpark Python
- Builds 5 analytics tables for business intelligence
- Delivers insights through an interactive Streamlit dashboard

---

## Architecture
Raw CSV Data (541,909 rows)
↓
Snowflake Internal Stage
↓
RAW.RAW_SALES (Snowflake)
↓
Snowpark Python (Cleaning & Transformation)
↓
TRANSFORMED.CLEAN_SALES (397,880 rows)
↓
Snowpark Python (Analytics)
↓
┌─────────────────────────────────┐
│ ANALYTICS.MONTHLY_REVENUE       │
│ ANALYTICS.TOP_PRODUCTS          │
│ ANALYTICS.COUNTRY_REVENUE       │
│ ANALYTICS.DAILY_REVENUE         │
│ ANALYTICS.CUSTOMER_SEGMENTS     │
└─────────────────────────────────┘
↓
Streamlit Dashboard (Live)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Warehouse | Snowflake |
| Data Processing | Snowpark Python |
| Pipeline Orchestration | Python Scripts |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.13 |
| Version Control | Git + GitHub |

---

## Key Results

| Metric | Value |
|---|---|
| Raw records ingested | 541,909 |
| Clean records after processing | 397,880 |
| Total revenue analyzed | £9.4 Million |
| Countries covered | 37 |
| Customers segmented | 4,338 |
| Months of data | 13 |

---

## Analytics Built

### 1. Monthly Revenue Trends
- Revenue, orders, and unique customers per month
- Peak month: November 2011 (£1.16M)

### 2. Top Products Analysis
- Top 10 products by revenue and quantity sold
- #1 Product: Paper Craft Little Birdie (£168K)

### 3. Country Revenue Analysis
- Revenue breakdown across 37 countries
- UK dominates at £7.3M (96% of total)
- Netherlands strongest international market (£285K)

### 4. Daily Revenue Trends
- 305 days of daily revenue patterns
- Identifies peak trading days and seasonal trends

### 5. RFM Customer Segmentation
| Segment | Count | Percentage |
|---|---|---|
| LOYAL | 1,631 | 37% |
| VIP | 1,250 | 29% |
| AT_RISK | 886 | 20% |
| DORMANT | 571 | 13% |

---

## Project Structure
Snowflake_Project/
│
├── config/
│   └── snowflake_config.py     # Snowflake connection config
│
├── snowpark/
│   ├── connection.py           # Snowpark session management
│   ├── cleaning.py             # Data cleaning pipeline
│   └── analytics.py           # Analytics aggregations
│
├── dashboard/
│   └── streamlit_app.py        # Interactive Streamlit dashboard
│
├── sql/
│   └── setup.sql               # Snowflake setup script
│
├── .gitignore                  # Excludes .env and data files
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

---

## Getting Started

### Prerequisites
- Python 3.8+
- Snowflake account (free trial at snowflake.com)
- Git

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/retail-analytics-pipeline.git
cd retail-analytics-pipeline

pip install -r requirements.txt

cp .env.example .env

```

### Environment Setup

Create a `.env` file with your Snowflake credentials:

```env
SNOWFLAKE_ACCOUNT=izc59408.us-east-1
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=RETAIL_WH
SNOWFLAKE_DATABASE=RETAIL_DB
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### Running the Pipeline

```bash

python snowpark/cleaning.py

python snowpark/analytics.py

streamlit run dashboard/streamlit_app.py
```

---

## Dashboard Screenshots

![Streamlit Dashboard](<Screenshot (444).png>)

---

## Future Improvements

- [ ] Add Apache Airflow for pipeline orchestration
- [ ] Integrate dbt for data transformations
- [ ] Add Power BI dashboard
- [ ] Implement Snowpipe for real-time ingestion
- [ ] Add data quality tests using Great Expectations
- [ ] Deploy Streamlit dashboard to Streamlit Cloud

---

## Author

**Jeet Dave**
- LinkedIn: [linkedin.com/in/jeetdave11](https://linkedin.com/in/jeetdave11)
- Portfolio: [jd878-gif.github.io/portfolio](https://jd878-gif.github.io/portfolio)
- Email: jeetd6220@gmail.com

---

## Dataset

[Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) 
from UCI Machine Learning Repository

---

