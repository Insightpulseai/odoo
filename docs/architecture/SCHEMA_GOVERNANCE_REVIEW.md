# Schema Governance Review

> Audit date: 2026-03-19
> Scope: All DBML, ORM, migration, ERD, and Prisma artifacts across the InsightPulse AI monorepo.
> Author: Agent (Claude Opus 4.6)

---

## A. Executive Summary

**There is no declared canonical schema source of truth.** The repo contains 5+ independent schema surfaces that were authored at different times, serve different systems, and have no synchronization mechanism between them. The Odoo ORM (`addons/ipai/*/models/*.py`) is the *de facto* runtime schema for the ERP database, but it is not documented as such. The Supabase migration corpus is the largest schema artifact set in the repo (~100+ SQL files across two locations) but targets a separate database entirely. Multiple DBML files exist in archive paths but none are actively maintained or generated from live state.

**Critical finding:** The `generate_odoo_dbml.py` script referenced in `CLAUDE.md` documentation as the way to regenerate data model artifacts has been archived to `archive/root/scripts/` and no longer exists at its documented path. The `docs/data-model/` directory referenced in `CLAUDE.md` does not exist at the repo root level. The `db/schema/` and `db/migrations/` directories documented in repo-topology.md do not exist.

**Remote Azure DB comparison:** Not possible in this session (Bash tool denied). The `scripts/odoo/check_prod_db_truth.sql` script exists for manual comparison but there is no automated CI gate that compares repo-declared models against live database state.

---

## B. Artifact Inventory

### B1. DBML Files

| Path | Technology | Authority | Freshness | Role |
|------|-----------|-----------|-----------|------|
| `supabase/db/schema/oca_docs_brain.dbml` | DBML | Hand-authored | 2025-12-20 | Supabase schema doc for OCA Docs Brain |
| `archive/root/docs/architecture/ODOO_CANONICAL_SCHEMA.dbml` | DBML | Generated (by `generate_odoo_dbml.py`) | Stale (archived) | Odoo table dump from ORM introspection |
| `archive/root/docs/architecture/insightpulse_canonical.dbml` | DBML | Hand-authored | Stale (archived) | Multi-tenant SaaS control plane design |
| `archive/root/docs/architecture/schema.dbml` | DBML | Hand-authored | Stale (archived) | Supabase public/auth/ops schema |
| `archive/root/docs/architecture/IPAI_AI_PLATFORM_SCHEMA.dbml` | DBML | Hand-authored | Stale (archived) | AI platform schema design |
| `archive/root/docs/architecture/IPAI_AI_PLATFORM_ERD.dbml` | DBML | Hand-authored | Stale (archived) | AI platform ERD |
| `archive/root/docs/architecture/EXTENDED_PLATFORM_SCHEMA.dbml` | DBML | Hand-authored | Stale (archived) | Extended platform schema |
| `archive/root/docs/architecture/IPAI_FINANCE_OKR_SCHEMA.dbml` | DBML | Hand-authored | Stale (archived) | Finance/OKR schema |
| `archive/root/docs/architecture/MULTI_TENANT_PROVIDER_SCHEMA.dbml` | DBML | Hand-authored | Stale (archived) | Multi-tenant provider design |
| `archive/root/docs/architecture/SCOUT_CES_ANALYTICS_SCHEMA.dbml` | DBML | Hand-authored | Stale (archived) | Scout analytics schema |
| `archive/root/docs/product/parity/EE_PARITY_SSOT.dbml` | DBML | Hand-authored | Stale (archived) | EE parity tracking schema |

**Note:** Every DBML file except `supabase/db/schema/oca_docs_brain.dbml` is either archived or duplicated 3-5 times across nested `odoo/odoo/odoo/...` directories (a git nesting artifact).

### B2. Mermaid ERD Files (.mmd)

| Path | Freshness | Role |
|------|-----------|------|
| `archive/root/docs/architecture/ODOO_ERD.mmd` | Stale (archived) | Odoo core ERD |
| `archive/root/docs/architecture/EXTENDED_PLATFORM_ERD.mmd` | Stale (archived) | Platform ERD |
| `archive/root/docs/architecture/IPAI_AI_PLATFORM_ERD.mmd` | Stale (archived) | AI platform ERD |
| `archive/root/docs/architecture/ipai_platform_flow.mmd` | Stale (archived) | Platform flow |

### B3. PlantUML Files (.puml)

