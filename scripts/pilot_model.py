"""Run the first spatially honest MietCheck modelling feasibility test.

This is intentionally a pilot, not the final model-selection workflow. It
compares a category-median baseline with location-only and context-enriched
Histogram Gradient Boosting models on held-out 25 km spatial blocks.

Usage:
    python scripts/pilot_model.py
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "model_table.parquet"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "pilot_spatial_metrics.json"
RANDOM_STATE = 42

TARGET = "rent_eur_sqm"
CATEGORY_FEATURES = ["building_after_1990", "dwelling_over_65sqm"]
LOCATION_FEATURES = ["x_laea_m", "y_laea_m", *CATEGORY_FEATURES]
CONTEXT_FEATURES = [
    *LOCATION_FEATURES,
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


def metrics(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
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


def train_hist_gradient(
    train: pd.DataFrame, test: pd.DataFrame, features: list[str]
) -> tuple[np.ndarray, dict[str, object]]:
    model = HistGradientBoostingRegressor(
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
    )
    x_train = train[features].to_numpy(dtype="float32", na_value=np.nan)
    x_test = test[features].to_numpy(dtype="float32", na_value=np.nan)
    started = time.perf_counter()
    model.fit(x_train, train[TARGET].to_numpy(dtype="float32"))
    elapsed = time.perf_counter() - started
    prediction = model.predict(x_test).astype("float32")
    details = {
        "features": features,
        "training_seconds": elapsed,
        "iterations": int(model.n_iter_),
    }
    return prediction, details


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")

    print(f"Reading {DATA_FILE.relative_to(PROJECT_ROOT)}...")
    frame = pd.read_parquet(DATA_FILE)
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )
    train_index, test_index = next(splitter.split(frame, groups=frame["spatial_block_25km"]))
    train = frame.iloc[train_index].reset_index(drop=True)
    test = frame.iloc[test_index].reset_index(drop=True)
    train_blocks = set(train["spatial_block_25km"].unique())
    test_blocks = set(test["spatial_block_25km"].unique())
    if train_blocks.intersection(test_blocks):
        raise AssertionError("Spatial block leakage detected")

    print(
        f"Spatial split: {len(train):,} training rows / {len(test):,} test rows; "
        f"{len(train_blocks)} / {len(test_blocks)} blocks"
    )
    y_test = test[TARGET].to_numpy(dtype="float32")
    results: dict[str, object] = {}

    baseline_prediction = category_median_prediction(train, test)
    results["category_median"] = {"metrics": metrics(y_test, baseline_prediction)}
    print("Category median MAE:", results["category_median"]["metrics"]["mae"])

    for name, features in (
        ("hist_gradient_location", LOCATION_FEATURES),
        ("hist_gradient_context", CONTEXT_FEATURES),
    ):
        print(f"Training {name} with {len(features)} features...")
        prediction, details = train_hist_gradient(train, test, features)
        all_metrics = metrics(y_test, prediction)
        certain = ~test["target_uncertain"].to_numpy(dtype=bool)
        details["metrics"] = all_metrics
        details["certain_target_metrics"] = metrics(y_test[certain], prediction[certain])
        details["uncertain_target_metrics"] = metrics(y_test[~certain], prediction[~certain])
        results[name] = details
        print(f"{name} MAE: {all_metrics['mae']:.4f}")

    baseline_mae = results["category_median"]["metrics"]["mae"]
    context_mae = results["hist_gradient_context"]["metrics"]["mae"]
    improvement = (baseline_mae - context_mae) / baseline_mae

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Feasibility pilot; not final model selection",
        "split": {
            "method": "GroupShuffleSplit on 25 km spatial blocks",
            "random_state": RANDOM_STATE,
            "training_rows": len(train),
            "test_rows": len(test),
            "training_blocks": len(train_blocks),
            "test_blocks": len(test_blocks),
            "shared_blocks": 0,
        },
        "results": results,
        "context_model_mae_improvement_vs_category_median": improvement,
        "passes_15_percent_feasibility_gate": improvement >= 0.15,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Improvement over category median: {improvement:.1%}; "
        f"gate passed={report['passes_15_percent_feasibility_gate']}"
    )
    print(f"Report: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
