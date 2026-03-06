"""Schema manager for connector tables.

Handles table creation with system columns, schema drift detection,
and SCD2 history column injection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from workbench.connectors.types import ColumnDef, SchemaPolicy, TableDef

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

# Fivetran-equivalent system columns added to every table
SYSTEM_COLUMNS: tuple[ColumnDef, ...] = (
    ColumnDef("_fivetran_synced", "TIMESTAMP", nullable=False, description="Sync timestamp"),
    ColumnDef("_fivetran_deleted", "BOOLEAN", nullable=False, description="Soft-delete flag"),
    ColumnDef("_fivetran_id", "STRING", nullable=False, description="Deterministic row ID"),
)

# SCD2 history columns (Phase 3)
HISTORY_COLUMNS: tuple[ColumnDef, ...] = (
    ColumnDef("_fivetran_active", "BOOLEAN", nullable=False, description="Current version flag"),
    ColumnDef("_fivetran_start", "TIMESTAMP", nullable=False, description="Version start time"),
    ColumnDef("_fivetran_end", "TIMESTAMP", nullable=True, description="Version end time"),
)


@dataclass
class DriftReport:
    """Structured drift detection result for a single table.

    Bug 0f fix: reports additions, removals, and type changes instead of
    only additions.
    """

    table_name: str
    added_columns: list[ColumnDef] = field(default_factory=list)
    removed_columns: list[str] = field(default_factory=list)
    type_changes: list[tuple[str, str, str]] = field(default_factory=list)  # (col, old_type, new_type)

    @property
    def has_drift(self) -> bool:
        return bool(self.added_columns or self.removed_columns or self.type_changes)


class SchemaManager:
    """Manages Delta table schemas for connector outputs.

    Creates tables with system columns, detects drift, and applies
    schema evolution based on the configured policy.
    """

    def __init__(
        self,
        spark: SparkSession,
        catalog: str,
        schema: str = "bronze",
        policy: SchemaPolicy = SchemaPolicy.ALLOW_ALL,
    ) -> None:
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.policy = policy

    def _fq_table(self, table_name: str) -> str:
        return f"{self.catalog}.{self.schema}.{table_name}"

    def table_exists(self, table_name: str) -> bool:
        """Check if a Delta table exists."""
        fq = self._fq_table(table_name)
        try:
            self.spark.table(fq)
            return True
        except Exception:
            return False

    def create_table_with_system_columns(
        self, table_def: TableDef, history_mode: bool = False
    ) -> None:
        """Create a Delta table with data columns + system columns.

        If history_mode is True, also adds SCD2 columns.
        """
        fq = self._fq_table(table_def.name)

        all_columns = list(table_def.columns) + list(SYSTEM_COLUMNS)
        if history_mode:
            all_columns += list(HISTORY_COLUMNS)

        col_defs = []
        for col in all_columns:
            nullable = "" if col.nullable else " NOT NULL"
            col_defs.append(f"    {col.name} {col.data_type}{nullable}")

        columns_sql = ",\n".join(col_defs)

        pk_clause = ""
        if table_def.primary_key:
            pk_cols = ", ".join(table_def.primary_key)
            pk_clause = f",\n    CONSTRAINT pk_{table_def.name} PRIMARY KEY ({pk_cols})"

        ddl = f"""
            CREATE TABLE IF NOT EXISTS {fq} (
{columns_sql}{pk_clause}
            )
            USING DELTA
            TBLPROPERTIES (
                'delta.enableChangeDataFeed' = 'true',
                'delta.autoOptimize.optimizeWrite' = 'true'
            )
        """

        if table_def.description:
            ddl += f"\n            COMMENT '{table_def.description}'"

        self.spark.sql(ddl)
        logger.info("Created table %s with %d columns", fq, len(all_columns))

    def get_existing_columns(self, table_name: str) -> set[str]:
        """Get column names from an existing Delta table."""
        fq = self._fq_table(table_name)
        try:
            df = self.spark.table(fq)
            return set(df.columns)
        except Exception:
            return set()

    def get_existing_dtypes(self, table_name: str) -> dict[str, str]:
        """Get column name -> data type mapping from an existing Delta table."""
        fq = self._fq_table(table_name)
        try:
            df = self.spark.table(fq)
            return {name: dtype for name, dtype in df.dtypes}
        except Exception:
            return {}

    def detect_drift(self, table_def: TableDef) -> list[ColumnDef]:
        """Compare declared schema vs actual Delta table.

        Returns list of new columns that exist in the declaration
        but not in the actual table. For backwards compatibility.
        """
        existing = self.get_existing_columns(table_def.name)
        if not existing:
            return []

        new_columns = [col for col in table_def.columns if col.name not in existing]

        if new_columns:
            logger.info(
                "Schema drift detected for %s: %d new columns",
                table_def.name,
                len(new_columns),
            )

        return new_columns

    def detect_full_drift(self, table_def: TableDef) -> DriftReport:
        """Bidirectional drift detection (Bug 0f fix).

        Detects:
        - Added columns (in declaration, not in table)
        - Removed columns (in table, not in declaration) — excluding system columns
        - Type changes (column exists in both but type differs)
        """
        report = DriftReport(table_name=table_def.name)

        existing = self.get_existing_columns(table_def.name)
        if not existing:
            return report

        # Declared column names (data columns only, not system)
        declared_names = {col.name for col in table_def.columns}
        declared_types = {col.name: col.data_type for col in table_def.columns}

        # System column names to exclude from removal detection
        system_col_names = {c.name for c in SYSTEM_COLUMNS} | {c.name for c in HISTORY_COLUMNS}

        # 1. Added columns: in declaration but not in table
        report.added_columns = [
            col for col in table_def.columns if col.name not in existing
        ]

        # 2. Removed columns: in table but not in declaration (excluding system cols)
        report.removed_columns = [
            name for name in existing
            if name not in declared_names and name not in system_col_names
        ]

        # 3. Type changes: column exists in both but type differs
        existing_dtypes = self.get_existing_dtypes(table_def.name)
        for col_name, declared_type in declared_types.items():
            if col_name in existing_dtypes:
                actual_type = existing_dtypes[col_name].upper()
                declared_upper = declared_type.upper()
                # Normalize common Spark type aliases
                type_map = {"LONG": "BIGINT", "INT": "INTEGER"}
                normalized_actual = type_map.get(actual_type, actual_type)
                normalized_declared = type_map.get(declared_upper, declared_upper)
                if normalized_actual != normalized_declared:
                    report.type_changes.append((col_name, actual_type, declared_type))

        if report.has_drift:
            parts = []
            if report.added_columns:
                parts.append(f"+{len(report.added_columns)} added")
            if report.removed_columns:
                parts.append(f"-{len(report.removed_columns)} removed")
            if report.type_changes:
                parts.append(f"~{len(report.type_changes)} type changes")
            logger.info("Schema drift for %s: %s", table_def.name, ", ".join(parts))

        return report

    def apply_drift(self, table_name: str, new_columns: list[ColumnDef]) -> None:
        """Apply schema drift by adding new columns to the Delta table.

        Respects the configured SchemaPolicy.
        """
        if self.policy == SchemaPolicy.BLOCK_ALL:
            logger.warning(
                "Schema drift blocked for %s (%d new columns, policy=BLOCK_ALL)",
                table_name,
                len(new_columns),
            )
            return

        fq = self._fq_table(table_name)
        for col in new_columns:
            nullable = "" if col.nullable else " NOT NULL"
            self.spark.sql(f"ALTER TABLE {fq} ADD COLUMN {col.name} {col.data_type}{nullable}")
            logger.info("Added column %s.%s (%s)", table_name, col.name, col.data_type)

    def ensure_tables(self, table_defs: list[TableDef], history_mode: bool = False) -> dict[str, list[ColumnDef]]:
        """Create or evolve all tables declared by a connector.

        Returns a dict of table_name -> list of newly added drift columns.
        """
        drift_report: dict[str, list[ColumnDef]] = {}

        for td in table_defs:
            if not self.table_exists(td.name):
                self.create_table_with_system_columns(td, history_mode=history_mode)
                drift_report[td.name] = []
            else:
                new_cols = self.detect_drift(td)
                if new_cols:
                    self.apply_drift(td.name, new_cols)
                drift_report[td.name] = new_cols

        return drift_report
