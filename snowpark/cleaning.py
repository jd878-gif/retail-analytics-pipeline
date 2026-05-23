import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import DoubleType, IntegerType
from snowpark.connection import create_snowpark_session, close_session

def load_raw_data(session):
    """Load raw data from Snowflake"""
    print("\nLoading raw data...")
    df = session.table("RAW.RAW_SALES")
    print(f"   Total rows loaded: {df.count()}")
    return df

def inspect_data(df):
    """Inspect data quality before cleaning"""
    print("\nInspecting raw data...")
    
    print("\n   Sample rows:")
    df.show(5)
    
    print("\n   Null counts per column:")
    for col in df.columns:
        null_count = df.filter(F.col(col).isNull()).count()
        print(f"   {col}: {null_count} nulls")

def clean_data(df):
    """Clean and transform raw data"""
    print("\n🧹 Cleaning data...")
    
    # Step 1: Remove null CustomerIDs
    df_clean = df.filter(F.col("CUSTOMERID").isNotNull())
    print(f"   After removing null CustomerIDs: {df_clean.count()} rows")
    
    # Step 2: Remove cancelled orders
    df_clean = df_clean.filter(~F.col("INVOICENO").startswith("C"))
    print(f"   After removing cancellations: {df_clean.count()} rows")
    
    # Step 3: Remove negative quantities
    df_clean = df_clean.filter(F.col("QUANTITY") > 0)
    print(f"   After removing negative quantities: {df_clean.count()} rows")
    
    # Step 4: Remove zero or negative prices
    df_clean = df_clean.filter(F.col("UNITPRICE") > 0)
    print(f"   After removing invalid prices: {df_clean.count()} rows")
    
    # Step 5: Remove null descriptions
    df_clean = df_clean.filter(F.col("DESCRIPTION").isNotNull())
    print(f"   After removing null descriptions: {df_clean.count()} rows")

    # Step 6: Cast columns to correct types — BEFORE timestamp conversion
    df_clean = df_clean.with_column(
        "QUANTITY", F.col("QUANTITY").cast(IntegerType())
    )
    df_clean = df_clean.with_column(
        "UNITPRICE", F.col("UNITPRICE").cast(DoubleType())
    )
    print("   ✅ Fixed column data types")

    # Step 7: Add REVENUE column
    df_clean = df_clean.with_column(
        "REVENUE",
        F.col("QUANTITY") * F.col("UNITPRICE")
    )
    print("   ✅ Added REVENUE column")

    print(f"\n   ✅ Final clean rows: {df_clean.count()}")
    return df_clean

def save_cleaned_data(session, df_clean):
    """Save cleaned data to TRANSFORMED schema — timestamp handled via SQL"""
    print("\n💾 Saving cleaned data to TRANSFORMED schema...")

    # Save without timestamp conversion first
    df_clean.write.mode("overwrite").save_as_table("TRANSFORMED.CLEAN_SALES")
    print("   ✅ Base table saved!")

    # Add INVOICEDATE_TS column using Snowflake native SQL
    session.sql("""
        ALTER TABLE TRANSFORMED.CLEAN_SALES
        ADD COLUMN INVOICEDATE_TS TIMESTAMP
    """).collect()

    session.sql("""
        UPDATE TRANSFORMED.CLEAN_SALES
        SET INVOICEDATE_TS = TO_TIMESTAMP(INVOICEDATE, 'MM/DD/YYYY HH24:MI:SS')
    """).collect()
    print("   ✅ INVOICEDATE_TS column added")

    # Add DATE only column
    session.sql("""
        ALTER TABLE TRANSFORMED.CLEAN_SALES
        ADD COLUMN INVOICE_DATE_ONLY DATE
    """).collect()

    session.sql("""
        UPDATE TRANSFORMED.CLEAN_SALES
        SET INVOICE_DATE_ONLY = TO_DATE(INVOICEDATE, 'MM/DD/YYYY HH24:MI:SS')
    """).collect()
    print("   ✅ INVOICE_DATE_ONLY column added")

    # Add YEAR and MONTH columns
    session.sql("""
        ALTER TABLE TRANSFORMED.CLEAN_SALES
        ADD COLUMN YEAR NUMBER
    """).collect()

    session.sql("""
        ALTER TABLE TRANSFORMED.CLEAN_SALES
        ADD COLUMN MONTH NUMBER
    """).collect()

    session.sql("""
        UPDATE TRANSFORMED.CLEAN_SALES
        SET YEAR = YEAR(INVOICEDATE_TS),
            MONTH = MONTH(INVOICEDATE_TS)
    """).collect()
    print("   ✅ YEAR and MONTH columns added")

    # Verify final result
    count = session.table("TRANSFORMED.CLEAN_SALES").count()
    print(f"\n   ✅ Saved successfully!")
    print(f"   Total rows in TRANSFORMED.CLEAN_SALES: {count}")

    # Preview
    print("\n   Preview of saved data:")
    session.table("TRANSFORMED.CLEAN_SALES").show(5)

def run_cleaning_pipeline(session):
    """Run full cleaning pipeline"""
    print("=" * 50)
    print("  RETAIL DATA CLEANING PIPELINE")
    print("=" * 50)
    
    df_raw = load_raw_data(session)
    inspect_data(df_raw)
    df_clean = clean_data(df_raw)
    save_cleaned_data(session, df_clean)
    
    print("\n✅ Cleaning pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    session = create_snowpark_session()
    run_cleaning_pipeline(session)
    close_session(session)