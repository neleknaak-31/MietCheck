from pathlib import Path

from scripts.verify_release import verify_release

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_release_artifacts_pass_governance_gates() -> None:
    result = verify_release(PROJECT_ROOT)
    assert result["mae_improvement_vs_baseline"] >= 0.15
    assert result["interval_coverage"] >= 0.84
    assert result["loaded_scenario_seconds"] < 2.0
