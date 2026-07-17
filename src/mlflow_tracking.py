"""Publish immutable MietCheck experiment reports to MLflow.

The computationally expensive training scripts remain the source of truth and
write versionable JSON reports. This module synchronizes those reports, the
final estimator and its governance documents into MLflow without requiring the
Streamlit runtime to depend on an external tracking server.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import joblib
import numpy as np

EXPERIMENT_NAME = "MietCheck QUA3CK"
REGISTERED_MODEL_NAME = "MietCheck-Zensus-Stock-Rent"


def default_tracking_uri(project_root: Path) -> str:
    """Return a portable local SQLite tracking URI."""
    database = (project_root / "mlflow.db").resolve().as_posix()
    return f"sqlite:///{database}"


def public_tracking_uri(uri: str) -> str:
    """Redact credentials before persisting a tracking URI as evidence."""
    parts = urlsplit(uri)
    if parts.username is None:
        return uri
    hostname = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    return urlunsplit((parts.scheme, f"***:***@{hostname}{port}", parts.path, parts.query, ""))


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required MLflow artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_mlflow() -> Any:
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError(
            "MLflow is not installed. Run: python -m pip install -r requirements-mlops.txt"
        ) from exc
    return mlflow


def publish_existing_results(
    project_root: Path,
    *,
    tracking_uri: str | None = None,
    register_model: bool = True,
    alias: str = "champion",
) -> dict[str, Any]:
    """Log A1, A3 and final C/K artifacts and optionally register the model."""
    root = project_root.resolve()
    reports = root / "reports"
    models = root / "models"
    docs = root / "docs"

    benchmark_path = reports / "algorithm_benchmark.json"
    tuning_path = reports / "hgb_tuning.json"
    final_path = reports / "final_model_evaluation.json"
    metadata_path = models / "zensus_hgb_meta.json"
    model_path = models / "zensus_hgb.joblib"
    manifest_path = models / "model_manifest.json"

    benchmark = _load_json(benchmark_path)
    tuning = _load_json(tuning_path)
    final = _load_json(final_path)
    metadata = _load_json(metadata_path)
    _load_json(manifest_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Missing required MLflow model: {model_path}")

    mlflow = _require_mlflow()
    uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI") or default_tracking_uri(root)
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(EXPERIMENT_NAME)
    evidence_uri = (
        "sqlite:///mlflow.db" if uri == default_tracking_uri(root) else public_tracking_uri(uri)
    )

    evidence: dict[str, Any] = {
        "schema_version": 1,
        "published_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "tracking_uri": evidence_uri,
        "experiment": EXPERIMENT_NAME,
        "runs": {},
        "registry": None,
    }

    with mlflow.start_run(run_name="A1 algorithm benchmark") as run:
        mlflow.set_tags(
            {
                "project": "MietCheck",
                "qua3ck_phase": "A1",
                "validation": benchmark["validation"]["method"],
            }
        )
        mlflow.log_params(
            {
                "sample_rows": benchmark["sample"]["rows"],
                "spatial_blocks": benchmark["sample"]["spatial_blocks"],
                "folds": benchmark["validation"]["folds"],
                "random_state": benchmark["sample"]["random_state"],
            }
        )
        metrics = {}
        for model_name, details in benchmark["models"].items():
            metrics[f"{model_name}.mean_mae"] = details["summary"]["mae"]["mean"]
            metrics[f"{model_name}.std_mae"] = details["summary"]["mae"]["std"]
            metrics[f"{model_name}.mean_rmse"] = details["summary"]["rmse"]["mean"]
            metrics[f"{model_name}.mean_r2"] = details["summary"]["r2"]["mean"]
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(benchmark_path), artifact_path="reports")
        evidence["runs"]["algorithm_benchmark"] = run.info.run_id

    selected = next(
        item for item in tuning["candidates"] if item["candidate"] == tuning["selected_candidate"]
    )
    with mlflow.start_run(run_name="A3 HGB tuning") as run:
        mlflow.set_tags(
            {
                "project": "MietCheck",
                "qua3ck_phase": "A3",
                "data_lock": "calibration-and-test-excluded",
            }
        )
        mlflow.log_params(
            {
                "selected_candidate": tuning["selected_candidate"],
                "tuning_sample_rows": tuning["data"]["tuning_sample_rows"],
                "tuning_sample_blocks": tuning["data"]["tuning_sample_blocks"],
                **{f"model.{key}": value for key, value in tuning["selected_parameters"].items()},
            }
        )
        mlflow.log_metrics(
            {
                "best.mean_mae": selected["summary"]["mean_mae"],
                "best.std_mae": selected["summary"]["std_mae"],
                "best.worst_fold_mae": selected["summary"]["worst_fold_mae"],
                "best.mean_r2": selected["summary"]["mean_r2"],
                "best.mean_training_seconds": selected["summary"]["mean_training_seconds"],
            }
        )
        mlflow.log_artifact(str(tuning_path), artifact_path="reports")
        evidence["runs"]["hgb_tuning"] = run.info.run_id

    estimator = joblib.load(model_path)
    input_example = np.asarray(
        [[metadata["feature_medians"][feature] for feature in metadata["feature_order"]]],
        dtype="float32",
    )
    signature = mlflow.models.infer_signature(input_example, estimator.predict(input_example))
    point = final["test"]["point_metrics"]
    interval = final["test"]["category_specific_90_percent_interval"]
    registry_name = REGISTERED_MODEL_NAME if register_model else None

    with mlflow.start_run(run_name="C final spatial evaluation") as run:
        mlflow.set_tags(
            {
                "project": "MietCheck",
                "qua3ck_phase": "C-K",
                "model_role": "champion",
                "serving_pattern": "versioned-batch-inference",
            }
        )
        mlflow.log_params(
            {
                "model_type": final["model"]["type"],
                "random_state": final["model"]["random_state"],
                "development_rows": metadata["training_rows"],
                "calibration_rows": metadata["calibration_rows"],
                "test_rows": metadata["test_rows"],
                **{f"model.{key}": value for key, value in final["model"]["parameters"].items()},
            }
        )
        mlflow.log_metrics(
            {
                "test.mae": point["mae"],
                "test.median_ae": point["median_ae"],
                "test.rmse": point["rmse"],
                "test.r2": point["r2"],
                "test.mae_improvement_vs_baseline": final["test"]["mae_improvement_vs_baseline"],
                "test.interval_coverage": interval["coverage"],
                "test.interval_mean_width": interval["mean_width_eur_sqm"],
            }
        )
        mlflow.log_artifacts(str(models), artifact_path="governance/model")
        for document in (
            docs / "DATA_CARD.md",
            docs / "MODEL_CARD.md",
            docs / "RISK_AND_ETHICS.md",
        ):
            mlflow.log_artifact(str(document), artifact_path="governance/docs")
        mlflow.log_artifact(str(final_path), artifact_path="reports")
        model_info = mlflow.sklearn.log_model(
            sk_model=estimator,
            name="model",
            input_example=input_example,
            signature=signature,
            registered_model_name=registry_name,
        )
        evidence["runs"]["final_model"] = run.info.run_id

    if register_model:
        version = getattr(model_info, "registered_model_version", None)
        if version is None:
            client = mlflow.MlflowClient()
            versions = client.search_model_versions(f"name='{REGISTERED_MODEL_NAME}'")
            matching = [item for item in versions if item.run_id == evidence["runs"]["final_model"]]
            if not matching:
                raise RuntimeError("Registered model version could not be resolved")
            version = max(matching, key=lambda item: int(item.version)).version
        client = mlflow.MlflowClient()
        client.set_registered_model_alias(REGISTERED_MODEL_NAME, alias, str(version))
        evidence["registry"] = {
            "model_name": REGISTERED_MODEL_NAME,
            "version": str(version),
            "alias": alias,
            "model_uri": f"models:/{REGISTERED_MODEL_NAME}@{alias}",
        }

    evidence_path = reports / "mlflow_publish.json"
    evidence_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return evidence
