import pandas as pd
import pytest

from src.app_logic import burden_label, category_codes, evaluate_scenario


def profile() -> pd.Series:
    return pd.Series(
        {
            "region": "Teststadt",
            "period": "2026-Q1",
            "asking_median_eur_sqm": 12.0,
            "asking_p25_eur_sqm": 10.0,
            "asking_p75_eur_sqm": 14.0,
            "index_qoq_pct": 1.5,
            "index_yoy_pct": 4.0,
            "stock_2022_age0_size0_eur_sqm": 7.0,
            "stock_2022_age0_size1_eur_sqm": 8.0,
            "stock_2022_age1_size0_eur_sqm": 9.0,
            "stock_2022_age1_size1_eur_sqm": 10.0,
            "interval_age0_size0_half_width_eur_sqm": 2.0,
            "interval_age0_size1_half_width_eur_sqm": 2.0,
            "interval_age1_size0_half_width_eur_sqm": 3.0,
            "interval_age1_size1_half_width_eur_sqm": 3.0,
        }
    )


def test_category_thresholds_follow_official_bins() -> None:
    assert category_codes(65, 1990) == (0, 0)
    assert category_codes(65.1, 1991) == (1, 1)


def test_evaluate_scenario_calculates_three_rent_realities() -> None:
    result = evaluate_scenario(
        profile(),
        area_sqm=70,
        construction_year=1980,
        current_cold_rent=700,
        net_income=3_000,
    )
    assert result["stock_monthly"] == 560
    assert result["asking_monthly"] == 840
    assert result["moving_premium_monthly"] == 280
    assert result["personal_move_delta_monthly"] == 140
    assert result["current_sqm"] == 10
    assert result["asking_burden"] == pytest.approx(0.28)


def test_burden_labels_are_descriptive_not_normative() -> None:
    assert burden_label(None) == "nicht berechnet"
    assert burden_label(0.29) == "unter 30 %"
    assert burden_label(0.35) == "30–40 %"
    assert burden_label(0.41) == "über 40 %"
