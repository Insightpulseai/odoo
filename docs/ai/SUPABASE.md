# Supabase — Integration Layer & Capability Maximization
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Key Principle

**Supabase is NOT a live replica of Odoo.** It is the **integration + intelligence layer**:

| Role | What lives there | Status |
|------|------------------|--------|
| **Auth** | Email + GitHub OAuth + OTP flows | Active |
| **Edge compute** | 42 Edge Functions (sync, auth, cron, MCP, RAG) | Active |
| **Event bus** | Webhook ingestion, event outbox, sync cursors | Active |
| **Secret Vault** | pgsodium-encrypted secrets + audit trail | Active |
| **Realtime** | 3 channels (jobs, approvals, notifications) | Active |
| **pgvector** | RAG pipeline — hybrid search, 1536-dim embeddings | Active |
| **Catalog** | Unity Catalog (assets, tools, lineage) | Active |
| **Shadow tables** | Read-only snapshots for verification | Active |
| **n8n bridge** | Cron → webhooks, event routing, 8+ workflows | Active |
| **GitHub bridge** | pulser-hub App — OAuth, webhooks, marketplace | Active |
| **Storage** | Configured (50MiB limit) — **not yet activated** | Ready |
| **pg_cron** | 4 jobs seeded — **not yet activated** | Ready |

Odoo PostgreSQL (self-hosted, PG 16) remains the authoritative ERP database.

---

## Project

| Item | Value |
|------|-------|
| **Project ID** | `spdtwktxdalcfigzeqrz` |
| **Config** | `supabase/config.toml` |
| **PG version** | 15 (Supabase) ↔ 16 (DO self-hosted): wire-compatible |
| **Migrations** | 103 files across 7 schema layers |
| **Edge Functions** | 43 deployed |
| **Deprecated projects** | `xkxyvboeubffxxbebsll`, `ublqmilcjtpnflofprkr` — never use |

---

## Monorepo Sync Architecture

```
Odoo CE 19 (PG 16)                    Supabase (PG 15)
+-----------------------+              +---------------------------+
| account.move          |  webhook     | odoo.webhook_events       |
| project.project       | ----------> | odoo.sync_cursors          |
| project.task          |  (HMAC)     | odoo.entity_mappings       |
| ir.module.module      |              | odoo.instances             |
+-----------------------+              +---------------------------+
                                                  |
                                       +----------+-----------+
                                       |                      |
                                  shadow-odoo          catalog-sync
                                  -finance              (Odoo models
                                  (snapshot)             + Scout views)
                                       |                      |
                                       v                      v
                              odoo_seed.shadow_*     catalog.assets
                              (verification only)    (FQDN indexed)
```

### Sync Patterns (Event-Driven, Not Mirroring)

| Pattern | Edge Function | Direction | Frequency |
|---------|--------------|-----------|-----------|
| **Webhook ingestion** | `odoo-webhook` | Odoo → Supabase | Real-time (on event) |
| **Module inventory** | `sync-odoo-modules` | Odoo → Supabase | Scheduled |
| **Finance shadow** | `shadow-odoo-finance` | Odoo → Supabase | Scheduled |
| **Asset catalog** | `catalog-sync` | Odoo + Scout → Supabase | Manual/scheduled |
| **Realtime broadcast** | `realtime-sync` | Supabase → clients | On change |

### Webhook Flow

```
Odoo → POST /odoo-webhook
  Headers: x-ipai-signature (HMAC-SHA256), x-ipai-timestamp
  Body: { event_type, aggregate_type, aggregate_id, payload }
  Validation: 5-minute replay window
  Destination: odoo.webhook_events (status: pending → completed/failed)
  Audit: event_log table
```

### Shadow Tables (Verification Only)

```sql
-- odoo_seed schema: read-only snapshots
shadow_projects (odoo_id, external_ref, name, synced_at, raw)
shadow_tasks    (odoo_id, external_ref, project_odoo_id, synced_at, raw)

-- Verification views (auto-detect drift)
v_missing_in_odoo   -- seed exists, shadow doesn't
v_orphan_in_odoo    -- shadow exists, seed doesn't
v_name_drift        -- names changed between sync cycles
```

### Unity Catalog

```sql
-- catalog schema: FQDN-indexed asset registry
catalog.assets (fqdn, type, metadata, registered_at)
-- FQDN format: system.db.model
-- e.g., odoo.odoo_core.account.move, scout.gold.v_revenue_summary
```

---

## Database Schema Layers

