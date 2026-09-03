import pandas as pd

from src.transformations.anp_oil_gold import (
    state_yearly_production,
)


def test_state_yearly_production():
    df = pd.DataFrame({
        "year": [2025, 2025],
        "state": ["RJ", "RJ"],
        "production_m3": [100.0, 200.0],
    })

    result = state_yearly_production(df)

    assert len(result) == 1
    assert result.iloc[0]["production_m3"] == 300.0