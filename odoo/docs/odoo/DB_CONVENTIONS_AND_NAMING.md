# InsightPulse Supabase DB – Conventions & House Style

**Scope:** This applies to all future schema/table/view/function work in this Supabase project (finance, expense, Scout, SariCoach, Kaggle, AI/RAG, agents, etc).

---

## Odoo Parity Rule

All business domains (finance, expense, inventory, maintenance, projects, rates, etc.) must follow **Odoo 18 CE + OCA data models and naming** as the baseline.

Our own tables are "Smart Delta" extensions on top of the closest OCA module (no Enterprise-only features, no IAP, no breaking OCA compatibility).

---

## 1. Schema Roles

### 1.1 System / Infra (no domain logic here)

These are treated as platform-owned:

* `auth`, `storage`, `realtime`, `supabase_migrations`, `supabase_functions`, `extensions`, `cron`, `pgmq`, `net`, `graphql`, `graphql_public`, `secret_vault`, `vault`, `llm`, `ocr`, `superset`, `pgbouncer`

**Rules:**

* No domain tables
* Only extension/config helpers as needed
* Changes limited to migrations/ext install and doc comments

### 1.2 Core / Shared

* `core` – tenants and app identity
  * Examples: `core.company`, `core.app_user`, `core.feature_flag`
* `notion` – Notion mirrors / sync
  * Examples: `notion.page`, `notion.block`, `notion.view`

**Rules:**

* Shared across multiple products / domains
* Anything tenant-wide or account-wide lives here, not in `public`

### 1.3 Business Domains

Canonical domain schemas:

* `finance` – BIR, month-end, close, finance SSC
* `expense` – T&E / Concur-style expenses and approvals
* `inventory` – assets, locations, checkouts
* `maintenance` – maintenance jobs and plans
* `projects` – PPM (projects, budgets, members)
* `rates` – rate cards, vendor governance
* `ai` – AI conversations and user-facing suggestions
* `mcp` – agent registry, embeddings, routing, skills
* `ops` / `opex` – operational telemetry, AI/RAG logs
* `gold` – RAG doc store and chunks (Gold layer)
* `platinum` – high-value AI cache (Platinum layer)

Product domains:

* `scout_bronze`, `scout_silver`, `scout_gold`, `scout`
* `saricoach`
* `kaggle`
* `analytics`, `odoo`, `oca`, `superset` as needed

**Rule:** All new domain tables MUST be created in one of these domain/product schemas, **not** in `public`.

### 1.4 `public` Schema (legacy + surface)

`public` is a **surface + compatibility layer**, not a domain:

* Compatibility views pointing to canonical domain tables
* Minimal, non-sensitive shared metadata
* BI surfaces if a tool insists on `public` (prefer views)

**Rule:** New *base* tables in `public` are forbidden unless explicitly justified in a migration / PR.

---

## 2. Table Naming

### 2.1 General

* **snake_case**, plural nouns where natural:
  * `expense_reports`, `cash_advances`, `project_budgets`, `rate_card_items`
* **Primary key:** prefer `id` (UUID or bigint identity)
* **Foreign keys:** `<ref>_id`:
  * `tenant_id`, `company_id`, `project_id`, `employee_id`, `vendor_id`
* **Timestamps:**
  * `created_at`, `updated_at` (and `deleted_at` for soft-delete, if used)
* **Audit / history:**
  * `<table>_history` or `<table>_audit`
  * Example: `finance_closing_snapshots`, `schema_snapshots`

### 2.2 Multi-tenant Pattern

* Shared tables should have `tenant_id` where applicable
* RLS should reference `tenant_id` and `auth.uid()` / JWT claims
* **Rule:** any new user-facing table must explicitly decide:
  `single-tenant` (no `tenant_id`) vs `multi-tenant` (with `tenant_id`)

---

## 3. Views, Materialized Views, and Compatibility

### 3.1 Logical Views

* Read-only aggregations / joins:
  * `v_<domain>_<purpose>`
  * Examples:
    * `v_expense_dashboard`
    * `v_project_overview`
    * `v_rate_card_latest`

### 3.2 Materialized Views

* Heavy aggregates or expensive queries:
  * `mv_<domain>_<purpose>`
  * Example: `mv_scout_daily_store_metrics`

### 3.3 Compatibility Views (for reorg)

