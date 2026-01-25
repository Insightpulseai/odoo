"""I/O utilities for file operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_yaml(path: str | Path) -> dict[str, Any]:
    """Read a YAML file.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML content as dict
    """
    with open(path) as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: str | Path, data: dict[str, Any]) -> None:
    """Write data to a YAML file.

    Args:
        path: Path to YAML file
        data: Data to write
    """
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
