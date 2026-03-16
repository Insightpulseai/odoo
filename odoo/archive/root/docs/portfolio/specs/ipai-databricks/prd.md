# IPAI Databricks – Product Requirements Document (PRD)

## 1. Overview

**Product Name:** IPAI Databricks
**Type:** Self-hosted Data & AI Lakehouse Platform
**Objective:** Provide Databricks-style capabilities (lakehouse, data engineering, apps, AI governance) using:
- Supabase (Postgres, Storage, Edge Functions, MCP)
- DigitalOcean (compute, managed Postgres / Spaces)
- Vercel (Next.js apps, AI Gateway, Sandbox)
- Odoo CE + OCA (ERP system of record)
- Pulser / MCP / n8n for agentic workflows and orchestration.

The platform is the "IPAI Data Intelligence Layer" that:
- Unifies Odoo CE, SaaS apps, operational DBs, files, events, and warehouses.
- Provides a governed, RLS-enforced lakehouse.
- Exposes interactive apps and AI agents tightly coupled to this data.

---

## 2. Goals & Non-Goals

### 2.1 Goals

1. **Lakehouse Core (Supabase-based)**
   - Implement bronze/silver/gold/platinum schemas for IPAI workloads (ERP, finance, ops, marketing, retail, creative effectiveness).
   - Provide unified catalog of:
     - Tables, views, materialized views
     - Data products (semantic models)
     - AI feature sets (vector embeddings, feature tables).

2. **Data Engineering & Pipelines**
   - Define a standard pattern for replication/ETL:
     - Odoo CE → Lakehouse
     - GitHub → Lakehouse
     - Files (CSV, Parquet, JSON) → Lakehouse
     - Events (webhooks, logs, metrics) → Lakehouse
     - Databases & Warehouses (Postgres, MySQL, BigQuery, Redshift-style) → Lakehouse
   - Implement IPAI Connector Framework to mirror Fivetran's:
     - Configurable sources, schemas, sync modes (full, incremental, CDC-style).

3. **Apps Platform (Databricks Apps Analog)**
   - Provide an "IPAI Apps" framework using Next.js (Vercel) with:
     - App registration in Supabase.
     - Standard runtime contract (auth, data access, logging, feature flags).
     - Example apps:
       - Finance & Ops Command Center
       - Odoo Health & Reconciliation
       - Data Quality Monitor
       - AI BI Genie-style dashboards.

4. **AI / Agent Governance**
   - Register each IPAI agent (Pulser, Claude, Gemini, internal agents) as:
     - A first-class entity in the catalog with:
       - Allowed data scopes
       - Allowed actions (read, transform, write, schedule)
       - Logging and audit requirements.
   - Integrate:
     - Supabase MCP server
     - Vercel AI Gateway (optional)
     - n8n flows for orchestration.

5. **Security, Compliance & Observability**
   - Use Supabase RLS + policies to protect all data access.
   - Provide observability:
     - Logs, traces, metrics for connectors, jobs, apps, agents.
   - Support financial-grade security and audit trails for:
     - ERP finance
     - Retail/marketing datasets
     - Internal/agency operations.

6. **Spec-to-Code & CI Governance**
   - All IPAI Databricks features must:
     - Be described in Spec Kit (constitution, PRD, plan, tasks).
     - Pass CI quality gates before merge:
       - Lint, tests, security scan, migration checks, docs presence.

### 2.2 Non-Goals

- Implementing proprietary Databricks features 1:1 (e.g., Unity Catalog internals).
- Providing a hosted SaaS for external customers (this is an internal platform, multi-tenant but self-hosted).
- Re-creating Fivetran as a commercial product; focus is on **IPAI connectors** with similar behavior for internal usage.
- Replacing Superset/Power BI/Tableau; rather, IPAI Databricks provides data and APIs these tools can consume.

---

## 3. Users & Use Cases

### 3.1 Primary Users

