"""
lakeflow_ingestion_etl — LakeFlow/DLT ingestion pipelines for the Bronze layer.

Provides:
- JDBC extractors for Odoo PostgreSQL
- REST API extractors for external sources
- Bronze table writers with append-only semantics
- Schema evolution tracking and registry

Usage:
    from lakeflow_ingestion_etl import __version__
    from lakeflow_ingestion_etl.extractors import OdooJdbcExtractor, RestApiExtractor
    from lakeflow_ingestion_etl.loaders import BronzeTableWriter
    from lakeflow_ingestion_etl.schema_registry import SchemaEvolutionTracker
"""

__version__ = "0.1.0"
__author__ = "InsightPulse AI Platform Team"
__license__ = "LGPL-3.0"
