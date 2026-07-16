"""Build the deployable quarterly GREIX asking-rent time series.

The official workbook contains monthly, quarterly and annual observations as
well as nominal and inflation-adjusted variants. MietCheck uses nominal
quarterly observations so that displayed EUR/m² values match current asking
rents and every region has one unambiguous value per quarter.

Usage:
    python scripts/build_greix.py
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "greix_city_metrics.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "app"
QUARTERLY_FILE = OUTPUT_DIR / "greix_quarterly.csv"
LATEST_FILE = OUTPUT_DIR / "greix_latest.csv"
METADATA_FILE = OUTPUT_DIR / "greix_metadata.json"

SOURCE_URL = (
    "https://www.kielinstitut.de/fileadmin/Dateiverwaltung/IfW_Unit/"
    "Macroeconomics/GREIX/Mietpreisindex/City_metrics_public.xlsx"
)
LANDING_PAGE = (
    "https://www.kielinstitut.de/de/institut/forschungszentren/"
    "makrooekonomie/makrofinanzen/mietpreisindex/"
)
EXPECTED_COLUMNS = {
    "Year",
    "Quarter",
    "Month",
    "City",
    "Index",
    "AVG_PRICE_SQM",
    "MED_PRICE_SQM",
    "P75_PRICE_SQM",
    "P25_PRICE_SQM",
    "Inflation_adjusted",
}


def prepare_quarterly(raw: pd.DataFrame) -> pd.DataFrame:
    missing = EXPECTED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"GREIX workbook is missing columns: {sorted(missing)}")

    quarterly = raw.loc[
        raw["Quarter"].notna() & raw["Month"].isna() & raw["Inflation_adjusted"].eq(0)
    ].copy()
    quarterly = quarterly.rename(
        columns={
            "Year": "year",
            "Quarter": "quarter",
            "City": "region",
            "Index": "rent_index",
            "AVG_PRICE_SQM": "asking_mean_eur_sqm",
            "MED_PRICE_SQM": "asking_median_eur_sqm",
            "P75_PRICE_SQM": "asking_p75_eur_sqm",
            "P25_PRICE_SQM": "asking_p25_eur_sqm",
        }
    )
    quarterly["year"] = quarterly["year"].astype("int16")
    quarterly["quarter"] = quarterly["quarter"].astype("int8")
    quarterly["period"] = quarterly["year"].astype(str) + "-Q" + quarterly["quarter"].astype(str)
    quarterly = quarterly[
        [
            "period",
            "year",
            "quarter",
            "region",
            "rent_index",
            "asking_mean_eur_sqm",
            "asking_median_eur_sqm",
            "asking_p25_eur_sqm",
            "asking_p75_eur_sqm",
        ]
    ].sort_values(["region", "year", "quarter"], ignore_index=True)
    quarterly["index_qoq_pct"] = (
        quarterly.groupby("region", observed=True)["rent_index"].pct_change() * 100
    )
    quarterly["index_yoy_pct"] = (
        quarterly.groupby("region", observed=True)["rent_index"].pct_change(4) * 100
    )
    quarterly["is_national_reference"] = quarterly["region"].eq("Greix")
    validate_quarterly(quarterly)
    return quarterly


def validate_quarterly(frame: pd.DataFrame) -> None:
    if len(frame) < 2_000:
        raise ValueError(f"Unexpectedly small GREIX quarterly table: {len(frame):,}")
    if frame.duplicated(["region", "year", "quarter"]).any():
        raise ValueError("Duplicate GREIX region-quarter observations")
    if frame["region"].nunique() < 38:
        raise ValueError("Expected at least 37 local GREIX regions plus national reference")
    if frame["quarter"].notna().any() and not frame["quarter"].between(1, 4).all():
        raise ValueError("Invalid quarter value")
    price_columns = [
        "asking_mean_eur_sqm",
        "asking_median_eur_sqm",
        "asking_p25_eur_sqm",
        "asking_p75_eur_sqm",
    ]
    available_prices = frame[price_columns].dropna(how="all")
    if not available_prices.stack().between(1, 100).all():
        raise ValueError("GREIX price outside expected range")
    if (frame["asking_p25_eur_sqm"] > frame["asking_p75_eur_sqm"]).fillna(False).any():
        raise ValueError("GREIX P25 exceeds P75")
    if frame["year"].max() < 2026 or frame["quarter"].max() < 1:
        raise ValueError("GREIX source is older than the required Q1 2026 release")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing {INPUT_FILE}. Run: python scripts/download_data.py")
    raw = pd.read_excel(INPUT_FILE, sheet_name="Sheet1")
    quarterly = prepare_quarterly(raw)
    latest = (
        quarterly.sort_values(["year", "quarter"])
        .groupby("region", observed=True, as_index=False)
        .tail(1)
        .sort_values("region", ignore_index=True)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    quarterly.to_csv(QUARTERLY_FILE, index=False, float_format="%.6f")
    latest.to_csv(LATEST_FILE, index=False, float_format="%.6f")
    metadata = {
        "schema_version": 1,
        "built_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_url": SOURCE_URL,
        "landing_page": LANDING_PAGE,
        "source_attribution": (
            "Kiel Institut für Weltwirtschaft auf Basis der VALUE Marktdatenbank"
        ),
        "price_basis": "Nominal quarterly asking rents",
        "rows": len(quarterly),
        "regions": int(quarterly["region"].nunique()),
        "local_regions": int(
            quarterly.loc[~quarterly["is_national_reference"], "region"].nunique()
        ),
        "first_period": quarterly["period"].iloc[0],
        "latest_period": latest.sort_values(["year", "quarter"])["period"].iloc[-1],
        "latest_regions": len(latest),
    }
    METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"GREIX: {len(quarterly):,} quarterly rows, "
        f"{quarterly['region'].nunique()} regions, latest={metadata['latest_period']}"
    )
    print(f"Output: {QUARTERLY_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
