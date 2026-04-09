# Odoo 18 Services — EE Parity Skill

> Source: https://www.odoo.com/documentation/19.0/applications/services.html
> Domain: `odoo_ce` / `ee_parity`
> Last validated: 2026-03-15

---

## What this skill is for

Agents building `ipai_*` modules that replace Odoo Enterprise "Services" apps use this
skill to understand the full EE feature surface, map it to CE + OCA + ipai_* replacements,
and verify parity scores.

The Services vertical covers: **Project, Timesheets, Field Service, Helpdesk, Planning, Appointments**.

---

## Feature Parity Matrix

### 1. Helpdesk (`helpdesk` → `ipai_helpdesk`)

**Current parity: ~40% (Live)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Helpdesk Teams | `ipai_helpdesk` team model | Live | Basic — needs assignment rules |
| Receiving Tickets (email, web, live chat) | `ipai_helpdesk` + `mail.thread` | Partial | Missing: live chat channel, web form portal |
| Help Center (knowledge base) | `ipai_knowledge_base` | Planned | 0% — module does not exist |
| SLA Policies (response/resolution time) | `ipai_helpdesk` SLA model | Partial | Exists but lacks escalation actions |
| SLA Reporting & Dashboards | Superset | Scaffolded | Needs Gold views for SLA metrics |
| Customer Ratings | `rating.mixin` (CE) | Available | Wire into `ipai_helpdesk` |
| After-Sales (returns, repairs, coupons) | — | Planned | Requires `ipai_after_sales` or OCA |
| Close Tickets (auto-close timer) | — | Missing | Implement `ir.cron` for auto-close |
| Track & Bill Time (timesheet on ticket) | `hr_timesheet` (CE) + custom | Missing | Link timesheet to helpdesk.ticket |
| Merge Tickets | — | Missing | Dedup action on helpdesk.ticket |
| Convert Ticket to Opportunity | — | Missing | CRM bridge action |
| Automatic Assignment (load-balanced) | — | Missing | Round-robin / least-load algo |
| Canned Responses | `mail.shortcode` (CE) | Available | Configure for helpdesk context |

**Priority actions to reach 80%:**
1. SLA escalation actions (cron + mail.activity)
2. Auto-close timer (`ir.cron`)
3. Timesheet on ticket (link `account.analytic.line`)
4. Merge tickets action
5. Customer rating wiring (`rating.mixin`)

### 2. Project (`project` — CE module, EE enhancements)

**Current parity: ~70% (CE base is strong)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Project Dashboard | CE `project` | Available | Basic — EE adds profitability |
| Project Profitability | `ipai_finance_ppm` | Live (~40%) | Needs margin calc from timesheets + invoices |
| Project Milestones | CE 19.0 `project.milestone` | Available | Native in CE 19 |
| Project Templates | CE `project.project` + `use_tasks` | Available | Native copy |
| Task Stages & Statuses | CE `project.task.type` | Available | Native |
| Recurring Tasks | CE `project.task` recurrence | Available | Native in CE 19 |
| Sub-tasks | CE `project.task` parent_id | Available | Native |
| Task Dependencies | CE `project.task` `depend_on_ids` | Available | Native in CE 19 |
| Burndown Chart | — | Missing | Superset dashboard from Gold views |
| Customer Portal (task visibility) | CE `portal` | Available | Native |

**Priority actions:**
1. Project Profitability → connect `ipai_finance_ppm` to timesheet cost + invoice revenue
2. Burndown chart → Superset Gold view

### 3. Timesheets (`hr_timesheet` — CE module, `timesheet_grid` — EE)

