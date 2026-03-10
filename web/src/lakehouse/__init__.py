"""
Lakehouse Adapter Layer
=======================

Provides unified access to Delta Lake storage with Supabase mirroring.

Usage:
    from src.lakehouse import load_pipeline_config, load_contracts

    config = load_pipeline_config()
    contracts = load_contracts()

    if config.storage_backend == "delta_plus_supabase":
        # Use Delta for heavy ETL
        pass
    else:
        # Use Supabase directly
        pass
"""

from .config import load_pipeline_config, PipelineConfig, DeltaS3Config
from .contracts import load_contracts, DeltaContract

__all__ = [
    "load_pipeline_config",
    "load_contracts",
    "PipelineConfig",
    "DeltaS3Config",
    "DeltaContract",
]
