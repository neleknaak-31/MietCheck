from pathlib import Path

from scripts.verify_release import governed_artifact_bytes, sha256, verify_release

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_release_artifacts_pass_governance_gates() -> None:
    result = verify_release(PROJECT_ROOT)
    assert result["mae_improvement_vs_baseline"] >= 0.15
    assert result["interval_coverage"] >= 0.84
    assert result["loaded_scenario_seconds"] < 2.0


def test_json_governance_hash_is_line_ending_independent(tmp_path: Path) -> None:
    windows_file = tmp_path / "windows.json"
    linux_file = tmp_path / "linux.json"
    windows_file.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')
    linux_file.write_bytes(b'{\n  "value": 1\n}\n')

    assert governed_artifact_bytes(windows_file) == governed_artifact_bytes(linux_file)
    assert sha256(windows_file) == sha256(linux_file)
