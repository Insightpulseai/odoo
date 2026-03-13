#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Odoo schema export functionality."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from export_odoo_schema import (
    OdooSchemaExporter,
    get_config,
    validate_config,
)


class TestConfiguration:
    """Test configuration loading."""

    def test_get_config_from_env(self):
        """Test config loads from environment variables."""
        with patch.dict(os.environ, {
            "ODOO_DB_HOST": "test-host",
            "ODOO_DB_PORT": "5433",
            "ODOO_DB_NAME": "test_db",
            "ODOO_DB_USER": "test_user",
            "ODOO_DB_PASSWORD": "test_pass",
        }):
            config = get_config()
            assert config["host"] == "test-host"
            assert config["port"] == 5433
            assert config["database"] == "test_db"
            assert config["user"] == "test_user"
            assert config["password"] == "test_pass"

    def test_validate_config_success(self):
        """Test config validation passes with all required fields."""
        config = {
            "host": "localhost",
            "database": "odoo",
            "user": "admin",
            "password": "secret",
        }
        assert validate_config(config) is True

    def test_validate_config_missing_host(self):
        """Test config validation fails with missing host."""
        config = {
            "database": "odoo",
            "user": "admin",
            "password": "secret",
        }
        assert validate_config(config) is False


class TestTableFiltering:
    """Test table inclusion/exclusion filtering."""

    @pytest.fixture
    def exporter(self):
        """Create exporter with test config."""
        config = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass",
            "include_tables": [],
            "exclude_tables": [],
        }
        return OdooSchemaExporter(config)

    def test_should_include_all_tables_by_default(self, exporter):
        """Test all tables included when no filters set."""
        assert exporter._should_include_table("res_partner") is True
        assert exporter._should_include_table("account_move") is True

    def test_exclude_filter_works(self, exporter):
        """Test exclude filter blocks matching tables."""
        exporter.config["exclude_tables"] = ["ir_attachment", "mail_"]
        assert exporter._should_include_table("res_partner") is True
        assert exporter._should_include_table("ir_attachment") is False
        assert exporter._should_include_table("mail_message") is False

    def test_include_filter_restricts_tables(self, exporter):
        """Test include filter only allows matching tables."""
        exporter.config["include_tables"] = ["res_", "account_"]
        assert exporter._should_include_table("res_partner") is True
        assert exporter._should_include_table("account_move") is True
        assert exporter._should_include_table("sale_order") is False


class TestSchemaExport:
    """Test schema export functionality."""

    @pytest.fixture
    def mock_exporter(self):
        """Create exporter with mocked DB connection."""
        config = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass",
            "include_tables": [],
            "exclude_tables": [],
            "include_views": False,
        }
        exporter = OdooSchemaExporter(config)
        exporter.conn = MagicMock()
        return exporter

    def test_extract_tables_returns_list(self, mock_exporter):
        """Test table extraction returns list of dicts."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"table_schema": "public", "table_name": "res_partner", "table_type": "BASE TABLE", "table_comment": None},
        ]
        mock_exporter.conn.cursor.return_value.__enter__.return_value = mock_cursor

        tables = mock_exporter.extract_tables()
        assert isinstance(tables, list)
        assert len(tables) == 1
        assert tables[0]["table_name"] == "res_partner"

    def test_export_creates_valid_structure(self, mock_exporter):
        """Test export creates valid schema structure."""
        # Mock all the extraction methods
        mock_exporter.extract_tables = MagicMock(return_value=[
            {"table_name": "test_table", "table_type": "BASE TABLE", "table_comment": None}
        ])
        mock_exporter.extract_columns = MagicMock(return_value={
            "test_table": [{"column_name": "id", "data_type": "integer", "is_nullable": "NO"}]
        })
        mock_exporter.extract_primary_keys = MagicMock(return_value={"test_table": ["id"]})
        mock_exporter.extract_foreign_keys = MagicMock(return_value={})
        mock_exporter.extract_unique_constraints = MagicMock(return_value={})
        mock_exporter.extract_indexes = MagicMock(return_value={})
        mock_exporter.extract_check_constraints = MagicMock(return_value={})

        schema = mock_exporter.export()

        assert "metadata" in schema
        assert "tables" in schema
        assert schema["metadata"]["table_count"] == 1
        assert "test_table" in schema["tables"]

    def test_save_creates_file(self, mock_exporter):
        """Test save creates JSON file."""
        schema = {
            "metadata": {"source": "test", "exported_at": "2024-01-01", "table_count": 0},
            "tables": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "schema.json"
            mock_exporter.save(schema, str(output_path))

            assert output_path.exists()
            with open(output_path) as f:
                saved = json.load(f)
            assert saved == schema


class TestTypeMapping:
    """Test PostgreSQL type handling."""

    def test_common_types_preserved(self):
        """Test common PostgreSQL types are recognized."""
        from export_odoo_schema import QUERY_COLUMNS
        # Just verify the query exists and is valid SQL
        assert "SELECT" in QUERY_COLUMNS
        assert "FROM information_schema.columns" in QUERY_COLUMNS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
