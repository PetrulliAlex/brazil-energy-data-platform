import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException


load_dotenv()

app = FastAPI(
    title="Brazil Energy Data API",
    description="API serving analytics-ready Brazilian oil production data.",
    version="1.0.0",
)


def get_connection():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        row_factory=dict_row,
    )


@app.get("/")
def root():
    return {
        "project": "Brazil Energy Data Platform",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc


@app.get("/states")
def get_states():
    query = """
        SELECT DISTINCT state
        FROM analytics.yearly_state_production
        ORDER BY state
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


@app.get("/production/states/{state}")
def get_state_production(state: str):
    query = """
        SELECT
            year,
            state,
            production_m3,
            previous_year_production_m3,
            yoy_growth_pct
        FROM analytics.yearly_state_production
        WHERE UPPER(state) = UPPER(%s)
        ORDER BY year
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (state,))
            results = cursor.fetchall()

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"State '{state}' not found",
        )

    return results


@app.get("/production/ranking/{year}")
def production_ranking(year: int):
    query = """
        SELECT
            state,
            production_m3,
            yoy_growth_pct
        FROM analytics.yearly_state_production
        WHERE year = %s
        ORDER BY production_m3 DESC
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (year,))
            results = cursor.fetchall()

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No data available for {year}",
        )

    return results