#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for DBML generation functionality."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_dbml import (
    DBMLGenerator,
    get_config,
    to_dbml_type,
    validate_config,
)


class TestTypeMapping:
    """Test PostgreSQL to DBML type mapping."""

    def test_bigint_maps_correctly(self):
        """Test bigint type mapping."""
        assert to_dbml_type("bigint") == "bigint"

    def test_integer_maps_to_int(self):
        """Test integer type mapping."""
        assert to_dbml_type("integer") == "int"

    def test_varchar_maps_to_varchar(self):
        """Test varchar type mapping."""
        assert to_dbml_type("character varying") == "varchar"

    def test_timestamp_maps_correctly(self):
        """Test timestamp type mapping."""
        assert to_dbml_type("timestamp with time zone") == "timestamptz"

    def test_unknown_type_passthrough(self):
        """Test unknown types pass through."""
        assert to_dbml_type("custom_type") == "custom_type"


class TestConfiguration:
    """Test configuration loading."""

    def test_get_config_from_env(self):
        """Test config loads from environment variables."""
        with patch.dict(os.environ, {
            "SUPABASE_DB_URL": "postgres://localhost/db",
            "SUPABASE_DB_SCHEMA": "custom_schema",
            "DBML_OUTPUT_DIR": "/custom/path",
        }):
            config = get_config()
            assert config["supabase_url"] == "postgres://localhost/db"
            assert config["schema"] == "custom_schema"
            assert config["output_dir"] == "/custom/path"

    def test_default_schema_is_odoo_shadow(self):
        """Test default schema is odoo_shadow."""
        with patch.dict(os.environ, {"SUPABASE_DB_URL": "postgres://localhost/db"}, clear=True):
            config = get_config()
            assert config["schema"] == "odoo_shadow"

    def test_validate_config_requires_url(self):
        """Test validation requires SUPABASE_DB_URL."""
        config = {"supabase_url": None}
        assert validate_config(config) is False

    def test_validate_config_passes_with_url(self):
        """Test validation passes with valid URL."""
        config = {"supabase_url": "postgres://localhost/db"}
        assert validate_config(config) is True


class TestDBMLGenerator:
    """Test DBML generation."""

    @pytest.fixture
    def generator(self):
        """Create generator with mock config."""
        config = {
            "supabase_url": "postgres://localhost/db",
            "schema": "odoo_shadow",
            "output_dir": "/tmp/dbml",
        }
        gen = DBMLGenerator(config)
        gen.conn = MagicMock()
        return gen

    def test_escape_dbml_handles_quotes(self, generator):
        """Test DBML escaping handles quotes."""
        assert generator._escape_dbml('Test "quoted"') == 'Test \\"quoted\\"'

    def test_escape_dbml_handles_newlines(self, generator):
        """Test DBML escaping handles newlines."""
        assert generator._escape_dbml("Line1\nLine2") == "Line1 Line2"

    def test_escape_dbml_handles_none(self, generator):
        """Test DBML escaping handles None."""
        assert generator._escape_dbml(None) == ""

    def test_generate_produces_valid_structure(self, generator):
        """Test generate produces valid DBML structure."""
        # Mock database queries
        mock_cursor = MagicMock()
        generator.conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock tables
        generator._get_tables = MagicMock(return_value=[
            {"table_name": "test_table", "table_comment": "Test table"}
        ])
        generator._get_columns = MagicMock(return_value=[
            {"column_name": "id", "data_type": "bigint", "is_nullable": "NO", "column_default": None, "column_comment": None}
        ])
        generator._get_primary_keys = MagicMock(return_value=["id"])
        generator._get_foreign_keys = MagicMock(return_value=[])
        generator._get_indexes = MagicMock(return_value=[])

        dbml = generator.generate()

        assert "Project odoo_shadow" in dbml
        assert "Table test_table" in dbml
        assert "id bigint [pk]" in dbml

    def test_generate_includes_foreign_keys(self, generator):
        """Test generate includes foreign key relationships."""
        generator._get_tables = MagicMock(return_value=[
            {"table_name": "order", "table_comment": None},
            {"table_name": "customer", "table_comment": None},
        ])
        generator._get_columns = MagicMock(return_value=[
            {"column_name": "id", "data_type": "bigint", "is_nullable": "NO", "column_default": None, "column_comment": None}
        ])
        generator._get_primary_keys = MagicMock(return_value=["id"])
        generator._get_foreign_keys = MagicMock(return_value=[
            {"table_name": "order", "column_name": "customer_id", "foreign_table": "customer", "foreign_column": "id"}
        ])
        generator._get_indexes = MagicMock(return_value=[])

        dbml = generator.generate()

        assert "Ref: order.customer_id > customer.id" in dbml

    def test_save_creates_file(self, generator):
        """Test save creates DBML file."""
        dbml = "// Test DBML\nTable test {}"

        with tempfile.TemporaryDirectory() as tmpdir:
            generator.config["output_dir"] = tmpdir
            path = generator.save(dbml)

            assert Path(path).exists()
            assert path.endswith(".dbml")
            with open(path) as f:
                content = f.read()
            assert content == dbml


class TestDBMLOutput:
    """Test complete DBML output."""

    def test_dbml_has_project_header(self):
        """Test DBML includes project definition."""
        config = {
            "supabase_url": "postgres://localhost/db",
            "schema": "test_schema",
        }
        generator = DBMLGenerator(config)
        generator.conn = MagicMock()
        generator._get_tables = MagicMock(return_value=[])
        generator._get_foreign_keys = MagicMock(return_value=[])

        dbml = generator.generate()

        assert "Project odoo_shadow" in dbml
        assert 'database_type: "PostgreSQL"' in dbml

    def test_dbml_has_table_definitions(self):
        """Test DBML includes table definitions."""
        config = {
            "supabase_url": "postgres://localhost/db",
            "schema": "test_schema",
        }
        generator = DBMLGenerator(config)
        generator.conn = MagicMock()
        generator._get_tables = MagicMock(return_value=[
            {"table_name": "users", "table_comment": "User accounts"}
        ])
        generator._get_columns = MagicMock(return_value=[
            {"column_name": "id", "data_type": "bigint", "is_nullable": "NO", "column_default": None, "column_comment": None},
            {"column_name": "email", "data_type": "text", "is_nullable": "NO", "column_default": None, "column_comment": None},
        ])
        generator._get_primary_keys = MagicMock(return_value=["id"])
        generator._get_foreign_keys = MagicMock(return_value=[])
        generator._get_indexes = MagicMock(return_value=[])

        dbml = generator.generate()

        assert "Table users" in dbml
        assert "id bigint [pk, not null]" in dbml
        assert "email text [not null]" in dbml


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
