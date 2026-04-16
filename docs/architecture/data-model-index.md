# IPAI Data Model — Master Index

> **Locked:** 2026-04-16
> **Authority:** this file is the single entry point for IPAI's data model across all 8 components.
> **Companion to:** [`canonical-platform-architecture.md`](./canonical-platform-architecture.md) §1 (8-component architecture).
>
> **Rule:** if you're looking for "where is X modeled", start here. If the answer is "planned — no schema yet", see §5.

---

## 1. Component → data-model file map

Maps the 8 canonical components to their data-model artifacts.

| # | Component (per canonical arch) | Data-model file(s) |
|---|---|---|
| 1.1 | Odoo 18 CE + OCA | [`data-model-erd.md`](./data-model-erd.md) §1 (schema), [`ODOO_CANONICAL_SCHEMA.dbml`](../data-model/ODOO_CANONICAL_SCHEMA.dbml), [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md), [`d365-to-odoo-mapping.md`](../research/d365-to-odoo-mapping.md), [`d365-data-model-inventory.md`](../research/d365-data-model-inventory.md) |
| 1.2 | PostgreSQL Flex (`pg-ipai-odoo`) | [`data-model-erd.md`](./data-model-erd.md) §0–2 (DBMS + 3 schemas: `public` / `ops` / `platform`) |
| 1.3 | Azure AI Foundry (`ipai-copilot-resource`) | §3 inline below — Foundry is stateless; deployments + connections documented via `ssot/ai/` |
| 1.4 | MAF Agent Platform (6 agents) | [`data-model-erd.md`](./data-model-erd.md) §2 `ops` schema (agent runs + events); §3 inline below for Cosmos session state |
| 1.5 | Databricks (`dbw-ipai-dev`) | §4 inline below — UC `ppm` catalog tables; DLT pipeline definitions live at [`infra/databricks/`](../../infra/databricks/) |
| 1.6 | Unity Catalog | §4 inline below — catalog/schema/table RBAC + tags |
| 1.7 | Microsoft Fabric (`fcipaidev`) | §5 inline below — mirror source tables + Fabric Data Agent surface |
| 1.8 | ADLS Gen2 (`stipaidevlake`) | [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md), [`cdm-odoo-mapping.md`](./cdm-odoo-mapping.md), [`cdm-entity-map.yaml`](../../platform/contracts/cdm-entity-map.yaml) |

**Cross-plane:** [`data-model-erd.md`](./data-model-erd.md) §4 (data flow) + §6 inline below.

---

## 2. File catalog — 8 data-model artifacts, 3,515 lines

| File | Lines | Format | Role |
|---|---|---|---|
| [`data-model-erd.md`](./data-model-erd.md) | 709 | Markdown | Canonical ERD — PG schemas, tables, multitenancy, access rules |
| [`ODOO_CANONICAL_SCHEMA.dbml`](../data-model/ODOO_CANONICAL_SCHEMA.dbml) | 664 | DBML | Renderable Odoo schema (dbdiagram.io) |
| [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) | 510 | Markdown | D365 OData entity → Odoo ORM mapping |
| [`cdm-entity-map.yaml`](../../platform/contracts/cdm-entity-map.yaml) | 438 | YAML (machine-readable) | CDM entity ↔ Odoo model contract; consumed by DLT pipelines |
| [`d365-to-odoo-mapping.md`](../research/d365-to-odoo-mapping.md) | 382 | Markdown | D365 Finance + Project Ops → Odoo CE+OCA+`ipai_*` mapping |
| [`d365-data-model-inventory.md`](../research/d365-data-model-inventory.md) | 284 | Markdown | D365 entity catalog for displacement tracking |
| [`cdm-odoo-mapping.md`](./cdm-odoo-mapping.md) | 273 | Markdown | CDM ↔ Odoo narrative mapping (companion to YAML) |
| [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md) | 255 | Markdown | PG → ADLS CDM bridge (Bronze/Silver/Gold) |

---

## 3. Component 1.3 + 1.4 — Foundry + MAF Agent Platform data shape

