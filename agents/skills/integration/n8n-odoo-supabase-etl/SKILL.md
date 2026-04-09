# Skill: Self-Hosted n8n → Supabase ETL → Iceberg → Odoo

## Metadata

| Field | Value |
|-------|-------|
| **id** | `n8n-odoo-supabase-etl` |
| **domain** | `integration` |
| **source** | https://n8n.io/integrations/odoo/ |
| **extracted** | 2026-03-15 |
| **applies_to** | automations, odoo, lakehouse, ops-platform |
| **tags** | n8n, odoo, supabase, etl, iceberg, parquet, medallion, adls, reverse-etl |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPERATIONAL LAYER                             │
│                                                                 │
│  Odoo CE 19 (SOR)          Supabase (SSOT)        n8n (Glue)   │
│  ┌──────────────┐         ┌──────────────┐       ┌───────────┐ │
│  │ account.move │         │ ops.runs     │       │ 31+ flows │ │
│  │ hr.expense   │◄───────►│ ops.events   │◄─────►│ webhooks  │ │
│  │ project.task │         │ ops.specs    │       │ cron jobs │ │
│  └──────┬───────┘         └──────┬───────┘       └───────────┘ │
│         │                        │                              │
└─────────┼────────────────────────┼──────────────────────────────┘
          │ Extract API            │ CDC / Batch
          ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAKE LAYER (ADLS Gen2)                  │
│                                                                 │
│  Bronze (Raw)        Silver (Cleaned)       Gold (Marts)        │
│  ┌──────────┐       ┌──────────┐          ┌──────────┐        │
│  │ Parquet  │──dbt──│ Parquet  │──dbt─────│ Parquet  │        │
│  │ (or Ice) │       │ (or Ice) │          │ (or Ice) │        │
│  └──────────┘       └──────────┘          └──────┬───┘        │
│                                                   │            │
└───────────────────────────────────────────────────┼────────────┘
                                                    │
┌───────────────────────────────────────────────────┼────────────┐
│                    CONSUMPTION LAYER               │            │
│                                                    ▼            │
│  Superset (BI)    Databricks (ML)    Reverse ETL → Odoo/Supa   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. n8n Odoo Integration

### Built-In Odoo Node

n8n provides a native Odoo node that uses XML-RPC to interact with any Odoo model.

| Capability | Details |
|-----------|---------|
| **Protocol** | XML-RPC (`/xmlrpc/2/common`, `/xmlrpc/2/object`) |
| **Auth** | URL + database + username + password |
| **Operations** | Create, Read, Update, Delete, Get All, Get Many |
| **Models** | Any Odoo model (dynamic — reads available models at runtime) |
| **Filters** | Domain filters `[['field', 'operator', 'value']]` |
| **Fields** | Select specific fields to return |
| **Pagination** | Offset + limit support |

### Credential Configuration

```
Name: Odoo API
Type: oAuth2 / API Key
Fields:
  - URL: https://erp.insightpulseai.com
  - Database: odoo
  - Username: (from Key Vault)
  - Password: (from Key Vault)
```

### Current IPAI Usage

| Pattern | What We Do Now | Recommendation |
|---------|---------------|----------------|
| HTTP Request node → XML-RPC | Manual JSON-RPC payloads | **Migrate to built-in Odoo node** |
| Hardcoded model names | Brittle, no validation | Use node's dynamic model discovery |
| Manual error handling | try/catch in code nodes | Use node's built-in retry + error output |

**Key workflows using Odoo XML-RPC today:**

| Workflow | File | Odoo Operations |
|----------|------|-----------------|
| Finance Close Orchestrator | `03-finance-close-orchestrator.json` | Read `account.move`, check close status |
| Finance PPM | `n8n_finance_ppm_workflow_odoo18.json` | Read `project.task` alerts |
| Invoice OCR → Odoo | `invoice_ocr_to_odoo.json` | Create `account.move` from OCR output |
| Odoo Reverse Mapper | `odoo_reverse_mapper.json` | Read + transform Odoo data |

---

## 2. Self-Hosted n8n on Azure

| Config | Value |
|--------|-------|
| **Endpoint** | `https://n8n.insightpulseai.com` |
| **Edge** | Azure Front Door (`ipai-fd-dev`) |
| **Runtime** | Docker Compose on ACA |
| **SSOT** | `odoo/infra/ssot/integrations/n8n.yaml` |
| **Credentials** | `odoo/automations/n8n/CREDENTIALS.md` |
| **Workflow count** | 31+ JSON files in `odoo/automations/n8n/workflows/` |

### Credential Security

