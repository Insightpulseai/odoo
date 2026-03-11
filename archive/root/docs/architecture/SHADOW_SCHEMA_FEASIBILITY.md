# Odoo Shadow Schema Feasibility Assessment

> **Status**: FEASIBLE
> **Date**: 2026-01-20
> **Purpose**: Validate canonical schema artifacts for Supabase shadow sync

---

## Executive Summary

The canonical schema artifacts in this repository fully support generating a Supabase `odoo_shadow` schema for the Innovation Sidecar architecture. Odoo's inheritance patterns are properly flattened, and 98.9% of fields are stored (mirrorable).

---

## Canonical Artifacts Validated

| Artifact | Location | Status |
|----------|----------|--------|
| `ODOO_MODEL_INDEX.json` | `docs/data-model/` | 357 models, 2847 fields |
| `ODOO_CANONICAL_SCHEMA.dbml` | `docs/data-model/` | DBML for dbdiagram.io |
| `ODOO_ORM_MAP.md` | `docs/data-model/` | Human-readable field mapping |
| `ODOO_MODULE_DELTAS.md` | `docs/data-model/` | Per-module schema changes |

---

## Inheritance Analysis

### Odoo Inheritance Patterns

| Pattern | Count | Description | Shadow Strategy |
|---------|-------|-------------|-----------------|
| Extension (`_inherit`) | 171 models | Adds fields to existing model | Flattened in canonical schema |
| Delegated (`_inherits`) | 1 model | Creates FK to parent table | Handle with explicit FK |
| Mixin | Common | `mail.thread`, `mail.activity.mixin` | Already flattened |

### Key Finding: Minimal Delegated Inheritance

Only ONE model uses `_inherits` (delegated inheritance):

```
attachment.queue (module: attachment_queue)
  └── inherits_delegated: {'ir.attachment': 'attachment_id'}
```

This simplifies shadow generation significantly.

---

## Field Storage Analysis

```
Total fields analyzed:    2,847
├── Stored:               2,819 (98.9%) → Mirror to shadow
│   ├── Regular stored:   2,507
│   └── Computed+stored:    312
└── NOT stored:               6 → Skip in shadow DDL
```

### Non-Stored Fields (Skip in Shadow)

These 6 fields have `store=False` and should be excluded from shadow tables:

- Computed display fields
- Related fields without storage
- Virtual aggregates

---

## Model Index Structure

The `ODOO_MODEL_INDEX.json` provides all metadata needed for shadow DDL generation:

```json
{
  "models": [{
    "name": "res.partner",
    "table": "res_partner",
    "module": "base",
    "inherits": ["mail.thread"],
    "inherits_delegated": {},
    "fields": [{
      "name": "email",
      "type": "Char",
      "store": true,
      "compute": null,
      "required": false,
      "index": true
    }]
  }]
}
```

### Available Metadata

| Field | Purpose | Generator Use |
|-------|---------|---------------|
| `name` | Model name (e.g., `res.partner`) | Documentation |
| `table` | SQL table name (e.g., `res_partner`) | Shadow table naming |
| `module` | Defining module | Filtering/prioritization |
| `fields[].type` | Odoo field type | PostgreSQL type mapping |
| `fields[].store` | Storage flag | Include/exclude decision |
| `fields[].compute` | Compute function | Identify computed fields |

---

## Module Distribution

### Top 15 Modules by Model Count

| Module | Models | Priority |
|--------|--------|----------|
| `ipai` | 105 | High - core IPAI |
| `account_financial_report` | 28 | Medium - reporting |
| `database_cleanup` | 19 | Low - maintenance |
| `partner_statement` | 11 | Medium - customer data |
| `excel_import_export` | 10 | Low - utilities |
| `ipai_bir_tax_compliance` | 9 | High - regulatory |
| `auditlog` | 7 | Medium - audit trail |
| `base_exception` | 7 | Low - error handling |
| `ipai_tbwa_finance` | 7 | High - finance |
| `ipai_superset_connector` | 6 | Medium - BI |

---

## Abstract/Transient Models (No Table)

These 5 models have no physical table and should be skipped:

| Model | Module | Reason |
|-------|--------|--------|
| `account.account.reconcile` | `account_reconcile_oca` | Wizard |
| `auditlog.log.line.view` | `auditlog` | Database view |
| `ipai.studio.ai.stats` | `ipai` | Computed stats |
| `ir.model.size.report` | `database_size` | Report |
| `mis.cash_flow` | `mis_builder_cash_flow` | MIS builder |

---

## Shadow Table Design

### Tracking Columns Pattern

Every shadow table includes these tracking columns:

```sql
_odoo_write_date  timestamptz,  -- Odoo write_date for incremental sync
_synced_at        timestamptz DEFAULT now(),  -- ETL sync timestamp
_sync_hash        text          -- MD5 hash for change detection
```

### Type Mapping

| Odoo Type | PostgreSQL Type |
|-----------|-----------------|
| `Char`, `Selection` | `text` |
| `Text`, `Html` | `text` |
| `Integer`, `Many2one` | `bigint` |
| `Float` | `double precision` |
| `Boolean` | `boolean` |
| `Date` | `date` |
| `Datetime` | `timestamptz` |
| `Binary` | `bytea` |
| `Monetary` | `numeric(16,2)` |
| `Json` | `jsonb` |
| Unknown | `jsonb` (fallback) |

### Excluded Field Types

| Odoo Type | Reason |
|-----------|--------|
| `One2many` | Reverse relation, not a column |
| `Many2many` | Stored in junction table |

---

## Implementation

### Generator Script

Location: `scripts/generate_shadow_ddl.py`

```bash
# Generate shadow DDL from canonical model index
python scripts/generate_shadow_ddl.py

# Output: docs/data-model/ODOO_SHADOW_SCHEMA.sql
```

### Generated Migration

Location: `db/migrations/shadow/`

Applied via Supabase CLI:
```bash
supabase db push
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Binary fields (large blobs) | Store metadata only; blobs in S3/Storage |
| Computed fields with `store=True` | Include in shadow (value persisted) |
| Computed fields with `store=False` | Skip; recreate as Supabase views if needed |
| Multi-company filtering | Apply `company_id` filter in ETL |
| Schema drift | Regenerate DDL when model index updates |

---

## Conclusion

**FEASIBILITY: HIGH**

The canonical schema artifacts are complete and properly structured for shadow DDL generation:

- 357 models with full metadata
- 98.9% of fields are stored (mirrorable)
- Inheritance properly flattened
- Only 1 delegated inheritance case
- 5 abstract models clearly identifiable

Proceed with implementation of `generate_shadow_ddl.py` and initial migration.

---

## References

- [Supabase + Odoo Integration Strategy](../architecture/SUPABASE_ODOO_INTEGRATION_STRATEGY.md)
- [ODOO_MODEL_INDEX.json](./ODOO_MODEL_INDEX.json)
- [ODOO_ORM_MAP.md](./ODOO_ORM_MAP.md)
- [ODOO_MODULE_DELTAS.md](./ODOO_MODULE_DELTAS.md)
