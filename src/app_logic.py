"""Pure scenario calculations shared by the Streamlit app and tests."""

from __future__ import annotations

from typing import Any

import pandas as pd


def category_codes(area_sqm: float, construction_year: int) -> tuple[int, int]:
    if area_sqm <= 0:
        raise ValueError("Living area must be positive")
    if not 1800 <= construction_year <= 2100:
        raise ValueError("Construction year is outside the supported range")
    return int(construction_year > 1990), int(area_sqm > 65)


def burden_label(share: float | None) -> str:
    if share is None:
        return "nicht berechnet"
    if share < 0.30:
        return "unter 30 %"
    if share < 0.40:
        return "30–40 %"
    return "über 40 %"


def evaluate_scenario(
    profile: pd.Series | dict[str, Any],
    *,
    area_sqm: float,
    construction_year: int,
    current_cold_rent: float | None,
    net_income: float | None,
) -> dict[str, float | int | str | None]:
    if current_cold_rent is not None and current_cold_rent < 0:
        raise ValueError("Current cold rent cannot be negative")
    if net_income is not None and net_income <= 0:
        raise ValueError("Net income must be positive")

    age_code, size_code = category_codes(area_sqm, construction_year)
    suffix = f"age{age_code}_size{size_code}"
    stock_sqm = float(profile[f"stock_2022_{suffix}_eur_sqm"])
    half_width_sqm = float(profile[f"interval_{suffix}_half_width_eur_sqm"])
    asking_sqm = float(profile["asking_median_eur_sqm"])
    market_p25_sqm = float(profile["asking_p25_eur_sqm"])
    market_p75_sqm = float(profile["asking_p75_eur_sqm"])

    stock_monthly = stock_sqm * area_sqm
    asking_monthly = asking_sqm * area_sqm
    current_sqm = (
        None
        if current_cold_rent is None or current_cold_rent == 0
        else current_cold_rent / area_sqm
    )
    current_burden = (
        None
        if current_cold_rent is None or current_cold_rent == 0 or net_income is None
        else current_cold_rent / net_income
    )
    asking_burden = None if net_income is None else asking_monthly / net_income

    return {
        "region": str(profile["region"]),
        "period": str(profile["period"]),
        "area_sqm": area_sqm,
        "construction_year": construction_year,
        "building_after_1990": age_code,
        "dwelling_over_65sqm": size_code,
        "stock_sqm": stock_sqm,
        "stock_lower_sqm": max(0.0, stock_sqm - half_width_sqm),
        "stock_upper_sqm": stock_sqm + half_width_sqm,
        "stock_monthly": stock_monthly,
        "asking_sqm": asking_sqm,
        "asking_monthly": asking_monthly,
        "market_p25_sqm": market_p25_sqm,
        "market_p75_sqm": market_p75_sqm,
        "market_p25_monthly": market_p25_sqm * area_sqm,
        "market_p75_monthly": market_p75_sqm * area_sqm,
        "moving_premium_sqm": asking_sqm - stock_sqm,
        "moving_premium_monthly": asking_monthly - stock_monthly,
        "moving_premium_pct": (asking_sqm / stock_sqm - 1) * 100,
        "current_cold_rent": current_cold_rent,
        "current_sqm": current_sqm,
        "personal_move_delta_monthly": (
            None
            if current_cold_rent is None or current_cold_rent == 0
            else asking_monthly - current_cold_rent
        ),
        "net_income": net_income,
        "current_burden": current_burden,
        "asking_burden": asking_burden,
        "current_burden_label": burden_label(current_burden),
        "asking_burden_label": burden_label(asking_burden),
        "interval_half_width_sqm": half_width_sqm,
        "interval_half_width_monthly": half_width_sqm * area_sqm,
        "index_qoq_pct": float(profile["index_qoq_pct"]),
        "index_yoy_pct": float(profile["index_yoy_pct"]),
    }
