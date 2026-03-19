#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Supabase schema sync functionality."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync_to_supabase import (
    MigrationGenerator,
    get_config,
    map_column_type,
    validate_config,
)


class TestTypeMapping:
    """Test Odoo to Supabase type mapping."""

    def test_integer_maps_to_bigint(self):
        """Test integer type mapping."""
        assert map_column_type("integer") == "bigint"

    def test_varchar_maps_to_text(self):
        """Test varchar type mapping."""
        assert map_column_type("character varying") == "text"

    def test_timestamp_maps_to_timestamptz(self):
        """Test timestamp type mapping."""
        assert map_column_type("timestamp without time zone") == "timestamptz"
        assert map_column_type("timestamp with time zone") == "timestamptz"

    def test_json_maps_to_jsonb(self):
        """Test JSON type mapping."""
        assert map_column_type("json") == "jsonb"
        assert map_column_type("jsonb") == "jsonb"

    def test_unknown_type_maps_to_text(self):
        """Test unknown types fallback to text."""
        assert map_column_type("custom_type") == "text"

    def test_array_type_mapping(self):
        """Test array type mapping."""
        assert "[]" in map_column_type("ARRAY", udt_name="_int4")


class TestConfiguration:
    """Test configuration loading."""

    def test_get_config_from_env(self):
        """Test config loads from environment variables."""
        with patch.dict(os.environ, {
            "SUPABASE_DB_URL": "postgres://user:pass@host/db",
            "SUPABASE_DB_SCHEMA": "custom_schema",
            "ODOO_SCHEMA_TABLE_PREFIX": "custom_prefix_",
        }):
            config = get_config()
            assert config["supabase_url"] == "postgres://user:pass@host/db"
            assert config["target_schema"] == "custom_schema"
            assert config["table_prefix"] == "custom_prefix_"

    def test_default_schema_is_odoo_shadow(self):
        """Test default schema is odoo_shadow."""
        with patch.dict(os.environ, {"SUPABASE_DB_URL": "postgres://localhost/db"}, clear=True):
            config = get_config()
            assert config["target_schema"] == "odoo_shadow"

    def test_validate_config_requires_url(self):
        """Test validation requires SUPABASE_DB_URL."""
        config = {"supabase_url": None}
        assert validate_config(config) is False

    def test_validate_config_passes_with_url(self):
        """Test validation passes with valid URL."""
        config = {"supabase_url": "postgres://localhost/db"}
        assert validate_config(config) is True


class TestMigrationGenerator:
    """Test migration generation."""

    @pytest.fixture
    def generator(self):
        """Create generator with test config."""
        config = {
            "supabase_url": "postgres://localhost/db",
            "target_schema": "odoo_shadow",
            "table_prefix": "odoo_shadow_",
            "allow_drops": False,
            "migration_dir": "/tmp/migrations",
        }
        gen = MigrationGenerator(config)
        gen.existing_tables = set()
        gen.existing_columns = {}
        return gen

    def test_shadow_table_name_adds_prefix(self, generator):
        """Test shadow table naming adds prefix."""
        assert generator._shadow_table_name("res_partner") == "odoo_shadow_res_partner"

    def test_shadow_table_name_no_double_prefix(self, generator):
        """Test shadow table naming doesn't double-prefix."""
        assert generator._shadow_table_name("odoo_shadow_res_partner") == "odoo_shadow_res_partner"

    def test_generate_create_table_includes_columns(self, generator):
        """Test CREATE TABLE includes column definitions."""
        table_info = {
            "columns": [
                {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
                {"column_name": "name", "data_type": "character varying", "is_nullable": "YES"},
            ],
            "primary_key": ["id"],
        }

        sql = generator._generate_create_table("test_table", table_info)

        assert "CREATE TABLE IF NOT EXISTS" in sql
        assert "odoo_shadow_test_table" in sql
        assert "id bigint NOT NULL PRIMARY KEY" in sql
        assert "name text" in sql
        assert "_odoo_write_date timestamptz" in sql
        assert "_synced_at timestamptz DEFAULT now()" in sql

    def test_generate_create_table_includes_index(self, generator):
        """Test CREATE TABLE includes write_date index."""
        table_info = {"columns": [], "primary_key": []}
        sql = generator._generate_create_table("test", table_info)
        assert "CREATE INDEX IF NOT EXISTS" in sql
        assert "_odoo_write_date DESC" in sql

    def test_generate_alter_table_for_new_columns(self, generator):
        """Test ALTER TABLE generated for new columns."""
        generator.existing_columns["odoo_shadow_test"] = {"id": {"data_type": "bigint"}}

        table_info = {
            "columns": [
                {"column_name": "id", "data_type": "integer"},
                {"column_name": "new_col", "data_type": "text"},
            ],
        }

        statements = generator._generate_alter_table("test", table_info)

        assert len(statements) == 1
        assert "ADD COLUMN IF NOT EXISTS new_col text" in statements[0]

    def test_generate_migration_creates_schema(self, generator):
        """Test migration includes schema creation."""
        odoo_schema = {
            "metadata": {"source": "test", "exported_at": "2024-01-01"},
            "tables": {},
        }

        sql = generator.generate_migration(odoo_schema)

        assert "CREATE SCHEMA IF NOT EXISTS odoo_shadow" in sql

    def test_save_migration_creates_file(self, generator):
        """Test migration is saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.config["migration_dir"] = tmpdir
            sql = "-- Test migration"

            path = generator.save_migration(sql)

            assert Path(path).exists()
            assert path.endswith(".sql")
            with open(path) as f:
                content = f.read()
            assert content == sql


class TestMigrationOutput:
    """Test complete migration output."""

    def test_migration_is_idempotent(self):
        """Test migration uses IF NOT EXISTS patterns."""
        config = {
            "supabase_url": "postgres://localhost/db",
            "target_schema": "odoo_shadow",
            "table_prefix": "odoo_shadow_",
            "allow_drops": False,
        }
        generator = MigrationGenerator(config)
        generator.existing_tables = set()
        generator.existing_columns = {}

        odoo_schema = {
            "metadata": {"source": "test"},
            "tables": {
                "res_partner": {
                    "columns": [{"column_name": "id", "data_type": "integer", "is_nullable": "NO"}],
                    "primary_key": ["id"],
                },
            },
        }

        sql = generator.generate_migration(odoo_schema)

        assert "IF NOT EXISTS" in sql
        assert "DROP TABLE" not in sql
        assert "DROP COLUMN" not in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
