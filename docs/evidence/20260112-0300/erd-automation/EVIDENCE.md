# ERD Automation Evidence Pack

**Date**: 2026-01-12 03:00 UTC
**Scope**: Automated ERD generation and Superset integration

## Summary

Implemented comprehensive ERD automation with multiple generation approaches and Superset integration.

## Changes Shipped

### GitHub Actions Workflows

1. **`.github/workflows/erd-schemaspy.yml`**
   - SchemaSpy-based ERD generation from live database
   - Produces HTML site + PNG/SVG diagrams
   - Publishes to gh-pages for browsable documentation
   - Falls back to codebase analysis if no DB credentials

2. **`.github/workflows/erd-graphviz.yml`**
   - Graphviz-based ERD generation from Odoo model AST
   - No database required - parses Python code directly
   - Generates DOT, SVG, PNG formats
   - Auto-commits artifacts on main branch

3. **`.github/workflows/erd-docs.yml`**
   - Combined workflow for all ERD artifacts
   - Generates: schema.sql, schema.dbml, erd.dot, erd.svg, tables.json
   - Uploads to Supabase Storage for stable URLs
   - Per-table JSON summary for LLM grounding

### Scripts

1. **`scripts/erd_dot.sql`**
   - SQL script to generate Graphviz DOT from pg_catalog
   - Extracts tables and foreign keys from PostgreSQL
   - Configurable schema filtering

2. **`scripts/generate_erd_graphviz.py`**
   - Python script extending existing DBML generator
   - Generates DOT format with color coding
   - Options: --format, --filter, --no-columns, --max-columns
   - Renders SVG/PNG via Graphviz if installed

### Supabase Edge Function

1. **`supabase/functions/serve-erd/index.ts`**
   - Edge function to serve ERD artifacts from Storage
   - Supports format selection (svg, png, dot)
   - Filter parameter for module-specific ERDs
   - Cache headers for performance

### Documentation

1. **`docs/data-model/README.md`** (updated)
   - Comprehensive artifact listing
   - Regeneration commands
   - CI/CD automation details
   - Color legend for diagrams

2. **`docs/data-model/SUPERSET_ERD_INTEGRATION.md`**
   - Superset embedding instructions
   - Multiple integration methods (GitHub raw, gh-pages, Storage, Edge Function)
   - Dashboard creation guide
   - LLM-friendly endpoint documentation

## Artifact Locations

### GitHub (after CI runs)
- `docs/data-model/ODOO_ERD.svg` - Full ERD
- `docs/data-model/ODOO_ERD_ipai.svg` - IPAI modules only
- `docs/data-model/ODOO_ERD.dot` - Graphviz source
- `docs/data-model/ODOO_MODEL_INDEX.json` - Model index

### Supabase Storage (stable URLs)
- `docs/erd/ODOO_ERD.svg`
- `docs/erd/ODOO_ERD_ipai.svg`
- `docs/schema/schema.dbml`
- `docs/schema/schema.sql`
- `docs/schema/tables.json`

### Edge Function
- `GET /functions/v1/serve-erd?format=svg`
- `GET /functions/v1/serve-erd?format=svg&filter=ipai`

## Superset Integration

Embed in Superset Markdown chart:
```markdown
<img src="https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD.svg"
     style="width:100%; max-width:2000px;" />
```

Or via Supabase Storage:
```markdown
<img src="https://spdtwktxdalcfigzeqrz.supabase.co/storage/v1/object/public/docs/erd/ODOO_ERD.svg"
     style="width:100%; max-width:2000px;" />
```

## LLM Grounding

For retrieval-augmented generation:
- `schema.dbml` - Structured schema definition
- `erd.dot` - Relationship graph (text format)
- `tables.json` - Per-table summaries with PK/FK

## Verification

- [x] Scripts created and syntax validated
- [x] Workflows follow repo patterns
- [x] Edge function matches existing function style
- [x] Documentation updated

## Files Created/Modified

| File | Action |
|------|--------|
| `.github/workflows/erd-schemaspy.yml` | Created |
| `.github/workflows/erd-graphviz.yml` | Created |
| `.github/workflows/erd-docs.yml` | Created |
| `scripts/erd_dot.sql` | Created |
| `scripts/generate_erd_graphviz.py` | Created |
| `supabase/functions/serve-erd/index.ts` | Created |
| `docs/data-model/README.md` | Updated |
| `docs/data-model/SUPERSET_ERD_INTEGRATION.md` | Created |
