import os
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine

# ---------------- Logging Setup ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

# ---------------- Configuration ---------------- #
INPUT_CSV = "hospital_data.csv"       # input CSV file
OUTPUT_CSV = "cleaned_data.csv"  # cleaned CSV output
DB_NAME = "etl_database"         # MySQL database name
TABLE_NAME = "etl_table"

MYSQL_CONFIG = {
    "user": "root",         # your MySQL username
    "password": "sai@#1609R", # your MySQL password
    "host": "localhost",
    "port": "3306"
}

# ---------------- ETL Functions ---------------- #

def extract(csv_file):
    """Extract data from CSV into DataFrame"""
    logging.info("Step 1: Extracting data from CSV...")
    df = pd.read_csv(csv_file)
    logging.info(f"Extracted {len(df)} rows.")
    return df


def transform(df):
    """Clean and transform the data"""
    logging.info("Step 2: Transforming data...")

    before = len(df)

    # Drop duplicates
    df = df.drop_duplicates()

    # Fill null values with defaults
    df = df.fillna("Unknown")

    after = len(df)
    cleaned_rows = before - after

    # Save cleaned CSV
    df.to_csv(OUTPUT_CSV, index=False)

    logging.info(f"Transformation done. {cleaned_rows} rows cleaned. {after} rows returned.")
    return df


def load(df, mysql_config, db_name, table_name):
    try:
        print("[INFO] - Step 3: Loading data into MySQL...")

        # Encode password safely
        password = quote_plus(mysql_config["password"])

        # Build connection string
        connection_url = (
            f"mysql+mysqlconnector://{mysql_config['user']}:{password}"
            f"@{mysql_config['host']}:{mysql_config['port']}/{db_name}"
        )

        # Create SQLAlchemy engine
        engine = create_engine(connection_url)

        # Load DataFrame into MySQL
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

        print(f"[INFO] - Data loaded successfully into `{table_name}`")

    except Exception as e:
        print("[ERROR] - Failed to load data into MySQL:", str(e))
        raise



# ---------------- Main ETL ---------------- #
def run_etl():
    logging.info(" ETL pipeline started...")
    df = extract(INPUT_CSV)
    transformed_df = transform(df)
    load(transformed_df, MYSQL_CONFIG, DB_NAME, TABLE_NAME)
    logging.info(" ETL process completed successfully.")


if __name__ == "__main__":
    run_etl()

