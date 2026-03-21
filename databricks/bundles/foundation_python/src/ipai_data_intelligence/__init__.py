"""
ipai_data_intelligence — Core Python library for InsightPulse AI Databricks workloads.

Provides:
- Medallion transform base classes (Bronze, Silver, Gold)
- Data quality check framework
- Unity Catalog utilities
- Structured logging for Databricks

Usage:
    from ipai_data_intelligence import __version__
    from ipai_data_intelligence.transforms import BronzeTransform, SilverTransform, GoldTransform
    from ipai_data_intelligence.quality import NullCheckRule, SchemaCheckRule, FreshnessCheckRule
    from ipai_data_intelligence.utils import resolve_catalog, load_config
"""

__version__ = "0.1.0"
__author__ = "InsightPulse AI Platform Team"
__license__ = "LGPL-3.0"
