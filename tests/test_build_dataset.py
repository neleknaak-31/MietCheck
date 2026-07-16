import pandas as pd

from scripts.build_dataset import ZERO_MARKER, marker_column, to_numeric


def test_to_numeric_parses_german_decimal_values() -> None:
    values = pd.Series(["12,50", "0,00", " 7,25 "])
    result = to_numeric(values)
    assert result.tolist() == [12.5, 0.0, 7.25]


def test_to_numeric_maps_official_zero_marker_to_zero() -> None:
    values = pd.Series([ZERO_MARKER, "3,50"])
    result = to_numeric(values)
    assert result.tolist() == [0.0, 3.5]


def test_to_numeric_keeps_invalid_values_missing() -> None:
    values = pd.Series(["not-a-number", None])
    assert to_numeric(values).isna().all()


def test_marker_column_is_case_insensitive() -> None:
    columns = ["GITTER_ID_100m", "Werterlaeuternde_Zeichen"]
    assert marker_column(columns) == "Werterlaeuternde_Zeichen"
