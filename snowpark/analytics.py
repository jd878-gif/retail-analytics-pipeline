import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snowflake.snowpark import functions as F
from snowflake.snowpark.window import Window
from snowpark.connection import create_snowpark_session, close_session

def load_clean_data(session):
    """Load cleaned data from TRANSFORMED schema"""
    print("\n📥 Loading clean data...")
    df = session.table("TRANSFORMED.CLEAN_SALES")
    print(f"   Total rows: {df.count()}")
    return df

def build_monthly_revenue(session, df):
    """Calculate total revenue per month"""
    print("\n Building Monthly Revenue...")

    monthly = df.group_by(
        F.col("YEAR"),
        F.col("MONTH")
    ).agg(
        F.sum("REVENUE").alias("TOTAL_REVENUE"),
        F.count("INVOICENO").alias("TOTAL_ORDERS"),
        F.countDistinct("CUSTOMERID").alias("UNIQUE_CUSTOMERS"),
        F.sum("QUANTITY").alias("TOTAL_ITEMS_SOLD")
    ).sort(
        F.col("YEAR").asc(),
        F.col("MONTH").asc()
    )

    monthly.write.mode("overwrite").save_as_table("ANALYTICS.MONTHLY_REVENUE")
    count = session.table("ANALYTICS.MONTHLY_REVENUE").count()
    print(f"  Monthly Revenue saved — {count} months of data")
    monthly.show(5)
    return monthly

def build_top_products(session, df):
    """Find top 10 products by total revenue"""
    print("\n Building Top Products...")

    top_products = df.group_by(
        F.col("STOCKCODE"),
        F.col("DESCRIPTION")
    ).agg(
        F.sum("REVENUE").alias("TOTAL_REVENUE"),
        F.sum("QUANTITY").alias("TOTAL_QUANTITY_SOLD"),
        F.count("INVOICENO").alias("TOTAL_ORDERS")
    ).sort(
        F.col("TOTAL_REVENUE").desc()
    ).limit(10)

    top_products.write.mode("overwrite").save_as_table("ANALYTICS.TOP_PRODUCTS")
    print(f"  Top Products saved")
    top_products.show(10)
    return top_products

def build_country_revenue(session, df):
    """Calculate revenue by country"""
    print("\n Building Country Revenue...")

    country = df.group_by(
        F.col("COUNTRY")
    ).agg(
        F.sum("REVENUE").alias("TOTAL_REVENUE"),
        F.count("INVOICENO").alias("TOTAL_ORDERS"),
        F.countDistinct("CUSTOMERID").alias("UNIQUE_CUSTOMERS")
    ).sort(
        F.col("TOTAL_REVENUE").desc()
    )

    country.write.mode("overwrite").save_as_table("ANALYTICS.COUNTRY_REVENUE")
    count = session.table("ANALYTICS.COUNTRY_REVENUE").count()
    print(f" Country Revenue saved — {count} countries")
    country.show(5)
    return country

def build_daily_revenue(session, df):
    """Calculate daily revenue trends"""
    print("\n Building Daily Revenue...")

    daily = df.group_by(
        F.col("INVOICE_DATE_ONLY")
    ).agg(
        F.sum("REVENUE").alias("TOTAL_REVENUE"),
        F.count("INVOICENO").alias("TOTAL_ORDERS"),
        F.countDistinct("CUSTOMERID").alias("UNIQUE_CUSTOMERS")
    ).sort(
        F.col("INVOICE_DATE_ONLY").asc()
    )

    daily.write.mode("overwrite").save_as_table("ANALYTICS.DAILY_REVENUE")
    count = session.table("ANALYTICS.DAILY_REVENUE").count()
    print(f"  Daily Revenue saved — {count} days of data")
    daily.show(5)
    return daily

def build_rfm_segmentation(session, df):
    """Build RFM customer segments"""
    print("\n Building RFM Customer Segmentation...")

    max_date = df.agg(F.max("INVOICE_DATE_ONLY")).collect()[0][0]
    print(f"   Reference date: {max_date}")

    rfm = df.group_by("CUSTOMERID").agg(
        F.datediff("day",
            F.max("INVOICE_DATE_ONLY"),
            F.lit(max_date)
        ).alias("RECENCY"),
        F.countDistinct("INVOICENO").alias("FREQUENCY"),
        F.sum("REVENUE").alias("MONETARY")
    )

    rfm = rfm.with_column(
        "R_SCORE",
        F.when(F.col("RECENCY") <= 30, 4)
        .when(F.col("RECENCY") <= 90, 3)
        .when(F.col("RECENCY") <= 180, 2)
        .otherwise(1)
    )

    rfm = rfm.with_column(
        "F_SCORE",
        F.when(F.col("FREQUENCY") >= 10, 4)
        .when(F.col("FREQUENCY") >= 5, 3)
        .when(F.col("FREQUENCY") >= 2, 2)
        .otherwise(1)
    )

    rfm = rfm.with_column(
        "M_SCORE",
        F.when(F.col("MONETARY") >= 1000, 4)
        .when(F.col("MONETARY") >= 500, 3)
        .when(F.col("MONETARY") >= 100, 2)
        .otherwise(1)
    )

    rfm = rfm.with_column(
        "RFM_SCORE",
        F.col("R_SCORE") + F.col("F_SCORE") + F.col("M_SCORE")
    )

    rfm = rfm.with_column(
        "SEGMENT",
        F.when(F.col("RFM_SCORE") >= 10, "VIP")
        .when(F.col("RFM_SCORE") >= 7, "LOYAL")
        .when(F.col("RFM_SCORE") >= 5, "AT_RISK")
        .otherwise("DORMANT")
    )

    rfm.write.mode("overwrite").save_as_table("ANALYTICS.CUSTOMER_SEGMENTS")
    count = session.table("ANALYTICS.CUSTOMER_SEGMENTS").count()
    print(f" Customer Segments saved — {count} customers segmented")

    print("\n   Segment Distribution:")
    session.table("ANALYTICS.CUSTOMER_SEGMENTS").group_by("SEGMENT").agg(
        F.count("CUSTOMERID").alias("COUNT")
    ).sort(F.col("COUNT").desc()).show()

    return rfm


def run_analytics_pipeline(session):
    print("=" * 50)
    print("  RETAIL ANALYTICS PIPELINE")
    print("=" * 50)

    
    df = load_clean_data(session)

    
    build_monthly_revenue(session, df)
    build_top_products(session, df)
    build_country_revenue(session, df)
    build_daily_revenue(session, df)
    build_rfm_segmentation(session, df)

    print("\n Analytics pipeline complete!")
    print("=" * 50)

    
    print("\n Analytics Tables Created:")
    print("  ANALYTICS.MONTHLY_REVENUE")
    print("  ANALYTICS.TOP_PRODUCTS")
    print("  ANALYTICS.COUNTRY_REVENUE")
    print("  ANALYTICS.DAILY_REVENUE")
    print("  ANALYTICS.CUSTOMER_SEGMENTS")

if __name__ == "__main__":
    session = create_snowpark_session()
    run_analytics_pipeline(session)
    close_session(session)