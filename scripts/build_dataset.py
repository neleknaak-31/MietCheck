"""Build the MietCheck modelling table from the downloaded raw sources.

The raw Zensus files remain unchanged. This script performs explicit parsing,
validated one-to-one joins on the INSPIRE 100 m grid identifier and writes a
columnar Parquet table plus an auditable JSON build report.

Usage:
    python scripts/build_dataset.py
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "model_table.parquet"
REPORT_FILE = PROCESSED_DIR / "build_report.json"
PUBLIC_REPORT_FILE = PROJECT_ROOT / "reports" / "dataset_build_report.json"
RAW_MANIFEST = RAW_DIR / "source_manifest.json"

GRID_ID = "GITTER_ID_100m"
ZERO_MARKER = "\u2013"


@dataclass(frozen=True)
class FeatureSpec:
    filename: str
    source_column: str
    output_column: str
    uncertainty_column: str | None = None


FEATURES = (
    FeatureSpec("zensus2022_population.zip", "Einwohner", "population"),
    FeatureSpec(
        "zensus2022_average_household_size.zip",
        "DurchschnHHGroesse",
        "avg_household_size",
        "household_size_uncertain",
    ),
    FeatureSpec(
        "zensus2022_ownership_rate.zip",
        "Eigentuemerquote",
        "ownership_rate_pct",
        "ownership_uncertain",
    ),
    FeatureSpec(
        "zensus2022_vacancy_rate.zip",
        "Leerstandsquote",
        "vacancy_rate_pct",
        "vacancy_uncertain",
    ),
    FeatureSpec(
        "zensus2022_average_dwelling_area.zip",
        "durchschnFlaechejeWohn",
        "avg_dwelling_area_sqm",
        "dwelling_area_uncertain",
    ),
    FeatureSpec(
        "zensus2022_rent_and_dwelling_count.zip",
        "AnzahlWohnungen",
        "dwelling_count",
        "rent_count_uncertain",
    ),
)


def csv_entry_100m(archive: zipfile.ZipFile) -> str:
    candidates = [
        name
        for name in archive.namelist()
        if name.lower().endswith(".csv") and "100m" in name.lower()
    ]
    if len(candidates) != 1:
        raise ValueError(f"Expected one 100 m CSV, found {candidates}")
    return candidates[0]


def read_header(archive: zipfile.ZipFile, entry: str) -> list[str]:
    with archive.open(entry) as handle:
        line = handle.readline().decode("utf-8-sig").strip()
    return line.split(";")


def marker_column(columns: list[str]) -> str | None:
    return next(
        (column for column in columns if column.casefold() == "werterlaeuternde_zeichen"),
        None,
    )


def to_numeric(series: pd.Series) -> pd.Series:
    if is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    missing = series.isna()
    cleaned = (
        series.astype("string")
        .str.strip()
        .mask(lambda values: values.eq(ZERO_MARKER), "0")
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce").mask(missing)


def read_context_feature(spec: FeatureSpec) -> pd.DataFrame:
    path = RAW_DIR / spec.filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python scripts/download_data.py")
    with zipfile.ZipFile(path) as archive:
        entry = csv_entry_100m(archive)
        columns = read_header(archive, entry)
        marker = marker_column(columns)
        usecols = [GRID_ID, spec.source_column]
        if marker:
            usecols.append(marker)
        with archive.open(entry) as handle:
            frame = pd.read_csv(handle, sep=";", usecols=usecols, low_memory=False)

    frame[spec.output_column] = to_numeric(frame.pop(spec.source_column))
    keep = [GRID_ID, spec.output_column]
    if spec.uncertainty_column:
        if marker:
            frame[spec.uncertainty_column] = frame.pop(marker).eq("KLAMMERN")
        else:
            frame[spec.uncertainty_column] = False
        keep.append(spec.uncertainty_column)
    frame = frame[keep]
    if frame[GRID_ID].duplicated().any():
        raise ValueError(f"Duplicate grid identifiers in {spec.filename}")
    return frame


def read_target() -> pd.DataFrame:
    path = RAW_DIR / "zensus2022_rent_building_age_size.zip"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python scripts/download_data.py")
    with zipfile.ZipFile(path) as archive:
        entry = csv_entry_100m(archive)
        with archive.open(entry) as handle:
            frame = pd.read_csv(handle, sep=";", decimal=",", low_memory=False)

    expected = {
        GRID_ID,
        "x_mp_100m",
        "y_mp_100m",
        "GEBAEUDEALTER",
        "WOHNUNGSGROESSE",
        "durchschnMieteQM",
        "Werterlaeuternde_Zeichen",
    }
    missing = expected.difference(frame.columns)
    if missing:
        raise ValueError(f"Target data is missing columns: {sorted(missing)}")

    age_map = {"alt_1990_und_frueher": 0, "jung_nach_1990": 1}
    size_map = {"klein_65qm_und_weniger": 0, "gross_ueber_65qm": 1}
    unknown_age = set(frame["GEBAEUDEALTER"].dropna().unique()).difference(age_map)
    unknown_size = set(frame["WOHNUNGSGROESSE"].dropna().unique()).difference(size_map)
    if unknown_age or unknown_size:
        raise ValueError(
            f"Unexpected categories: building_age={unknown_age}, dwelling_size={unknown_size}"
        )

    frame = frame.rename(
        columns={
            "x_mp_100m": "x_laea_m",
            "y_mp_100m": "y_laea_m",
            "durchschnMieteQM": "rent_eur_sqm",
        }
    )
    frame["building_after_1990"] = frame.pop("GEBAEUDEALTER").map(age_map).astype("int8")
    frame["dwelling_over_65sqm"] = frame.pop("WOHNUNGSGROESSE").map(size_map).astype("int8")
    frame["target_uncertain"] = frame.pop("Werterlaeuternde_Zeichen").eq("KLAMMERN")
    frame["x_laea_m"] = frame["x_laea_m"].astype("int32")
    frame["y_laea_m"] = frame["y_laea_m"].astype("int32")
    frame["rent_eur_sqm"] = frame["rent_eur_sqm"].astype("float32")
    frame["spatial_block_25km"] = (
        (frame["x_laea_m"] // 25_000).astype("string")
        + "_"
        + (frame["y_laea_m"] // 25_000).astype("string")
    )
    return frame


def validate_output(frame: pd.DataFrame) -> None:
    if len(frame) < 2_000_000:
        raise ValueError(f"Unexpectedly small model table: {len(frame):,} rows")
    if frame["rent_eur_sqm"].isna().any():
        raise ValueError("Target contains missing values")
    if not frame["rent_eur_sqm"].between(0.5, 60).all():
        bad = frame.loc[~frame["rent_eur_sqm"].between(0.5, 60), "rent_eur_sqm"]
        raise ValueError(f"Target outside the expected range: {bad.describe().to_dict()}")
    key = [GRID_ID, "building_after_1990", "dwelling_over_65sqm"]
    if frame.duplicated(key).any():
        raise ValueError("Duplicate target grain after joining context features")


def build_report(frame: pd.DataFrame) -> dict[str, object]:
    context_columns = [spec.output_column for spec in FEATURES]
    manifest = (
        json.loads(RAW_MANIFEST.read_text(encoding="utf-8")) if RAW_MANIFEST.exists() else None
    )
    return {
        "schema_version": 1,
        "built_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "rows": len(frame),
        "unique_grid_cells": int(frame[GRID_ID].nunique()),
        "spatial_blocks_25km": int(frame["spatial_block_25km"].nunique()),
        "target": {
            "name": "rent_eur_sqm",
            "min": float(frame["rent_eur_sqm"].min()),
            "median": float(frame["rent_eur_sqm"].median()),
            "mean": float(frame["rent_eur_sqm"].mean()),
            "max": float(frame["rent_eur_sqm"].max()),
            "uncertain_share": float(frame["target_uncertain"].mean()),
        },
        "feature_non_null_share": {
            column: float(frame[column].notna().mean()) for column in context_columns
        },
        "raw_source_manifest": manifest,
    }


def main() -> None:
    print("Reading target data...")
    target = read_target()
    context = target[[GRID_ID]].drop_duplicates().reset_index(drop=True)

    for spec in FEATURES:
        print(f"Joining {spec.output_column} from {spec.filename}...")
        feature = read_context_feature(spec)
        context = context.merge(feature, on=GRID_ID, how="left", validate="one_to_one")

    print("Joining context features to target grain...")
    model_table = target.merge(context, on=GRID_ID, how="left", validate="many_to_one")
    validate_output(model_table)

    for column in (
        "avg_household_size",
        "ownership_rate_pct",
        "vacancy_rate_pct",
        "avg_dwelling_area_sqm",
    ):
        model_table[column] = model_table[column].astype("float32")
    for column in ("population", "dwelling_count"):
        model_table[column] = model_table[column].astype("float32")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing {OUTPUT_FILE.relative_to(PROJECT_ROOT)}...")
    model_table.to_parquet(OUTPUT_FILE, index=False, compression="zstd")
    report = build_report(model_table)
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    PUBLIC_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Built {len(model_table):,} rows across "
        f"{model_table[GRID_ID].nunique():,} grid cells and "
        f"{model_table['spatial_block_25km'].nunique():,} spatial blocks."
    )
    print(f"Report: {REPORT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