* When moving from `public` → domain schema:

  ```sql
  CREATE OR REPLACE VIEW public.expense_reports AS
  SELECT * FROM expense.expense_reports;

  COMMENT ON VIEW public.expense_reports IS
    'Compatibility view. Canonical table: expense.expense_reports.';
  ```

* For write compatibility, use `INSTEAD OF` triggers on `public.<view>` forwarding to the domain table.

**Rule:** When a table is moved, `public.<name>` becomes a view pointing to `<schema>.<name>` until all consumers are updated.

---

## 4. Medallion / Layering Rules

You already effectively use Bronze/Silver/Gold/Platinum:

* **Bronze** – raw data
  * `scout_bronze.*`, raw `saricoach` events, `kaggle.*`
* **Silver** – cleaned/modelled
  * `scout_silver.*`
  * Domain tables in `finance`, `expense`, `projects`, `rates`, etc.
* **Gold** – analytics / AI-ready
  * `scout_gold.*`
  * `gold.docs`, `gold.doc_chunks`
  * Domain `v_*` views used by BI / agents
* **Platinum** – cached, high-value
  * `platinum.ai_cache`
  * Selected, high-traffic AI results

**Rule:** For any new analytics/AI surface:

* Bronze → ingest into `*_bronze` or dedicated raw schema
* Transform to domain tables (Silver)
* Expose analytics in Gold:
  * View or table named `v_<domain>_<purpose>` or `<domain>_fact_*`
* Use Platinum only for cache or pre-computed AI outputs

---

## 5. AI / RAG / Agents

### 5.1 RAG Surfaces

Canonical RAG structures:

* `gold.docs`
* `gold.doc_chunks`
* `mcp.rag_embeddings`
* `opex.rag_queries`

**Required columns (or mapping table) on RAG entities:**

* `source_schema text`
* `source_table text`
* `source_pk text`
* `embedding vector` (when applicable)
* `model text`
* `created_at timestamptz`

### 5.2 Agents & Skills

Consolidate around:

* `mcp.*` for core registry + routing:
  * `mcp.agents`, `mcp.agent_tasks`, `mcp.agent_feedback`, `mcp.rag_embeddings`
* `agents.*` / `agent.*` as secondary/legacy; new stuff should lean to `mcp` unless justified

**Rule:** For new agent/skill tables, prefer `mcp` and add clear comments:

```sql
COMMENT ON TABLE mcp.agents IS
  'Canonical agent registry for InsightPulseAI. See docs/agents/AGENT_REGISTRY.md.';
```

---

## 6. RLS & Security Patterns

### 6.1 Baseline

For any user-facing table:

* **Enable RLS**
* Standard patterns:
  * Tenant isolation: `tenant_id = current_setting('request.jwt.claims.tenant_id')::uuid`
  * User-only rows: `user_id = auth.uid()`
  * Service role bypass: policy granting full access to `service_role`

Example (multi-tenant expense reports):

```sql
ALTER TABLE expense.expense_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY expense_reports_tenant_select
  ON expense.expense_reports
  FOR SELECT
  USING (
    tenant_id = current_setting('request.jwt.claims.tenant_id', true)::uuid
  );

CREATE POLICY expense_reports_tenant_write
  ON expense.expense_reports
  FOR INSERT, UPDATE
  WITH CHECK (
    tenant_id = current_setting('request.jwt.claims.tenant_id', true)::uuid
  );
```

### 6.2 Public Exposure

* Expose to client SDKs via:
  * Domain tables with strict RLS, or
  * `public.v_*` views on top of domain tables

**Rule:** No table should be both publicly exposed and without RLS.

---

## 7. Governance & CI Guardrails

To keep this enforced:

* **New tables:**
  * CI fails if:
    * New table is created in `public` (unless explicitly whitelisted)
    * New table has no PK
    * Multi-tenant table has no `tenant_id`
* **Comments:**
  * Every domain table must have a `COMMENT ON TABLE` with:
    * Domain
    * Canonical owner (team/email)
    * Brief purpose

Example:

```sql
COMMENT ON TABLE expense.expense_reports IS
  'Domain: T&E. Canonical home for expense reports (migrated from public.expense_reports). Owner: finance-ssc@insightpulseai.com.';
```

---

## 8. Contacts

* **Data Owner**: business@insightpulseai.com
* **Technical Owner**: jgtolentino_rn@yahoo.com
