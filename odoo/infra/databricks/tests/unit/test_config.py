"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from workbench.config.settings import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.env == "dev"
    assert settings.catalog == "dev_ppm"
    assert settings.schema_bronze == "bronze"
    assert settings.schema_silver == "silver"
    assert settings.schema_gold == "gold"


def test_settings_from_env():
    """Test settings loaded from environment."""
    env_vars = {
        "ENV": "prod",
        "DATABRICKS_CATALOG": "ppm",
        "SCHEMA_BRONZE": "raw",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        # Clear the cache to get fresh settings
        get_settings.cache_clear()
        settings = Settings.from_env()
        assert settings.env == "prod"
        assert settings.catalog == "ppm"
        assert settings.schema_bronze == "raw"


def test_get_table_paths():
    """Test table path generation."""
    settings = Settings(catalog="test_catalog")
    assert settings.get_bronze_path("my_table") == "test_catalog.bronze.my_table"
    assert settings.get_silver_path("my_table") == "test_catalog.silver.my_table"
    assert settings.get_gold_path("my_table") == "test_catalog.gold.my_table"
