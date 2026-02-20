# Monorepo Contract — Governance & Boundaries

> **SSOT for Insightpulseai/odoo monorepo structure and data flow rules.**
> All architectural decisions regarding directory layout, cross-domain communication, and CI invariants must reference this document.

**Status:** Canonical (enforced by CI gates)
**Last Updated:** 2026-02-20
**Owner:** Architecture Team

---

## Purpose

This monorepo merges **two distinct archetypes** under unified governance:

1. **Supabase-style platform mono** (`web/`, `supabase/`, `automations/`)
2. **Odoo-style ERP mono** (`odoo/addons/`, Python runtime, OCA-first)

**Goal:** Keep architectural boundaries **enforceable** while avoiding forced convergence to a single toolchain.

---

## Top-Level Directory Structure (SSOT)

```
.
├── .github/                      # CI workflows, templates, policies
├── odoo/                         # ERP runtime + addons (CE + OCA + ipai bridges)
├── supabase/                     # DB SSOT: schema, functions, policies, seeds, Edge Functions
├── web/                          # Next.js control plane + product web apps
├── automations/                  # n8n workflows, runbooks, audits, secret scanners
├── infra/                        # Cloudflare/DO/Vercel/IaC + drift detection
├── design/                       # tokens.json SSOT + extracted assets
├── agents/                       # Agent registry + skills + runbooks (repo-local)
├── docs/                         # Architecture + contracts + runbooks (human-facing)
├── scripts/                      # Repo-wide tooling (lint, checks, release, evidence)
└── spec/                         # Spec Kit bundles (spec/<slug>/{constitution,prd,plan,tasks}.md)
```

### Design Rationale

| Directory | Purpose | Toolchain | Owner Team |
|-----------|---------|-----------|------------|
| `odoo/` | ERP System of Record (SOR) | Python, Odoo CE 19, OCA modules | ERP/Backend |
| `supabase/` | Control plane SSOT, ops.* tables | PostgreSQL, Edge Functions (Deno) | Platform/DB |
| `web/` | Odoo.sh-equivalent control plane UI | Next.js, TypeScript, Tailwind | Frontend/Platform |
| `automations/` | Workflow automation as code | n8n JSON exports | DevOps/Automations |
| `infra/` | Infrastructure as Code + DNS SSOT | Terraform, Cloudflare, DigitalOcean | DevOps/Infra |
| `design/` | Design tokens SSOT | JSON (framework-agnostic) | Design/Frontend |

**Why this works:**
- Odoo stays pure (Python runtime + addons conventions intact)
- Supabase stays pure (migrations, RLS, Edge Functions)
- Control plane stays Next.js (platform UI + API gateway)
- No forced convergence to a single build tool or language

---

## Sub-Structure Standards

### 1. `odoo/` — ERP + OCA-First + Bridge-Only ipai_*

```
odoo/
├── addons/
│   ├── odoo/                     # Upstream Odoo CE (pinned submodule or vendored)
│   ├── oca/                      # OCA addons (pinned via submodules/vendor scripts)
│   └── ipai/                     # Integration bridge connectors ONLY (thin adapters)
├── config/
│   ├── dev/                      # Development environment config
│   ├── staging/                  # Staging environment config
│   └── prod/                     # Production environment config
├── docker/                       # Dockerfiles for dev/staging/prod
├── scripts/                      # Odoo-specific scripts
├── tests/                        # Odoo integration tests
├── docs/                         # Odoo-specific documentation
└── spec/                         # Optional: odoo-scoped specs
```

**Invariants (CI-enforced):**
- ✅ `addons/ipai/*` **must not** implement "EE parity modules" (only connector/bridge glue)
- ✅ EE parity lives in `addons/oca/*` or CE core
- ✅ No `<tree>` views: use `<list>` (Odoo 17+ convention)
- ✅ All ipai_* modules require `PARITY_CONNECTOR_JUSTIFICATION.md` if outside reserved categories:
  - Integration Bridge connectors (e.g. `ipai_slack_connector`, `ipai_auth_oidc`)
  - AI/MCP tools with no OCA equivalent
  - BIR compliance modules (Philippine-specific)
  - OCR/expense automation glue

---

### 2. `supabase/` — Control Plane SSOT (ops.*)

```
supabase/
├── migrations/                   # Database schema migrations (timestamped SQL)
├── functions/                    # Edge Functions (Deno TypeScript)
├── seed/                         # Seed data (dev/staging/test)
├── policies/                     # Optional: generated snapshots of RLS policies
└── README.md                     # How to apply, verify, rollback
```

**Invariants:**
- ✅ `ops.*` tables are canonical for control plane audit/state (`ops.platform_events`, `ops.runs`, `ops.artifacts`)
- ✅ Migrations **must be idempotent** or have strict ordering with checks
- ✅ No secrets in repo; `.env*` ignored; examples only (`.env.example`)
- ✅ RLS policies required for all client-accessible tables

