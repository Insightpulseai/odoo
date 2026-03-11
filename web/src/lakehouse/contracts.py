"""
Delta Table Contract Loader
===========================

Loads and validates Delta table contracts from YAML files.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass(frozen=True)
class ColumnSpec:
    """Column specification in a Delta table contract."""
    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None


@dataclass(frozen=True)
class DeltaContract:
    """
    Delta table contract defining schema and behavior.

    Contracts are the source of truth for:
    - Table schema (columns, types, nullability)
    - Partitioning strategy
    - Primary/merge keys for upserts
    - Retention policy
    """
    table: str
    location: str
    format: str = "delta"
    partition_by: tuple[str, ...] = field(default_factory=tuple)
    primary_key: tuple[str, ...] = field(default_factory=tuple)
    columns: tuple[ColumnSpec, ...] = field(default_factory=tuple)
    merge_key: Optional[str] = None
    retention_days: int = 365

    @property
    def schema_name(self) -> str:
        """Extract schema name (e.g., 'bronze' from 'bronze.raw_pages')."""
        return self.table.split(".")[0] if "." in self.table else "default"

    @property
    def table_name(self) -> str:
        """Extract table name (e.g., 'raw_pages' from 'bronze.raw_pages')."""
        return self.table.split(".")[-1]

    def get_column(self, name: str) -> Optional[ColumnSpec]:
        """Get column specification by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def validate(self) -> list[str]:
        """
        Validate contract for common issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.table:
            errors.append("Missing table name")
        if not self.location:
            errors.append("Missing location")
        if not self.columns:
            errors.append("No columns defined")

        # Check partition columns exist
        col_names = {c.name for c in self.columns}
        for part_col in self.partition_by:
            if part_col not in col_names:
                errors.append(f"Partition column '{part_col}' not in columns")

        # Check primary key columns exist
        for pk_col in self.primary_key:
            if pk_col not in col_names:
                errors.append(f"Primary key column '{pk_col}' not in columns")

        return errors


def load_contracts(dir_path: str = "contracts/delta") -> dict[str, DeltaContract]:
    """
    Load all Delta table contracts from directory.

    Args:
        dir_path: Path to contracts directory

    Returns:
        Dict mapping table name to DeltaContract
    """
    if yaml is None:
        raise ImportError("PyYAML required: pip install pyyaml")

    contracts: dict[str, DeltaContract] = {}
    contracts_dir = Path(dir_path)

    if not contracts_dir.exists():
        return contracts

    for yaml_file in contracts_dir.glob("*.yaml"):
        data = yaml.safe_load(yaml_file.read_text())

        # Parse columns
        columns = []
        for col_name, col_spec in data.get("columns", {}).items():
            columns.append(ColumnSpec(
                name=col_name,
                type=col_spec.get("type", "varchar"),
                nullable=col_spec.get("nullable", True),
                description=col_spec.get("description"),
            ))

        contract = DeltaContract(
            table=data["table"],
            location=data["location"],
            format=data.get("format", "delta"),
            partition_by=tuple(data.get("partition_by", [])),
            primary_key=tuple(data.get("primary_key", [])),
            columns=tuple(columns),
            merge_key=data.get("merge_key"),
            retention_days=int(data.get("retention_days", 365)),
        )

        contracts[contract.table] = contract

    return contracts


def generate_trino_ddl(contract: DeltaContract, catalog: str = "delta") -> str:
    """
    Generate Trino CREATE TABLE statement from contract.

    Args:
        contract: DeltaContract to generate DDL for
        catalog: Trino catalog name

    Returns:
        SQL CREATE TABLE statement
    """
    # Type mapping from contract types to Trino types
    type_map = {
        "uuid": "uuid",
        "varchar": "varchar",
        "integer": "integer",
        "double": "double",
        "boolean": "boolean",
        "timestamp": "timestamp",
        "date": "date",
        "array_double": "array(double)",
    }

    lines = [f"CREATE TABLE IF NOT EXISTS {catalog}.{contract.table} ("]

    col_defs = []
    for col in contract.columns:
        trino_type = type_map.get(col.type, "varchar")
        col_defs.append(f"  {col.name} {trino_type}")

    lines.append(",\n".join(col_defs))
    lines.append(")")

    # Add WITH clause for location and partitioning
    with_parts = [f"location = '{contract.location}'"]
    if contract.partition_by:
        parts_str = ", ".join(f"'{p}'" for p in contract.partition_by)
        with_parts.append(f"partitioned_by = ARRAY[{parts_str}]")

    lines.append("WITH (")
    lines.append("  " + ",\n  ".join(with_parts))
    lines.append(");")

    return "\n".join(lines)