### 3.1 Foundry `ipai-copilot-resource`

Foundry itself is **stateless**. No IPAI-owned data persists inside Foundry. What is modeled:

- **Model deployments** — declared in `ssot/ai/models.yaml` (reflects `az cognitiveservices account deployment list` state)
- **Connections** — declared in `ssot/ai/connections.yaml`
- **Agent definitions** — declared in `ssot/ai/agents.yaml`

These are *infrastructure state*, not data-plane. They show up in `ssot/` not `docs/architecture/`.

### 3.2 MAF Agent Platform — state split

Per [`canonical-platform-architecture.md`](./canonical-platform-architecture.md) §5 decision #7:

```
Agent session state       = cosmos-ipai-dev (Cosmos DB)
Agent audit trail         = pg-ipai-odoo.platform.ops.run_events
Two stores, two purposes.
```

**Cosmos DB `cosmos-ipai-dev` container layout (proposed — not yet deployed):**

| Container | Partition key | TTL | Contents |
|---|---|---|---|
| `sessions` | `/tenant_id` | 7 days sliding | Active user-agent sessions: conversation turns, scratchpad state, working memory |
| `tool_calls` | `/session_id` | 7 days sliding | Tool-call traces tied to a session (input, output, latency) for mid-session replay |
| `artifacts` | `/session_id` | 24 hours | Ephemeral artifacts generated mid-session (drafts, renderings) before persist-to-Odoo |

**Rule:** Cosmos is the *ephemeral* plane. Nothing load-bearing to audit or truth lives there. Anything that must survive session expiry gets written to Odoo (truth) or `platform.ops.*` (audit) before session end.

**PG `platform.ops.*` schema** (detailed in [`data-model-erd.md`](./data-model-erd.md) §2):

```sql
platform.ops.runs          -- one row per agent invocation (run_id, agent_id, tenant_id, started_at, ended_at, status)
platform.ops.run_events    -- append-only event log per run (input, tool call, tool response, output, errors)
platform.ops.tool_catalog  -- allowlist of tools per agent
platform.ops.feature_flags -- per-tenant runtime toggles
platform.ops.tenants       -- tenant registry (used by public schema company_id FK)
```

---

## 4. Component 1.5 + 1.6 — Databricks + Unity Catalog

### 4.1 UC catalog structure

Per [`databricks-ipai-grounded.md`](../skills/databricks-ipai-grounded.md):

```
ppm                              ← catalog (one per env in target state: ppm-dev, ppm-stg, ppm-prod)
├── bronze                       ← raw Odoo exports, minimally transformed
├── silver                       ← cleaned, type-conformed, joined
├── gold                         ← domain aggregates (the consumer layer)
├── metrics                      ← (planned) pre-computed metric tables for dashboards
└── features                     ← (planned) ML feature store
```

### 4.2 Gold-layer tables (planned — not yet populated)

These are the tables that business users + Power BI + Fabric mirror will read. Names locked here so downstream consumers can reference before tables exist.

| Table | Source (Bronze → Silver) | Grain | Consumers |
|---|---|---|---|
| `ppm.gold.finance_gl_trial_balance` | `account.move.line` | account × period × company | CFO dashboard, close agent |
| `ppm.gold.finance_ap_aging` | `account.move` where `move_type='in_invoice'` | vendor × aging bucket × company | AP dashboard, payment planning |
| `ppm.gold.finance_ar_aging` | `account.move` where `move_type='out_invoice'` | customer × aging bucket × company | AR collections agent |
| `ppm.gold.finance_cash_position` | `account.move.line` on liquidity accounts | day × account × company | Treasury dashboard |
| `ppm.gold.ops_project_burn` | `project.task` + `account.analytic.line` | project × week | PPM dashboard, project manager |
| `ppm.gold.ops_agent_run_summary` | `platform.ops.runs` + `run_events` | day × agent × tenant × outcome | Ops dashboard, Pulser QA |
| `ppm.gold.compliance_bir_filing_status` | `ipai.bir.*` models | filing × period × form-type | Tax Guru dashboard, compliance agent |

