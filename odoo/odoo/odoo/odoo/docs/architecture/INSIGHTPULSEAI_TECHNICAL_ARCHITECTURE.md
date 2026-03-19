# InsightPulseAI Technical Architecture

**Version:** 1.0.0
**Status:** Authoritative
**Last Updated:** 2025-12-07

---

## 1. Platform Overview

InsightPulseAI is a multi-tenant AI-powered business platform built on:

- **Supabase** (PostgreSQL 15) — primary data store, RLS-enforced multi-tenancy
- **Odoo 18 CE/OCA** — ERP backbone for finance, HR, projects
- **n8n** — workflow automation and event orchestration
- **Mattermost** — ChatOps and notifications
- **Edge Functions** — serverless compute for API endpoints
- **Vector Store** — pgvector for RAG and semantic search

---

## 2. Engine Architecture

The platform is organized into four core engines, each owning specific domains and schemas:

### E1: Data Intake Engine
**Purpose:** Ingest, parse, and normalize raw data from multiple sources.

| Component | Description |
|-----------|-------------|
| doc-ocr | Document OCR & handwriting recognition |
| scout-ingest | Retail transaction ingestion |
| expense-capture | Receipt and expense document capture |

**Owned Schemas:** `doc.*`, `scout_bronze.*`, `expense_raw.*`

### E2: Automation Engine
**Purpose:** Orchestrate workflows, trigger events, manage state machines.

| Component | Description |
|-----------|-------------|
| n8n workflows | Event-driven automation |
| Edge Functions | Serverless API handlers |
| Cron jobs | Scheduled data processing |

**Owned Schemas:** `logs.*`, `events.*`

### E3: Intelligence Engine
**Purpose:** Transform data, generate insights, power AI agents.

| Component | Description |
|-----------|-------------|
| scout-analytics | Retail intelligence (silver/gold) |
| rag-pipeline | Document chunking and embedding |
| ai-sessions | Agent conversation management |

**Owned Schemas:** `scout_silver.*`, `scout_gold.*`, `gold.*`, `rag.*`, `ai.*`

### E4: Creative Engine
**Purpose:** Generate content, manage prompts, cache AI outputs.

| Component | Description |
|-----------|-------------|
| prompt-studio | Prompt template management |
| ai-cache | Response caching and deduplication |
| content-gen | Creative content generation |

**Owned Schemas:** `ai.*`, `platinum.*`

---

## 3. Domain Engines

Built on top of core engines, these implement specific business domains:

### TE-Cheq (Travel & Expense)
- **Domain:** Finance
- **Owner:** finance-ssc
- **Primary Schemas:** `teq.*`, `expense.*`, `ref.*`
- **Integrates With:** doc-ocr, Odoo hr.expense

### Retail-Intel (SariCoach/Scout)
- **Domain:** Retail Analytics
- **Owner:** retail-analytics
- **Primary Schemas:** `analytics.*`, `dim.*`, `intel.*`, `scout_*.*`
- **Integrates With:** scout-ingest, ai-sessions

### PPM (Project Portfolio Management)
- **Domain:** Finance / Operations
- **Owner:** finance-ssc
- **Primary Schemas:** `projects.*`, `finance.*`
- **Integrates With:** Odoo project.project, rates.*

### SRM (Supplier Rate Management)
- **Domain:** Procurement
- **Owner:** procurement
- **Primary Schemas:** `rates.*`
- **Integrates With:** Odoo res.partner, purchase.*

---

## 4. Schema Architecture

### Authoritative Schema Set

| Category | Schemas |
|----------|---------|
| Core / SaaS / Infra | `core`, `saas`, `logs`, `doc`, `rag`, `ai`, `agents`, `mcp` |
| Finance Domain | `finance`, `expense`, `projects`, `rates`, `teq` |
| Retail Domain | `scout_bronze`, `scout_silver`, `scout_gold`, `scout_dim`, `scout_fact`, `saricoach` |
| Medallion Cache | `gold`, `platinum` |
| Compatibility | `public` (views only) |

### Schema Ownership Matrix

| Schema | Owner Engine | Domain | Tenant-Scoped | RLS Required |
|--------|--------------|--------|---------------|--------------|
| `core` | Platform | Infrastructure | No | No |
| `saas` | Platform | Tenancy | Yes | Yes |
| `logs` | E2 Automation | Observability | Yes | Yes |
| `doc` | E1 Data Intake | Document Processing | Yes | Yes |
| `rag` | E3 Intelligence | Vector Store | Yes | Yes |
| `ai` | E3/E4 | AI Sessions | Yes | Yes |
| `agents` | E3/E4 | Agent Registry | Partial | Yes |
| `mcp` | Platform | MCP Tools | No | No |
| `expense` | TE-Cheq | T&E | Yes | Yes |
| `teq` | TE-Cheq | T&E Facts | Yes | Yes |
| `projects` | PPM | Engagements | Yes | Yes |
| `finance` | PPM | Finance Ops | Yes | Yes |
| `rates` | SRM | Rate Cards | Yes | Yes |
| `scout_bronze` | E1 Data Intake | Raw Retail | Yes | Yes |
| `scout_silver` | E3 Intelligence | Cleaned Retail | Yes | Yes |
| `scout_gold` | E3 Intelligence | Aggregated Retail | Yes | Yes |
| `scout_dim` | Retail-Intel | Dimensions | Yes | Yes |
| `scout_fact` | Retail-Intel | Facts | Yes | Yes |
| `analytics` | Retail-Intel | Analytics | Yes | Yes |
| `dim` | Retail-Intel | Shared Dimensions | Yes | Yes |
| `intel` | Retail-Intel | External Indices | Yes | Yes |
| `gold` | E3 Intelligence | Shared RAG Source | Yes | Yes |
| `platinum` | E4 Creative | AI Cache | Yes | Yes |

