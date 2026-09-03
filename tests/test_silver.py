import pandas as pd

from src.transformations.anp_oil_silver import (
    create_month_number,
    remove_duplicates,
)


def test_create_month_number():
    df = pd.DataFrame({
        "month": ["JAN", "FEV", "DEZ"]
    })

    result = create_month_number(df)

    assert result["month_number"].tolist() == [1, 2, 12]


def test_remove_duplicates():
    df = pd.DataFrame({
        "year": [2025, 2025],
        "state": ["RJ", "RJ"],
    })

    result = remove_duplicates(df)

    assert len(result) == 1