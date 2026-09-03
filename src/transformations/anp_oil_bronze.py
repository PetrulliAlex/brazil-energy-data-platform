from pathlib import Path
import logging

import pandas as pd


RAW_PATH = Path(
    "data/raw/anp/oil_production/oil_production.csv"
)

BRONZE_PATH = Path(
    "data/bronze/anp/oil_production/oil_production.parquet"
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


COLUMN_MAPPING = {
    "ANO": "year",
    "MÊS": "month",
    "GRANDE REGIÃO": "region",
    "UNIDADE DA FEDERAÇÃO": "state",
    "PRODUTO": "product",
    "LOCALIZAÇÃO": "location",
    "PRODUÇÃO": "production_m3",
}


def read_raw_data(path: Path) -> pd.DataFrame:
    logger.info("Reading raw ANP dataset")

    return pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_MAPPING)

    return df


def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    df["year"] = pd.to_numeric(
        df["year"],
        errors="raise",
    ).astype("int16")

    df["production_m3"] = pd.to_numeric(
        df["production_m3"],
        errors="coerce",
    )

    return df


def validate_data(df: pd.DataFrame) -> None:
    required_columns = set(COLUMN_MAPPING.values())

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Dataset is empty")

    if df["year"].isna().any():
        raise ValueError("Null values found in year")

    logger.info(
        "Validation successful: %s rows",
        len(df),
    )


def save_bronze(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        path,
        index=False,
    )

    logger.info(
        "Bronze dataset saved to %s",
        path,
    )


def main() -> None:
    df = read_raw_data(RAW_PATH)

    logger.info(
        "Raw dataset: %s rows / %s columns",
        len(df),
        len(df.columns),
    )

    df = normalize_columns(df)

    validate_data(df)

    df = enforce_schema(df)

    save_bronze(
        df=df,
        path=BRONZE_PATH,
    )


if __name__ == "__main__":
    main()