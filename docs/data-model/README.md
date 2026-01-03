# Odoo Data Model Artifacts

This folder contains canonical, generated representations of the Odoo CE data model as defined by this repository’s addons.

## Contents

- `ODOO_CANONICAL_SCHEMA.dbml`: Canonical DBML schema suitable for dbdiagram.io.
- `ODOO_ERD.mmd`: Mermaid ER diagram export.
- `ODOO_ERD.puml`: PlantUML ER diagram export.
- `ODOO_ORM_MAP.md`: ORM map linking Odoo models, tables, and fields.
- `ODOO_MODULE_DELTAS.md`: Per-module deltas highlighting new and extended tables.
- `ODOO_MODEL_INDEX.json`: Machine-readable index of models, fields, and relations.

## Regenerate locally

Run the generator from the repo root:

```bash
python scripts/generate_odoo_dbml.py
```

## Viewing ERDs

- DBML: import into https://dbdiagram.io
- Mermaid: use a Mermaid-compatible renderer or GitHub preview.
- PlantUML: render with PlantUML tooling.