| Path | Freshness | Role |
|------|-----------|------|
| `archive/root/docs/architecture/ODOO_ERD.puml` | Stale (archived) | Odoo ERD |

### B4. DrawIO Diagrams

| Path | Freshness | Role |
|------|-----------|------|
| `docs/architecture/diagrams/azure-platform-overview.drawio` | Active | Azure platform overview |
| `archive/root/docs/architecture/supabase_integrations_erd.drawio` | Stale | Supabase ERD |
| `archive/root/docs/kb/odoo19/assets/odoo_core_erd.drawio` | Stale | Odoo core ERD |
| (5+ more in archive) | Stale | Various architecture diagrams |

### B5. Prisma Schema

| Path | Technology | Authority | Freshness | Role |
|------|-----------|-----------|-----------|------|
| `platform/pkgs/saas-types/prisma/schema.prisma` | Prisma | Hand-authored | 2026-01-12 | Multi-tenant SaaS type definitions |
| `archive/root/docs/architecture/schema.prisma` | Prisma | Hand-authored | Stale | Same content (archived copy) |

### B6. Odoo ORM Models (the de facto runtime schema)

| Path | Models Defined | Models Inherited | Role |
|------|---------------|-----------------|------|
| `addons/ipai/ipai_odoo_copilot/models/` | `ipai.copilot.conversation`, `ipai.copilot.message` | -- | Copilot chat models |
| `addons/ipai/ipai_enterprise_bridge/models/` | `ipai.doc.digitization.config`, `ipai.foundry.provider.config` | `res.config.settings` (x2) | Enterprise bridge config |
| `addons/ipai/ipai_finance_ppm/models/` | -- | `project.project`, `project.task`, `account.analytic.account` | PPM finance extensions |
| `addons/ipai/ipai_finance_ppm/wizards/` | `ipai.ppm.import.wizard` | -- | Import wizard |
| `addons/ipai/ipai_bir_tax_compliance/engine/` | -- | -- | Rules engine (no ORM models) |

**Total active ipai modules with `__manifest__.py`:** 14 (in `addons/ipai/`)
**Total modules with ORM model files:** 4 (ipai_odoo_copilot, ipai_enterprise_bridge, ipai_finance_ppm, ipai_bir_tax_compliance)
**New ORM models defined:** 5 (`ipai.copilot.conversation`, `ipai.copilot.message`, `ipai.doc.digitization.config`, `ipai.foundry.provider.config`, `ipai.ppm.import.wizard`)
**Inherited/extended models:** 4 (`project.project`, `project.task`, `account.analytic.account`, `res.config.settings`)

### B7. Supabase Migrations (SQL)

| Location | Count | Freshness | Target DB |
|----------|-------|-----------|-----------|
| `ops-platform/supabase/migrations/` | ~100+ files | 2024-01 to 2026-02 | Supabase (self-hosted on Azure VM) |
| `odoo/supabase/migrations/` | ~90+ files | 2024-01 to 2026-03 | Same Supabase instance (duplicated corpus) |

**Schemas covered:** `core`, `saas`, `logs`, `scout_dim`, `scout_fact`, `scout_gold`, `scout_meta`, `erp`, `ops`, `mcp_jobs`, `app`, `infra`, `docs`, `kg`, `public`, `auth`

### B8. Schema-Adjacent Scripts

| Path | Technology | Status | Purpose |
|------|-----------|--------|---------|
| `archive/root/scripts/generate_odoo_dbml.py` | Python (AST parsing) | **Archived** | Generates DBML/Mermaid/PlantUML from Odoo ORM `.py` files |
| `scripts/odoo/check_prod_db_truth.sql` | SQL | Active | Manual prod DB comparison queries |
| `scripts/odoo/extract_settings_catalog.py` | Python | Referenced (SSOT rule) | Extracts Odoo settings to `ssot/odoo/settings_catalog.yaml` |

### B9. Documented-But-Missing Paths

| Referenced In | Path | Exists? |
|--------------|------|---------|
| `odoo/odoo/odoo/CLAUDE.md` | `docs/data-model/` | **No** (not at repo root) |
| `odoo/odoo/odoo/CLAUDE.md` | `scripts/generate_odoo_dbml.py` | **No** (archived to `archive/root/scripts/`) |
| `.claude/rules/repo-topology.md` | `db/schema/` | **No** |
| `.claude/rules/repo-topology.md` | `db/migrations/` | **No** |
| `.claude/rules/repo-topology.md` | `db/seeds/` | **No** |
| `.claude/rules/repo-topology.md` | `db/rls/` | **No** |

