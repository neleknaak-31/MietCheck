import pandas as pd

from scripts.build_greix import prepare_quarterly


def sample_raw() -> pd.DataFrame:
    rows = []
    periods = [(year, quarter) for year in range(2012, 2026) for quarter in range(1, 5)]
    periods.append((2026, 1))
    for city in [f"City {index}" for index in range(37)] + ["Greix"]:
        for sequence, (year, quarter) in enumerate(periods):
            rows.append(
                {
                    "Year": year,
                    "Quarter": quarter,
                    "Month": None,
                    "City": city,
                    "Index": 100 + sequence,
                    "AVG_PRICE_SQM": 12.0,
                    "MED_PRICE_SQM": 11.5,
                    "P75_PRICE_SQM": 14.0,
                    "P25_PRICE_SQM": 9.0,
                    "Inflation_adjusted": 0,
                }
            )
            rows.append(
                {
                    "Year": year,
                    "Quarter": quarter,
                    "Month": None,
                    "City": city,
                    "Index": 99,
                    "AVG_PRICE_SQM": 11.0,
                    "MED_PRICE_SQM": 10.5,
                    "P75_PRICE_SQM": 13.0,
                    "P25_PRICE_SQM": 8.0,
                    "Inflation_adjusted": 1,
                }
            )
    return pd.DataFrame(rows)


def test_prepare_quarterly_selects_nominal_quarter_rows() -> None:
    result = prepare_quarterly(sample_raw())
    assert len(result) == 2_166
    assert result["region"].nunique() == 38
    assert not result["is_national_reference"].isna().any()
    assert result["period"].max() == "2026-Q1"


def test_prepare_quarterly_calculates_changes_per_region() -> None:
    result = prepare_quarterly(sample_raw())
    first = result.groupby("region", observed=True).head(1)
    second = result.groupby("region", observed=True).tail(1)
    assert first["index_qoq_pct"].isna().all()
    assert second["index_qoq_pct"].notna().all()