### 4.3 Tag contract on UC objects

Every `ppm.*.*` table MUST carry tags matching the mandatory tag set per [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml): `owner`, `sensitivity`, `tenant_scope`, `freshness_sla`, `source_repo`. Tags enforced by Databricks Asset Bundle templates.

---

## 5. Component 1.7 — Fabric Mirror source tables

Per [`fabric-mirroring-target-state.md`](./fabric-mirroring-target-state.md) §2: Fabric Database Mirroring from PG is **GA** for PG Flex.

### 5.1 Mirror scope — Phase 1 tables

Starting narrow — only operational truth, not derived data:

| PG table | Why mirrored | Consumers |
|---|---|---|
| `public.account_move` | Invoice/journal header — operational truth of every financial transaction | Power BI Direct Lake, Fabric Data Agent |
| `public.account_move_line` | Journal lines — enables GL analysis | Same |
| `public.account_payment` | Payment events | Same |
| `public.account_bank_statement_line` | Bank statement truth | Bank-recon agent, finance dashboards |
| `public.res_partner` | Master data for customer/vendor | Joined analytics |
| `public.res_company` | Multitenancy boundary | Tenant-aware dashboards |
| `public.project_project` + `project.task` | PPM analytics | PPM dashboard |

### 5.2 What is NOT mirrored (and why)

- `ops.*` and `platform.*` schemas — these are agent-plane operational state; they land in Databricks via Lakehouse Federation, not Fabric mirror. Double-mirror is forbidden (per `canonical-platform-architecture.md` §3.4).
- Odoo `ir.*` tables (Odoo internals) — no analytics value.
- Audit log entries that already flow to `platform.ops.run_events` — agent events are Databricks-side, not Fabric-mirrored.

### 5.3 Fabric Data Agent surface

Per `canonical-platform-architecture.md` §1.7, Fabric exposes a **Fabric Data Agent** endpoint so M365 Copilot can query Odoo data via Fabric without touching PG. The data agent reads the Phase-1 mirror + UC `ppm.gold.*` via OneLake shortcuts.

---

## 6. Cross-plane data flow — entity-level

The authoritative flow per `canonical-platform-architecture.md` §3, at entity granularity:

### 6.1 Write path — user action to durable truth

```
User action on Odoo UI / MAF agent tool call via ipai-odoo-mcp
      │
      ▼
Odoo ORM (public.account_move, public.res_partner, public.project_task, etc.)
      │  (triggers + constraints + Odoo business rules)
      ▼
pg-ipai-odoo.public.<table>  ← SoR row persisted
      │
      │  (concurrent audit write)
      ▼
pg-ipai-odoo.platform.ops.runs / run_events  ← audit row written before session end
      │
      │  (Fabric Database Mirroring, ~15s cadence, Phase-1 tables only)
      ▼
Fabric OneLake Delta (mirrored source tables)
```

### 6.2 Analytics path — truth to consumable insight

```
pg-ipai-odoo.public.*  ──(Databricks Lakehouse Federation, zero-copy read)──▶ Databricks DLT
                                                                                    │
                                                                                    ▼
                                                                    ADLS stipaidevlake/bronze/*
                                                                                    │
                                                                                    ▼
                                                                    ADLS stipaidevlake/silver/*
                                                                                    │
                                                                                    ▼
                                                                    ADLS stipaidevlake/gold/*
                                                                                    │
                                                                          (UC registration + RLS/CLS)
                                                                                    │
                                                                                    ▼
                                                                        Unity Catalog ppm.gold.*
                                                                                    │
                                                               ┌────────────────────┴────────────────────┐
                                                               ▼                                          ▼
                                                  Fabric (OneLake shortcut)              Power BI (Direct Lake via UC)
                                                               │
                                                               ▼
                                                  Fabric Data Agent (for M365 Copilot)
```

### 6.3 Agent path — user question to action