1. **Platform Admin / Data Platform Owner**
   - Manages infrastructure, Supabase, DO, Vercel, Odoo.
   - Curates allowed connectors and agents.

2. **Data Engineer / Analytics Engineer**
   - Builds connectors, transformations, and semantic models.
   - Ensures pipelines are reliable, cost-efficient, and observable.

3. **BI Developer / Analyst**
   - Consumes `gold_*` and `platinum_*` views.
   - Builds dashboards (Scout, CES, Superset, Power BI, Tableau).

4. **AI Engineer / Agent Orchestrator**
   - Configures agents (Pulser, Claude, MCP tools).
   - Connects agents to data products via MCP and Supabase.

5. **Business Stakeholders (Finance, Ops, Creative, Retail)**
   - Use IPAI apps and dashboards to:
     - View KPIs and trends.
     - Trigger workflows (approvals, reconciliations, what-if analysis).

### 3.2 Representative Use Cases

1. **ERP → Lakehouse**
   - Odoo CE invoices, journal entries, vendors, projects replicated into bronze → silver → gold tables.
   - Finance dashboards and AI reconciliation agents run on `gold_finance_*` views.

2. **GitHub & CI Telemetry**
   - GitHub events and repo metadata replicated into lakehouse.
   - IPAI "DevOps Health" app visualizes:
     - Spec Kit compliance
     - CI status
     - Deployment frequency and MTTR.

3. **Retail / Marketing Intelligence**
   - Transactions, campaigns, creative assets ingested from CSV/files, Supabase, or Odoo.
   - AI agents surface insights and recommendations for trade, promo, and creative effectiveness.

4. **Connector-Style Ingestion**
   - A new SaaS (e.g., Figma, Slack, HubSpot, etc.) is added:
     - Create `ipai_connector_<source>` function/workflow.
     - Register in catalog.
     - Configure schedule and schema mapping.

---

## 4. Architecture Overview

### 4.1 High-Level Components

1. **Data Lakehouse Core (Supabase)**
   - **Postgres schemas:**
     - `ipai_bronze_*` – raw ingested data (Odoo, GitHub, etc.).
     - `ipai_silver_*` – cleaned, normalized models.
     - `ipai_gold_*` – analytic views, aggregated metrics.
     - `ipai_platinum_*` – ML features, AI-ready vectors, scenario models.
   - **Object Storage:**
     - Supabase storage and/or DO Spaces for blobs (files, images, PDFs, audio, video, parquet).

2. **Connector & Pipeline Layer (IPAI Connector Framework)**
   - IPAI connectors are implemented as:
     - Supabase Edge Functions
     - n8n workflows
     - DO jobs when heavy compute is required
   - Standard contract:
     - `connector_config` table defines:
       - source_type (odoo, github, file, db, warehouse, figma, mcp, mail, etc.)
       - auth parameters (via Vault)
       - schedule
       - observed schemas (source, target)
     - `connector_run` table records:
       - start/end time
       - success/failure
       - row counts
       - cost/time.

3. **Transformation & Semantic Layer**
   - Transformations implemented via:
     - SQL scripts, views, materialized views in Supabase migrations.
     - Optional dbt-style patterns if needed, but stored and executed through Supabase.
   - Semantic models:
     - `ipai_semantic_model` table for:
       - dataset name
       - grain
       - measures and dimensions
       - RLS policy references.

4. **Apps Platform (Next.js on Vercel / DO)**
   - Each IPAI App:
     - Has an entry in `ipai_app_registry`.
     - Is a Next.js app (Vercel) or DO-hosted app.
     - Uses Supabase client for data access and auth.
     - Emits logs to Supabase or an observability backend (Axiom / Sentry / DO logs).
   - Example apps:
     - `ipai-finance-command-center`
     - `ipai-retail-scout-genieview`
     - `ipai-ces-dashboard`
     - `ipai-erp-health-monitor`.