---

## C. Canonicality Assessment

### C1. Odoo Domain (ERP Database on Azure PostgreSQL)

**Declared SSOT:** None explicitly declared for schema.
**De facto SSOT:** Odoo ORM model definitions in `addons/ipai/*/models/*.py` + Odoo core (in `vendor/odoo/`).
**How schema changes propagate:** Odoo's ORM auto-creates/migrates tables on module install/upgrade (`-i` / `-u` flags). There are no SQL migration files for the Odoo database -- the ORM is the migration engine.
**Documentation:** DBML/ERD artifacts that were once generated from ORM introspection are now archived. No active generated documentation exists.

### C2. Supabase Domain (Platform/Ops Database on Azure VM)

**Declared SSOT:** SQL migration files in `ops-platform/supabase/migrations/` (and duplicated in `odoo/supabase/migrations/`).
**Authority:** `SSOT_BOUNDARIES.md` states "Schema changes only via migrations" (Rule 4 in SSOT platform rules).
**Problem:** Two copies of the migration corpus exist (`ops-platform/supabase/migrations/` and `odoo/supabase/migrations/`). It is unclear which is canonical. They appear to be near-duplicates with some differences (the `odoo/supabase/` copy has additional files like `20260308_erp_entity_model.sql`).

### C3. SaaS/Platform Types (Prisma)

**Location:** `platform/pkgs/saas-types/prisma/schema.prisma`
**Status:** Appears to be a type-generation schema for the SaaS layer. Defines multi-tenant models that map to Odoo's `res.company`/`res.partner`. Not connected to any database migration pipeline.

---

## D. Local Sync Assessment

| Schema Surface | In Sync With Repo? | Evidence |
|----------------|-------------------|----------|
| Odoo ORM models | Yes (they ARE the repo) | Models in `addons/ipai/*/models/*.py` are the source |
| Supabase migrations | Likely out of sync | Two copies exist; unknown which was last applied |
| DBML files | No | All archived; no generation pipeline active |
| Mermaid/PlantUML ERDs | No | All archived |
| Prisma schema | Unknown | No migration or sync pipeline exists |
| DrawIO diagrams | Partially | Only 1 active (`azure-platform-overview.drawio`); rest archived |

---

## E. Remote Azure Sync Assessment

**Odoo DB (`ipai-odoo-dev-pg`):**
- Cannot verify (Bash tool denied in this session).
- `scripts/odoo/check_prod_db_truth.sql` exists for manual comparison but is not automated in CI.
- Odoo's ORM handles schema migration at startup; the risk is modules installed in the DB but removed from repo, or repo modules not yet installed in the DB.
- **No CI gate exists** to detect schema drift between repo ORM definitions and the live Odoo database.

**Supabase DB (`vm-ipai-supabase-dev`):**
- Cannot verify (Bash tool denied).
- Supabase CLI `supabase db push` is the declared mechanism.
- **No CI gate exists** to verify migration state against the live Supabase instance.

---

## F. Governance Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Schema SSOT explicitly declared | **FAIL** | No document declares "X is the canonical schema source of truth" |
| Schema changes gated in CI | **FAIL** | No workflow validates schema consistency |
| DBML/ERD kept in sync with ORM | **FAIL** | Generator script archived; `docs/data-model/` does not exist |
| Supabase migration corpus deduplicated | **FAIL** | Two copies: `ops-platform/supabase/migrations/` and `odoo/supabase/migrations/` |
| Odoo<->Supabase boundary documented | **PARTIAL** | `SSOT_BOUNDARIES.md` declares ownership boundaries but does not enumerate shared entities |
| Live DB drift detection | **FAIL** | No CI job compares repo schema against live Azure databases |
| Schema change review required | **PARTIAL** | SSOT rules say "migrations only" but no PR label/CODEOWNERS enforcement for schema paths |
| Documented paths match actual paths | **FAIL** | `db/schema/`, `db/migrations/`, `docs/data-model/` referenced but do not exist |

---

## G. Remediation Plan

### P0 -- Critical (schema truth gap)

1. **Declare Odoo ORM as the canonical schema SSOT for the ERP domain.** Add to `SSOT_BOUNDARIES.md`:
   - Odoo ORM (`addons/ipai/*/models/*.py` + `vendor/odoo/addons/*/models/*.py`) is the schema source of truth for the `odoo` database.
   - No external DBML/ERD is authoritative -- they are derived artifacts only.