---

## 5. Multi-Tenancy Model

### Tenant Isolation
- **Model:** Row-Level Security (RLS) with `tenant_id` column
- **Enforcement:** PostgreSQL RLS policies on all tenant-scoped tables
- **Key Column:** `tenant_id UUID NOT NULL`

### Tenant Context
```sql
-- Set tenant context for session
SELECT set_config('app.current_tenant_id', 'uuid-here', true);

-- Core function for RLS policies
CREATE FUNCTION core.current_tenant_id() RETURNS uuid AS $$
  SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid;
$$ LANGUAGE sql STABLE;
```

### RLS Policy Pattern
```sql
CREATE POLICY tenant_isolation ON schema.table_name
  FOR ALL
  USING (tenant_id = core.current_tenant_id());
```

---

## 6. Security Architecture

### Role Hierarchy

| Role | Scope | Permissions |
|------|-------|-------------|
| `platform_admin` | Global | Full access, tenant management |
| `tenant_admin` | Tenant | Full tenant access, user management |
| `engine_admin` | Engine | Engine-specific admin |
| `engine_user` | Engine | Standard engine access |
| `readonly` | Tenant | Read-only access |

### Domain-Specific Roles

**Finance Domain:**
- `finance_director` — Full finance access
- `teq_admin` — TE-Cheq administration
- `teq_approver` — Expense approval
- `teq_employee` — Self-service expense

**Retail Domain:**
- `retail_admin` — Full retail access
- `sari_store_owner` — Store-level access
- `brand_sponsor` — Brand aggregate access
- `scout_viewer` — Read-only analytics

---

## 7. Integration Architecture

### Odoo 18 CE/OCA Integration

| Business Concept | Supabase Table | Odoo Model | Sync Direction |
|-----------------|----------------|------------|----------------|
| Vendor | `rates.vendor_profile` | `res.partner` | Bi-directional |
| Rate Card | `rates.rate_cards` | `ipai.rate.card` | Supabase → Odoo |
| Expense Report | `expense.expense_reports` | `hr.expense.sheet` | Odoo → Supabase |
| Expense Line | `expense.expenses` | `hr.expense` | Odoo → Supabase |
| Project | `projects.projects` | `project.project` | Bi-directional |
| Employee | `core.employees` | `hr.employee` | Odoo → Supabase |

### Sync Mechanisms
1. **Webhooks:** Odoo → n8n → Supabase
2. **Edge Functions:** Supabase → Odoo API
3. **Cron Jobs:** Batch reconciliation
4. **Real-time:** Supabase Realtime → n8n

---

## 8. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
│  Mattermost │ Web Apps │ Mobile │ Odoo │ API Clients             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      GATEWAY LAYER                               │
│  Supabase Auth │ Edge Functions │ n8n Webhooks │ MCP Server     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      ENGINE LAYER                                │
│  E1 Data Intake │ E2 Automation │ E3 Intelligence │ E4 Creative │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      DATA LAYER                                  │
│  PostgreSQL (RLS) │ pgvector │ Storage │ Realtime               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Observability

### Logging
- **Sink:** Supabase `logs.*` schema
- **Retention:** 365 days (agent actions), 730 days (audit logs)
- **Format:** Structured JSON with trace IDs

### Dashboards
- **Platform:** Apache Superset
- **Location:** `dashboards/*.json`

### Alerts
- **Channel:** Mattermost
- **Rules:** `alerts/*.yml`

---

## 10. Deployment Environments

| Environment | Supabase Project | Purpose |
|-------------|------------------|---------|
| dev | dev-* | Development and testing |
| staging | staging-* | Pre-production validation |
| prod | spdtwktxdalcfigzeqrz | Production |

### Feature Flags
Managed via Supabase:
- `engine_enable_*` — Engine-specific toggles
- `tenant_*` — Tenant-specific features

---

## Related Documents

- [DB_TARGET_ARCHITECTURE.md](../../db/DB_TARGET_ARCHITECTURE.md) — Schema ownership and migration plan
- [RLS_ROLES.md](../../db/rls/RLS_ROLES.md) — Role definitions and permissions
- [ODOO_INTEGRATION_MAP.md](../../odoo/ODOO_INTEGRATION_MAP.md) — Odoo sync specifications
- [Engine Specs](../../engines/) — Individual engine YAML specifications

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial authoritative release |
