"""Compare linear and RBF support-vector regression on a spatial sample.

Exact kernel SVR has super-linear memory and runtime growth and is therefore
not a credible full-data candidate for 600,000 rows. This supplementary
experiment keeps the same feature set and spatial GroupKFold logic, but uses a
deterministic 10,000-row sample to compare the linear and kernel variants
requested in the course guidance.

Usage:
    python scripts/svm_kernel_benchmark.py
    python scripts/svm_kernel_benchmark.py --sample-rows 10000
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR, LinearSVR

if __package__:
    from scripts.algorithm_benchmark import FEATURES, GROUP, RANDOM_STATE, TARGET
else:
    from algorithm_benchmark import FEATURES, GROUP, RANDOM_STATE, TARGET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "model_table.parquet"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "svm_kernel_benchmark.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-rows", type=int, default=10_000)
    return parser.parse_args()


def model_factories() -> dict[str, object]:
    def preparation() -> Pipeline:
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]
        )

    return {
        "linear_svr": lambda: Pipeline(
            [
                ("prepare", preparation()),
                (
                    "model",
                    LinearSVR(
                        C=1.0,
                        epsilon=0.1,
                        loss="squared_epsilon_insensitive",
                        dual="auto",
                        tol=1e-3,
                        max_iter=5_000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "rbf_svr": lambda: Pipeline(
            [
                ("prepare", preparation()),
                ("model", SVR(kernel="rbf", C=10.0, epsilon=0.1, gamma="scale", cache_size=1_000)),
            ]
        ),
    }


def main() -> None:
    args = parse_args()
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run: python scripts/build_dataset.py")

    columns = [*FEATURES, TARGET, GROUP]
    frame = pd.read_parquet(DATA_FILE, columns=columns)
    if args.sample_rows < len(frame):
        frame = frame.sample(n=args.sample_rows, random_state=RANDOM_STATE)
    frame = frame.reset_index(drop=True)
    x = frame[FEATURES].to_numpy(dtype="float32", na_value=np.nan)
    y = frame[TARGET].to_numpy(dtype="float32")
    splits = list(GroupKFold(n_splits=3).split(x, y, groups=frame[GROUP]))

    results: dict[str, object] = {}
    for model_name, factory in model_factories().items():
        folds = []
        for fold_number, (train_index, test_index) in enumerate(splits, start=1):
            model = factory()
            started = time.perf_counter()
            model.fit(x[train_index], y[train_index])
            seconds = time.perf_counter() - started
            prediction = model.predict(x[test_index])
            folds.append(
                {
                    "fold": fold_number,
                    "training_rows": len(train_index),
                    "test_rows": len(test_index),
                    "training_seconds": seconds,
                    "mae": float(mean_absolute_error(y[test_index], prediction)),
                    "rmse": float(root_mean_squared_error(y[test_index], prediction)),
                    "r2": float(r2_score(y[test_index], prediction)),
                }
            )
        results[model_name] = {
            "folds": folds,
            "summary": {
                metric: {
                    "mean": float(np.mean([fold[metric] for fold in folds])),
                    "std": float(np.std([fold[metric] for fold in folds])),
                }
                for metric in ("mae", "rmse", "r2", "training_seconds")
            },
        }

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "purpose": "Supplementary linear-versus-kernel SVM feasibility study",
        "scope": {
            "rows": len(frame),
            "spatial_blocks": int(frame[GROUP].nunique()),
            "random_state": RANDOM_STATE,
            "not_full_benchmark": True,
            "reason": (
                "Exact RBF SVR grows super-linearly and is not a scalable candidate "
                "for the 600,000-row main benchmark."
            ),
        },
        "validation": {"method": "GroupKFold", "groups": GROUP, "folds": 3},
        "preprocessing": {
            "fit_scope": "inside each training fold only",
            "imputer": "SimpleImputer(strategy=median, add_indicator=True)",
            "scaler": "StandardScaler",
        },
        "features": FEATURES,
        "models": results,
    }
    OUTPUT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["models"], ensure_ascii=False, indent=2))
    print(f"Report: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
