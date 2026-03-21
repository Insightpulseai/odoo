# Odoo Data Model Artifacts

> Generated schema, ERD, and ORM mapping for IPAI custom modules.

---

## Artifacts

| File | Format | Purpose |
|------|--------|---------|
| `ODOO_CANONICAL_SCHEMA.dbml` | DBML | Schema definition for [dbdiagram.io](https://dbdiagram.io) |
| `ODOO_ERD.mmd` | Mermaid | Entity-relationship diagram (render in GitHub, VS Code, etc.) |
| `ODOO_ERD.puml` | PlantUML | UML entity-relationship diagram |
| `ODOO_ORM_MAP.md` | Markdown | Comprehensive ORM field mapping — all models, fields, types |
| `ODOO_MODEL_INDEX.json` | JSON | Machine-readable model index with full field metadata |
| `ODOO_MODULE_DELTAS.md` | Markdown | Per-module delta report (models added/extended) |

## Generation

```bash
python3 scripts/generate_odoo_dbml.py
```

**Generator**: `scripts/generate_odoo_dbml.py` — AST-based parser that scans Python
source files for `_name`, `_inherit`, `_table`, field declarations, and constraints.
Does not require a running database or Odoo instance.

**Execution root**: `odoo/odoo/odoo/` (repo root where `addons/` lives)

**Scan directories**: `addons/ipai/`, `addons/oca/`

## Coverage Caveat

**Last generated**: 2026-03-21

| Metric | Value |
|--------|-------|
| Models scanned | 139 |
| Tables generated | 142 |
| References (FK) | 163 |
| IPAI models | 139 |
| OCA models | 0 (not hydrated locally) |

This snapshot reflects **locally hydrated addons only**. OCA modules under `addons/oca/`
are hydrated at runtime via gitaggregate and were not present during this generation run.
The artifacts are valid for the current IPAI module set but do not represent full
OCA + IPAI parity coverage.

To include OCA models, hydrate OCA addons first (`git submodule update --remote addons/oca/*`),
then re-run the generator.

## Source-Derived vs Runtime-Derived

This directory contains **source-derived** artifacts (AST-parsed from Python source code).
A companion set of **runtime-derived** artifacts lives in `docs/data-model/runtime/`.

| Dimension | Source (this dir) | Runtime (`runtime/`) |
|-----------|-------------------|----------------------|
| Generator | `scripts/generate_odoo_dbml.py` | `scripts/dev/run_schema_mirror_local.sh` |
| Input | Python source files | Live PostgreSQL database |
| Requires DB | No | Yes |
| Captures | ORM declarations | Actual tables + indexes |
| Use case | Design review | Drift detection |

## Regeneration

These files are **generated artifacts**. Do not hand-edit them. To update:

1. Make changes to the source Odoo models in `addons/ipai/`
2. Run `python3 scripts/generate_odoo_dbml.py`
3. Commit all regenerated files together

For runtime artifacts: `./scripts/dev/run_schema_mirror_local.sh`
