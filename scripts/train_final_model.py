"""Train, calibrate and evaluate the final Zensus stock-rent model.

The selected model is trained on all development blocks. Absolute residuals on
the locked calibration blocks create finite-sample 90% conformal intervals.
The locked spatial test blocks are evaluated once and the deployable model,
metadata and machine-readable evaluation report are persisted.

Usage:
    python scripts/train_final_model.py
"""

from __future__ import annotations

import json
import math
import time
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    mean_absolute_error,
    median_absolute_error,
    r2_score,
    root_mean_squared_error,
)

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
OUTPUT_REPORT = PROJECT_ROOT / "reports" / "final_model_evaluation.json"
MODEL_FILE = PROJECT_ROOT / "models" / "zensus_hgb.joblib"
METADATA_FILE = PROJECT_ROOT / "models" / "zensus_hgb_meta.json"
ALPHA = 0.10
CATEGORY_FEATURES = ["building_after_1990", "dwelling_over_65sqm"]


def regression_metrics(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, prediction)),
        "median_ae": float(median_absolute_error(y_true, prediction)),
        "rmse": float(root_mean_squared_error(y_true, prediction)),
        "r2": float(r2_score(y_true, prediction)),
    }


def finite_sample_quantile(residuals: np.ndarray, alpha: float = ALPHA) -> float:
    """Return the split-conformal absolute-residual quantile."""
    values = np.asarray(residuals, dtype="float64")
    if values.ndim != 1 or not len(values):
        raise ValueError("Residuals must be a non-empty one-dimensional array")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    rank = min(len(values), math.ceil((len(values) + 1) * (1 - alpha)))
    return float(np.partition(values, rank - 1)[rank - 1])


def category_labels(frame: pd.DataFrame) -> pd.Series:
    return frame["building_after_1990"].astype(str) + "_" + frame["dwelling_over_65sqm"].astype(str)


def interval_metrics(
    y_true: np.ndarray,
    prediction: np.ndarray,
    half_width: np.ndarray | float,
) -> dict[str, float]:
    widths = np.broadcast_to(np.asarray(half_width, dtype="float64"), prediction.shape)
    lower = prediction - widths
    upper = prediction + widths
    return {
        "coverage": float(np.mean((y_true >= lower) & (y_true <= upper))),
        "mean_width_eur_sqm": float(np.mean(2 * widths)),
        "mean_half_width_eur_sqm": float(np.mean(widths)),
    }


