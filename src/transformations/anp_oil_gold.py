from pathlib import Path
import logging

import pandas as pd


SILVER_PATH = Path(
    "data/silver/anp/oil_production/oil_production.parquet"
)

GOLD_BASE_PATH = Path(
    "data/gold/anp/oil_production"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def read_silver() -> pd.DataFrame:
    logger.info("Reading Silver dataset")
    return pd.read_parquet(SILVER_PATH)


def monthly_state_production(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby(
            [
                "production_date",
                "state",
            ],
            as_index=False,
        )["production_m3"]
        .sum()
    )

    return result


def monthly_location_production(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby(
            [
                "production_date",
                "location",
            ],
            as_index=False,
        )["production_m3"]
        .sum()
    )

    return result


def state_yearly_production(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby(
            [
                "year",
                "state",
            ],
            as_index=False,
        )["production_m3"]
        .sum()
    )

    return result


def add_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(
        ["state", "year"]
    )

    df["previous_year_production_m3"] = (
        df.groupby("state")["production_m3"]
        .shift(1)
    )

    df["yoy_growth_pct"] = (
        (
            df["production_m3"]
            / df["previous_year_production_m3"]
            - 1
        )
        * 100
    )

    return df


def save_dataset(
    df: pd.DataFrame,
    filename: str,
) -> None:

    GOLD_BASE_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = GOLD_BASE_PATH / filename

    df.to_parquet(
        path,
        index=False,
    )

    logger.info(
        "Saved Gold dataset: %s (%s rows)",
        filename,
        len(df),
    )


def main() -> None:
    df = read_silver()

    state_monthly = monthly_state_production(df)

    location_monthly = monthly_location_production(df)

    state_yearly = state_yearly_production(df)

    state_yearly = add_yoy_growth(
        state_yearly
    )

    save_dataset(
        state_monthly,
        "monthly_state_production.parquet",
    )

    save_dataset(
        location_monthly,
        "monthly_location_production.parquet",
    )

    save_dataset(
        state_yearly,
        "yearly_state_production.parquet",
    )


if __name__ == "__main__":
    main()