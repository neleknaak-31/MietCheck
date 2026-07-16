"""Tune Histogram Gradient Boosting with spatially isolated validation folds.

The script creates a persistent three-way split on 25 km blocks. Only the
development partition participates in hyperparameter selection; calibration
and final-test blocks stay locked for the subsequent final-model workflow.

Usage:
    python scripts/tune_hgb.py
    python scripts/tune_hgb.py --sample-rows 300000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GroupKFold

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "model_table.parquet"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "hgb_tuning.json"
RANDOM_STATE = 2026
TARGET = "rent_eur_sqm"
GROUP = "spatial_block_25km"
FEATURES = [
    "x_laea_m",
    "y_laea_m",
    "building_after_1990",
    "dwelling_over_65sqm",
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

# Deliberately compact, theory-guided search space for a large-data workflow.
# All candidates are evaluated on exactly the same spatial folds.
PARAMETER_CANDIDATES = [
    {
        "learning_rate": 0.04,
        "max_iter": 350,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 100,
        "l2_regularization": 1.0,
    },
    {
        "learning_rate": 0.06,
        "max_iter": 300,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 250,
        "l2_regularization": 5.0,
    },
    {
        "learning_rate": 0.06,
        "max_iter": 300,
        "max_leaf_nodes": 63,
        "min_samples_leaf": 100,
        "l2_regularization": 1.0,
    },
    {
        "learning_rate": 0.08,
        "max_iter": 250,
        "max_leaf_nodes": 63,
        "min_samples_leaf": 50,
        "l2_regularization": 0.0,
    },
    {
        "learning_rate": 0.08,
        "max_iter": 250,
        "max_leaf_nodes": 63,
        "min_samples_leaf": 100,
        "l2_regularization": 5.0,
    },
    {
        "learning_rate": 0.06,
        "max_iter": 300,
        "max_leaf_nodes": 127,
        "min_samples_leaf": 100,
        "l2_regularization": 5.0,
    },
    {
        "learning_rate": 0.08,
        "max_iter": 250,
        "max_leaf_nodes": 127,
        "min_samples_leaf": 250,
        "l2_regularization": 10.0,
    },
    {
        "learning_rate": 0.10,
        "max_iter": 200,
        "max_leaf_nodes": 63,
        "min_samples_leaf": 250,
        "l2_regularization": 10.0,
    },
]


def spatial_group_partition(
    groups: pd.Series,
    random_state: int = RANDOM_STATE,
) -> dict[str, set[str]]:
    """Return deterministic 70/15/15 development/calibration/test group sets."""
    unique_groups = np.asarray(sorted(groups.astype(str).unique()), dtype=object)
    if len(unique_groups) < 10:
        raise ValueError("At least ten spatial groups are required")
    rng = np.random.default_rng(random_state)
    rng.shuffle(unique_groups)
    calibration_count = round(len(unique_groups) * 0.15)
    test_count = round(len(unique_groups) * 0.15)
    return {
        "calibration": set(unique_groups[:calibration_count]),
        "test": set(unique_groups[calibration_count : calibration_count + test_count]),
        "development": set(unique_groups[calibration_count + test_count :]),
    }


def group_digest(groups: set[str]) -> str:
    payload = "\n".join(sorted(groups)).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_partitions(partitions: dict[str, set[str]]) -> None:
    names = list(partitions)
    for index, name in enumerate(names):
        for other_name in names[index + 1 :]:
            if partitions[name].intersection(partitions[other_name]):
                raise AssertionError(f"Spatial leakage between {name} and {other_name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=750_000,
        help="Maximum development rows used for spatial hyperparameter CV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")
    if TARGET in FEATURES or "target_uncertain" in FEATURES:
        raise AssertionError("Target information must not be used as a model feature")

    columns = [*FEATURES, TARGET, GROUP]
    print(f"Reading {DATA_FILE.relative_to(PROJECT_ROOT)}...")
    frame = pd.read_parquet(DATA_FILE, columns=columns)
    partitions = spatial_group_partition(frame[GROUP])
    validate_partitions(partitions)

    partition_rows = {
        name: int(frame[GROUP].astype(str).isin(group_set).sum())
        for name, group_set in partitions.items()
    }
    development = frame[frame[GROUP].astype(str).isin(partitions["development"])].copy()
    if args.sample_rows < len(development):
        development = development.sample(n=args.sample_rows, random_state=RANDOM_STATE)
    development = development.reset_index(drop=True)
    print(
        f"Tuning sample: {len(development):,} rows across "
        f"{development[GROUP].nunique():,} development blocks"
    )

    x = development[FEATURES].to_numpy(dtype="float32", na_value=np.nan)
    y = development[TARGET].to_numpy(dtype="float32")
    groups = development[GROUP].to_numpy()
    splits = list(GroupKFold(n_splits=3).split(x, y, groups))

    candidate_results: list[dict[str, object]] = []
    for candidate_number, parameters in enumerate(PARAMETER_CANDIDATES, start=1):
        print(f"\n=== candidate {candidate_number}/{len(PARAMETER_CANDIDATES)} ===")
        fold_results = []
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
                "rmse": float(root_mean_squared_error(y[validation_index], prediction)),
                "r2": float(r2_score(y[validation_index], prediction)),
            }
            fold_results.append(
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
                f"R2={metrics['r2']:.4f}, train={elapsed:.1f}s"
            )

        mean_mae = float(np.mean([fold["metrics"]["mae"] for fold in fold_results]))
        std_mae = float(np.std([fold["metrics"]["mae"] for fold in fold_results]))
        mean_r2 = float(np.mean([fold["metrics"]["r2"] for fold in fold_results]))
        candidate_results.append(
            {
                "candidate": candidate_number,
                "parameters": parameters,
                "folds": fold_results,
                "summary": {
                    "mean_mae": mean_mae,
                    "std_mae": std_mae,
                    "worst_fold_mae": float(max(fold["metrics"]["mae"] for fold in fold_results)),
                    "mean_r2": mean_r2,
                    "mean_training_seconds": float(
                        np.mean([fold["training_seconds"] for fold in fold_results])
                    ),
                },
            }
        )

    ranked = sorted(candidate_results, key=lambda item: item["summary"]["mean_mae"])
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Spatial HGB tuning with untouched calibration and final-test blocks",
        "data": {
            "total_rows": len(frame),
            "tuning_sample_rows": len(development),
            "tuning_sample_blocks": int(development[GROUP].nunique()),
            "random_state": RANDOM_STATE,
        },
        "partition": {
            name: {
                "rows": partition_rows[name],
                "blocks": len(group_set),
                "group_sha256": group_digest(group_set),
            }
            for name, group_set in partitions.items()
        },
        "validation": {
            "method": "3-fold GroupKFold within development blocks",
            "early_stopping": {
                "enabled": True,
                "validation_fraction_within_outer_training_fold": 0.1,
                "n_iter_no_change": 20,
            },
            "primary_metric": "MAE in EUR per square metre",
        },
        "features": FEATURES,
        "candidates": candidate_results,
        "ranking": [
            {
                "rank": rank,
                "candidate": item["candidate"],
                "mean_mae": item["summary"]["mean_mae"],
                "std_mae": item["summary"]["std_mae"],
            }
            for rank, item in enumerate(ranked, start=1)
        ],
        "selected_candidate": ranked[0]["candidate"],
        "selected_parameters": ranked[0]["parameters"],
    }
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nRanking:")
    for rank, item in enumerate(ranked, start=1):
        print(
            f"{rank}. candidate {item['candidate']}: "
            f"MAE={item['summary']['mean_mae']:.4f} +/- "
            f"{item['summary']['std_mae']:.4f}"
        )
    print(f"Report: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
