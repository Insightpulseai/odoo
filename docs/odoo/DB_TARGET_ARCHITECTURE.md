# DB Target Architecture — Odoo 18 EE/CE + OCA-equivalent on Supabase Postgres

---

## Goals

1. **Domain schema layout** (no new business data in `public`)
2. **Multi-tenant via row-level tenancy** (JWT claim)
3. **SaaS/subscription first-class**
4. **AI/RAG**: gold/platinum + mcp

---

## Odoo Parity Rule

All business domains (finance, expense, inventory, maintenance, projects, rates, etc.) must follow **Odoo 18 CE + OCA data models and naming** as the baseline.

Our own tables are "Smart Delta" extensions on top of the closest OCA module (no Enterprise-only features, no IAP, no breaking OCA compatibility).

---

## Top-Level Schema Map

```
[System]
  auth | storage | realtime | supabase_migrations | supabase_functions | cron

[Core]
  core (tenants, app_user, company)

[Domains]
  finance | expense | projects | rates | inventory | maintenance
  ai | mcp | gold | platinum | ops | opex | scout_*

[Product]
  saricoach | kaggle

[Public]
  compatibility views (public.v_*), BI surfaces
```

---

## Schema Roles

### 1. System / Infra (do not domain-ize)
- `auth`, `storage`, `realtime`, `supabase_migrations`, `supabase_functions`, `cron`, `extensions`, `pgmq`, `net`, `superset`, `pgbouncer`

### 2. Domain Schemas

| Schema | Purpose | Odoo Equivalent |
|--------|---------|-----------------|
| `core` | tenants, company, app_user, feature_flag | res.company, res.users |
| `saas` | plan, plan_feature, subscription, subscription_usage | subscription app |
| `crm` | partner, lead, activity | res.partner, crm.lead |
| `sales` | order, order_line, pricelist | sale.order |
| `finance` | account, journal, move, move_line, invoice, payment, tax | account.move |
| `purchase` / `rates` | vendor_profile, PO, rate_cards | purchase.order |
| `inventory` | product, product_category, uom, stock_location, stock_move | stock.move |
| `maintenance` | plan, job, job_log | maintenance |
| `projects` | project, task, timesheet, milestone, budget | project.project |
| `hr` | employee, department, contract, attendance, leave | hr.employee |
| `expense` | expense_report, expense_line, cash_advance, approval_item | hr_expense |
| `helpdesk` | team, ticket, stage, sla | helpdesk |
| `cms` | page, menu, form, form_submission | website |

### 3. AI / RAG Schemas

| Schema | Purpose |
|--------|---------|
| `ai` | conversations, messages, budget_suggestions |
| `mcp` | agents, rag_embeddings, agent_tasks, usage_metrics |
| `gold` | docs, doc_chunks (RAG Gold layer) |
| `platinum` | ai_cache (Platinum cache layer) |
| `ops` / `opex` | operational telemetry, rag_queries |

### 4. Product Domains
- `scout_bronze`, `scout_silver`, `scout_gold`, `scout`
- `saricoach`
- `kaggle`

---

## Multi-Tenant Strategy

- **Tenant identifier**: JWT claim key `'tenant_id'`
- **Pattern**: `current_setting('request.jwt.claims', true)::jsonb ->> 'tenant_id'` cast to uuid
- **Every tenant-scoped table** must include `tenant_id uuid`
- **RLS**: enforce tenant isolation via templates (see `DB_RLS_POLICY_TEMPLATES.md`)
- **Service-role bypass**: `service_role` user for migrations and background tasks

---

## Naming Conventions

### Tables
- `snake_case`, plural nouns: `expense_reports`, `project_budgets`, `rate_card_items`

### Primary Keys
- Prefer `id` (uuid via `gen_random_uuid()`)
- Use bigint/identity only if sequential numeric ID required

### Foreign Keys
- `<ref>_id`: `employee_id`, `project_id`, `tenant_id`

### Audit/History
- `<table>_audit` or `<table>_history`

---

## Medallion Layers

| Layer | Schemas | Purpose |
|-------|---------|---------|
| Bronze | `scout_bronze`, `kaggle` raw, `saricoach` raw | Raw/landing data |
| Silver | `scout_silver`, domain tables | Cleaned/modeled |
| Gold | `scout_gold`, `gold.docs`, `gold.doc_chunks` | Analytics/AI-ready |
| Platinum | `platinum.ai_cache` | High-value cached results |

---

## Compatibility & Governance

- Keep old names as read-only compatibility views in `public` until apps are migrated
- Add `COMMENT ON TABLE` for canonical ownership
- Enforce by CI: avoid new tables in `public` without exception

---

## ASCII Map (Detailed)

```
┌─────────────────────────────────────────────────────────────────┐
│                        SYSTEM / INFRA                           │
│  auth | storage | realtime | supabase_functions | cron | pgmq   │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                          CORE / SHARED                          │
│              core (tenants, company, app_user, roles)           │
│              saas (plans, subscriptions)                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                        BUSINESS DOMAINS                         │
│  finance | expense | projects | rates | inventory | maintenance │
│  crm | sales | purchase | hr | helpdesk | cms                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                         AI / RAG LAYER                          │
│  ai | mcp | gold | platinum | ops | opex                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCT / ANALYTICS                        │
│  scout_* | saricoach | kaggle | analytics                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                     PUBLIC (Compatibility)                      │
│  compatibility views, BI surfaces, legacy                       │
└─────────────────────────────────────────────────────────────────┘
```