5. **AI & Agent Layer (Pulser, MCP, Vercel AI Gateway)**
   - Agents are modeled as:
     - `ipai_agent` table:
       - code_name, description, allowed_tools, allowed_schemas, cost/latency budgets.
     - Tools defined through:
       - Supabase MCP server
       - Pulser MCP integration
       - Vercel AI Gateway for multi-model routing (optional).
   - All agent invocations must be:
     - Logged with input/output metadata.
     - Bound to user identity and data scopes.

6. **Governance, Security & Observability**
   - RLS:
     - Role-aware policies for user, app, agent.
   - Auditing:
     - Activity logs for:
       - connector runs
       - schema changes
       - agent calls
       - app actions (critical ones, e.g., finance approvals).
   - Monitoring & Alerts:
     - Error budgets and SLOs for connectors and apps.
     - Alerts via n8n/Slack/Mattermost.

### 4.2 System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              IPAI Databricks                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                           Presentation Layer                              │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │ Finance │  │ DevOps  │  │ Retail  │  │   CES   │  │  Scout  │        │  │
│  │  │ Command │  │ Health  │  │ Scout   │  │Dashboard│  │BI Genie │        │  │
│  │  │ Center  │  │   App   │  │  App    │  │   App   │  │   App   │        │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │  │
│  └───────┼────────────┼────────────┼────────────┼────────────┼─────────────┘  │
│          │            │            │            │            │                 │
│  ┌───────┴────────────┴────────────┴────────────┴────────────┴─────────────┐  │
│  │                           Agent Layer (MCP)                              │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │ Pulser  │  │ Claude  │  │ Gemini  │  │ Custom  │  │  n8n    │        │  │
│  │  │ Agent   │  │ Agent   │  │ Agent   │  │ Agents  │  │ Flows   │        │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │  │
│  └───────┼────────────┼────────────┼────────────┼────────────┼─────────────┘  │
│          │            │            │            │            │                 │
│  ┌───────┴────────────┴────────────┴────────────┴────────────┴─────────────┐  │
│  │                       Governance & Security                              │  │
│  │           ┌─────────────────────────────────────────────┐               │  │
│  │           │  RLS │ Auth │ Audit │ Policies │ Vault      │               │  │
│  │           └─────────────────────────────────────────────┘               │  │
│  └──────────────────────────────────┬──────────────────────────────────────┘  │
│                                     │                                         │
│  ┌──────────────────────────────────┴──────────────────────────────────────┐  │
│  │                      Supabase Lakehouse                                  │  │
│  │                                                                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │   Bronze   │  │   Silver   │  │    Gold    │  │  Platinum  │         │  │
│  │  │  (Raw)     │→ │ (Cleaned)  │→ │ (Analytic) │→ │  (ML/AI)   │         │  │
│  │  │            │  │            │  │            │  │            │         │  │
│  │  │ erp_raw    │  │ erp_clean  │  │ erp_metrics│  │ erp_vectors│         │  │
│  │  │ github_raw │  │ github_norm│  │ devops_kpi │  │ ai_features│         │  │
│  │  │ files_raw  │  │ files_std  │  │ retail_agg │  │ embeddings │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘         │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │  │                    Object Storage (Blobs)                       │    │  │
│  │  │    Supabase Storage / DO Spaces (files, images, parquet)       │    │  │
│  │  └─────────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────┬──────────────────────────────────────┘  │
│                                     │                                         │
│  ┌──────────────────────────────────┴──────────────────────────────────────┐  │
│  │                    IPAI Connector Framework                              │  │
│  │                                                                          │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │  │
│  │  │  Odoo   │  │ GitHub  │  │  Files  │  │   DB    │  │ Events  │       │  │
│  │  │Connector│  │Connector│  │Connector│  │Connector│  │Connector│       │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │  │
│  └───────┼────────────┼────────────┼────────────┼────────────┼─────────────┘  │
│          │            │            │            │            │                 │
├──────────┼────────────┼────────────┼────────────┼────────────┼─────────────────┤
│          ▼            ▼            ▼            ▼            ▼                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                         External Data Sources                           │  │
│  │  Odoo CE │ GitHub │ CSV/Parquet │ Postgres │ Webhooks │ Figma │ Mail   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Detailed Requirements