```
User question via Teams/Web/Copilot
      │
      ▼
Pulser router agent (ACA)
      │  consults ssot/ai/agents.yaml for routing policy
      ▼
Specialist agent (tax-guru / bank-recon / ap-invoice / doc-intel / finance-close) — on ACA
      │  reads session state from cosmos-ipai-dev.sessions (if mid-conversation)
      │
      ├──▶ Foundry (ipai-copilot-resource) for inference  [gpt-4.1 today]
      │
      ├──▶ ipai-odoo-mcp (canonical Odoo tool path) for CRUD on public.* models
      │         │
      │         ▼
      │      pg-ipai-odoo.public.*  (mutation goes through Odoo business rules)
      │
      └──▶ writes run_event row to pg-ipai-odoo.platform.ops.run_events
```

---

## 7. Open gaps (as of 2026-04-16)

Tracked here to prevent future "I thought this was documented":

| Gap | Current status | Owner | Deadline |
|---|---|---|---|
| `cosmos-ipai-dev` not yet deployed | Documented in this doc §3.2 as proposed shape; schema-ready when deployed | platform | Deploy before first MAF agent hits production |
| UC `ppm.gold.*` tables not yet populated | Schema names + grains locked in §4.2; DLT pipelines pending | data | Wave-2 Finance (R2 target 2026-07-14) |
| Fabric mirror not yet wired | Source table list locked in §5.1; Fabric capacity trial expires ~2026-05-20 | data | F-SKU procurement gate 2026-05-01 |
| `ssot/ai/agents.yaml` + `models.yaml` + `connections.yaml` not yet populated | Referenced in §3.1 but not yet written | platform | When 715-123420 deploy blocker clears |
| Frontier model deployments (gpt-5.4, o3-pro, Sora 2, gpt-image-1.5) | Approved + quota granted; deploy fails with `715-123420` — MS-acknowledged bug per [microsoft/microsoft-foundry-for-vscode#515](https://github.com/microsoft/microsoft-foundry-for-vscode/issues/515) | ops | Support ticket pending |

---

## 8. Mutation rules (what changes where)

Non-negotiable:

1. **Odoo schema (`public.*`)** mutates ONLY via Odoo migrations (`addons/<module>/migrations/`) or the ORM at runtime. No ad-hoc DDL.
2. **`ops.*` and `platform.*`** mutate via `agent-platform/migrations/` or `migrations/odoo/`. Append-only where possible.
3. **UC `ppm.*.*`** tables mutate via Databricks Asset Bundle deploys from `infra/databricks/`. No portal clicks.
4. **CDM entity map** (`platform/contracts/cdm-entity-map.yaml`) is PR-only; code changes consuming it (DLT pipelines) must not precede the YAML update.
5. **Fabric Mirror + UC shortcut configs** committed as IaC under `infra/fabric/` when we adopt `microsoft/unified-data-foundation` — see #753.

---

## 9. References

Internal (all linked above):
- [`canonical-platform-architecture.md`](./canonical-platform-architecture.md) — 8-component architecture
- [`data-model-erd.md`](./data-model-erd.md) — canonical ERD
- [`fabric-mirroring-target-state.md`](./fabric-mirroring-target-state.md)
- [`databricks-one-and-workspace-operating-model.md`](./databricks-one-and-workspace-operating-model.md)
- [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md)
- [`cdm-odoo-mapping.md`](./cdm-odoo-mapping.md)
- [`cdm-entity-map.yaml`](../../platform/contracts/cdm-entity-map.yaml)
- [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md)
- [`d365-to-odoo-mapping.md`](../research/d365-to-odoo-mapping.md)
- [`d365-data-model-inventory.md`](../research/d365-data-model-inventory.md)
- [`ODOO_CANONICAL_SCHEMA.dbml`](../data-model/ODOO_CANONICAL_SCHEMA.dbml)

External (Microsoft Learn):
- [Common Data Model folder format](https://learn.microsoft.com/common-data-model/data-lake)
- [Unity Catalog](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/)
- [Fabric Database Mirroring from Azure Postgres Flex](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql)

---

*Last updated: 2026-04-16*