| Layer | Migration Range | Content |
|-------|----------------|---------|
| **Auth** | 5000–5003 | Identity, JWT, RLS |
| **Core** | 1000 | Tenancy, ERP base |
| **ERP** | 2000 | Finance, expense, inventory |
| **Engine** | 3000 | Processing engines |
| **Odoo Bridge** | 2025-01-25 | Integration schemas |
| **Operations** | 2026-01-24 | Ops control plane |
| **Cleanup** | 99999999 | Rollback examples |

**Key schemas**: `public`, `odoo`, `odoo_seed`, `scout_gold`, `catalog`, `integration`

---

## Seed Strategy (9-Part)

```
9000_core/       → Tenants, roles, users, auth
9001_erp/        → Odoo data + BIR templates
9002_engines/    → Processing engines (retail intel, PPM, TE, OCR)
9003_ai_rag/     → AI agent + knowledge base
9004_analytics/  → KPI registry + Superset dashboards
9005_catalog/    → Asset catalog
9006_catalog/    → Scout SUQI semantic
9007_skills/     → Certification
9008_drawio/     → DrawIO assessment
```

Master orchestrator: `supabase/seed.sql`

---

## Infrastructure as Code

```
infra/supabase/
├── main.tf              # Provider config
├── production.tf        # Project resources
├── vault_secrets.tf     # Secret management
├── envs/
│   ├── dev/             # terraform.tfvars.example
│   ├── staging/
│   └── prod/
```

Commands: `make plan ENV=prod`, `make apply`, `make db-push`

---

## Feature Utilization (Verified 2026-02-07)

### Fully Operational

| Feature | Details | Evidence |
|---------|---------|----------|
| **Database** | 208 tables, 7 schema layers, 103 migrations | `supabase/migrations/` |
| **Auth** | Email + GitHub OAuth (pulser-hub) + OTP, JWT 1hr | `supabase/functions/auth-otp-*` |
| **Edge Functions** | 42 deployed (see catalog below) | `supabase/functions/` |
| **Vault** | pgsodium encryption, `control_plane` schema, 4 bots registered, audit trail | `vault_secrets.tf` |
| **Realtime** | 3 channels: `control_room_jobs`, `approval_requests`, `notifications` | `apps/*/lib/supabase.ts` |
| **pgvector** | text-embedding-3-small (1536d), hybrid search (vector + FTS + trigram) | `rag.documents`, `rag.chunks` |
| **n8n bridge** | 8+ workflows, cron → webhook, event routing, marketplace | `n8n/workflows/` |
| **GitHub bridge** | pulser-hub App (ID 2191216), OAuth, webhooks, HMAC verification | `supabase/functions/github-app-auth/` |

### Ready to Activate (Low Effort)

| Feature | What's needed | Impact |
|---------|--------------|--------|
| **Storage** | Create buckets, wire upload routes in apps | Replace external file hosting for BIR docs, attachments |
| **pg_cron** | Execute `cron.schedule()` for 4 seeded jobs | Activate BIR alerts, PPM reminders, health checks, cleanup |

---

## Edge Function Catalog (42 Functions)

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Auth** (5) | `auth-otp-request`, `auth-otp-verify`, `github-app-auth`, `auth-callback`, `token-refresh` | Identity + OAuth flows |
| **Sync** (6) | `odoo-webhook`, `sync-odoo-modules`, `shadow-odoo-finance`, `catalog-sync`, `realtime-sync`, `seed-odoo-finance` | Odoo ↔ Supabase data bridge |
| **AI/RAG** (8) | `docs-ai-ask`, `copilot-chat`, `semantic-query`, `memory-ingest`, `embedding-worker`, `classify-intent`, `summarize`, `context-resolve` | RAG pipeline + AI assistants |
| **Orchestration** (4) | `cron-processor`, `mcp-gateway`, `job-dispatcher`, `workflow-trigger` | Job queue + MCP routing |
| **Webhooks** (4) | `marketplace-webhook`, `billing-webhook`, `slack-events`, `deployment-hook` | External event ingestion |
| **Monitoring** (4) | `health-probe`, `schema-changed`, `drift-detector`, `alert-dispatcher` | Observability + drift detection |
| **Config** (5) | `config-publish`, `feature-flags`, `tenant-provision`, `env-resolve`, `secret-rotate` | Configuration management |
| **Knowledge** (6) | `kb-ingest`, `kb-search`, `kb-update`, `kb-delete`, `kb-reindex`, `kb-export` | Knowledge base CRUD |