### 5.1 Lakehouse Schemas

**R1.1** – Create canonical schemas:
- `ipai_bronze_core`, `ipai_silver_core`, `ipai_gold_core`, `ipai_platinum_core`.
- Specialized schemas:
  - `ipai_bronze_erp`, `ipai_silver_erp`, `ipai_gold_erp` (Odoo finance & ops).
  - `ipai_bronze_devops`, `ipai_gold_devops` (GitHub, CI, logs).
  - `ipai_bronze_retail`, `ipai_gold_retail`.
  - `ipai_bronze_creative`, `ipai_gold_creative`.

**R1.2** – Supabase migrations must manage:
- All table definitions
- Constraints
- Indexes
- Views / materialized views.

**R1.3** – All direct access must go through:
- RLS policies
- Supabase Auth
- Verified JWT.

---

### 5.2 IPAI Connector Framework

**R2.1** – Connector types to prioritize:
- Odoo CE (ERP)
- GitHub
- Files (CSV/Parquet/JSON)
- Databases (Postgres/MySQL)
- Data warehouses (BigQuery/Redshift-style via FDW/FDW-like patterns)
- Event streams (webhooks, logs)
- Figma, n8n, MCP, mail providers (for long-term).

**R2.2** – Each connector:
- Has its own code module (Edge Function / n8n flow).
- Uses Supabase Vault for secrets.
- Implements:
  - initial full sync
  - incremental sync (timestamp/ID/CDC style where possible).

**R2.3** – Connector orchestration:
- Config and runs stored in Supabase tables.
- A single scheduler (n8n / DO cron / Supabase scheduled functions) triggers:
  - `run_connector(connector_id)` with parameters.

**R2.4** – Connector tables:

```sql
-- Connector configuration
CREATE TABLE ipai_connector_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_type TEXT NOT NULL,  -- odoo, github, file, db, etc.
    name TEXT NOT NULL,
    config JSONB NOT NULL,         -- type-specific configuration
    vault_secret_refs TEXT[],      -- references to Vault secrets
    schedule TEXT,                 -- cron expression
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Connector run history
CREATE TABLE ipai_connector_run (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID REFERENCES ipai_connector_config(id),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL,          -- running, success, failed
    rows_read INTEGER,
    rows_written INTEGER,
    error_message TEXT,
    metadata JSONB
);
```

---

### 5.3 Databricks-Style Apps

**R3.1** – Apps are registered in `ipai_app_registry` with:
- id, slug, name
- GitHub repo
- deployment target (Vercel/DO)
- required roles and permissions.

**R3.2** – All apps use:
- Supabase Auth for sign-in / JWT.
- Supabase JS client for data.
- RLS and policies enforced at DB.

**R3.3** – Provide at least 2 reference apps:
1. `ipai-finance-command-center`
   - Views:
     - P&L, balance sheet, cashflow.
     - Open items / receivables / payables.
   - Features:
     - Reconciliation helper (AI suggestions).
2. `ipai-devops-health`
   - Views:
     - Spec Kit coverage
     - CI status
     - Deployment summary.

**R3.4** – App registry table:

