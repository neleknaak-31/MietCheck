"""Execute and persist all QUA³CK notebooks with the project kernel."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import nbformat
from nbclient import NotebookClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
REPORT_FILE = PROJECT_ROOT / "reports" / "notebook_execution.json"

os.environ["IPYTHONDIR"] = str(PROJECT_ROOT / ".ipython")
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main() -> None:
    results = []
    for path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        print(f"Executing {path.name}...", flush=True)
        notebook = nbformat.read(path, as_version=4)
        started = time.perf_counter()
        client = NotebookClient(
            notebook,
            timeout=600,
            kernel_name="mietcheck",
            resources={"metadata": {"path": str(PROJECT_ROOT)}},
            allow_errors=False,
        )
        client.execute()
        elapsed = time.perf_counter() - started
        nbformat.write(notebook, path)
        results.append(
            {
                "notebook": path.name,
                "status": "passed",
                "seconds": elapsed,
                "code_cells": sum(cell.cell_type == "code" for cell in notebook.cells),
                "executed_code_cells": sum(
                    cell.cell_type == "code" and cell.execution_count is not None
                    for cell in notebook.cells
                ),
            }
        )
        print(f"  passed in {elapsed:.1f}s", flush=True)

    if len(results) != 7:
        raise AssertionError(f"Expected seven notebooks, executed {len(results)}")
    report = {
        "schema_version": 1,
        "executed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "kernel": "mietcheck",
        "working_directory": ".",
        "all_passed": all(item["status"] == "passed" for item in results),
        "notebooks": results,
    }
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Report: {REPORT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
