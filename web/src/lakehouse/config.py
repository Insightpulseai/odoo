"""
Pipeline Configuration Loader
=============================

Loads pipeline.yaml with environment variable substitution.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import re
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass(frozen=True)
class DeltaS3Config:
    """S3/MinIO configuration for Delta Lake storage."""
    endpoint: str
    access_key: str
    secret_key: str
    region: str
    bucket: str
    path_style_access: bool


@dataclass(frozen=True)
class TrinoConfig:
    """Trino connection configuration."""
    host: str
    port: int
    user: str
    catalog: str


@dataclass(frozen=True)
class MirrorMapping:
    """Mapping from Delta table to Supabase table."""
    from_table: str
    to_table: str
    mode: str  # upsert | replace
    key: str


@dataclass(frozen=True)
class PipelineConfig:
    """Complete pipeline configuration."""
    storage_backend: str
    delta_s3: DeltaS3Config
    delta_tables: dict[str, str]
    mirror_enabled: bool
    mirror_batch_size: int
    mirror_lookback_days: int
    mirror_mappings: list[MirrorMapping]
    trino: Optional[TrinoConfig]
    mlflow_tracking_uri: Optional[str]


def _expand_env(value: str) -> str:
    """
    Expand environment variables in string.

    Supports:
        ${VAR}          - Required variable
        ${VAR:-default} - Variable with default
    """
    if not isinstance(value, str):
        return value

    pattern = r'\$\{([^}]+)\}'

    def replacer(match: re.Match) -> str:
        inner = match.group(1)
        if ":-" in inner:
            key, default = inner.split(":-", 1)
            return os.getenv(key.strip(), default)
        return os.getenv(inner.strip(), "")

    return re.sub(pattern, replacer, value)


def load_pipeline_config(path: str = "config/pipeline.yaml") -> PipelineConfig:
    """
    Load pipeline configuration from YAML file.

    Args:
        path: Path to pipeline.yaml (relative to repo root)

    Returns:
        PipelineConfig with all settings resolved

    Raises:
        ImportError: If PyYAML not installed
        FileNotFoundError: If config file missing
    """
    if yaml is None:
        raise ImportError("PyYAML required: pip install pyyaml")

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    data = yaml.safe_load(config_path.read_text())

    # Parse S3 config
    s3_data = data.get("delta", {}).get("s3", {})
    delta_s3 = DeltaS3Config(
        endpoint=_expand_env(s3_data.get("endpoint", "")),
        access_key=_expand_env(s3_data.get("access_key", "")),
        secret_key=_expand_env(s3_data.get("secret_key", "")),
        region=_expand_env(s3_data.get("region", "us-east-1")),
        bucket=_expand_env(s3_data.get("bucket", "lakehouse")),
        path_style_access=bool(s3_data.get("path_style_access", True)),
    )

    # Parse mirror config
    mirror_data = data.get("mirror_to_supabase", {})
    mirror_mappings = []
    for m in mirror_data.get("mappings", []):
        mirror_mappings.append(MirrorMapping(
            from_table=m["from"],
            to_table=m["to"],
            mode=m.get("mode", "upsert"),
            key=m["key"],
        ))

    # Parse Trino config
    trino_data = data.get("trino", {})
    trino = None
    if trino_data:
        trino = TrinoConfig(
            host=_expand_env(trino_data.get("host", "trino")),
            port=int(_expand_env(str(trino_data.get("port", 8080)))),
            user=_expand_env(trino_data.get("user", "lakehouse")),
            catalog=trino_data.get("catalog", "delta"),
        )

    # Parse MLflow config
    mlflow_data = data.get("mlflow", {})
    mlflow_uri = None
    if mlflow_data:
        mlflow_uri = _expand_env(mlflow_data.get("tracking_uri", ""))

    return PipelineConfig(
        storage_backend=data.get("storage_backend", "supabase_only"),
        delta_s3=delta_s3,
        delta_tables=data.get("delta", {}).get("tables", {}),
        mirror_enabled=bool(mirror_data.get("enabled", False)),
        mirror_batch_size=int(mirror_data.get("batch_size", 1000)),
        mirror_lookback_days=int(mirror_data.get("lookback_days", 7)),
        mirror_mappings=mirror_mappings,
        trino=trino,
        mlflow_tracking_uri=mlflow_uri,
    )
