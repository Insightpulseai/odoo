# -*- coding: utf-8 -*-
"""
ADE Pipeline Registry.

Loads and caches YAML pipeline definitions for document extraction.
"""
import logging
from pathlib import Path
from typing import Dict, Optional

import yaml

_logger = logging.getLogger(__name__)

PIPELINE_DIR = Path(__file__).parent.parent / "pipelines"


class PipelineRegistry:
    """
    Registry for ADE pipeline configurations.

    Loads YAML files from the pipelines directory and caches them
    for efficient repeated access.
    """

    def __init__(self, pipeline_dir: Optional[Path] = None):
        """
        Initialize the pipeline registry.

        Args:
            pipeline_dir: Optional custom directory for pipeline YAML files.
                         Defaults to ../pipelines relative to this file.
        """
        self._cache: Dict[str, dict] = {}
        self._pipeline_dir = pipeline_dir or PIPELINE_DIR

    def load(self, pipeline_id: str) -> dict:
        """
        Load a pipeline configuration by ID.

        Args:
            pipeline_id: Pipeline identifier (e.g., 'invoice_basic_v1')

        Returns:
            dict: Pipeline configuration

        Raises:
            FileNotFoundError: If pipeline YAML doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if pipeline_id in self._cache:
            return self._cache[pipeline_id]

        path = self._pipeline_dir / f"{pipeline_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Pipeline not found: {path}")

        _logger.debug("Loading pipeline from %s", path)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._cache[pipeline_id] = data
        return data

    def list_pipelines(self) -> list:
        """
        List all available pipeline IDs.

        Returns:
            list: Pipeline IDs found in the pipelines directory
        """
        if not self._pipeline_dir.exists():
            return []

        pipelines = []
        for path in self._pipeline_dir.glob("*.yaml"):
            pipelines.append(path.stem)
        return sorted(pipelines)

    def clear_cache(self):
        """Clear the pipeline cache to force reload."""
        self._cache.clear()

    def get_pipeline_for_doc_type(self, doc_type: str) -> Optional[str]:
        """
        Find the default pipeline for a document type.

        Args:
            doc_type: Document type (e.g., 'invoice', 'receipt')

        Returns:
            str or None: Pipeline ID if found
        """
        for pipeline_id in self.list_pipelines():
            try:
                config = self.load(pipeline_id)
                if config.get("doc_type") == doc_type:
                    return pipeline_id
            except Exception:
                continue
        return None
