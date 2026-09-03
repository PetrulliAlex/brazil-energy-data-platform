from pathlib import Path
import logging
import unicodedata

import pandas as pd


BRONZE_PATH = Path(
    "data/bronze/anp/oil_production/oil_production.parquet"
)

SILVER_PATH = Path(
    "data/silver/anp/oil_production/oil_production.parquet"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


MONTH_MAPPING = {
    "JAN": 1,
    "FEV": 2,
    "MAR": 3,
    "ABR": 4,
    "MAI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SET": 9,
    "OUT": 10,
    "NOV": 11,
    "DEZ": 12,
}


def read_bronze(path: Path) -> pd.DataFrame:
    logger.info("Reading Bronze dataset")
    return pd.read_parquet(path)


def clean_text(value):
    if pd.isna(value):
        return None

    return str(value).strip()


def normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "region",
        "state",
        "product",
        "location",
    ]

    for column in columns:
        df[column] = df[column].map(clean_text)

    return df


def create_month_number(df: pd.DataFrame) -> pd.DataFrame:
    month = (
        df["month"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    numeric_month = pd.to_numeric(month, errors="coerce")
    mapped_month = month.map(MONTH_MAPPING)

    df["month_number"] = numeric_month.fillna(mapped_month)

    if df["month_number"].isna().any():
        invalid = df.loc[
            df["month_number"].isna(),
            "month"
        ].unique()

        raise ValueError(
            f"Invalid month values found: {invalid}"
        )

    df["month_number"] = df["month_number"].astype("int8")

    return df


def create_production_date(df: pd.DataFrame) -> pd.DataFrame:
    df["production_date"] = pd.to_datetime(
        {
            "year": df["year"],
            "month": df["month_number"],
            "day": 1,
        }
    )

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    logger.info("Removed %s duplicate rows", removed)

    return df


def validate_silver(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("Silver dataset is empty")

    if df["production_date"].isna().any():
        raise ValueError("Null production dates found")

    null_production = df["production_m3"].isna().sum()

    if null_production > 0:
        logger.warning(
            "Dropping %s rows with null production values",
            null_production,
        )

    if (df["production_m3"] < 0).any():
        raise ValueError("Negative production values found")

    if not df["month_number"].between(1, 12).all():
        raise ValueError("Invalid month number found")

    logger.info(
        "Silver validation successful: %s rows",
        len(df),
    )


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        [
            "production_date",
            "year",
            "month_number",
            "region",
            "state",
            "product",
            "location",
            "production_m3",
        ]
    ]


def save_silver(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        path,
        index=False,
    )

    logger.info(
        "Silver dataset saved to %s",
        path,
    )


def main() -> None:
    df = read_bronze(BRONZE_PATH)

    logger.info("Bronze rows: %s", len(df))

    df = normalize_text_columns(df)
    df = create_month_number(df)
    df = create_production_date(df)
    df = remove_duplicates(df)

    df = df.dropna(subset=["production_m3"])

    validate_silver(df)

    df = select_columns(df)

    save_silver(
        df=df,
        path=SILVER_PATH,
    )


if __name__ == "__main__":
    main()