- All credentials use `$credentials.<name>` references — never plaintext
- Secrets sourced from Azure Key Vault (`kv-ipai-dev`)
- Key credential refs: `OdooAPI`, `SupabaseIPAI`, `SlackBot`, `GitHubApp`
- n8n encryption key stored as env var (never committed)

---

## 3. n8n → Supabase Bridge

### Pattern

```
n8n workflow execution
    ↓
HTTP POST → Supabase REST API
    POST https://<supabase>/rest/v1/ops.runs
    Headers:
      Authorization: Bearer $credentials.SupabaseIPAI
      apikey: $credentials.SupabaseIPAI
      Content-Type: application/json
    Body:
      {
        "source": "n8n",
        "workflow_id": "{{$workflow.id}}",
        "execution_id": "{{$execution.id}}",
        "status": "completed",
        "payload": { ... },
        "idempotency_key": "n8n:workflow:{{$workflow.id}}:{{$execution.id}}"
      }
```

### Tables Used

| Table | Purpose | Access Pattern |
|-------|---------|----------------|
| `ops.runs` | Audit trail for all durable state mutations | Append-only INSERT |
| `ops.run_events` | Granular step-level events within a run | Append-only INSERT |
| `ops.platform_events` | System-level events (health, alerts) | Append-only INSERT |

### Boundary Rules (from SSOT)

- n8n NEVER writes directly to Odoo tables in Supabase
- n8n NEVER reads/writes to `odoo` (prod) database without explicit approval
- All Supabase writes go through REST API (never direct SQL)
- Every mutation logged to `ops.runs` for audit trail

---

## 4. ETL: Odoo → ADLS Bronze

**Status: PLANNED — not yet deployed**

**SSOT**: `odoo/ssot/integrations/adls-etl-reverse-etl.yaml`

### Defined Flows

| Flow | Odoo Model | Method | Cadence | Priority |
|------|-----------|--------|---------|----------|
| Journal entries | `account.move` + `account.move.line` | Extract API | Hourly | P0 |
| Projects | `project.project` + `project.task` | JSON-2 API | Daily | P1 |
| Employees | `hr.employee` | JSON-2 API | Weekly | P2 |
| BIR filings | `ipai.bir.*` | Extract API | Daily | P1 |
| Analytic accounts | `account.analytic.account` + `account.analytic.line` | Extract API | Daily | P1 |

### Extraction Methods

| Method | When to Use | Pros | Cons |
|--------|------------|------|------|
| **Extract API** | Structured ERP data, large volumes | Efficient, paginated, incremental | Requires Odoo 18 API |
| **JSON-2 API** | Simple reads, small datasets | Easy to implement | No incremental support |
| **DB Replica** | Full table access, complex joins | Most flexible | Requires read replica setup |

### Landing Format

```
adls://ipai-lakehouse/bronze/odoo/
├── account_move/
│   ├── dt=2026-03-15/
│   │   └── part-00000.parquet
│   └── _metadata.json
├── account_move_line/
│   └── dt=2026-03-15/
│       └── part-00000.parquet
└── ...
```

---

## 5. ETL: Supabase → ADLS Bronze

**Status: PLANNED — not yet deployed**

### Defined Flows

| Flow | Supabase Table | Method | Cadence |
|------|---------------|--------|---------|
| Auth users | `auth.users` | Incremental batch | Daily |
| Platform events | `ops.platform_events` | CDC (logical replication) | Hourly |
| Run audit | `ops.runs` + `ops.run_events` | Incremental batch | Hourly |
| Specs + tasks | `ops.specs` + `ops.spec_tasks` | Incremental batch | Daily |
| Incidents | `ops.incidents` | Incremental batch | Hourly |

### CDC Options

| Method | How | Complexity | Latency |
|--------|-----|-----------|---------|
| Logical replication | PostgreSQL WAL → Debezium/Airbyte | High | Real-time |
| Incremental batch | Query `WHERE updated_at > last_sync` | Low | Minutes |
| Supabase Realtime | WebSocket → n8n → ADLS | Medium | Seconds |

**Recommendation**: Start with incremental batch (simplest). Upgrade to CDC when latency requirements justify.

---

## 6. Lakehouse: Bronze → Silver → Gold

**Status: PLANNED — dbt project not deployed**

**SSOT**: `odoo/odoo/docs/analytics/LAKEHOUSE_PLAN.md`

### Medallion Architecture

| Layer | Purpose | Transform | Format |
|-------|---------|-----------|--------|
| **Bronze** | Raw ingested data, immutable | None (land as-is) | Parquet |
| **Silver** | Cleaned, deduplicated, typed | dbt models | Parquet |
| **Gold** | Business marts, KPIs, aggregates | dbt marts | Parquet |
| **Platinum** | ML features, embeddings | Databricks | Parquet/Delta |

