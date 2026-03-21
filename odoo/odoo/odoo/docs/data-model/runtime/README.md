# Runtime-Derived Data Model Artifacts

> Produced by introspecting a **live Odoo PostgreSQL database** — complements
> the source-derived artifacts in `docs/data-model/` (AST-parsed from Python source).

---

## Source vs Runtime Artifacts

| Dimension | Source-Derived (`docs/data-model/`) | Runtime-Derived (`docs/data-model/runtime/`) |
|-----------|-------------------------------------|----------------------------------------------|
| Generator | `scripts/generate_odoo_dbml.py` | `scripts/dev/run_schema_mirror_local.sh` |
| Input | Python AST of `addons/ipai/` source | Live PostgreSQL `odoo_dev` database |
| Requires DB | No | Yes |
| Captures | ORM field declarations, model names | Actual tables, columns, indexes, constraints |
| Misses | Runtime-only tables (Odoo core, OCA) | Fields declared but not yet migrated |
| Use case | Design review, model documentation | Drift detection, deployment verification |

## Artifacts

| File | Format | Purpose |
|------|--------|---------|
| `odoo_schema.json` | JSON | Full PostgreSQL introspection (tables, columns, PKs, FKs, indexes) |
| `manifest.json` | JSON | Generation metadata (timestamp, source DB, steps executed) |

## Generation

```bash
./scripts/dev/run_schema_mirror_local.sh
```

**Prerequisites**: Local PostgreSQL running with `odoo_dev` database initialized.

## Drift Guard

```bash
./scripts/validate_runtime_schema_mirror.sh        # Check artifacts exist and are fresh
./scripts/validate_runtime_schema_mirror.sh 14      # Allow up to 14 days staleness
```

## Supabase Shadow Schema (Future)

When `SUPABASE_DB_URL` is configured, the wrapper also runs:
- `generate_dbml.py` — produces DBML from Supabase `odoo_shadow` schema
- `validate_parity.py` — compares Odoo PG vs Supabase shadow for drift

These are skipped in local-only mode.