**Current parity: ~50% (CE base + grid gap)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Basic Timesheet Entry | `hr_timesheet` (CE) | Available | Native |
| Timesheet Grid View | `ipai_timesheet` | Planned (0%) | EE grid view — build with OWL |
| Billing Rates | CE `project.sale.line.employee.map` | Available | Native |
| Leaderboard | — | Missing | Superset dashboard |
| Timer (start/stop) | — | Missing | OWL widget for `account.analytic.line` |
| Time Off Entries in Timesheet | `hr_holidays` + `hr_timesheet` | Partial | CE has basic, EE adds auto-fill |
| Timesheet Validation | OCA `hr_timesheet_sheet` | OCA | Adopt from OCA |
| Manager Approval | OCA `hr_timesheet_sheet` | OCA | Adopt from OCA |

**Priority actions:**
1. Adopt OCA `hr_timesheet_sheet` for validation/approval
2. Build grid view widget (`ipai_timesheet`) or adopt OCA `hr_timesheet_sheet`
3. Timer widget (OWL component)

### 4. Planning (`planning` → `ipai_planning`)

**Current parity: 0% (Planned)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Shift Planning (Gantt) | `ipai_planning` | Planned | Full build needed |
| Resource Allocation | — | Planned | Model: `planning.slot` equivalent |
| Role-based Scheduling | — | Planned | `planning.role` model |
| Recurring Shifts | — | Planned | Recurrence on planning.slot |
| Copy Previous Week | — | Planned | Action method |
| Send Schedule to Employees | — | Planned | `mail.template` + cron |
| Open Shifts (self-assign) | — | Planned | Portal + state machine |
| Gantt View | OCA or OWL | Planned | Most complex piece — OWL Gantt |
| Forecasting | — | Planned | Superset + ML (future) |

**Priority actions (P1 — needed for operations):**
1. Core `planning.slot` model with employee + project + datetime
2. List/Kanban views (skip Gantt initially — use calendar view)
3. Recurring shifts via `ir.cron`
4. Email schedule digest

### 5. Field Service (`industry_fsm` → `ipai_field_service`)

**Current parity: 0% (Planned)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Field Service Tasks | `project.task` + location fields | Planned | Extend project.task |
| Worksheets (digital forms) | — | Planned | Dynamic form builder |
| Product Management (on-site) | `sale.order` from task | Planned | Action to create SO from task |
| Itinerary Planning | — | Planned | Map integration or calendar |
| Time Tracking (on-site) | `hr_timesheet` | Available | Wire to FSM task |
| Signature Capture | `ipai_sign` | Live (~20%) | Extend for FSM |

**Priority: P3 (future roadmap) — not blocking operations.**

### 6. Appointments (`appointment` — EE)

**Current parity: 0% (Planned, P3)**

| EE Feature | CE/OCA/IPAI Replacement | Status | Gap |
|---|---|---|---|
| Online Booking | OCA `website_booking` or custom | Planned | Portal calendar widget |
| Calendar Sync | CE `calendar` | Available | Native Google/Outlook sync |
| Appointment to Opportunity | CRM bridge | Planned | `crm.lead.create()` action |
| Resource Slots | — | Planned | Availability model |

---

## SSOT/SOR Mapping

| Entity | SOR | SSOT | Analytics |
|---|---|---|---|
| `helpdesk.ticket` | Odoo PG | Odoo | Gold: `helpdesk_sla_summary` |
| `project.task` | Odoo PG | Odoo | Gold: `project_profitability` |
| `account.analytic.line` (timesheets) | Odoo PG | Odoo | Gold: `timesheet_utilization` |
| `planning.slot` | Odoo PG | Odoo | Gold: `planning_coverage` |
| SLA metrics | Derived | Superset | Gold: `sla_compliance_rate` |

---

## ETL Pipeline Integration

These entities feed the full ETL pipeline:

```
Odoo PG (SOR) → Supabase ETL (CDC/Iceberg) → ADLS Bronze → Databricks DLT Silver → Gold → AI/BI Dashboard
```

### Supabase ETL Config Pattern (extend `odoo-expense.toml`)

