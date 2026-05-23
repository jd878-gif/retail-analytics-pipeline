# snowpark/connection.py
import sys
import os

# Fix Python path - add root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snowflake.snowpark import Session
from dotenv import load_dotenv

# Load .env file directly
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_snowflake_config():
    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "role": os.getenv("SNOWFLAKE_ROLE")
    }

def create_snowpark_session():
    """Creates and returns a Snowpark session"""
    try:
        config = get_snowflake_config()
        session = Session.builder.configs(config).create()
        print(f"Connected to Snowflake!")
        print(f"   Account  : {config['account']}")
        print(f"   Database : {config['database']}")
        print(f"   Schema   : {config['schema']}")
        print(f"   Warehouse: {config['warehouse']}")
        return session
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        raise

def close_session(session):
    """Closes the Snowpark session"""
    try:
        session.close()
        print("Session closed successfully")
    except Exception as e:
        print(f"Error closing session: {str(e)}")

# Test connection
if __name__ == "__main__":
    session = create_snowpark_session()
    result = session.sql("SELECT CURRENT_VERSION()").collect()
    print(f"   Snowflake Version: {result[0][0]}")
    count = session.sql("SELECT COUNT(*) FROM RAW.RAW_SALES").collect()
    print(f"   Total Rows in RAW_SALES: {count[0][0]}")
    close_session(session)