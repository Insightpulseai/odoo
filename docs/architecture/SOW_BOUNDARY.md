# SoR / SSOT / SoW Boundary Doctrine

> **Last updated:** 2026-03-01
> **Status:** ENFORCED — agents must not cross these boundaries without a contract doc.
> **Owner:** Platform Architecture

---

## Definitions

| Acronym | Name | Layer | Owner |
|---------|------|-------|-------|
| **SoR** | System of Record | Business transactions & structured data | Odoo CE 19.0 |
| **SSOT** | Single Source of Truth | Orchestration, audit, task bus, identity | Supabase `ops.*` + `auth.*` |
| **SoW** | System of Work | Knowledge, collaboration, workspace pages | Supabase `work.*` + Vercel apps |

---

## Platform Assignment

### Odoo (SoR)

Odoo owns all **authoritative business records**. Any mutation to these surfaces must go through Odoo's business logic (ORM hooks, constraints, workflows).

| Data | Odoo table / model |
|------|--------------------|
| Vendors, customers, employees | `res.partner`, `hr.employee` |
| Purchase orders, invoices | `purchase.order`, `account.move` |
| Expenses | `hr.expense` |
| Projects & timesheets | `project.project`, `hr.timesheet` |
| BIR tax filings | `ipai.bir.filing` |
| Product catalog | `product.template`, `product.product` |
| Journal entries | `account.journal`, `account.move.line` |

**Rules:**
1. SoW and SSOT can **read** from Odoo (via REST/JSON-RPC) but **never write directly**.
2. All writes to Odoo go through the `sync-odoo-agent` handler — which currently emits `NOT_CONFIGURED` until credentials are present. This is intentional: the agent boundary prevents accidental SoR corruption.
3. Odoo data surfaced in `work.*` (e.g., vendor name on a page) is a **cached snapshot**, not the authoritative record.

---

### Supabase ops.* (SSOT)

The `ops` schema is the orchestration and audit backbone. It is **append-only for events**.

| Table | Purpose |
|-------|---------|
| `ops.runs` | Durable ledger of every agent execution |
| `ops.run_events` | Immutable event stream per run |
| `ops.artifacts` | Outputs produced by runs |
| `ops.schedules` | Cron job registry |

**Rules:**
1. `ops.runs` / `ops.run_events` are **never deleted** outside of a migration with explicit approval.
2. Agents write to `ops.*` only via the `enqueue`, `markRunning`, `markFinished` helpers in `packages/taskbus`.
3. Direct Supabase dashboard mutations to `ops.*` are **prohibited** in production.

---

### Supabase work.* (SoW)

The `work` schema is the collaborative knowledge layer — a Notion-like workspace.

| Table | Purpose |
|-------|---------|
| `work.spaces` | Top-level workspace tenants |
| `work.pages` | Hierarchical documents |
| `work.blocks` | Rich content blocks within pages |
| `work.databases` | Notion-style databases |
| `work.db_columns` | Schema for database columns |
| `work.db_rows` | Row data (jsonb `data` field keyed by column name) |
| `work.relations` | Cross-page / cross-db links |
| `work.comments` | Discussion threads on pages/blocks |
| `work.attachments` | File references |
| `work.permissions` | Space-level ACL (member, editor, admin) |
| `work.templates` | Reusable page / block templates |
| `work.search_index` | Denormalized index: tsvector + pgvector embedding |

**Rules:**
1. `work.*` can reference Odoo IDs (e.g., `odoo_partner_id` on a page) for **display** — never for joins that trigger writes back to Odoo.
2. `work.search_index` is maintained asynchronously by the `workspace-indexer` Edge Function — never manually edited.
3. Embeddings in `work.search_index.embedding` use `text-embedding-3-small` (1536 dims). Changing the model requires a migration to re-embed all rows.
4. RLS on `work.*` scopes authenticated users to spaces they appear in via `work.permissions`. Service-role bypasses RLS for Edge Functions and scheduled jobs.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                      SoR (Odoo)                      │
│  res.partner · account.move · hr.expense · project   │
│  ← authoritative write surface (Odoo ORM only) →    │
└─────────────┬────────────────────────────────────────┘
              │ READ via REST/JSON-RPC (sync-odoo-agent)
              ▼
┌─────────────────────────────────────────────────────┐
│              SSOT (Supabase ops.*)                   │
│  runs · run_events · artifacts · schedules           │
│  ← append-only orchestration ledger →               │
└─────────────┬────────────────────────────────────────┘
              │ Task bus dispatch · cron tick
              ▼