### Compute Stack Options

| Option | Components | Cost | When |
|--------|-----------|------|------|
| **A: Lightweight** | dbt-core + DuckDB + Superset | Low | < 10M rows, dev/staging |
| **B: Databricks** | Databricks + Unity Catalog + dbt | Medium | Production, ML workloads |
| **C: Azure Synapse** | Synapse Serverless + dbt | Medium | Azure-native preference |

**Current recommendation**: Option A for now, Option B when ML workloads materialize.

### Sample dbt Models

```sql
-- silver/stg_account_move.sql
SELECT
    id,
    name AS move_name,
    date AS move_date,
    partner_id,
    journal_id,
    amount_total,
    state,
    _extracted_at
FROM {{ source('bronze', 'account_move') }}
WHERE state != 'cancel'

-- gold/fct_monthly_revenue.sql
SELECT
    DATE_TRUNC('month', move_date) AS month,
    SUM(amount_total) AS total_revenue,
    COUNT(*) AS invoice_count
FROM {{ ref('stg_account_move') }}
WHERE journal_id IN (SELECT id FROM {{ ref('dim_sales_journals') }})
GROUP BY 1
```

---

## 7. Iceberg Decision

**Status: PENDING — Parquet is accepted baseline**

| Feature | Parquet | Apache Iceberg |
|---------|---------|----------------|
| Read performance | Excellent | Excellent |
| Write performance | Good | Good (with compaction) |
| Schema evolution | Manual (new files) | Native (ALTER TABLE) |
| Time travel | Not supported | Native (snapshot-based) |
| ACID transactions | Not supported | Full ACID |
| Partition evolution | Requires rewrite | In-place |
| Tooling support | Universal | Growing (Spark, Trino, Databricks) |
| Operational complexity | Minimal | Moderate (catalog, compaction) |

### Decision Framework

```
IF total_data_volume < 10M rows
   AND no time-travel requirement
   AND no concurrent writers
   → Use Parquet (simpler ops, universal tooling)

IF total_data_volume > 10M rows
   OR need time-travel (audit, compliance, rollback)
   OR concurrent ETL writers
   OR schema evolves frequently
   → Migrate to Iceberg
```

### Migration Path (Parquet → Iceberg)

1. Deploy Iceberg catalog (Nessie or AWS Glue compatible)
2. Convert Bronze tables: `CREATE TABLE ... USING iceberg AS SELECT * FROM parquet_table`
3. Update dbt to write Iceberg format
4. Enable time-travel queries for compliance audit
5. Update Superset to query via Trino/Spark (Iceberg-aware)

**Current recommendation**: Stay Parquet. Revisit Iceberg at Phase 2 (post-ETL deployment).

---

## 8. Reverse ETL: ADLS → Supabase / Odoo

**Status: PLANNED — guardrails defined, orchestrator not chosen**

**SSOT**: `odoo/spec/adls-etl-reverse-etl/constitution.md`

### Approved Writeback Types

| Type | Target | Example | Guardrails |
|------|--------|---------|-----------|
| `scoring_writeback` | Supabase user profiles | ML risk scores | Append-only, versioned |
| `enrichment_writeback` | Odoo analytic accounts | Budget forecasts | Draft status only |
| `draft_record_creation` | Odoo `hr.expense` (draft) | OCR-extracted expenses | Always draft, never post |
| `read_model_refresh` | Supabase materialized views | Dashboard summaries | Truncate + reload |

### Rules (from Constitution)

1. **Never UPDATE** production Odoo records directly — always create drafts
2. **Append-only audit** — every writeback logged to `ops.runs`
3. **Idempotent** — re-running a writeback produces same result
4. **Schema-validated** — Pydantic models validate before write
5. **Rollback-capable** — every writeback has a compensating action

### Orchestrator Options

| Option | Pros | Cons | Fit |
|--------|------|------|-----|
| **n8n** (existing) | Already deployed, visual | Limited data volume handling | Simple flows |
| **Azure Functions** | Serverless, event-driven | Cold starts, debugging | Medium flows |
| **Azure Data Factory** | Enterprise ETL, monitoring | Complex, expensive | Complex flows |
| **Databricks Jobs** | ML integration, Spark | Requires workspace | ML-dependent flows |

**Recommendation**: n8n for simple reverse ETL (draft creation, notifications). Azure Functions for scheduled batch (scoring, refresh). Databricks only when ML models are in production.

---

## 9. Live Workflow Inventory

### Production Workflows (31+)