---

## Vault (Secret Management)

```
control_plane schema:
├── secrets (pgsodium-encrypted)
├── bot_registry (4 bots: bugbot, vercel-bot, do-infra-bot, n8n-orchestrator)
├── audit_log (IP, user-agent, access type)
└── RPC: control_plane_get_secret_logged()
```

Access pattern: bot authenticates → `control_plane_get_secret_logged(bot_id, secret_name)` → returns decrypted value + writes audit entry.

---

## n8n Integration

| Pattern | Flow | Trigger |
|---------|------|---------|
| **Cron → n8n** | `cron-processor` edge function → n8n webhook URL | pg_cron schedule |
| **Odoo → n8n** | Odoo event → `odoo-webhook` → event_log → n8n | Real-time |
| **GitHub → n8n** | pulser-hub webhook → n8n router → Slack/Odoo | Push, PR, issue, CI |
| **n8n → Supabase** | n8n HTTP node → Supabase REST API / Edge Functions | Scheduled/event |

Seeded cron jobs (pending activation):

| Job | Schedule | Target |
|-----|----------|--------|
| BIR compliance alerts | Daily 8 AM MNL | n8n webhook |
| PPM reminders | Weekly Monday 9 AM MNL | n8n webhook |
| Health check | Every 15 min | n8n webhook |
| Stale data cleanup | Daily 2 AM MNL | n8n webhook |

---

## GitHub Integration (pulser-hub)

```
App ID: 2191216
Webhook: https://n8n.insightpulseai.com/webhook/github-pulser
```

| Feature | Implementation |
|---------|---------------|
| **OAuth** | `github-app-auth` edge function → Supabase Auth |
| **Webhooks** | HMAC-SHA256 verification → n8n event router |
| **Installation tokens** | JWT signing for secure API access |
| **Marketplace** | `marketplace-webhook` for GitHub/GDrive/S3/Slack |
| **Event routing** | Push → deploy, PR → Odoo task, @claude → agent queue |

---

## pgvector (RAG Pipeline)

```sql
-- Schema: rag
rag.documents (id, title, source, version, provenance, language, embedding)
rag.chunks    (id, document_id, content, embedding, metadata)

-- Hybrid search: vector + FTS + trigram
SELECT * FROM rag.hybrid_search(
  query_embedding := embed('question'),   -- cosine similarity
  query_text := 'question',               -- tsvector FTS
  match_threshold := 0.7,
  match_count := 10
);
```

Used by: `docs-ai-ask`, `copilot-chat`, `semantic-query`, `memory-ingest`

---

## Storage (Ready to Activate)

Configured in `config.toml` with 50MiB file limit. Target buckets:

| Bucket | Use Case | Access |
|--------|----------|--------|
| `documents` | BIR forms, compliance exports | Authenticated |
| `attachments` | Odoo record attachments (synced) | Authenticated |
| `exports` | Report exports, CSV/PDF downloads | Authenticated + signed URLs |
| `public` | Landing page assets, logos | Public |

```typescript
await supabase.storage
  .from('documents')
  .upload(`bir/${year}/${form_type}/${filename}`, file)
```

---

## Maximization Priority

| Priority | Feature | Action | ROI |
|----------|---------|--------|-----|
| **P0** | pg_cron | Activate 4 seeded jobs (one SQL call) | Automated compliance + health |
| **P0** | Storage | Create buckets, wire BIR doc uploads | Replace manual file handling |
| **P1** | Realtime | Add `odoo-sync` channel for ERP change feed | Live dashboard updates |
| **P1** | Auth | Increase adoption in vendor portal (planned) | Self-service onboarding |
| **P2** | Database webhooks | Route table changes to n8n | Event-driven automation |
| **P2** | pgvector | Expand RAG corpus (Odoo docs, specs, wikis) | Better AI assistant answers |

---

## Security Verification

```bash
scripts/supabase/checks.sh                     # Health checks
scripts/supabase/exposed_schemas.py             # PostgREST exposure audit
scripts/supabase/sql/assert_exposed_schemas.sql # Schema checks
scripts/supabase/sql/assert_rls_enabled.sql     # RLS verification
scripts/supabase/sql/assert_policies_exist.sql  # Policy checks
```

---

## No Dedicated Odoo Connector Module

Supabase integration is handled at the **function/API layer** — 42 Edge Functions for webhooks + catalog sync + RAG, Python `requests` for Odoo → Supabase calls. No `ipai_supabase_connector` module needed.
