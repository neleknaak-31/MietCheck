import json
from pathlib import Path

from src.mlflow_tracking import default_tracking_uri, public_tracking_uri

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_default_tracking_uri_uses_local_sqlite(tmp_path: Path) -> None:
    uri = default_tracking_uri(tmp_path)
    assert uri.startswith("sqlite:///")
    assert uri.endswith("/mlflow.db")


def test_public_tracking_uri_redacts_credentials() -> None:
    assert (
        public_tracking_uri("https://user:secret@example.org/mlflow")
        == "https://***:***@example.org/mlflow"
    )


def test_published_mlflow_evidence_contains_registry_alias() -> None:
    evidence = json.loads(
        (PROJECT_ROOT / "reports" / "mlflow_publish.json").read_text(encoding="utf-8")
    )
    assert set(evidence["runs"]) == {
        "algorithm_benchmark",
        "hgb_tuning",
        "final_model",
    }
    assert evidence["registry"]["alias"] == "champion"
    assert evidence["registry"]["model_uri"].endswith("@champion")
