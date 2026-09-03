from pathlib import Path
import logging
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


load_dotenv()

GOLD_PATH = Path("data/gold/anp/oil_production")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )


def nullable_float(value):
    if pd.isna(value):
        return None
    return float(value)


def load_monthly_state(conn):
    df = pd.read_parquet(
        GOLD_PATH / "monthly_state_production.parquet"
    )

    sql = """
        INSERT INTO analytics.monthly_state_production (
            production_date,
            state,
            production_m3
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (production_date, state)
        DO UPDATE SET
            production_m3 = EXCLUDED.production_m3
    """

    rows = [
        (
            row.production_date.date(),
            row.state,
            float(row.production_m3),
        )
        for row in df.itertuples(index=False)
    ]

    with conn.cursor() as cursor:
        cursor.executemany(sql, rows)

    logger.info("Loaded %s monthly state rows", len(rows))


def load_monthly_location(conn):
    df = pd.read_parquet(
        GOLD_PATH / "monthly_location_production.parquet"
    )

    sql = """
        INSERT INTO analytics.monthly_location_production (
            production_date,
            location,
            production_m3
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (production_date, location)
        DO UPDATE SET
            production_m3 = EXCLUDED.production_m3
    """

    rows = [
        (
            row.production_date.date(),
            row.location,
            float(row.production_m3),
        )
        for row in df.itertuples(index=False)
    ]

    with conn.cursor() as cursor:
        cursor.executemany(sql, rows)

    logger.info("Loaded %s monthly location rows", len(rows))


def load_yearly_state(conn):
    df = pd.read_parquet(
        GOLD_PATH / "yearly_state_production.parquet"
    )

    sql = """
        INSERT INTO analytics.yearly_state_production (
            year,
            state,
            production_m3,
            previous_year_production_m3,
            yoy_growth_pct
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (year, state)
        DO UPDATE SET
            production_m3 = EXCLUDED.production_m3,
            previous_year_production_m3 =
                EXCLUDED.previous_year_production_m3,
            yoy_growth_pct = EXCLUDED.yoy_growth_pct
    """

    rows = [
        (
            int(row.year),
            row.state,
            float(row.production_m3),
            nullable_float(row.previous_year_production_m3),
            nullable_float(row.yoy_growth_pct),
        )
        for row in df.itertuples(index=False)
    ]

    with conn.cursor() as cursor:
        cursor.executemany(sql, rows)

    logger.info("Loaded %s yearly state rows", len(rows))


def verify_load(conn):
    query = """
        SELECT 'monthly_state_production', COUNT(*)
        FROM analytics.monthly_state_production

        UNION ALL

        SELECT 'monthly_location_production', COUNT(*)
        FROM analytics.monthly_location_production

        UNION ALL

        SELECT 'yearly_state_production', COUNT(*)
        FROM analytics.yearly_state_production
    """

    with conn.cursor() as cursor:
        cursor.execute(query)

        for table, count in cursor.fetchall():
            logger.info("%s: %s rows", table, count)


def main():
    logger.info("Connecting to PostgreSQL")

    with get_connection() as conn:
        load_monthly_state(conn)
        load_monthly_location(conn)
        load_yearly_state(conn)

        conn.commit()

        verify_load(conn)

    logger.info("PostgreSQL load completed")


if __name__ == "__main__":
    main()