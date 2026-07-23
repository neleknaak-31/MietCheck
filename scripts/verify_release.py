"""Verify model lineage, quality, segments and loaded serving latency."""

from __future__ import annotations

import hashlib
import json
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app_logic import evaluate_scenario  # noqa: E402


def governed_artifact_bytes(path: Path) -> bytes:
    """Return stable bytes for cross-platform governance checks.

    Git can materialize text files with CRLF on Windows and LF on Linux.
    JSON artifacts are normalized to UTF-8/LF before hashing, while binary
    model artifacts remain byte-exact.
    """
    payload = path.read_bytes()
    if path.suffix.lower() == ".json":
        text = payload.decode("utf-8")
        return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(governed_artifact_bytes(path)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_citation_version(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", maxsplit=1)[1].strip().strip("\"'")
    raise AssertionError("CITATION.cff does not declare a top-level version")


def verify_release(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = project_root.resolve()
    manifest = load_json(root / "models" / "model_manifest.json")
    metadata = load_json(root / "models" / "zensus_hgb_meta.json")
    report = load_json(root / "reports" / "final_model_evaluation.json")
    profile_metadata = load_json(root / "data" / "app" / "region_profiles_metadata.json")
    profiles = pd.read_csv(root / "data" / "app" / "region_profiles.csv")

    project_version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
    citation_version = load_citation_version(root / "CITATION.cff")
    model_version = manifest["model_version"]
    if len({project_version, citation_version, model_version}) != 1:
        raise AssertionError(
            "Release version drift between pyproject.toml, CITATION.cff and model manifest"
        )

    for relative, expected in manifest["files"].items():
        path = (root / "models" / relative).resolve()
        if not path.exists():
            raise AssertionError(f"Missing governed artifact: {path}")
        stable_bytes = governed_artifact_bytes(path)
        if len(stable_bytes) != expected["bytes"]:
            raise AssertionError(f"Artifact size drift: {path}")
        if hashlib.sha256(stable_bytes).hexdigest() != expected["sha256"]:
            raise AssertionError(f"Artifact hash drift: {path}")

    gates = manifest["quality_gates"]
    improvement = report["test"]["mae_improvement_vs_baseline"]
    coverage = report["test"]["category_specific_90_percent_interval"]["coverage"]
    if improvement < gates["minimum_mae_improvement_vs_baseline"]:
        raise AssertionError("Model no longer beats the release baseline")
    if coverage < gates["minimum_interval_coverage"]:
        raise AssertionError("Interval coverage is below the release floor")

    subgroups = report["test"]["subgroups"]
    max_subgroup_mae = max(item["point_metrics"]["mae"] for item in subgroups.values())
    min_subgroup_coverage = min(item["interval_metrics"]["coverage"] for item in subgroups.values())
    if max_subgroup_mae > gates["maximum_subgroup_mae_eur_sqm"]:
        raise AssertionError("A documented reliability segment exceeds the MAE gate")
    if min_subgroup_coverage < gates["minimum_interval_coverage"]:
        raise AssertionError("A documented reliability segment misses the coverage gate")

    if metadata["test_metrics"] != report["test"]["point_metrics"]:
        raise AssertionError("Model metadata and final report metrics differ")
    if profile_metadata["model_file"] != "zensus_hgb.joblib":
        raise AssertionError("Deployable profiles reference an unexpected model")
    if len(profiles) != profile_metadata["regions"] or profiles["region"].duplicated().any():
        raise AssertionError("Deployable regional profiles violate their data contract")

    profile = profiles.loc[profiles["region"] == "Berlin"].iloc[0]
    started = time.perf_counter()
    for _ in range(1_000):
        scenario = evaluate_scenario(
            profile,
            area_sqm=70,
            construction_year=1980,
            current_cold_rent=800,
            net_income=3_000,
        )
    serving_seconds = time.perf_counter() - started
    if serving_seconds > gates["maximum_loaded_scenario_latency_seconds"]:
        raise AssertionError("Loaded scenario evaluation exceeds the latency gate")

    return {
        "project_version": project_version,
        "model_version": model_version,
        "model_sha256": manifest["files"]["zensus_hgb.joblib"]["sha256"],
        "mae_improvement_vs_baseline": improvement,
        "interval_coverage": coverage,
        "max_subgroup_mae_eur_sqm": max_subgroup_mae,
        "min_subgroup_coverage": min_subgroup_coverage,
        "loaded_scenarios": 1_000,
        "loaded_scenario_seconds": serving_seconds,
        "sample_moving_premium_monthly": scenario["moving_premium_monthly"],
    }


def main() -> None:
    result = verify_release()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
