"""Compare candidate regression algorithms under spatial group validation.

All candidates receive the same deterministic 600k-row sample and the same
three GroupKFold splits over 25 km spatial blocks. The benchmark is used for
algorithm selection; the selected scalable model is validated on all rows in a
separate workflow.

Usage:
    python scripts/algorithm_benchmark.py
    python scripts/algorithm_benchmark.py --sample-rows 200000
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "model_table.parquet"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "algorithm_benchmark.json"
RANDOM_STATE = 2026
TARGET = "rent_eur_sqm"
GROUP = "spatial_block_25km"
CATEGORY_FEATURES = ["building_after_1990", "dwelling_over_65sqm"]
FEATURES = [
    "x_laea_m",
    "y_laea_m",
    *CATEGORY_FEATURES,
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


def regression_metrics(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, prediction)),
        "median_ae": float(median_absolute_error(y_true, prediction)),
        "rmse": float(root_mean_squared_error(y_true, prediction)),
        "r2": float(r2_score(y_true, prediction)),
    }


def category_median_prediction(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    medians = train.groupby(CATEGORY_FEATURES, observed=True)[TARGET].median()
    fallback = float(train[TARGET].median())
    keys = pd.MultiIndex.from_frame(test[CATEGORY_FEATURES])
    return medians.reindex(keys, fill_value=fallback).to_numpy(dtype="float32")


def model_factories() -> dict[str, Callable[[], object]]:
    def impute_and_scale() -> Pipeline:
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]
        )

    return {
        "ridge": lambda: Pipeline(
            [
                ("prepare", impute_and_scale()),
                ("model", Ridge(alpha=10.0)),
            ]
        ),
        "random_forest": lambda: Pipeline(
            [
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                (
                    "model",
                    RandomForestRegressor(
                        n_estimators=60,
                        max_depth=20,
                        min_samples_leaf=50,
                        max_features=0.8,
                        n_jobs=-1,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "hist_gradient_boosting": lambda: HistGradientBoostingRegressor(
            loss="absolute_error",
            learning_rate=0.08,
            max_iter=250,
            max_leaf_nodes=63,
            min_samples_leaf=100,
            l2_regularization=1.0,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=20,
            random_state=RANDOM_STATE,
        ),
        "mlp": lambda: Pipeline(
            [
                ("prepare", impute_and_scale()),
                (
                    "model",
                    MLPRegressor(
                        hidden_layer_sizes=(64, 32),
                        activation="relu",
                        solver="adam",
                        alpha=0.0001,
                        batch_size=2048,
                        learning_rate_init=0.001,
                        max_iter=80,
                        early_stopping=True,
                        validation_fraction=0.1,
                        n_iter_no_change=8,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def mean_and_std(folds: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    metric_names = ["mae", "median_ae", "rmse", "r2"]
    return {
        metric: {
            "mean": float(np.mean([fold["metrics"][metric] for fold in folds])),
            "std": float(np.std([fold["metrics"][metric] for fold in folds])),
        }
        for metric in metric_names
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=600_000,
        help="Deterministic row sample used for the fair algorithm comparison.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")
    if TARGET in FEATURES or "target_uncertain" in FEATURES:
        raise AssertionError("Target information must not be used as a model feature")

    columns = [*FEATURES, TARGET, GROUP, "target_uncertain"]
    print(f"Reading {DATA_FILE.relative_to(PROJECT_ROOT)}...")
    frame = pd.read_parquet(DATA_FILE, columns=columns)
    if args.sample_rows < len(frame):
        frame = frame.sample(n=args.sample_rows, random_state=RANDOM_STATE)
    frame = frame.reset_index(drop=True)
    print(f"Benchmark sample: {len(frame):,} rows across {frame[GROUP].nunique():,} spatial blocks")

    splitter = GroupKFold(n_splits=3)
    splits = list(splitter.split(frame, groups=frame[GROUP]))
    report_models: dict[str, object] = {}

    baseline_folds: list[dict[str, object]] = []
    for fold_number, (train_index, test_index) in enumerate(splits, start=1):
        train = frame.iloc[train_index]
        test = frame.iloc[test_index]
        prediction = category_median_prediction(train, test)
        baseline_folds.append(
            {
                "fold": fold_number,
                "training_rows": len(train),
                "test_rows": len(test),
                "metrics": regression_metrics(test[TARGET].to_numpy(), prediction),
            }
        )
    report_models["category_median"] = {
        "folds": baseline_folds,
        "summary": mean_and_std(baseline_folds),
    }

    x = frame[FEATURES].to_numpy(dtype="float32", na_value=np.nan)
    y = frame[TARGET].to_numpy(dtype="float32")
    for model_name, factory in model_factories().items():
        print(f"\n=== {model_name} ===")
        model_folds: list[dict[str, object]] = []
        for fold_number, (train_index, test_index) in enumerate(splits, start=1):
            model = factory()
            started = time.perf_counter()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model.fit(x[train_index], y[train_index])
            elapsed = time.perf_counter() - started
            prediction = np.asarray(model.predict(x[test_index]), dtype="float32")
            fold_metrics = regression_metrics(y[test_index], prediction)
            warning_messages = sorted({str(item.message) for item in caught})
            result = {
                "fold": fold_number,
                "training_rows": len(train_index),
                "test_rows": len(test_index),
                "training_seconds": elapsed,
                "metrics": fold_metrics,
                "warnings": warning_messages,
            }
            model_folds.append(result)
            print(
                f"fold {fold_number}: MAE={fold_metrics['mae']:.4f}, "
                f"R2={fold_metrics['r2']:.4f}, train={elapsed:.1f}s"
            )
        report_models[model_name] = {
            "folds": model_folds,
            "summary": mean_and_std(model_folds),
        }

    ranked = sorted(
        (
            {
                "model": name,
                "mean_mae": details["summary"]["mae"]["mean"],
                "std_mae": details["summary"]["mae"]["std"],
            }
            for name, details in report_models.items()
        ),
        key=lambda item: item["mean_mae"],
    )
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Spatially grouped candidate algorithm comparison",
        "sample": {
            "rows": len(frame),
            "spatial_blocks": int(frame[GROUP].nunique()),
            "random_state": RANDOM_STATE,
        },
        "validation": {
            "method": "GroupKFold",
            "groups": GROUP,
            "folds": 3,
        },
        "features": FEATURES,
        "models": report_models,
        "ranking_by_mean_mae": ranked,
    }
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nRanking:")
    for rank, item in enumerate(ranked, start=1):
        print(f"{rank}. {item['model']}: MAE={item['mean_mae']:.4f} +/- {item['std_mae']:.4f}")
    print(f"Report: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
