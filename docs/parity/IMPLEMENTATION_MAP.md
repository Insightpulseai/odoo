# Implementation Map

**Odoo CE + OCA + IPAI + Supabase + n8n + MCP + Superset**

---

## Systems of Record

| System | Purpose | Data Owned |
|--------|---------|------------|
| **Odoo CE** | Transactional truth | Expenses, POs, assets, projects, approvals, GL entries |
| **Supabase Postgres** | Ops hub + event log | Agent runs, portal sessions, external sync state, audit events |

## Integration & Automation

| System | Purpose | Triggers |
|--------|---------|----------|
| **n8n** | Workflow orchestration | Approval escalations, SLA alerts, scheduled sync, notifications |
| **MCP** | Tool surface for agents | Odoo RPC, Supabase RPC, Superset API, storage, email |

## Analytics

| System | Purpose | Data Source |
|--------|---------|-------------|
| **Superset** | BI dashboards + metrics | Curated analytics schema (not direct Odoo tables) |

## UI Consistency

| System | Purpose | Output |
|--------|---------|--------|
| **ipai_design_system** | Shared tokens | Odoo theme + portal CSS + component library |

---

## Detailed Capability Mapping

### 1. SAP Concur → Expense & Travel

| Concur Feature | Odoo/IPAI Implementation | OCA Module | n8n Workflow |
|----------------|--------------------------|------------|--------------|
| Expense capture | `hr.expense` + mobile | - | - |
| Receipt OCR | External OCR → `hr.expense.line` | - | `expense_ocr_ingest` |
| Policy enforcement | `ipai.expense.policy` | - | `policy_check` |
| Multi-level approval | `hr.expense.sheet` workflow | `hr_expense_tier_validation` | `approval_escalation` |
| Travel request | `ipai.travel.request` | - | - |
| Reimbursement batch | `account.payment.group` | `account_payment_group` | `reimbursement_batch` |
| Per diem rules | `ipai.per.diem.rule` | - | - |
| PH BIR compliance | `ipai_finance_bir_compliance` | - | `bir_extract` |

### 2. SAP Ariba SRM → Procurement

| Ariba Feature | Odoo/IPAI Implementation | OCA Module | n8n Workflow |
|---------------|--------------------------|------------|--------------|
| Supplier master | `res.partner` (supplier) | `partner_tier_validation` | - |
| KYC documents | `res.partner.document` | `partner_documents` | `kyc_check` |
| RFQ/RFP | `purchase.requisition` | `purchase_requisition` | - |
| Purchase order | `purchase.order` | - | `po_approval` |
| 3-way match | Bill vs Receipt vs PO | `purchase_stock_picking_invoice_link` | `invoice_match` |
| Approval matrix | `ipai.approval.matrix` | - | `approval_route` |
| Vendor portal | Supabase + Next.js | - | `vendor_onboard` |
| Audit trail | `mail.tracking.value` | `auditlog` | - |

### 3. Cheqroom → Equipment Booking

| Cheqroom Feature | Odoo/IPAI Implementation | OCA Module | n8n Workflow |
|------------------|--------------------------|------------|--------------|
| Asset catalog | `product.product` (equipment) | - | - |
| Location tracking | `stock.location` | - | - |
| Availability calendar | `ipai.equipment.availability` | - | - |
| Reservations | `ipai.equipment.booking` | - | `booking_confirm` |
| Check-out/in | `stock.picking` (internal) | - | `checkout_notify` |
| Condition logging | `ipai.equipment.condition` | - | - |
| Maintenance | `maintenance.request` | `maintenance` | `maintenance_schedule` |
| QR/barcode | `stock.lot` + barcode | `stock_barcodes` | - |
| Custody chain | `ipai.custody.log` | - | - |

### 4. Microsoft Planner → Work Management

| Planner Feature | Odoo/IPAI Implementation | OCA Module | n8n Workflow |
|-----------------|--------------------------|------------|--------------|
| Buckets/boards | `project.task.type` | - | - |
| Tasks | `project.task` | - | - |
| Assignments | `project.task` user_ids | - | `task_assign` |
| Due dates | `project.task` date_deadline | - | `due_reminder` |
| Checklists | `project.task` checklist | `project_task_checklist` | - |
| Dependencies | `project.task` depend_on_ids | `project_task_dependency` | - |
| Recurrence | `ipai.task.recurrence` | `project_task_recurrent` | `task_generate` |
| Plan templates | `ipai.plan.template` | - | `plan_instantiate` |
| Schedule view | Gantt view | `project_timeline` | - |
| Workload | Resource allocation | `project_resource_calendar` | - |

### 5. SAP Joule → Embedded Copilot

