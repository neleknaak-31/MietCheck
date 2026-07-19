import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"


def test_reference_aligned_qua3ck_artifacts_are_clean_and_substantive() -> None:
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    assert {path.name for path in notebooks} == {
        "Q-Phase.ipynb",
        "U-Phase.ipynb",
        "A-Phase.ipynb",
        "C-Phase.ipynb",
    }
    assert (NOTEBOOK_DIR / "K-Phase.md").exists()
    for path in notebooks:
        content = json.loads(path.read_text(encoding="utf-8"))
        cells = content["cells"]
        source = "".join("".join(cell["source"]) for cell in cells)
        assert content["nbformat"] == 4
        assert sum(cell["cell_type"] == "code" for cell in cells) >= 3
        assert "MietCheck" in source
        assert "202.908" not in source
        assert "immo_clean" not in source
    assert "Knowledge Transfer" in (NOTEBOOK_DIR / "K-Phase.md").read_text(encoding="utf-8")


def test_notebooks_use_mietcheck_kernel() -> None:
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        content = json.loads(path.read_text(encoding="utf-8"))
        assert content["metadata"]["kernelspec"]["name"] == "mietcheck"


def test_notebook_execution_report_proves_all_cells_passed() -> None:
    report_path = PROJECT_ROOT / "reports" / "notebook_execution.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["all_passed"] is True
    assert {item["notebook"] for item in report["notebooks"]} == {
        "Q-Phase.ipynb",
        "U-Phase.ipynb",
        "A-Phase.ipynb",
        "C-Phase.ipynb",
    }
    for result in report["notebooks"]:
        assert result["status"] == "passed"
        assert result["executed_code_cells"] == result["code_cells"]