2. **Deduplicate Supabase migration corpus.** Choose one canonical location (`ops-platform/supabase/migrations/` or `odoo/supabase/migrations/`) and symlink or remove the other. Document the decision in `SSOT_BOUNDARIES.md`.

3. **Remove phantom paths from documentation.** Update `repo-topology.md` and the nested `CLAUDE.md` files to remove references to `db/schema/`, `db/migrations/`, `db/seeds/`, `db/rls/`, `docs/data-model/`, and `scripts/generate_odoo_dbml.py` (or mark them as archived/planned).

### P1 -- High (operational risk)

4. **Restore `generate_odoo_dbml.py` to an active path** (e.g., `scripts/odoo/generate_odoo_dbml.py`) and create a CI workflow that regenerates DBML/ERD on every push that touches `addons/ipai/*/models/*.py`. Output to `docs/data-model/` (create the directory).

5. **Add a schema drift detection CI gate for Odoo.** A lightweight script that:
   - Parses all `_name` and `_inherit` declarations from `addons/ipai/*/models/*.py`
   - Optionally connects to the live DB to compare installed `ir_model` records
   - Fails if new models exist in code but not in DB (or vice versa)

6. **Add CODEOWNERS rule for schema-critical paths:**
   ```
   addons/ipai/*/models/ @schema-reviewers
   ops-platform/supabase/migrations/ @schema-reviewers
   supabase/db/schema/ @schema-reviewers
   ```

### P2 -- Medium (documentation debt)

7. **Create `docs/data-model/` at repo root** with:
   - Generated `ODOO_CANONICAL_SCHEMA.dbml` (from restored script)
   - Generated `ODOO_ERD.mmd`
   - `SUPABASE_SCHEMA_MAP.md` listing all Supabase schemas and their ownership
   - `SCHEMA_BOUNDARY_CONTRACT.md` documenting which entities live where

8. **Add `ssot/governance/schema_governance.yaml`** declaring:
   - Schema surfaces and their authority
   - Generation pipelines
   - Drift detection gates
   - Review requirements

### P3 -- Low (cleanup)

9. **Clean up nested `odoo/odoo/odoo/...` directory duplication.** The recursive nesting creates 3-5 copies of every archived DBML, ERD, and script. This is a git submodule or clone artifact that should be resolved.

10. **Archive or delete the Prisma schema** if it is not connected to any runtime. If it is planned for the SaaS layer, add a migration pipeline and document it.

---

## H. Schema Surface Summary Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    Schema Governance Map                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ODOO DB (Azure PG: ipai-odoo-dev-pg)                           │
│  ┌─────────────────────────────────────┐                        │
│  │ Schema SSOT: Odoo ORM              │                        │
│  │ addons/ipai/*/models/*.py          │  5 new models          │
│  │ vendor/odoo/addons/*/models/*.py   │  ~400+ core models     │
│  │ Migration engine: Odoo ORM (-u)    │                        │
│  │ Drift detection: NONE              │                        │
│  │ Generated docs: ARCHIVED           │                        │
│  └─────────────────────────────────────┘                        │
│                                                                  │
│  SUPABASE DB (Azure VM: vm-ipai-supabase-dev)                   │
│  ┌─────────────────────────────────────┐                        │
│  │ Schema SSOT: SQL migrations        │                        │
│  │ ops-platform/supabase/migrations/  │  ~100+ files           │
│  │ odoo/supabase/migrations/          │  ~90+ files (DUPE?)    │
│  │ supabase/db/schema/*.dbml          │  1 active DBML         │
│  │ Migration engine: supabase db push │                        │
│  │ Drift detection: NONE              │                        │
│  └─────────────────────────────────────┘                        │
│                                                                  │
│  SAAS TYPES (No runtime DB)                                      │
│  ┌─────────────────────────────────────┐                        │
│  │ platform/pkgs/saas-types/prisma/   │  Design-time only      │
│  │ schema.prisma                      │  No migration pipeline │
│  └─────────────────────────────────────┘                        │
│                                                                  │
│  ARCHIVED (Not maintained)                                       │
│  ┌─────────────────────────────────────┐                        │
│  │ archive/root/docs/architecture/    │  11 DBML files         │
│  │ archive/root/docs/architecture/    │  4 Mermaid ERDs        │
│  │ archive/root/docs/architecture/    │  1 PlantUML ERD        │
│  │ archive/root/scripts/              │  1 DBML generator      │
│  └─────────────────────────────────────┘                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

*Generated: 2026-03-19 by schema governance audit agent*
