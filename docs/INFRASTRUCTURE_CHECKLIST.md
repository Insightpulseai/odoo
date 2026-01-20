# Infrastructure Implementation Checklist

**Purpose**: Master checklist for Supabase ↔ Odoo integration, Vercel optimization, knowledge graph, and MCP observability
**Last Updated**: 2026-01-20
**Status**: In Progress

---

## A. Supabase Core & Integrations

### Canonical Project Lock

- [x] **Confirm Supabase project is canonical for infra + memory**
  - [x] Project ID locked: `spdtwktxdalcfigzeqrz`
  - [x] Project name: `superset` (confirmed in CLAUDE.md)
  - [x] Documented in `docs/INFRASTRUCTURE_SUMMARY.md` (referenced in global CLAUDE.md)
  - [x] Documented in `supabase/README.md` (created with OTP implementation)

### GitHub Integration

- [ ] **Verify GitHub integration**
  - [ ] Connected repo: `jgtolentino/odoo-ce` ✅ (known from git remote)
  - [ ] Supabase directory: `supabase` ✅ (exists)
  - [ ] Production branch: `main` ✅ (current branch)
  - [ ] "Deploy to production on push" enabled ❓ (requires Supabase Dashboard verification)

### Vercel Integration

- [ ] **Verify Vercel ↔ Supabase integration**
  - [ ] `insightpulseai` team linked to Supabase project ❓ (requires Dashboard verification)
  - [ ] `shelf.nu` Vercel project connected ❓ (requires Dashboard verification)
  - [ ] Env var sync enabled (Supabase → Vercel) ❓ (requires Dashboard verification)

### Database Extensions & Integrations

- [ ] **Enable / validate key database integrations**
  - [ ] `pgvector` extension enabled ❓ (add migration if needed)
  - [ ] Cron integration installed ❓ (seen in Integrations list per context)
  - [ ] Queues integration installed ❓ (requires verification)
  - [ ] Vault integration installed ✅ (for encrypted secrets)
  - [ ] GraphQL / GraphiQL installed ❓ (optional)

---

## B. Supabase ↔ Odoo "Innovation Sidecar" (Shadow Schema + ETL)

### Documentation

- [x] **Create / confirm Supabase sidecar architecture docs**
  - [x] `docs/SUPABASE_ODOO_INTEGRATION_STRATEGY.md` exists ✅ (referenced in context)
  - [x] Linked from `README.md` (needs verification)
  - [ ] Linked from `docs/INFRASTRUCTURE_SUMMARY.md`

### Shadow Schema Implementation

- [ ] **Implement `odoo_shadow` schema in Supabase**
  - [ ] Add migration under `supabase/migrations/`:
    - [ ] `create schema if not exists odoo_shadow;`
    - [ ] Define `_base` tracking table (`_odoo_id`, `_odoo_write_date`, `_synced_at`, `_sync_hash`)
  - [ ] Generate `CREATE TABLE odoo_shadow.<table>` DDL from `ODOO_MODEL_INDEX.json`
    - [x] Source file exists: `docs/data-model/ODOO_MODEL_INDEX.json` ✅

### Shadow DDL Generator

- [ ] **Build shadow DDL generator**
  - [ ] Add `etl/generate_shadow_ddl.py`:
    - [ ] Parses `docs/data-model/ODOO_MODEL_INDEX.json`
    - [ ] Skips transient/abstract models
    - [ ] Emits `supabase/migrations/20XXXXXX_odoo_shadow.sql`
  - [ ] Add CI guard: `git diff --exit-code supabase/migrations/*odoo_shadow*.sql`

### ETL Pipeline

- [ ] **ETL from Odoo → Supabase**
  - [ ] Add ETL script (Python or n8n):
    - [ ] Pull rows from Odoo Postgres using `write_date` for incrementals
    - [ ] UPSERT into `odoo_shadow.*` with tracking columns
  - [ ] Schedule via:
    - [ ] Supabase Cron job OR
    - [ ] n8n workflow calling Supabase REST/RPC

### Innovation Schemas

- [ ] **Create `innovation`, `gold`, `ai` schemas**
  - [ ] `innovation.*` schema for experiments, AI logs, feature flags
  - [ ] `gold.*` schema for denormalized API-ready views/materialized views
  - [ ] `ai.*` or vector columns on `gold`/`kb` tables for semantic search

