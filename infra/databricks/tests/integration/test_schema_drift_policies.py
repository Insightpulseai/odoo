"""Integration tests for schema drift policies."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from workbench.connectors.schema_manager import DriftReport, SchemaManager
from workbench.connectors.types import ColumnDef, SchemaPolicy, TableDef


@pytest.fixture
def make_schema_mgr(mock_spark: MagicMock):
    def _factory(policy: SchemaPolicy = SchemaPolicy.ALLOW_ALL) -> SchemaManager:
        return SchemaManager(mock_spark, "test_catalog", "bronze", policy=policy)

    return _factory


class TestSchemaDriftPolicies:
    def test_allow_all_adds_columns(self, make_schema_mgr, mock_spark: MagicMock) -> None:
        """ALLOW_ALL policy adds new columns via ALTER TABLE."""
        mgr = make_schema_mgr(SchemaPolicy.ALLOW_ALL)
        new_cols = [ColumnDef("new_col", "STRING")]
        mgr.apply_drift("test_table", new_cols)
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        alter_calls = [s for s in sql_calls if "ALTER TABLE" in s and "new_col" in s]
        assert len(alter_calls) == 1

    def test_block_all_rejects_columns(self, make_schema_mgr, mock_spark: MagicMock) -> None:
        """BLOCK_ALL policy does NOT add columns."""
        mgr = make_schema_mgr(SchemaPolicy.BLOCK_ALL)
        new_cols = [ColumnDef("new_col", "STRING")]
        mgr.apply_drift("test_table", new_cols)
        sql_calls = [c[0][0] for c in mock_spark.sql.call_args_list]
        alter_calls = [s for s in sql_calls if "ALTER TABLE" in s]
        assert len(alter_calls) == 0

    def test_detect_full_drift_additions(self, make_schema_mgr, mock_spark: MagicMock) -> None:
        """detect_full_drift finds columns in declaration but not in table."""
        mgr = make_schema_mgr()
        # Mock existing table has col_a only
        mock_df = MagicMock()
        mock_df.columns = ["col_a", "_fivetran_id", "_fivetran_synced", "_fivetran_deleted"]
        mock_df.dtypes = [
            ("col_a", "string"),
            ("_fivetran_id", "string"),
            ("_fivetran_synced", "timestamp"),
            ("_fivetran_deleted", "boolean"),
        ]
        mock_spark.table.return_value = mock_df
        mock_spark.table.side_effect = None

        td = TableDef(
            name="test_table",
            columns=(ColumnDef("col_a", "STRING"), ColumnDef("col_b", "LONG")),
            primary_key=("col_a",),
        )
        report = mgr.detect_full_drift(td)
        assert len(report.added_columns) == 1
        assert report.added_columns[0].name == "col_b"

    def test_detect_full_drift_removals(self, make_schema_mgr, mock_spark: MagicMock) -> None:
        """detect_full_drift finds columns in table but not in declaration."""
        mgr = make_schema_mgr()
        mock_df = MagicMock()
        mock_df.columns = [
            "col_a",
            "col_b",
            "old_col",
            "_fivetran_id",
            "_fivetran_synced",
            "_fivetran_deleted",
        ]
        mock_df.dtypes = [
            ("col_a", "string"),
            ("col_b", "long"),
            ("old_col", "string"),
            ("_fivetran_id", "string"),
            ("_fivetran_synced", "timestamp"),
            ("_fivetran_deleted", "boolean"),
        ]
        mock_spark.table.return_value = mock_df
        mock_spark.table.side_effect = None

        td = TableDef(
            name="test_table",
            columns=(ColumnDef("col_a", "STRING"), ColumnDef("col_b", "LONG")),
            primary_key=("col_a",),
        )
        report = mgr.detect_full_drift(td)
        assert "old_col" in report.removed_columns

    def test_detect_full_drift_type_changes(self, make_schema_mgr, mock_spark: MagicMock) -> None:
        """detect_full_drift finds type mismatches."""
        mgr = make_schema_mgr()
        mock_df = MagicMock()
        mock_df.columns = ["col_a", "_fivetran_id", "_fivetran_synced", "_fivetran_deleted"]
        mock_df.dtypes = [
            ("col_a", "string"),
            ("_fivetran_id", "string"),
            ("_fivetran_synced", "timestamp"),
            ("_fivetran_deleted", "boolean"),
        ]
        mock_spark.table.return_value = mock_df
        mock_spark.table.side_effect = None

        # Declaration says col_a is LONG, but table has STRING
        td = TableDef(
            name="test_table",
            columns=(ColumnDef("col_a", "LONG"),),
            primary_key=("col_a",),
        )
        report = mgr.detect_full_drift(td)
        assert len(report.type_changes) == 1
        col, old, new = report.type_changes[0]
        assert col == "col_a"

    def test_system_columns_excluded_from_removals(
        self, make_schema_mgr, mock_spark: MagicMock
    ) -> None:
        """System columns are never reported as removals."""
        mgr = make_schema_mgr()
        mock_df = MagicMock()
        mock_df.columns = ["col_a", "_fivetran_id", "_fivetran_synced", "_fivetran_deleted"]
        mock_df.dtypes = [
            ("col_a", "string"),
            ("_fivetran_id", "string"),
            ("_fivetran_synced", "timestamp"),
            ("_fivetran_deleted", "boolean"),
        ]
        mock_spark.table.return_value = mock_df
        mock_spark.table.side_effect = None

        td = TableDef(name="test_table", columns=(ColumnDef("col_a", "STRING"),))
        report = mgr.detect_full_drift(td)
        assert len(report.removed_columns) == 0
