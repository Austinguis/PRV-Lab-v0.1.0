"""Small helpers for reproducible result files."""

from __future__ import annotations

import csv
import json
import platform
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np


def write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("cannot write a CSV without rows")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


def run_metadata(command: str, parameters: Mapping[str, Any]) -> dict[str, Any]:
    try:
        package_version = version("prv-lab")
    except PackageNotFoundError:
        package_version = "source-checkout"
    try:
        prv_version = version("prv-accountant")
    except PackageNotFoundError:
        prv_version = None
    return {
        "project": "prv-lab",
        "project_version": package_version,
        "command": command,
        "parameters": dict(parameters),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "prv_accountant_version": prv_version,
    }