| Category | Workflows | Trigger | Integration |
|----------|----------|---------|-------------|
| **Health & Ops** | `01-health-check` | Cron (5m) | All services |
| **Git & CI** | `02-git-operations-hub`, `github-*` | Webhook | GitHub |
| **Finance** | `03-finance-close-orchestrator`, `finance_closing_automation`, `ppm_monthly_close` | Cron + webhook | Odoo, Slack |
| **BIR Tax** | `04-bir-compliance`, `bir_deadline_reminder`, `bir_overdue_nudge` | Cron | Odoo, Slack |
| **Plane PM** | `plane-odoo-github-sync`, `ppm-clarity-*` | Webhook | Plane, Odoo, GitHub |
| **Auth** | `05-github-oauth-callback` | Webhook | GitHub |
| **OCR** | `invoice_ocr_to_odoo`, `expense_receipt_capture` | Webhook | ADE/DI, Odoo |
| **Deploy** | `deployment-notify`, `github-deploy-trigger` | Webhook | GitHub, Slack |
| **Integration** | `sentry-plane-sync`, `chatops-hotfix` | Webhook | Sentry, Slack |
| **Cache** | `superset-cache-refresh` | Cron | Superset |

### Workflow Naming Convention

```
{nn}-{descriptive-name}.json        # Core numbered workflows
{domain}_{action}_{target}.json     # Domain-specific
{platform}-{action}.json            # Platform integration
```

---

## 10. Gaps & Next Steps

### Current State Summary

| Component | Status | Blocking? |
|-----------|--------|-----------|
| n8n self-hosted | **Active** (31+ workflows) | No |
| n8n → Odoo (XML-RPC) | **Active** (HTTP nodes) | No (works, not optimal) |
| n8n → Supabase (HTTP) | **Active** (REST API) | No (works, not optimal) |
| Odoo → ADLS ETL | **PLANNED** (SSOT defined) | Yes — no data flows |
| Supabase → ADLS ETL | **PLANNED** (SSOT defined) | Yes — no data flows |
| dbt transforms | **PLANNED** (samples exist) | Yes — no project deployed |
| Iceberg format | **PENDING** (Parquet accepted) | No — defer decision |
| Reverse ETL | **PLANNED** (guardrails defined) | No — do after forward ETL |
| Superset dashboards | **Active** (basic views) | No |

### Priority Execution Order

1. **Deploy first ETL flow**: `account.move` → ADLS Bronze (Parquet)
   - Tool: n8n scheduled workflow → Odoo Extract API → Azure Blob upload
   - Validates: extraction, landing, schema

2. **Deploy dbt project**: Bronze → Silver for `account.move`
   - Tool: dbt-core with DuckDB (lightweight)
   - Validates: transformation pipeline

3. **Migrate n8n Odoo nodes**: HTTP → built-in Odoo node
   - Benefit: Type safety, dynamic model discovery, built-in retry

4. **Deploy Supabase CDC**: `ops.platform_events` → ADLS Bronze
   - Tool: Incremental batch query via n8n scheduled workflow
   - Validates: Supabase → lake pipeline

5. **Build Gold marts**: Monthly revenue, expense summary, BIR tax summary
   - Tool: dbt marts → Superset dashboards
   - Validates: end-to-end value delivery

6. **Decide Iceberg**: Evaluate volume + requirements after 30 days of data
   - Trigger: >10M rows or audit time-travel need

---

## Related Skills

- [azure-document-intelligence](../../azure-foundry/document-intelligence/SKILL.md) — OCR for invoice/receipt extraction
- [landing-ai-ade](../../inference/landing-ai-ade/SKILL.md) — Agentic document extraction for novel documents
- [odoo18-expenses](../../odoo/odoo18-expenses/SKILL.md) — Expense workflow + automation pipelines
- [odoo18-accounting-map](../../odoo/odoo18-accounting-map/SKILL.md) — Full accounting feature map
- [sap-concur-parity](../../industries/sap-concur-parity/SKILL.md) — Concur replacement scorecard
- [agentic-sdlc-msft-pattern](../../sdlc/agentic-sdlc-msft-pattern/SKILL.md) — SDLC feedback loop

## SSOT References

| Document | Path (in `odoo/` repo) |
|----------|------------------------|
| ETL flow definitions | `ssot/integrations/adls-etl-reverse-etl.yaml` |
| ETL constitution | `spec/adls-etl-reverse-etl/constitution.md` |
| ETL PRD | `spec/adls-etl-reverse-etl/prd.md` |
| ETL plan | `spec/adls-etl-reverse-etl/plan.md` |
| n8n integration SSOT | `infra/ssot/integrations/n8n.yaml` |
| Credential index | `automations/n8n/CREDENTIALS.md` |
| Lakehouse plan | `odoo/docs/analytics/LAKEHOUSE_PLAN.md` |