```sql
CREATE TABLE ipai_app_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    github_repo TEXT,
    deployment_target TEXT NOT NULL,  -- vercel, do, self-hosted
    deployment_url TEXT,
    required_roles TEXT[],
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

---

### 5.4 AI & Agent Governance

**R4.1** – Define `ipai_agent` and `ipai_agent_run` tables:
- agent metadata and run logs.

**R4.2** – Agents can only:
- Access data via MCP tools bound to specific views/RPCs.
- Operate within cost and latency budgets.

**R4.3** – For each agent:
- Define allowed tools (Supabase MCP, custom functions).
- Define allowed schemas/tables via configuration.

**R4.4** – Agent governance tables:

```sql
-- Agent registry
CREATE TABLE ipai_agent (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    agent_type TEXT NOT NULL,      -- pulser, claude, gemini, custom
    allowed_tools TEXT[],
    allowed_schemas TEXT[],
    allowed_operations TEXT[],     -- read, write, transform, schedule
    cost_budget_usd DECIMAL(10, 4),
    latency_budget_ms INTEGER,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Agent execution log
CREATE TABLE ipai_agent_run (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES ipai_agent(id),
    user_id UUID,                  -- invoking user
    session_id TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL,          -- running, success, failed
    input_summary JSONB,
    output_summary JSONB,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    error_message TEXT,
    metadata JSONB
);
```

---

### 5.5 Security & Observability

**R5.1** – Enable logging of:
- Connector runs
- Agent runs
- App critical actions.

**R5.2** – Implement SLO targets:
- E.g. 99% successful connector runs over last 7 days.
- No more than X failed agent calls per day per project.

**R5.3** – Integrate with:
- Sentry / Axiom / DO logs for error tracking and traces.

**R5.4** – Audit log table:

```sql
CREATE TABLE ipai_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,      -- connector_run, agent_run, app_action, schema_change
    entity_type TEXT NOT NULL,     -- connector, agent, app, table
    entity_id UUID,
    user_id UUID,
    action TEXT NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audit_event_type ON ipai_audit_log(event_type);
CREATE INDEX idx_audit_entity ON ipai_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created ON ipai_audit_log(created_at);
```

---

### 5.6 CI/CD & Spec-to-Code

**R6.1** – Spec Kit enforcement:
- CI job verifies:
  - `spec/ipai-databricks/constitution.md`
  - `spec/ipai-databricks/prd.md`
  - `plan.md` and `tasks.md` (even as stubs)
  are present and non-empty.

**R6.2** – Migration checks:
- All DB changes must be introduced via Supabase migrations.
- CI simulates migrations on a scratch DB before merge.

**R6.3** – Quality gates:
- Linting of backend and frontend code.
- Tests for connectors and shared libraries.

---

## 6. Milestones (High-Level)

| Milestone | Name | Deliverables |
|-----------|------|--------------|
| **M1** | Foundations | Schemas (bronze/silver/gold/platinum), Supabase + DO/Vercel infra, Spec Kit CI |
| **M2** | Core Connectors | Odoo CE connector, GitHub connector, File connector |
| **M3** | Apps v1 | Finance Command Center, DevOps Health app, basic AI copilot |
| **M4** | Agent Governance | Agent registry, run logging, MCP integration, data scopes |
| **M5** | Observability | Logs, metrics, alerts, SLOs, security review, runbooks |

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Connector success rate | > 99% over 7 days |
| Agent response latency (p95) | < 5s |
| App availability | 99.9% uptime |
| Spec Kit coverage | 100% for new features |
| RLS policy coverage | 100% for gold/platinum tables |

---

## 8. Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Supabase project | Lakehouse + Auth + Vault | Active |
| DigitalOcean | Compute + Storage | Active |
| Vercel | Apps + AI Gateway | Active |
| Odoo CE | ERP system of record | Active |
| n8n | Workflow orchestration | Active |
| Pulser/MCP | Agent framework | Active |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep (Databricks parity) | High | Spawn sub-specs for connectors, apps, agents |
| Governance complexity | Medium | Centralize policies in dedicated tables |
| Infra fragmentation | Medium | Architecture doc + ADRs |
| License/IP concerns | High | Document "inspired by" vs implementation |
| Operational load | Medium | M5 is mandatory, not optional |

---

*Last updated: 2026-01-25*
