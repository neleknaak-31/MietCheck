"""Publish existing MietCheck experiments and the final model to MLflow.

Usage:
    python scripts/publish_mlflow.py
    python scripts/publish_mlflow.py --tracking-uri http://127.0.0.1:5000
    python scripts/publish_mlflow.py --no-register
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mlflow_tracking import publish_existing_results  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tracking-uri",
        help="MLflow tracking URI. Defaults to MLFLOW_TRACKING_URI or local SQLite.",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Track runs and artifacts without creating a registered model version.",
    )
    parser.add_argument(
        "--alias",
        default="champion",
        help="Registry alias assigned to the published final model.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evidence = publish_existing_results(
        PROJECT_ROOT,
        tracking_uri=args.tracking_uri,
        register_model=not args.no_register,
        alias=args.alias,
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