```toml
[source.odoo_services]
type = "postgres"
publication = "odoo_services_pub"

[[source.odoo_services.tables]]
schema = "public"
table = "helpdesk_ticket"
columns = ["id", "name", "team_id", "user_id", "partner_id", "stage_id", "priority", "sla_deadline", "create_date", "close_date", "write_date"]

[[source.odoo_services.tables]]
schema = "public"
table = "project_task"
columns = ["id", "name", "project_id", "user_ids", "stage_id", "date_deadline", "planned_hours", "effective_hours", "remaining_hours", "create_date", "write_date"]

[[source.odoo_services.tables]]
schema = "public"
table = "account_analytic_line"
columns = ["id", "name", "project_id", "task_id", "employee_id", "unit_amount", "date", "amount", "create_date"]
```

### Gold Views for AI/BI Dashboard

```sql
-- Helpdesk SLA Compliance
CREATE OR REPLACE VIEW ipai_gold.services.helpdesk_sla_summary AS
SELECT
    DATE_TRUNC('week', ht.create_date) AS period,
    hst.name AS team_name,
    COUNT(*) AS total_tickets,
    COUNT(*) FILTER (WHERE ht.close_date <= ht.sla_deadline) AS sla_met,
    ROUND(100.0 * COUNT(*) FILTER (WHERE ht.close_date <= ht.sla_deadline) / NULLIF(COUNT(*), 0), 1) AS sla_rate
FROM ipai_silver.odoo.helpdesk_ticket ht
JOIN ipai_silver.odoo.helpdesk_team hst ON ht.team_id = hst.id
GROUP BY 1, 2;

-- Timesheet Utilization
CREATE OR REPLACE VIEW ipai_gold.services.timesheet_utilization AS
SELECT
    DATE_TRUNC('month', aal.date) AS period,
    he.name AS employee_name,
    SUM(aal.unit_amount) AS logged_hours,
    160.0 AS capacity_hours,  -- configurable
    ROUND(100.0 * SUM(aal.unit_amount) / 160.0, 1) AS utilization_pct
FROM ipai_silver.odoo.account_analytic_line aal
JOIN ipai_silver.odoo.hr_employee he ON aal.employee_id = he.id
WHERE aal.project_id IS NOT NULL
GROUP BY 1, 2;

-- Project Profitability
CREATE OR REPLACE VIEW ipai_gold.services.project_profitability AS
SELECT
    pp.name AS project_name,
    SUM(aal.unit_amount) AS total_hours,
    SUM(aal.amount) AS total_cost,
    COALESCE(SUM(sol.price_subtotal), 0) AS total_revenue,
    COALESCE(SUM(sol.price_subtotal), 0) + SUM(aal.amount) AS margin
FROM ipai_silver.odoo.project_project pp
LEFT JOIN ipai_silver.odoo.account_analytic_line aal ON aal.project_id = pp.id
LEFT JOIN ipai_silver.odoo.sale_order_line sol ON sol.project_id = pp.id
GROUP BY 1;
```

---

## Odoo-Native Workflow Primitives

Per feedback memory: copilot triggers Odoo-native workflow primitives, never replaces them.

| Primitive | Used By | Pattern |
|---|---|---|
| `project.task.type` (stages) | Project, Helpdesk, Planning | Kanban columns = stage progression |
| `mail.activity` | All services | Scheduled actions with deadline |
| `mail.thread` | All services | Chatter for audit trail |
| `rating.mixin` | Helpdesk | Customer satisfaction after close |
| `ir.cron` | Auto-close, recurring, digest | Scheduled background jobs |
| `mail.template` | Notifications | Email templates for state changes |

---

## When to use this skill

- Building any `ipai_helpdesk`, `ipai_planning`, `ipai_timesheet`, `ipai_field_service` module
- Planning EE parity sprints for Services vertical
- Designing Gold views for services analytics (AI/BI Dashboard)
- Extending Supabase ETL CDC to capture services entities
- Estimating parity score for Services domain

## When NOT to use this skill

- Finance/Accounting parity → use `bir-tax-filing` or `finance-month-end` skills
- Marketing/CRM parity → separate skill needed
- Studio/Customization parity → separate skill needed
