# Odoo Data Model Artifacts

This folder contains canonical, generated representations of the Odoo CE data model as defined by this repository's addons.

## Contents

### Schema Definitions
- `ODOO_CANONICAL_SCHEMA.dbml`: Canonical DBML schema suitable for dbdiagram.io.
- `ODOO_MODEL_INDEX.json`: Machine-readable index of models, fields, and relations.
- `ODOO_ORM_MAP.md`: ORM map linking Odoo models, tables, and fields.
- `ODOO_MODULE_DELTAS.md`: Per-module deltas highlighting new and extended tables.

### Diagram Formats
- `ODOO_ERD.mmd`: Mermaid ER diagram export.
- `ODOO_ERD.puml`: PlantUML ER diagram export.
- `ODOO_ERD.dot`: Graphviz DOT format (full ERD).
- `ODOO_ERD.svg`: SVG rendering (scalable, web-friendly).
- `ODOO_ERD.png`: PNG rendering (raster image).
- `ODOO_ERD_ipai.dot`: IPAI modules only (DOT).
- `ODOO_ERD_ipai.svg`: IPAI modules only (SVG).

### Extended Schemas
- `EXTENDED_PLATFORM_SCHEMA.dbml`: Extended platform DBML.
- `EXTENDED_PLATFORM_ERD.mmd`: Extended platform Mermaid.
- `EXTENDED_PLATFORM_ORM_MAP.md`: Extended platform ORM map.
- `IPAI_AI_PLATFORM_SCHEMA.dbml`: AI platform DBML.
- `IPAI_AI_PLATFORM_ERD.mmd`: AI platform Mermaid.

### Integration Docs
- `SUPERSET_ERD_INTEGRATION.md`: How to embed ERDs in Superset dashboards.
- `schemaspy/`: SchemaSpy HTML output (when generated from database).

## Regenerate Locally

### All formats (DBML, Mermaid, PlantUML)
```bash
python scripts/generate_odoo_dbml.py
```

### Graphviz formats (DOT, SVG, PNG)
```bash
# Requires: apt-get install graphviz
python scripts/generate_erd_graphviz.py --format all
```

### IPAI modules only
```bash
python scripts/generate_erd_graphviz.py --filter ipai_ --format all
```

### From live database (requires DB connection)
```bash
psql -f scripts/erd_dot.sql -t -A > erd.dot
dot -Tsvg erd.dot -o erd.svg
```

## CI/CD Automation

ERDs are automatically regenerated when:
- Model files change in `addons/ipai/**/models/**`
- Migration files change in `db/migrations/**`
- Generator scripts are updated

### Workflows
- `erd-graphviz.yml`: Generates ERD from codebase (no DB required)
- `erd-schemaspy.yml`: Generates ERD from live database (requires DB secrets)

## Viewing ERDs

### Local
- **SVG/PNG**: Open directly in browser or image viewer
- **DOT**: Render with `dot -Tpng file.dot -o file.png`
- **DBML**: Import into https://dbdiagram.io
- **Mermaid**: Use Mermaid Live Editor or GitHub preview
- **PlantUML**: Render with PlantUML tooling

### Online
- **GitHub**: Raw file URLs work in markdown:
  ```markdown
  ![ERD](https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD.svg)
  ```

### Superset Dashboard
See `SUPERSET_ERD_INTEGRATION.md` for embedding in Superset.

### Supabase Edge Function
```
GET https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/serve-erd?format=svg
GET https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/serve-erd?format=svg&filter=ipai
```

## Color Legend (SVG/PNG)

| Color | Meaning |
|-------|---------|
| Light Green | IPAI custom modules (`ipai_*`) |
| Light Yellow | Odoo core models (`res_*`, `ir_*`) |
| Light Gray | Relation tables (`*_rel`) |
| Light Blue | Other tables |

## Options

### generate_erd_graphviz.py

| Option | Description |
|--------|-------------|
| `--format` | Output format: `dot`, `svg`, `png`, `all` |
| `--filter` | Filter tables by prefix (e.g., `ipai_`) |
| `--no-columns` | Don't show column details |
| `--max-columns` | Max columns per table (default: 15) |
| `--output-dir` | Output directory (default: `docs/data-model`) |