┌─────────────────────────────────────────────────────┐
│               SoW (Supabase work.*)                  │
│  spaces · pages · blocks · databases · search_index  │
│  ← collaborative knowledge · never writes to SoR →  │
└─────────────┬────────────────────────────────────────┘
              │ Next.js Vercel apps read via anon/service key
              ▼
┌─────────────────────────────────────────────────────┐
│           Execution Fabric (Vercel)                  │
│  apps/ops-console · apps/workspace                   │
│  api/cron/tick · api/queues/consume                  │
│  supabase/functions/workspace-indexer                │
│  supabase/functions/workspace-ask-docs               │
└─────────────────────────────────────────────────────┘
```

---

## Cross-Boundary Contract Rules

Any feature that **crosses a boundary** (e.g., a work page embedding Odoo invoice data) requires:

1. A contract doc under `docs/contracts/<NAME>_CONTRACT.md`
2. Registration in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
3. A CI validation rule in `.github/workflows/ssot-surface-guard.yml`

**Existing contracts:**
- `docs/contracts/DNS_EMAIL_CONTRACT.md` — DNS + mail routing

---

## What Agents May NOT Do

| Agent | Prohibited action |
|-------|-------------------|
| `sync-odoo-agent` | Write to `work.*` or `ops.run_events` directly |
| `workspace-indexer` | Read from `ops.*` or write to `ops.*` |
| `workspace-ask-docs` | Write to any table |
| Any agent | Write to Odoo PostgreSQL directly (bypass ORM) |
| Any agent | Read Supabase Vault secrets and return them in a response |

---

## Allowed Read Paths

| Consumer | May read | Auth |
|----------|----------|------|
| `apps/workspace` server components | `work.*` | service role (SSR only) |
| `apps/ops-console` server components | `ops.*` | service role (SSR only) |
| Authenticated Next.js client | `work.*` | anon key + RLS |
| `workspace-indexer` Edge Function | `work.pages`, `work.blocks` (via webhook payload) | service role |
| `workspace-ask-docs` Edge Function | `work.search_index` via RPC | service role |
| `cron/tick` API route | `ops.schedules` | service role |
| `queues/consume` API route | `ops.runs` | service role |

---

## No UI-Only Configuration Rule (ENFORCED)

> **No deployment-critical step may depend on "set it in the dashboard".**

All automation must be expressed as the combination of:

| Component | Where it lives |
|-----------|---------------|
| Schema change | `supabase/migrations/<timestamp>_<name>.sql` |
| Edge Function | `supabase/functions/<name>/index.ts` |
| Cron schedule | `supabase/migrations/` via `pg_cron` + `pg_net`, OR taskbus schedule in `ops.schedules` |
| Secret identity | `ssot/secrets/registry.yaml` (names only, never values) |
| Secret value | Supabase Vault / GitHub Actions Secrets / Vercel env vars |

**Examples of forbidden UI-only config:**
- Setting up Database Webhooks in the Supabase dashboard to trigger Edge Functions
- Adding cron jobs via the Supabase dashboard Cron UI without a corresponding migration
- Adding Supabase Vault secrets without registering them in `ssot/secrets/registry.yaml`

**Correct pattern for event-driven indexing:**
```
work.pages / work.blocks (Postgres table)
  └─ AFTER INSERT OR UPDATE trigger (in migration 000003)
       └─ calls work.enqueue_index() RPC
            └─ inserts into work.index_queue

pg_cron (scheduled in migration 000003)
  └─ every 2 min → POST /functions/v1/workspace-indexer
       └─ work.claim_index_batch() → process → work.ack_index()
```

**SoW indexing is always async via queue — never inline on writes.**
Inline indexing would block the write transaction and couple latency to LLM/embedding API calls.

## Enforcement

- **CI**: `ssot-surface-guard.yml` scans PRs for direct cross-boundary writes.
- **RLS**: Postgres policies prevent authenticated users writing to `ops.*`.
- **Agent policies**: `AGENT_POLICIES` in `packages/taskbus/src/policies.ts` allowlists write surfaces per agent.
- **TypeScript**: `import 'server-only'` in Vercel apps prevents service-role key reaching client bundles.
- **SSOT gate**: Any secret consumed by a SoW function must have an entry in `ssot/secrets/registry.yaml` before the PR is merged.