**Control Plane Schema (Required):**
```sql
ops.builds           -- git SHA, dependencies hash, Docker image SHA256
ops.deployments      -- environment, deployed SHA, health checks, rollback SHA
ops.migrations       -- module versions, migration scripts, execution time
ops.platform_events  -- audit log for control plane actions
ops.runs             -- automation run history
ops.artifacts        -- evidence bundles and deployment artifacts
```

---

### 3. `web/` — Next.js Control Plane + Product Apps

```
web/
├── ai-control-plane/             # Next.js platform UI + API routes (proxy/gates)
│   ├── app/                      # Next.js App Router
│   ├── components/               # React components
│   ├── lib/                      # Utilities and API clients
│   └── public/                   # Static assets
├── apps/                         # Optional: separate Next/Vite apps if truly isolated
├── shared-ui/                    # Shared components/tokens consumers
└── docs/                         # Evidence bundles for web work (optional)
```

**Hard Boundary Rule:**
- ✅ Anything "**Odoo.sh-like**" (build logs, PR envs, promote, rollback, evidence) lives here
- ❌ Anything "**ERP workflow**" lives in Odoo native OWL/QWeb
- ✅ Next.js for control plane, Vite **only** for isolated micro-apps (marketing, POCs)

**Decision Matrix:**
| Feature | Frontend Stack | Location |
|---------|---------------|----------|
| ERP workflows (accounting, inventory, CRM) | Odoo native (OWL/QWeb) | `odoo/addons/ipai/*` |
| Odoo.sh control plane (builds, deploys) | Next.js | `web/ai-control-plane/` |
| Isolated prototypes, marketing sites | Vite (case-by-case) | `web/apps/*` |

---

### 4. `automations/` — n8n as Code

```
automations/
└── n8n/
    ├── workflows/                # JSON workflows (exported, normalized)
    ├── credentials/              # NEVER actual secrets; only models/templates
    ├── docs/                     # RUNBOOK.md, ODOO_CONNECTOR.md, CREDENTIALS_MODEL.md
    └── scripts/                  # Validation/normalization utilities
```

**Invariants:**
- ✅ CI secret scanner runs here (blocks hardcoded tokens/keys)
- ✅ Workflows must not contain hard-coded secrets
- ✅ Expressions like `={{ $env.X }}` are allowed (environment variable references)
- ✅ Credential references via credential IDs (not inline values)

---

### 5. `design/` — Design Tokens SSOT

```
design/
├── tokens/
│   └── tokens.json               # Single SSOT for design tokens
├── figma/
│   ├── exports/                  # Generated (gitignored unless intentional)
│   └── mappings/                 # Code↔Figma component mapping
└── README.md
```

**Invariants:**
- ✅ `tokens.json` is canonical; Odoo theme module **reads** tokens but doesn't **own** them
- ✅ Extracted assets are generated and either gitignored or versioned intentionally (explicit policy)
- ✅ Framework-agnostic format (consumable by Tailwind, MUI, Odoo, etc.)

---

## Data Flow Rules — What Talks to What

### ✅ Allowed Communication Patterns

```
Odoo (SOR) ↔ Supabase (SSOT ops + analytics)
    ↓                 ↓
Bridge connectors   Edge Functions
(ipai_*)           (Deno runtime)
    ↓                 ↓
n8n workflows ← → Next.js control plane
```

**Detailed Flows:**

1. **Odoo (SOR) ↔ Supabase (SSOT ops + analytics)**
   - Via **ipai_* bridge connectors** (thin adapters, no business logic)
   - Supabase stores **references** to Odoo entities (external_ids, hashes, timestamps)
   - Supabase stores **replicas** for analytics (read-only, never authoritative for SOR data)

2. **Next.js Control Plane** reads/writes:
   - `ops.*` tables only (audit, runs, events, artifacts)
   - Never writes directly to Odoo SOR domains (accounting, inventory, posted docs)

3. **n8n Workflows** trigger:
   - Odoo RPC endpoints (via connector)
   - Supabase Edge Functions / DB RPC (via service role in runtime, never stored)

### ❌ Forbidden Patterns

| Forbidden Pattern | Rationale | CI Gate |
|-------------------|-----------|---------|
| Next.js client directly writing privileged `ops.*` without gateway rules | RLS bypass risk | `check_supabase_rls.sh` |
| `ipai_*` implementing EE parity modules | Violates OCA-first + CE parity policy | `check_ipai_parity.sh` |
| Secrets in workflow JSON, `.env.local`, evidence bundles | Secret leakage | `check_n8n_workflow_secrets.sh` |
| Supabase becoming "shadow ledger" (authoritative accounting outside Odoo) | SOR/SSOT boundary violation | Architecture review |
| Odoo modules writing to `ops.*` without audit trail | Control plane integrity | Schema contract |

---

## SSOT/SOR Boundary (Non-Negotiable)

### Definitions