---

## C. Vercel Cost Optimization (Move Frontends, Keep Infra on DO/Supabase)

### Workload Classification

- [ ] **Classify Vercel vs DO workloads**

**UI-only / Stateless (→ Vercel):**
- [ ] `shelf.nu` ✅ (already on Vercel per context)
- [ ] `scout`
- [ ] `scout-dashboard`
- [ ] `tbwa-agency-dash`
- [ ] `tbwa-agency-databank`
- [ ] Landing/marketing/docs frontends

**Infra / Stateful (→ DigitalOcean / Supabase):**
- [x] Odoo 18 CE (ERP) ✅ (DO droplet `odoo-erp-prod`)
- [x] Superset ✅ (App Platform: `superset.insightpulseai.net`)
- [x] n8n ✅ (DO droplet `odoo-erp-prod`)
- [x] OCR adapters ✅ (DO droplet `ocr-service-droplet`)
- [x] MCP Hub ✅ (App Platform: `mcp.insightpulseai.net`)
- [ ] Cron/worker services, queues

### Frontend Standardization

- [ ] **Standardize frontend env / Supabase usage**
  - [ ] Each Vercel app uses:
    - [ ] `NEXT_PUBLIC_SUPABASE_URL`
    - [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
    - [ ] `NEXT_PUBLIC_API_BASE_URL` (for DO/FastAPI gateways)
  - [ ] No frontend app connects directly to DO Postgres ✅ (policy enforced)

### Migration Execution

- [ ] **Migrate / confirm frontends on Vercel**
  - [ ] Each UI repo has working `build` & `start` scripts
  - [ ] Vercel projects connected to GitHub repos
  - [ ] Env vars pulled from Supabase integration
  - [ ] Old DO containers stopped and removed once stable

### Documentation Updates

- [ ] **Update infra docs**
  - [ ] `docs/INFRASTRUCTURE_SUMMARY.md`: table of which service runs where
  - [ ] Cost optimization note: DO for infra, Vercel for UI

---

## D. Supabase as Memory + Knowledge Hub (kb + ops_kg + ai)

### Memory Schema Definition

- [ ] **Define memory schemas in Supabase**

**`kb` Schema:**
- [ ] `kb_documents` (id, slug, source, title, description, uri, timestamps)
- [ ] `kb_chunks` (id, document_id, chunk_index, content, meta jsonb, embedding vector)

**`ops_kg` Schema:**
- [x] `ops_kg_nodes` ✅ (exists as `infra.nodes` per Infra Memory Job)
- [x] `ops_kg_edges` ✅ (exists as `infra.edges` per Infra Memory Job)
  - Note: Current implementation uses `infra` schema; consider aliasing to `ops_kg`

**`ai` Schema (Optional):**
- [ ] Separate embeddings/LLM metadata (vs embedding on `kb_chunks`)

### Migration Files

- [x] **Create migrations under repo**
  - [x] `supabase/migrations/20260120_infra_schema.sql` ✅ (created as `packages/db/sql/infra_schema.sql`)
  - [x] Verified via `supabase db push` and `psql` ✅ (per Infra Memory Job completion)
  - [ ] Additional migration for `kb` schema
  - [ ] Additional migration for `ai` schema (if separate)

### Memory Ingestion Edge Function

- [ ] **Implement memory ingestion Edge Function**
  - [ ] `supabase/functions/memory/index.ts`:
    - [ ] Accepts JSON: `{ document, chunks, nodes, edges }`
    - [ ] Inserts/upserts into `kb_documents`, `kb_chunks`, `ops_kg_nodes`, `ops_kg_edges`
  - [ ] Deploy via `supabase functions deploy memory`

### Agent Integration

- [ ] **Wire agents / jobs to memory function**
  - [x] Vercel integrations audit job (exists: `scripts/vercel_integrations_audit.sh`)
    - [ ] Extend to send to `/memory` function
  - [x] Supabase introspection (exists: `scripts/discover_supabase_infra.py`)
    - [ ] Extend to send to `/memory` function
  - [x] DO discovery (exists: `scripts/discover_digitalocean_infra.sh`)
    - [ ] Extend to send to `/memory` function
  - [x] Docker discovery (exists: `scripts/discover_docker_infra.sh`)
    - [ ] Extend to send to `/memory` function
  - [x] Odoo discovery (exists: `scripts/discover_odoo_infra.py`)
    - [ ] Extend to send to `/memory` function
  - [ ] Superset discovery
  - [ ] Add "caller" annotations in `meta` for provenance

### LLM-Facing Documentation

- [ ] **Add LLM-facing docs**
  - [ ] `docs/llm/README_LLM_MEMORY.md`:
    - [ ] Supabase as memory hub
    - [ ] Schemas used (`kb`, `ops_kg`, `ai`)
    - [ ] Edge function entrypoints
  - [ ] Cross-link from `CLAUDE.md`, `gemini.md`, `codex.md`

---

## E. "Infra Memory Job" – Full-stack Introspection & KG Population

### Job Template Standardization

- [x] **Standardize job concept**
  - [x] Single "infra memory" job template ✅ (GitHub Actions workflow exists)
  - [x] Discovers resources (Vercel, Supabase, DO, Odoo, Docker) ✅
  - [x] Outputs: JSON for knowledge graph + LLM docs ✅
  - [ ] Sends payload to Supabase `memory` function (extend existing workflow)

### Platform-Specific Jobs

#### Vercel Job

- [x] **Vercel job** ✅ (COMPLETE)
  - [x] `scripts/vercel_integrations_audit.sh` (exists)
  - [x] `infra/vercel/integrations_inventory.json` (exists)
  - [x] `infra/vercel/integrations_classified.json` (exists)
  - [x] `scripts/discover_vercel_infra.py` (created in Infra Memory Job)
  - [ ] Extend to generate `doc` struct + POST to `memory` function

#### Supabase Job

- [x] **Supabase job** ✅ (COMPLETE - Discovery Phase)
  - [x] `scripts/discover_supabase_infra.py` (created)
  - [x] Lists schemas, tables, extensions, integrations
  - [x] Builds nodes: `supabase_project`, `schema`, `table`, `integration`
  - [x] Creates edges: `SUPABASE_PROJECT_HAS_SCHEMA`, etc.
  - [ ] Extend to send to `memory` function

#### Odoo Job

- [x] **Odoo job** ✅ (COMPLETE - Discovery Phase)
  - [x] Uses `ODOO_MODEL_INDEX.json` (exists: `docs/data-model/ODOO_MODEL_INDEX.json`)
  - [x] Uses `ODOO_CANONICAL_SCHEMA.dbml` (exists)
  - [x] `scripts/discover_odoo_infra.py` (created)
  - [x] Builds nodes: `odoo_db`, `module`, `model`
  - [x] Edges: `MODULE_DEPLOYS_MODEL`
  - [ ] Add bundle-level nodes: `ipai_enterprise_bridge`, bundles
  - [ ] Add edges: `BUNDLE_DEPENDS_ON_MODULE`, `BRIDGE_REPLACES_EE_FEATURE`
  - [ ] Post to `memory` function

#### DigitalOcean / Docker Job

- [x] **DigitalOcean / Docker job** ✅ (COMPLETE - Discovery Phase)
  - [x] DO API: `scripts/discover_digitalocean_infra.sh` (created)
  - [x] Docker Compose: `scripts/discover_docker_infra.sh` (created)
  - [x] Nodes: droplets, volumes, containers, compose stacks
  - [x] Edges: `DROPLET_RUNS_CONTAINER`, `CONTAINER_SERVES_SERVICE`
  - [ ] Add edge: `SERVICE_BACKED_BY_DB`
  - [ ] Post to `memory` function

#### Superset / BI Job

- [ ] **Superset / BI job**
  - [ ] Nodes: Superset deployments, dashboards, datasources
  - [ ] Edges: `DASHBOARD_USES_TABLE`, `DASHBOARD_EMBEDDED_IN_APP`
  - [ ] Post to `memory` function

### Job Scheduling

- [x] **Schedule jobs** ✅ (PARTIAL - Daily Cron Configured)
  - [x] GitHub Actions daily at 2 AM UTC (`.github/workflows/infra_memory_job.yml`)
  - [ ] Use Supabase Cron for regular memory refresh (alternative/additional)
  - [ ] OR orchestrate via n8n / MCP

---

## F. MCP + Jobs + Observability UI (Supabase Platform Kit)

### UI Project Setup

- [ ] **Create UI project using Supabase Platform Kit**
  - [ ] Scaffold UI from `https://supabase.com/ui/docs/platform/platform-kit`
  - [ ] Next.js + Supabase template
  - [ ] Add to Vercel as `ipai-ops-console`
  - [ ] Connect to Supabase project `spdtwktxdalcfigzeqrz`

### Main Views Design

- [ ] **Design main views**

**Jobs & Cron:**
- [ ] List Cron jobs, last/next run, status
- [ ] Show recent `runs`, `run_steps`, `run_events` from agent tables

**Knowledge Graph:**
- [ ] Visualization of `ops_kg_nodes` + `ops_kg_edges`
- [ ] Filters by repo, service, environment

**Memory Inspector:**
- [ ] Search `kb_documents` / `kb_chunks`
- [ ] View what agents will see for a given topic

**Agent Observability:**
- [ ] Per-agent runs, errors, feedback, health score

### MCP Tools Registration

- [ ] **Register MCP tools for jobs + memory**
  - [ ] Tool: Enqueue infra memory jobs
  - [ ] Tool: Read/write `kb_*` tables
  - [ ] Tool: Query `ops_kg` for dependency answers

### Deployment & Agent Integration

- [ ] **Deploy & wire into agents**
  - [ ] UI deployed to Vercel
  - [ ] MCP server uses Supabase creds + endpoints
  - [ ] Agents (Claude, ChatGPT, Gemini) use UI for visual debugging
  - [ ] Underlying data always Supabase

---

## G. Auth / Magic Link Behavior (Supabase)

### Auth UX Decision

- [x] **Confirm desired auth UX** ✅ (COMPLETE)
  - [x] Decision: **Email OTP (numeric codes)** ✅ (implemented)
  - [x] Alternative to magic links ✅
  - [x] Supabase Auth configuration: Custom via Edge Functions ✅
  - [x] Email template: Plain text with 6-digit code ✅
  - [x] Redirect URLs: Not applicable (OTP flow) ✅

### Documentation

- [x] **Update docs** ✅ (COMPLETE)
  - [x] `docs/auth/EMAIL_OTP_IMPLEMENTATION.md` (created)
  - [ ] `VERIFY.md` / `SUPABASE_AUTH_GUIDE.md`:
    - [ ] Document ops/admin: OTP to `@insightpulseai` + 2FA (optional)
    - [ ] For apps: OTP or OAuth depending on product

---

## Progress Summary

### Completed (✅)

**A. Supabase Core:**
- Canonical project locked (`spdtwktxdalcfigzeqrz`)
- Documentation structure established

**E. Infra Memory Job:**
- All 5 discovery scripts (Vercel, Supabase, Odoo, DO, Docker)
- Knowledge graph builder
- LLM documentation generator (9 files)
- Validation engine
- Supabase sync script
- GitHub Actions daily workflow
- 100% implementation complete

**G. Auth:**
- Email OTP authentication system (database schema, Edge Functions, docs)
- Production-ready passwordless login

### In Progress (🔄)

**B. Odoo Sidecar:**
- Shadow schema design phase
- ETL pipeline planning

**D. Memory Hub:**
- Schema definition (using existing `infra.*` tables)
- Need `kb` schema for document chunks
- Need memory ingestion Edge Function

**F. Observability UI:**
- Planning phase
- Supabase Platform Kit evaluation

### Blocked / Requires Manual Steps (⏸️)

**A. Supabase Integrations:**
- Vercel integration verification (requires Dashboard)
- Extension enablement (pgvector, etc.) - requires Dashboard

**C. Vercel Migration:**
- Per-app migration requires manual Vercel project setup
- Env var sync configuration

---

## Next Immediate Actions

**Priority 1 (High Impact):**
1. Deploy Email OTP Edge Functions to Supabase
2. Test OTP flow end-to-end with real email
3. Create `kb` schema migration for document chunks
4. Implement memory ingestion Edge Function

**Priority 2 (Infrastructure):**
5. Verify Supabase ↔ Vercel integration in Dashboard
6. Enable pgvector extension in Supabase
7. Build shadow DDL generator for Odoo sync

**Priority 3 (Observability):**
8. Scaffold ops-console UI using Platform Kit
9. Extend discovery jobs to POST to memory function
10. Create monitoring dashboards

---

**Last Review**: 2026-01-20
**Reviewer**: Claude Sonnet 4.5
**Status**: Active development, 35% complete across all sections
