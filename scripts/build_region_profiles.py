"""Geocode GREIX regions and build deployable local Zensus reference profiles.

Region centres are fetched once from OpenStreetMap Nominatim and committed as a
small attributed lookup. They are transformed to ETRS89-LAEA (EPSG:3035).
For every centre, median context values from nearby occupied Zensus cells feed
the final model for all four building-age/size combinations.

Usage:
    python scripts/build_region_profiles.py
    python scripts/build_region_profiles.py --refresh-centres
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from pyproj import Transformer
from sklearn.neighbors import NearestNeighbors

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LATEST_GREIX_FILE = PROJECT_ROOT / "data" / "app" / "greix_latest.csv"
CENTRES_FILE = PROJECT_ROOT / "data" / "app" / "greix_region_centres.csv"
PROFILES_FILE = PROJECT_ROOT / "data" / "app" / "region_profiles.csv"
PROFILE_METADATA_FILE = PROJECT_ROOT / "data" / "app" / "region_profiles_metadata.json"
MODEL_TABLE_FILE = PROJECT_ROOT / "data" / "processed" / "model_table.parquet"
MODEL_FILE = PROJECT_ROOT / "models" / "zensus_hgb.joblib"
MODEL_METADATA_FILE = PROJECT_ROOT / "models" / "zensus_hgb_meta.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "MietCheck/1.0 academic data-analytics project"
CONTEXT_FEATURES = [
    "population",
    "avg_household_size",
    "ownership_rate_pct",
    "vacancy_rate_pct",
    "avg_dwelling_area_sqm",
    "dwelling_count",
    "household_size_uncertain",
    "ownership_uncertain",
    "vacancy_uncertain",
    "dwelling_area_uncertain",
    "rent_count_uncertain",
]


def geocode_region(region: str) -> dict[str, object]:
    location_query = (
        {"q": f"{region}, Deutschland"}
        if "Kreis" in region
        else {"city": region, "country": "Deutschland"}
    )
    params = urllib.parse.urlencode(
        {
            **location_query,
            "format": "jsonv2",
            "countrycodes": "de",
            "limit": 1,
            "addressdetails": 0,
        }
    )
    request = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT, "Accept-Language": "de"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        results = json.loads(response.read().decode("utf-8"))
    if not results:
        raise ValueError(f"No Nominatim result for {region}")
    result = results[0]
    return {
        "region": region,
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
        "osm_type": result["osm_type"],
        "osm_id": result["osm_id"],
        "display_name": result["display_name"],
    }


def fetch_centres(regions: list[str]) -> pd.DataFrame:
    rows = []
    for index, region in enumerate(regions, start=1):
        print(f"Geocoding {index}/{len(regions)}: {region}", flush=True)
        rows.append(geocode_region(region))
        if index < len(regions):
            time.sleep(1.1)
    return pd.DataFrame(rows).sort_values("region", ignore_index=True)


def validate_centres(centres: pd.DataFrame, expected_regions: set[str]) -> None:
    if set(centres["region"]) != expected_regions:
        missing = expected_regions.difference(centres["region"])
        extra = set(centres["region"]).difference(expected_regions)
        raise ValueError(f"Region-centre mismatch: missing={missing}, extra={extra}")
    if centres["region"].duplicated().any():
        raise ValueError("Duplicate GREIX region centres")
    if not centres["latitude"].between(47, 56).all():
        raise ValueError("Latitude outside Germany")
    if not centres["longitude"].between(5, 16).all():
        raise ValueError("Longitude outside Germany")


def transform_centres(centres: pd.DataFrame) -> pd.DataFrame:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    x, y = transformer.transform(
        centres["longitude"].astype(float).tolist(),
        centres["latitude"].astype(float).tolist(),
    )
    transformed = centres.copy()
    transformed["x_laea_m"] = np.asarray(x).round().astype("int32")
    transformed["y_laea_m"] = np.asarray(y).round().astype("int32")
    return transformed


def context_profiles(
    centres: pd.DataFrame,
    grid_context: pd.DataFrame,
    neighbors: int = 500,
    radius_m: float = 10_000,
) -> pd.DataFrame:
    search = NearestNeighbors(n_neighbors=neighbors, algorithm="kd_tree")
    search.fit(grid_context[["x_laea_m", "y_laea_m"]].to_numpy())
    distances, indices = search.kneighbors(
        centres[["x_laea_m", "y_laea_m"]].to_numpy(), return_distance=True
    )
    profiles = []
    for row_number, centre in centres.reset_index(drop=True).iterrows():
        inside = distances[row_number] <= radius_m
        selected_indices = indices[row_number][inside]
        selected_distances = distances[row_number][inside]
        if len(selected_indices) < 30:
            selected_indices = indices[row_number][:100]
            selected_distances = distances[row_number][:100]
        neighborhood = grid_context.iloc[selected_indices]
        profile = {
            "region": centre["region"],
            "latitude": centre["latitude"],
            "longitude": centre["longitude"],
            "x_laea_m": centre["x_laea_m"],
            "y_laea_m": centre["y_laea_m"],
            "context_cells": len(neighborhood),
            "nearest_grid_distance_m": float(selected_distances.min()),
            "farthest_context_distance_m": float(selected_distances.max()),
        }
        for feature in CONTEXT_FEATURES:
            profile[feature] = float(neighborhood[feature].median())
        profiles.append(profile)
    return pd.DataFrame(profiles)


def add_model_predictions(profiles: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(MODEL_FILE)
    metadata = json.loads(MODEL_METADATA_FILE.read_text(encoding="utf-8"))
    rows = []
    for _, profile in profiles.iterrows():
        result = profile.to_dict()
        for building_after_1990 in (0, 1):
            for dwelling_over_65sqm in (0, 1):
                model_input = {
                    **profile.to_dict(),
                    "building_after_1990": building_after_1990,
                    "dwelling_over_65sqm": dwelling_over_65sqm,
                }
                vector = np.asarray(
                    [[model_input[feature] for feature in metadata["feature_order"]]],
                    dtype="float32",
                )
                prediction = float(model.predict(vector)[0])
                suffix = f"age{building_after_1990}_size{dwelling_over_65sqm}"
                result[f"stock_2022_{suffix}_eur_sqm"] = prediction
                category = f"{building_after_1990}_{dwelling_over_65sqm}"
                result[f"interval_{suffix}_half_width_eur_sqm"] = metadata[
                    "category_interval_half_widths_eur_sqm"
                ][category]
        rows.append(result)
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-centres",
        action="store_true",
        help="Refresh the attributed Nominatim region-centre lookup.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    required = [LATEST_GREIX_FILE, MODEL_TABLE_FILE, MODEL_FILE, MODEL_METADATA_FILE]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")

    greix = pd.read_csv(LATEST_GREIX_FILE)
    local_regions = sorted(greix.loc[~greix["is_national_reference"], "region"].unique())
    if args.refresh_centres or not CENTRES_FILE.exists():
        centres = fetch_centres(local_regions)
        centres.to_csv(
            CENTRES_FILE,
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            float_format="%.7f",
        )
    else:
        centres = pd.read_csv(CENTRES_FILE)
    validate_centres(centres, set(local_regions))
    centres = transform_centres(centres)

    grid_columns = ["GITTER_ID_100m", "x_laea_m", "y_laea_m", *CONTEXT_FEATURES]
    grid_context = (
        pd.read_parquet(MODEL_TABLE_FILE, columns=grid_columns)
        .drop_duplicates("GITTER_ID_100m")
        .reset_index(drop=True)
    )
    print(f"Building local profiles from {len(grid_context):,} grid cells...", flush=True)
    profiles = context_profiles(centres, grid_context)
    profiles = add_model_predictions(profiles)
    profiles = profiles.merge(
        greix.drop(columns=["is_national_reference"]), on="region", validate="one_to_one"
    )
    stock_columns = [column for column in profiles if column.startswith("stock_2022_")]
    if len(profiles) != 37 or profiles[stock_columns].isna().any().any():
        raise AssertionError("Incomplete deployable region profiles")
    if not profiles[stock_columns].stack().between(1, 50).all():
        raise AssertionError("Implausible regional stock-rent prediction")
    profiles.to_csv(PROFILES_FILE, index=False, float_format="%.6f")

    profile_metadata = {
        "schema_version": 1,
        "regions": len(profiles),
        "greix_period": str(profiles["period"].max()),
        "zensus_reference_date": "2022-05-15",
        "context_method": (
            "Median context of up to 500 occupied Zensus cells within 10 km of the "
            "Nominatim region centre; at least the 100 nearest cells as fallback"
        ),
        "coordinate_reference_system": "ETRS89-extended / LAEA Europe (EPSG:3035)",
        "geocoding_source": "OpenStreetMap contributors, Nominatim",
        "geocoding_license": "Open Database License (ODbL)",
        "geocoding_url": "https://nominatim.openstreetmap.org/",
        "model_file": MODEL_FILE.name,
    }
    PROFILE_METADATA_FILE.write_text(
        json.dumps(profile_metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Profiles: {PROFILES_FILE.relative_to(PROJECT_ROOT)} ({len(profiles)} regions)")


if __name__ == "__main__":
    main()
