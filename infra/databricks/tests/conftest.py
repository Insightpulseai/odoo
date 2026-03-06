"""Test configuration — mock heavy dependencies not available locally."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Mock pyspark and delta before any workbench imports
for mod in (
    "pyspark",
    "pyspark.sql",
    "pyspark.sql.functions",
    "pyspark.sql.types",
    "delta",
    "delta.tables",
    "databricks",
    "databricks.sdk",
    "psycopg2",
    "notion_client",
    "azure",
    "azure.identity",
    "azure.mgmt",
    "azure.mgmt.resourcegraph",
    "azure.mgmt.resourcegraph.models",
):
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()
