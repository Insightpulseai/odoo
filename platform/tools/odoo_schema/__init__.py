"""
Odoo Schema Tools

Introspect Odoo metadata and generate:
- schema.json / schema.yaml (full schema)
- erd.mmd (Mermaid ERD)
- erd.drawio (diagrams.net ERD)
- orm_models.py (Pydantic stubs)
- EXTENSION_POINTS.md (ipai_* analysis)
"""
from .export_schema import export_schema
from .schema_to_drawio import render_drawio
from .schema_to_pydantic import generate_pydantic

__all__ = ["export_schema", "render_drawio", "generate_pydantic"]
