# Database Target Architecture

**Version:** 1.0.0
**Status:** Authoritative
**Last Updated:** 2025-12-07

---

## 1. Overview

This document defines the canonical database schema architecture for InsightPulseAI, including schema ownership, table organization, and migration strategy.

---

## 2. Schema Ownership Matrix

| Schema | Owner Engine | Domain | Tenant-Scoped | RLS Required | Migration Priority |
|--------|--------------|--------|---------------|--------------|-------------------|
| `core` | Platform | Infrastructure | No | No | P0 |
| `saas` | Platform | Tenancy | Yes | Yes | P0 |
| `logs` | E2 Automation | Observability | Yes | Yes | P1 |
| `doc` | E1 Data Intake | Document Processing | Yes | Yes | P1 |
| `expense` | TE-Cheq | T&E | Yes | Yes | P1 |
| `teq` | TE-Cheq | T&E Facts | Yes | Yes | P1 |
| `projects` | PPM | Engagements | Yes | Yes | P1 |
| `finance` | PPM | Finance Ops | Yes | Yes | P1 |
| `rates` | SRM | Rate Cards | Yes | Yes | P2 |
| `rag` | E3 Intelligence | Vector Store | Yes | Yes | P2 |
| `ai` | E3/E4 | AI Sessions | Yes | Yes | P2 |
| `agents` | E3/E4 | Agent Registry | Partial | Yes | P2 |
| `mcp` | Platform | MCP Tools | No | No | P2 |
| `scout_bronze` | E1 Data Intake | Raw Retail | Yes | Yes | P3 |
| `scout_silver` | E3 Intelligence | Cleaned Retail | Yes | Yes | P3 |
| `scout_gold` | E3 Intelligence | Aggregated Retail | Yes | Yes | P3 |
| `scout_dim` | Retail-Intel | Dimensions | Yes | Yes | P3 |
| `scout_fact` | Retail-Intel | Facts | Yes | Yes | P3 |
| `analytics` | Retail-Intel | Analytics | Yes | Yes | P3 |
| `dim` | Retail-Intel | Shared Dimensions | Yes | Yes | P3 |
| `intel` | Retail-Intel | External Indices | Yes | Yes | P3 |
| `gold` | E3 Intelligence | Shared RAG Source | Yes | Yes | P3 |
| `platinum` | E4 Creative | AI Cache | Yes | Yes | P3 |
| `ref` | Shared | Reference Data | Yes | Yes | P1 |
| `public` | Legacy | Compatibility Views | N/A | N/A | P0 |

---

## 3. Core Tables by Schema

### 3.1 `core` Schema (Platform Infrastructure)

```sql
core.tenants          -- Tenant registry
core.tenant_settings  -- Tenant configuration
core.employees        -- Employee master (synced from Odoo)
core.audit_log        -- Platform audit trail
```

### 3.2 `expense` Schema (TE-Cheq)

```sql
expense.expense_reports   -- Header-level expense reports
expense.expenses          -- Line-level expenses
expense.cash_advances     -- Cash advances
expense.receipt_documents -- OCR'd receipts
```

### 3.3 `teq` Schema (TE-Cheq Facts)

```sql
teq.expense_reports       -- Fact table for reports
teq.expense_lines         -- Fact table for lines
teq.cash_advances         -- Fact table for advances
teq.receipt_documents     -- OCR log with confidence scores
```

### 3.4 `projects` Schema (PPM)

```sql
projects.projects         -- Project master
projects.project_members  -- Project team assignments
projects.project_budgets  -- Budget allocations
projects.project_tasks    -- Task breakdown
```

### 3.5 `rates` Schema (SRM)

```sql
rates.vendor_profile      -- Vendor master
rates.rate_cards          -- Rate card definitions
rates.rate_card_items     -- Rate card line items
rates.rate_approvals      -- Approval workflow
```

### 3.6 `ref` Schema (Reference Data)

```sql
ref.expense_policies      -- Expense policy rules
ref.expense_categories    -- Category master
ref.cost_centers          -- Cost center hierarchy
ref.currencies            -- Currency master
```

