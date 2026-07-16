"""Measure incremental feature value with spatially grouped validation.

The selected HGB parameters are read from the tuning report. Every feature set
receives the same development sample and the same three spatial folds. Locked
calibration and test blocks remain unused.

Usage:
    python scripts/feature_ablation.py
    python scripts/feature_ablation.py --sample-rows 100000
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

if __package__:
    from scripts.tune_hgb import (
        DATA_FILE,
        FEATURES,
        GROUP,
        RANDOM_STATE,
        TARGET,
        group_digest,
        spatial_group_partition,
        validate_partitions,
    )
else:
    from tune_hgb import (
        DATA_FILE,
        FEATURES,
        GROUP,
        RANDOM_STATE,
        TARGET,
        group_digest,
        spatial_group_partition,
        validate_partitions,
    )

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TUNING_REPORT = PROJECT_ROOT / "reports" / "hgb_tuning.json"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "feature_ablation.json"

CATEGORY_FEATURES = ["building_after_1990", "dwelling_over_65sqm"]
LOCATION_FEATURES = ["x_laea_m", "y_laea_m", *CATEGORY_FEATURES]
NUMERIC_CONTEXT_FEATURES = [
    *LOCATION_FEATURES,
    "population",
    "avg_household_size",
    "ownership_rate_pct",
    "vacancy_rate_pct",
    "avg_dwelling_area_sqm",
    "dwelling_count",
]
FEATURE_SETS = {
    "categories_only": CATEGORY_FEATURES,
    "location": LOCATION_FEATURES,
    "location_plus_numeric_context": NUMERIC_CONTEXT_FEATURES,
    "all_context_and_quality_flags": FEATURES,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=300_000,
        help="Maximum development rows used for each feature-set comparison.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")
    if not TUNING_REPORT.exists():
        raise FileNotFoundError(f"Missing {TUNING_REPORT}. Run: python scripts/tune_hgb.py")

    tuning = json.loads(TUNING_REPORT.read_text(encoding="utf-8"))
    parameters = tuning["selected_parameters"]
    columns = sorted(set(FEATURES + [TARGET, GROUP]))
    frame = pd.read_parquet(DATA_FILE, columns=columns)
    partitions = spatial_group_partition(frame[GROUP])
    validate_partitions(partitions)
    for name, group_set in partitions.items():
        expected = tuning["partition"][name]["group_sha256"]
        if group_digest(group_set) != expected:
            raise AssertionError(f"Partition drift detected for {name}")

    development = frame[frame[GROUP].astype(str).isin(partitions["development"])].copy()
    if args.sample_rows < len(development):
        development = development.sample(n=args.sample_rows, random_state=RANDOM_STATE)
    development = development.reset_index(drop=True)
    groups = development[GROUP].to_numpy()
    y = development[TARGET].to_numpy(dtype="float32")
    splits = list(GroupKFold(n_splits=3).split(development, y, groups))
    print(
        f"Ablation sample: {len(development):,} rows across "
        f"{development[GROUP].nunique():,} development blocks",
        flush=True,
    )

    feature_set_results: dict[str, object] = {}
    for set_name, features in FEATURE_SETS.items():
        print(f"\n=== {set_name}: {len(features)} features ===", flush=True)
        x = development[features].to_numpy(dtype="float32", na_value=np.nan)
        folds = []
        for fold_number, (train_index, validation_index) in enumerate(splits, start=1):
            model = HistGradientBoostingRegressor(
                loss="absolute_error",
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=20,
                random_state=RANDOM_STATE,
                **parameters,
            )
            started = time.perf_counter()
            model.fit(x[train_index], y[train_index])
            elapsed = time.perf_counter() - started
            prediction = model.predict(x[validation_index]).astype("float32")
            metrics = {
                "mae": float(mean_absolute_error(y[validation_index], prediction)),
                "r2": float(r2_score(y[validation_index], prediction)),
            }
            folds.append(
                {
                    "fold": fold_number,
                    "training_rows": len(train_index),
                    "validation_rows": len(validation_index),
                    "training_seconds": elapsed,
                    "metrics": metrics,
                }
            )
            print(
                f"fold {fold_number}: MAE={metrics['mae']:.4f}, "
                f"R2={metrics['r2']:.4f}, train={elapsed:.1f}s",
                flush=True,
            )
        feature_set_results[set_name] = {
            "features": features,
            "folds": folds,
            "summary": {
                "mean_mae": float(np.mean([fold["metrics"]["mae"] for fold in folds])),
                "std_mae": float(np.std([fold["metrics"]["mae"] for fold in folds])),
                "mean_r2": float(np.mean([fold["metrics"]["r2"] for fold in folds])),
                "mean_training_seconds": float(
                    np.mean([fold["training_seconds"] for fold in folds])
                ),
            },
        }

    baseline_mae = feature_set_results["categories_only"]["summary"]["mean_mae"]
    previous_mae = None
    comparison = []
    for set_name in FEATURE_SETS:
        result = feature_set_results[set_name]["summary"]
        mean_mae = result["mean_mae"]
        comparison.append(
            {
                "feature_set": set_name,
                "mean_mae": mean_mae,
                "improvement_vs_categories": (baseline_mae - mean_mae) / baseline_mae,
                "improvement_vs_previous": (
                    None if previous_mae is None else (previous_mae - mean_mae) / previous_mae
                ),
            }
        )
        previous_mae = mean_mae

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Spatial feature ablation within development blocks",
        "data": {
            "rows": len(development),
            "blocks": int(development[GROUP].nunique()),
            "random_state": RANDOM_STATE,
        },
        "validation": "3-fold GroupKFold; calibration and test partitions unused",
        "model_parameters": parameters,
        "feature_sets": feature_set_results,
        "incremental_comparison": comparison,
    }
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nIncremental comparison:")
    for item in comparison:
        print(
            f"{item['feature_set']}: MAE={item['mean_mae']:.4f}, "
            f"vs categories={item['improvement_vs_categories']:.1%}"
        )
    print(f"Report: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
