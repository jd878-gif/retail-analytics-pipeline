# dashboard/streamlit_app.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from snowpark.connection import create_snowpark_session


st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    h1 { color: #2c3e50; }
    h2 { color: #34495e; }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_session():
    """Create cached Snowflake session"""
    return create_snowpark_session()

@st.cache_data
def load_data():
    """Load all analytics data from Snowflake"""
    session = get_session()
    
    monthly = session.table("ANALYTICS.MONTHLY_REVENUE").to_pandas()
    top_products = session.table("ANALYTICS.TOP_PRODUCTS").to_pandas()
    country = session.table("ANALYTICS.COUNTRY_REVENUE").to_pandas()
    daily = session.table("ANALYTICS.DAILY_REVENUE").to_pandas()
    segments = session.table("ANALYTICS.CUSTOMER_SEGMENTS").to_pandas()
    
    return monthly, top_products, country, daily, segments

with st.spinner("Connecting to Snowflake..."):
    monthly, top_products, country, daily, segments = load_data()

# Create YEAR_MONTH column for display
monthly["YEAR_MONTH"] = monthly["YEAR"].astype(str) + "-" + monthly["MONTH"].astype(str).str.zfill(2)


st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Snowflake_Logo.svg/1280px-Snowflake_Logo.svg.png", width=200)
st.sidebar.title("Retail Analytics")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["Overview", "Revenue Trends", "Top Products", "Country Analysis", "Customer Segments"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** Snowflake")
st.sidebar.markdown("**Records:** 397,880")
st.sidebar.markdown("**Period:** Dec 2010 — Dec 2011")


if page == "Overview":
    st.title("Retail Analytics Dashboard")
    st.markdown("**Powered by Snowflake + Snowpark + Streamlit**")
    st.markdown("---")

    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_revenue = monthly["TOTAL_REVENUE"].sum()
        st.metric(
            label="💰 Total Revenue",
            value=f"£{total_revenue:,.0f}",
            delta="Full Period"
        )

    with col2:
        total_orders = monthly["TOTAL_ORDERS"].sum()
        st.metric(
            label="Total Orders",
            value=f"{total_orders:,}",
            delta="All Time"
        )

    with col3:
        unique_customers = segments["CUSTOMERID"].nunique()
        st.metric(
            label="Unique Customers",
            value=f"{unique_customers:,}",
            delta="Segmented"
        )

    with col4:
        countries = len(country)
        st.metric(
            label="Countries",
            value=f"{countries}",
            delta="Global Reach"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")
        fig = px.line(
            monthly,
            x="YEAR_MONTH",
            y="TOTAL_REVENUE",
            markers=True,
            color_discrete_sequence=["#3498db"]
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (£)",
            plot_bgcolor="white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Segments")
        segment_counts = segments["SEGMENT"].value_counts().reset_index()
        segment_counts.columns = ["SEGMENT", "COUNT"]
        fig = px.pie(
            segment_counts,
            values="COUNT",
            names="SEGMENT",
            color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c", "#95a5a6"],
            hole=0.4
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5 Products")
        top5 = top_products.head(5)
        fig = px.bar(
            top5,
            x="TOTAL_REVENUE",
            y="DESCRIPTION",
            orientation="h",
            color_discrete_sequence=["#9b59b6"]
        )
        fig.update_layout(
            xaxis_title="Revenue (£)",
            yaxis_title="",
            plot_bgcolor="white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 5 Countries")
        top5_countries = country.head(5)
        fig = px.bar(
            top5_countries,
            x="COUNTRY",
            y="TOTAL_REVENUE",
            color_discrete_sequence=["#e67e22"]
        )
        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Revenue (£)",
            plot_bgcolor="white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)


elif page == "Revenue Trends":
    st.title("Revenue Trends")
    st.markdown("---")

    
    st.subheader("Monthly Revenue")
    fig = px.bar(
        monthly,
        x="YEAR_MONTH",
        y="TOTAL_REVENUE",
        color="TOTAL_REVENUE",
        color_continuous_scale="Blues",
        text="TOTAL_REVENUE"
    )
    fig.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (£)",
        plot_bgcolor="white",
        height=450,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Orders")
        fig = px.line(
            monthly,
            x="YEAR_MONTH",
            y="TOTAL_ORDERS",
            markers=True,
            color_discrete_sequence=["#e74c3c"]
        )
        fig.update_layout(
            plot_bgcolor="white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Unique Customers Per Month")
        fig = px.line(
            monthly,
            x="YEAR_MONTH",
            y="UNIQUE_CUSTOMERS",
            markers=True,
            color_discrete_sequence=["#2ecc71"]
        )
        fig.update_layout(
            plot_bgcolor="white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    
    st.subheader("Daily Revenue Trend")
    fig = px.area(
        daily,
        x="INVOICE_DATE_ONLY",
        y="TOTAL_REVENUE",
        color_discrete_sequence=["#3498db"]
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue (£)",
        plot_bgcolor="white",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Monthly Data Table")
    st.dataframe(
        monthly.style.format({
            "TOTAL_REVENUE": "£{:,.2f}",
            "TOTAL_ORDERS": "{:,}",
            "UNIQUE_CUSTOMERS": "{:,}",
            "TOTAL_ITEMS_SOLD": "{:,}"
        }),
        use_container_width=True
    )


elif page == "Top Products":
    st.title("Top Products Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 by Revenue")
        fig = px.bar(
            top_products,
            x="TOTAL_REVENUE",
            y="DESCRIPTION",
            orientation="h",
            color="TOTAL_REVENUE",
            color_continuous_scale="Purples"
        )
        fig.update_layout(
            xaxis_title="Revenue (£)",
            yaxis_title="",
            plot_bgcolor="white",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 by Quantity Sold")
        fig = px.bar(
            top_products.sort_values("TOTAL_QUANTITY_SOLD", ascending=False),
            x="TOTAL_QUANTITY_SOLD",
            y="DESCRIPTION",
            orientation="h",
            color="TOTAL_QUANTITY_SOLD",
            color_continuous_scale="Greens"
        )
        fig.update_layout(
            xaxis_title="Quantity Sold",
            yaxis_title="",
            plot_bgcolor="white",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Product Details Table")
    st.dataframe(
        top_products.style.format({
            "TOTAL_REVENUE": "£{:,.2f}",
            "TOTAL_QUANTITY_SOLD": "{:,}",
            "TOTAL_ORDERS": "{:,}"
        }),
        use_container_width=True
    )

elif page == "Country Analysis":
    st.title("Country Revenue Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Country")
        fig = px.bar(
            country.head(10),
            x="COUNTRY",
            y="TOTAL_REVENUE",
            color="TOTAL_REVENUE",
            color_continuous_scale="Oranges"
        )
        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Revenue (£)",
            plot_bgcolor="white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue Distribution")
        fig = px.pie(
            country.head(10),
            values="TOTAL_REVENUE",
            names="COUNTRY",
            hole=0.3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    
    st.subheader("International Revenue (Excluding UK)")
    non_uk = country[country["COUNTRY"] != "United Kingdom"].head(10)
    fig = px.bar(
        non_uk,
        x="COUNTRY",
        y="TOTAL_REVENUE",
        color="TOTAL_REVENUE",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        plot_bgcolor="white",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Country Data Table")
    st.dataframe(
        country.style.format({
            "TOTAL_REVENUE": "£{:,.2f}",
            "TOTAL_ORDERS": "{:,}",
            "UNIQUE_CUSTOMERS": "{:,}"
        }),
        use_container_width=True
    )


elif page == " Customer Segments":
    st.title("Customer Segmentation (RFM)")
    st.markdown("---")
    
    segment_counts = segments["SEGMENT"].value_counts().reset_index()
    segment_counts.columns = ["SEGMENT", "COUNT"]

    col1, col2, col3, col4 = st.columns(4)

    for i, (_, row) in enumerate(segment_counts.iterrows()):
        colors = {"VIP": "🟢", "LOYAL": "🔵", "AT_RISK": "🟡", "DORMANT": "🔴"}
        with [col1, col2, col3, col4][i]:
            st.metric(
                label=f"{colors.get(row['SEGMENT'], '⚪')} {row['SEGMENT']}",
                value=f"{row['COUNT']:,}",
                delta=f"{row['COUNT']/len(segments)*100:.1f}%"
            )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Segment Distribution")
        fig = px.pie(
            segment_counts,
            values="COUNT",
            names="SEGMENT",
            color_discrete_sequence=["#2ecc71", "#3498db", "#f39c12", "#e74c3c"],
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg Monetary Value by Segment")
        avg_monetary = segments.groupby("SEGMENT")["MONETARY"].mean().reset_index()
        fig = px.bar(
            avg_monetary,
            x="SEGMENT",
            y="MONETARY",
            color="SEGMENT",
            color_discrete_sequence=["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
        )
        fig.update_layout(
            plot_bgcolor="white",
            height=400,
            yaxis_title="Avg Revenue (£)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("RFM Score Distribution")
    fig = px.scatter(
        segments,
        x="RECENCY",
        y="MONETARY",
        color="SEGMENT",
        size="FREQUENCY",
        hover_data=["CUSTOMERID"],
        color_discrete_sequence=["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
    )
    fig.update_layout(
        plot_bgcolor="white",
        height=450,
        xaxis_title="Recency (days)",
        yaxis_title="Monetary Value (£)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Data Sample")
    st.dataframe(
        segments.head(100).style.format({
            "MONETARY": "£{:,.2f}",
            "RECENCY": "{:,} days",
            "FREQUENCY": "{:,} orders"
        }),
        use_container_width=True
    )