### 3.7 `doc` Schema (Document Processing)

```sql
doc.raw_documents         -- Uploaded files metadata
doc.parsed_documents      -- Parsed output JSON
doc.user_corrections      -- Active learning corrections
```

### 3.8 `analytics` / `scout_*` Schemas (Retail)

```sql
analytics.sales_daily     -- Daily sales facts
scout_bronze.transactions -- Raw transactions
scout_silver.transactions -- Cleaned transactions
scout_gold.store_daily    -- Aggregated store metrics
scout_dim.stores          -- Store dimension
scout_dim.products        -- Product dimension
scout_dim.brands          -- Brand dimension
scout_fact.sales          -- Sales fact table
intel.external_indices_daily -- Weather, holidays, etc.
```

### 3.9 `rag` / `ai` Schemas (Intelligence)

```sql
rag.documents             -- Source documents
rag.chunks                -- Document chunks with embeddings
ai.sessions               -- AI conversation sessions
ai.messages               -- Session messages
ai.tool_calls             -- Tool invocation log
```

### 3.10 `logs` Schema (Observability)

```sql
logs.engine_events        -- Engine-level events
logs.agent_actions        -- Agent action log
logs.api_requests         -- API request log
logs.errors               -- Error log
```

---

## 4. Migration Strategy

### 4.1 Phase 1: Create Domain Schemas (P0)

```sql
-- Create all domain schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS saas;
CREATE SCHEMA IF NOT EXISTS expense;
CREATE SCHEMA IF NOT EXISTS teq;
CREATE SCHEMA IF NOT EXISTS projects;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS rates;
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS doc;
CREATE SCHEMA IF NOT EXISTS logs;
```

### 4.2 Phase 2: Create Tables in New Schemas (P1)

See: `db/migrations/202512xx0001_REORG_CREATE_DOMAIN_TABLES.sql`

### 4.3 Phase 3: Migrate Data from Legacy (P1)

See: `db/migrations/202512xx0002_REORG_COPY_DATA.sql`

### 4.4 Phase 4: Create Compatibility Views (P1)

See: `db/migrations/202512xx0003_REORG_CREATE_COMPAT_VIEWS.sql`

---

## 5. Naming Conventions

### Tables
- Plural nouns: `expense_reports`, `projects`, `rate_cards`
- Snake_case: `cash_advances`, `user_corrections`

### Columns
- Primary key: `id UUID DEFAULT gen_random_uuid()`
- Foreign keys: `<table>_id` (e.g., `expense_report_id`)
- Tenant key: `tenant_id UUID NOT NULL`
- Timestamps: `created_at`, `updated_at`, `deleted_at`

### Indexes
- Format: `idx_<table>_<columns>`
- Example: `idx_expense_reports_tenant_status`

### Constraints
- Primary key: `pk_<table>`
- Foreign key: `fk_<table>_<ref_table>`
- Unique: `uq_<table>_<columns>`
- Check: `ck_<table>_<description>`

---

## 6. Standard Table Template

```sql
CREATE TABLE schema.table_name (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Business columns
    -- ...

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID REFERENCES core.employees(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by UUID REFERENCES core.employees(id),
    deleted_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT fk_table_name_tenant
        FOREIGN KEY (tenant_id) REFERENCES core.tenants(id)
);

-- RLS
ALTER TABLE schema.table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON schema.table_name
    FOR ALL
    USING (tenant_id = core.current_tenant_id());

-- Indexes
CREATE INDEX idx_table_name_tenant ON schema.table_name(tenant_id);

-- Updated trigger
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON schema.table_name
    FOR EACH ROW
    EXECUTE FUNCTION core.set_updated_at();
```

---

## 7. Related Documents

- [RLS_BASE_TEMPLATE.sql](rls/RLS_BASE_TEMPLATE.sql) — RLS policy templates
- [RLS_ROLES.md](rls/RLS_ROLES.md) — Role definitions
- [SEEDING_STRATEGY.md](seeds/SEEDING_STRATEGY.md) — Data seeding approach
- [Migration Files](migrations/) — SQL migration scripts

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial authoritative release |