def category_median_prediction(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    medians = train.groupby(CATEGORY_FEATURES, observed=True)[TARGET].median()
    fallback = float(train[TARGET].median())
    keys = pd.MultiIndex.from_frame(test[CATEGORY_FEATURES])
    return medians.reindex(keys, fill_value=fallback).to_numpy(dtype="float32")


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")
    if not TUNING_REPORT.exists():
        raise FileNotFoundError(f"Missing {TUNING_REPORT}. Run: python scripts/tune_hgb.py")
    if TARGET in FEATURES or "target_uncertain" in FEATURES:
        raise AssertionError("Target information must not be used as a model feature")

    tuning = json.loads(TUNING_REPORT.read_text(encoding="utf-8"))
    parameters = tuning["selected_parameters"]
    columns = [*FEATURES, TARGET, GROUP, "target_uncertain"]
    print(f"Reading {DATA_FILE.relative_to(PROJECT_ROOT)}...", flush=True)
    frame = pd.read_parquet(DATA_FILE, columns=columns)
    partitions = spatial_group_partition(frame[GROUP])
    validate_partitions(partitions)
    for name, group_set in partitions.items():
        expected = tuning["partition"][name]["group_sha256"]
        if group_digest(group_set) != expected:
            raise AssertionError(f"Partition drift detected for {name}")

    split_frames = {
        name: frame[frame[GROUP].astype(str).isin(group_set)].reset_index(drop=True)
        for name, group_set in partitions.items()
    }
    development = split_frames["development"]
    calibration = split_frames["calibration"]
    test = split_frames["test"]
    print(
        f"Development/calibration/test rows: {len(development):,} / "
        f"{len(calibration):,} / {len(test):,}",
        flush=True,
    )

    model = HistGradientBoostingRegressor(
        loss="absolute_error",
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        random_state=RANDOM_STATE,
        **parameters,
    )
    x_development = development[FEATURES].to_numpy(dtype="float32", na_value=np.nan)
    y_development = development[TARGET].to_numpy(dtype="float32")
    started = time.perf_counter()
    model.fit(x_development, y_development)
    training_seconds = time.perf_counter() - started
    print(
        f"Final model trained in {training_seconds:.1f}s ({model.n_iter_} iterations)", flush=True
    )

    def predict(frame_to_score: pd.DataFrame) -> np.ndarray:
        x = frame_to_score[FEATURES].to_numpy(dtype="float32", na_value=np.nan)
        return model.predict(x).astype("float32")

    calibration_prediction = predict(calibration)
    test_prediction = predict(test)
    y_calibration = calibration[TARGET].to_numpy(dtype="float32")
    y_test = test[TARGET].to_numpy(dtype="float32")
    calibration_residuals = np.abs(y_calibration - calibration_prediction)
    global_half_width = finite_sample_quantile(calibration_residuals)

    calibration_categories = category_labels(calibration)
    test_categories = category_labels(test)
    category_half_widths = {
        label: finite_sample_quantile(calibration_residuals[calibration_categories == label])
        for label in sorted(calibration_categories.unique())
    }
    test_half_widths = test_categories.map(category_half_widths).to_numpy(dtype="float64")
    if np.isnan(test_half_widths).any():
        raise AssertionError("Missing category-specific interval width")

    test_metrics = regression_metrics(y_test, test_prediction)
    baseline_prediction = category_median_prediction(development, test)
    baseline_metrics = regression_metrics(y_test, baseline_prediction)
    improvement = (baseline_metrics["mae"] - test_metrics["mae"]) / baseline_metrics["mae"]

    subgroup_metrics = {}
    for label, mask in {
        "official_target_certain": ~test["target_uncertain"].to_numpy(dtype=bool),
        "official_target_uncertain": test["target_uncertain"].to_numpy(dtype=bool),
    }.items():
        subgroup_metrics[label] = {
            "rows": int(mask.sum()),
            "point_metrics": regression_metrics(y_test[mask], test_prediction[mask]),
            "interval_metrics": interval_metrics(
                y_test[mask], test_prediction[mask], test_half_widths[mask]
            ),
        }
    for label in sorted(test_categories.unique()):
        mask = test_categories.eq(label).to_numpy()
        subgroup_metrics[f"category_{label}"] = {
            "rows": int(mask.sum()),
            "point_metrics": regression_metrics(y_test[mask], test_prediction[mask]),
            "interval_metrics": interval_metrics(
                y_test[mask], test_prediction[mask], test_half_widths[mask]
            ),
        }

    importance_sample = calibration.sample(
        n=min(50_000, len(calibration)), random_state=RANDOM_STATE
    )
    importance = permutation_importance(
        model,
        importance_sample[FEATURES].to_numpy(dtype="float32", na_value=np.nan),
        importance_sample[TARGET].to_numpy(dtype="float32"),
        scoring="neg_mean_absolute_error",
        n_repeats=3,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    feature_importance = sorted(
        [
            {
                "feature": feature,
                "mae_increase_mean": float(mean),
                "mae_increase_std": float(std),
            }
            for feature, mean, std in zip(
                FEATURES, importance.importances_mean, importance.importances_std, strict=True
            )
        ],
        key=lambda item: item["mae_increase_mean"],
        reverse=True,
    )

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Final spatial evaluation and split-conformal interval calibration",
        "partition": {
            name: {
                "rows": len(split_frames[name]),
                "blocks": len(group_set),
                "group_sha256": group_digest(group_set),
            }
            for name, group_set in partitions.items()
        },
        "model": {
            "type": "HistGradientBoostingRegressor",
            "parameters": parameters,
            "features": FEATURES,
            "training_seconds": training_seconds,
            "iterations": int(model.n_iter_),
            "random_state": RANDOM_STATE,
        },
        "test": {
            "point_metrics": test_metrics,
            "category_median_baseline_metrics": baseline_metrics,
            "mae_improvement_vs_baseline": improvement,
            "global_90_percent_interval": {
                "calibrated_half_width_eur_sqm": global_half_width,
                **interval_metrics(y_test, test_prediction, global_half_width),
            },
            "category_specific_90_percent_interval": {
                "calibrated_half_widths_eur_sqm": category_half_widths,
                **interval_metrics(y_test, test_prediction, test_half_widths),
            },
            "subgroups": subgroup_metrics,
        },
        "permutation_importance_on_calibration_sample": {
            "rows": len(importance_sample),
            "repeats": 3,
            "results": feature_importance,
        },
    }

    metadata = {
        "schema_version": 1,
        "model_name": "MietCheck Zensus stock-rent HGB",
        "created_at_utc": report["created_at_utc"],
        "target": TARGET,
        "target_unit": "EUR per square metre net cold rent",
        "feature_order": FEATURES,
        "feature_medians": {feature: float(development[feature].median()) for feature in FEATURES},
        "category_interval_half_widths_eur_sqm": category_half_widths,
        "global_interval_half_width_eur_sqm": global_half_width,
        "nominal_interval_coverage": 1 - ALPHA,
        "test_metrics": test_metrics,
        "test_interval_coverage": report["test"]["category_specific_90_percent_interval"][
            "coverage"
        ],
        "training_rows": len(development),
        "calibration_rows": len(calibration),
        "test_rows": len(test),
        "data_reference_date": "2022-05-15",
        "data_release": "Zensus 2022 open 100 m grid data, released 2025",
        "license": "Datenlizenz Deutschland - Namensnennung - Version 2.0",
        "sklearn_version": sklearn.__version__,
    }

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE, compress=3)
    METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OUTPUT_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Test MAE={test_metrics['mae']:.4f}, R2={test_metrics['r2']:.4f}, "
        f"category interval coverage="
        f"{report['test']['category_specific_90_percent_interval']['coverage']:.1%}",
        flush=True,
    )
    print(f"Model: {MODEL_FILE.relative_to(PROJECT_ROOT)}", flush=True)
    print(f"Report: {OUTPUT_REPORT.relative_to(PROJECT_ROOT)}", flush=True)


if __name__ == "__main__":
    main()