| Joule Feature | Odoo/IPAI Implementation | MCP Tool | Supabase Table |
|---------------|--------------------------|----------|----------------|
| Ask (query) | RAG over Odoo + docs | `odoo_search`, `docs_search` | - |
| Act (execute) | RPC endpoints | `odoo_create`, `odoo_update` | `agent_runs` |
| Explain (why) | Reasoning trace | `explain_action` | `agent_explanations` |
| Audit (log) | Full provenance | - | `agent_audit_log` |
| Permissions | Role-based tool access | `check_permission` | `tool_permissions` |
| Approval gate | Write approval workflow | `request_approval` | `pending_approvals` |

### 6. Superset → BI & Analytics

| Superset Feature | Implementation | Data Source | Configuration |
|------------------|----------------|-------------|---------------|
| Certified datasets | Semantic layer | `analytics.*` schema | Dataset certification |
| Metrics | `ipai.metric.definition` | Metric YAML | Superset metric API |
| Dashboards | Superset native | Curated views | Dashboard JSON |
| RLS | Row-level security | DB roles | Superset RLS rules |
| Embedded | Superset embed SDK | - | Guest tokens |
| Alerts | Superset alerts | - | Alert rules |

---

## Supabase Schema (Ops Hub)

```sql
-- Agent runs and audit
CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE ops.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type TEXT NOT NULL,
    session_id TEXT,
    user_id INTEGER REFERENCES public.res_users(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'running',
    input_summary JSONB,
    output_summary JSONB,
    tool_calls JSONB[],
    tokens_used INTEGER
);

CREATE TABLE ops.agent_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES ops.agent_runs(id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    action TEXT NOT NULL,
    target_model TEXT,
    target_id INTEGER,
    before_state JSONB,
    after_state JSONB,
    explanation TEXT
);

CREATE TABLE ops.tool_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    allowed BOOLEAN DEFAULT false,
    requires_approval BOOLEAN DEFAULT false,
    UNIQUE(role_name, tool_name)
);

-- Portal sessions
CREATE TABLE ops.portal_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address INET,
    user_agent TEXT
);

-- Enable RLS
ALTER TABLE ops.agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.portal_sessions ENABLE ROW LEVEL SECURITY;
```

---

## n8n Workflow Index

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `expense_ocr_ingest` | Webhook (OCR result) | Create expense lines, attach receipt |
| `policy_check` | Expense submit | Validate against policy rules |
| `approval_escalation` | Cron (hourly) | Escalate overdue approvals |
| `reimbursement_batch` | Cron (daily) | Create payment batch |
| `bir_extract` | Cron (monthly) | Generate BIR reporting files |
| `po_approval` | PO create | Route to approval matrix |
| `invoice_match` | Bill create | Attempt 3-way match |
| `vendor_onboard` | Partner create | KYC workflow trigger |
| `booking_confirm` | Booking create | Send confirmation, update calendar |
| `checkout_notify` | Stock move | Notify borrower, log custody |
| `maintenance_schedule` | Cron (daily) | Create maintenance requests |
| `task_assign` | Task create | Notify assignees |
| `due_reminder` | Cron (daily) | Send due date reminders |
| `task_generate` | Cron (configurable) | Generate recurring tasks |
| `plan_instantiate` | Manual trigger | Create tasks from template |

---

## MCP Tool Registry

| Tool | Capability | Parameters | Returns |
|------|------------|------------|---------|
| `odoo_search` | Read records | model, domain, fields | records[] |
| `odoo_create` | Create record | model, values | id |
| `odoo_update` | Update record | model, id, values | success |
| `odoo_action` | Execute action | model, action, ids | result |
| `supabase_query` | Query ops tables | table, filters | rows[] |
| `supabase_insert` | Insert ops record | table, values | id |
| `superset_query` | Run chart query | chart_id, filters | data |
| `docs_search` | Search documentation | query, scope | matches[] |
| `send_notification` | Send alert | channel, message | success |
| `request_approval` | Gate write action | action_type, target | approval_id |

---

## CI Parity Gates

```yaml
# .github/workflows/parity-gate.yml
name: Parity Gate

on: [push, pull_request]

jobs:
  parity-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check Concur Parity
        run: ./scripts/ci/check_expense_parity.sh

      - name: Check Ariba Parity
        run: ./scripts/ci/check_procurement_parity.sh

      - name: Check Cheqroom Parity
        run: ./scripts/ci/check_equipment_parity.sh

      - name: Check Planner Parity
        run: ./scripts/ci/check_project_parity.sh

      - name: Check Joule Parity
        run: ./scripts/ci/check_copilot_parity.sh

      - name: Check Superset Parity
        run: ./scripts/ci/check_bi_parity.sh
```

---

*See: [TARGET_CAPABILITIES.md](./TARGET_CAPABILITIES.md) for capability overview*