- **System of Record (SOR):** The authoritative system for legally auditable ERP transactions and accounting artifacts.
- **System of Truth (SSOT):** The authoritative system for control-plane truth: identity/authorization for non-Odoo apps, orchestration state, integration checkpoints, master-data overlays, analytics/AI layers, and governance evidence.

### Odoo is the SOR for:
- ✅ Accounting truth: invoices/bills, journal entries, payments, taxes, reconciliations
- ✅ ERP operational truth (final state): stock moves, POs/SOs (final), manufacturing orders
- ✅ Legal/audit artifacts: posted documents and final approvals that must match the ledger

**Rule:** Supabase may store **references** to Odoo SOR entities (ids, external_ids, hashes, timestamps) and **replicas** for analytics, but must not become authoritative for the above.

### Supabase is the SSOT for:
- ✅ **ops/control plane:** runs, run_events, job queues, retries/DLQ, idempotency keys, artifacts/evidence
- ✅ **Identity & access for non-Odoo surfaces:** portals, ops-console, agents, APIs (RLS-first)
- ✅ **Integration state:** cursors/checkpoints, mapping tables, sync configurations, webhook receipts
- ✅ **Master data overlays:** enrichment, canonical product/brand/category registries (when not owned by Odoo)
- ✅ **Analytics & AI layers:** gold/platinum views, embeddings, feature stores, insight artifacts

### Conflict Resolution Policy

1. Each entity has **exactly one owner system** (Odoo **OR** Supabase)
2. If owned by Odoo, Supabase **never "wins" conflicts**; conflicts become exceptions routed to review/repair
3. Write paths into Odoo are **restricted** to non-SOR domains (e.g., enrichment tags) and must be audited (`ops.runs` + `ops.artifacts`)

---

## CI Invariants (Enforceable Gates)

### 1. Spec Kit Presence & Drift

**Gate:** `.github/workflows/spec-kit-hygiene.yml`

**Checks:**
- If `/spec/<slug>/` touched → require all 4 files exist (`constitution.md`, `prd.md`, `plan.md`, `tasks.md`)
- Canonical paths enforced (no `docs/development/*` drift)
- DoD-style tasks required (`Owner:`, `Deliverable:`, `DoD:` markers)
- UI/manual steps labeled `Optional:` (automation-first)

### 2. Secrets & Workspace Artifact Hygiene

**Gate:** `.github/workflows/secret-scan.yml` + `.gitignore` enforcement

**Blocks:**
- `.env.local`, `.env.*.local` files
- `.cache/`, `_work/`, `artifacts/`, `sandbox/dev/.artifacts/` directories
- `design-tokens/.figma-*` files (gitignored unless intentional)

**Scans:**
- `automations/n8n/workflows/**/*.json` (hardcoded secrets)
- `web/**` (API keys, tokens in source)
- `supabase/**` (migration comments with leaked tokens)

**Script:** `scripts/ci/check_n8n_workflow_secrets.sh`

### 3. Odoo Policy Gates

**Gate:** `.github/workflows/odoo-hygiene.yml` (TODO: implement)

**Checks:**
- ❌ Forbid EE-parity logic in `addons/ipai/**` (allow only "connector-like" patterns)
- ✅ Enforce `<list>` over `<tree>` in Odoo 17+ view definitions
- ✅ Require `PARITY_CONNECTOR_JUSTIFICATION.md` for ipai_* modules outside reserved categories

**Script:** `scripts/ci/check_ipai_parity.sh` (TODO: implement)

### 4. Supabase Schema Contract

**Gate:** `.github/workflows/supabase-hygiene.yml` (TODO: implement)

**Checks:**
- ✅ `ops.*` schema tables required for control plane features
- ✅ Migrations naming convention (`YYYYMMDDHHMMSS_description.sql`)
- ✅ Idempotency check (basic lint for `CREATE IF NOT EXISTS`, `DROP IF EXISTS`)
- ✅ RLS policies present for all client-accessible tables

**Script:** `scripts/ci/check_supabase_schema.sh` (TODO: implement)

---

## Maintenance & Enforcement

**Single-maintainer repository:** No CODEOWNERS file. Domain boundaries and architectural invariants are enforced via CI policy gates only.

---

## Verification Checklist

Before merging changes that modify directory structure or cross-domain communication:

- [ ] Top-level directories match this contract (no new random roots)
- [ ] `odoo/`, `supabase/`, `web/`, `automations/`, `design/` boundaries are explicit
- [ ] README "Repo Map" points to this contract
- [ ] `.gitignore` blocks `.env.local` + workspace artifacts
- [ ] CI gates list is documented (even if some gates are "TODO")
- [ ] Data flow follows allowed patterns (no forbidden boundary crossings)
- [ ] SSOT/SOR boundaries are respected

---

## Evolution & Amendments

**Process:**
1. Propose amendment via GitHub Issue (label: `architecture`)
2. Update this document via PR
3. Update affected CI gates
4. Document changes in amendment log below

**Amendment Log:**
- 2026-02-20: Initial contract ratified
