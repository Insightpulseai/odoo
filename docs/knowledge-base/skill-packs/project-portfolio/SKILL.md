# Skill Pack: Project Portfolio Management

## Scope

Project lifecycle management from opportunity through delivery and billing.
Covers resource planning, timesheet capture, milestone-based invoicing, earned value
analysis, and portfolio-level health dashboards. Targets parity with SAP PS
(Project System) and SAP PPM (Portfolio and Project Management) using Odoo 18 CE + OCA.

---

## Concepts

| Concept | SAP Equivalent | Odoo 18 CE Surface |
|---------|---------------|---------------------|
| Project | WBS Element | `project.project` |
| Task / Work Package | Network Activity | `project.task` |
| Timesheet Entry | CATS (Time Sheet) | `account.analytic.line` |
| Analytic Account | Cost Center / WBS | `account.analytic.account` |
| Milestone Billing | Billing Plan | `sale.order.line` (delivered qty) |
| Resource Allocation | Capacity Planning | `resource.resource` + `resource.calendar` (no `planning.slot` in CE — EE only) |
| Earned Value | EVA in PS | Computed from planned vs. actual cost on analytic |
| Portfolio | Portfolio in PPM | Tag/category grouping on `project.project` |

---

## Must-Know Vocabulary

- **EV (Earned Value)**: Budgeted cost of work actually performed.
- **PV (Planned Value)**: Budgeted cost of work scheduled to date.
- **AC (Actual Cost)**: Real cost incurred (timesheets + expenses + vendor bills).
- **CPI (Cost Performance Index)**: EV / AC. Below 1.0 = over budget.
- **SPI (Schedule Performance Index)**: EV / PV. Below 1.0 = behind schedule.
- **SOW (Statement of Work)**: Contractual deliverable scope tied to a sale order.
- **WBS (Work Breakdown Structure)**: Hierarchical decomposition; maps to task tree.
- **T&M (Time and Materials)**: Billing model where invoices follow timesheets.
- **Fixed Price / Milestone**: Billing model where invoices follow deliverable acceptance.
- **Burn Rate**: Cost per unit time; derived from analytic line aggregation.

---

## Core Workflows

### 1. Project Creation from Sales Order

```
sale.order (service product, service_policy='delivered_timesheet')
  -> confirm -> project.project auto-created
  -> project.task created per SO line (if configured)
  -> analytic account linked to project
```

Key fields on `product.template`: `type='service'`, `service_tracking='task_in_project'`,
`service_policy='delivered_timesheet'` (T&M) or `'delivered_manual'` (milestone).

### 2. Task Decomposition and Planning

- Create parent tasks (phases) with child tasks (work packages).
- Assign `allocated_hours` per task for EV baseline (no `planned_hours` field in CE).
- Use `project.tags` for cross-project categorization.
- OCA `project_timeline` adds Gantt-style date ranges (`date_start`, `date_end`).
- OCA `project_task_code` auto-generates unique task references (e.g., PRJ-001-T042).

### 3. Timesheet Capture

- Users log time via `hr.timesheet` (writes to `account.analytic.line`).
- Fields: `employee_id`, `project_id`, `task_id`, `unit_amount` (hours), `date`.
- Manager approval via `timesheet.validation` (OCA `hr_timesheet_sheet`).
- Approved timesheets feed into invoicing and cost reporting.

### 4. Milestone Billing

- Create SO lines with `product.template.service_policy = 'delivered_manual'`.
- Project manager marks milestones as delivered (updates `qty_delivered`).
- Finance creates invoice from SO: only delivered milestones appear.
- Native `project.project.stage_id` provides stage-gate tracking. No `project_status` OCA module exists.

### 5. Earned Value Computation

```
PV  = sum(allocated_hours * standard_cost_rate) for tasks due by today
EV  = sum(allocated_hours * standard_cost_rate * completion_pct / 100)  # requires custom progress field
AC  = sum(analytic_line.amount) where account = project.analytic_account_id
CPI = EV / AC
SPI = EV / PV
```

No native EV module exists in CE. Implement via `ipai_project_ev` custom module
or spreadsheet formulas over analytic data.

---

## Edge Cases

1. **Multi-company projects**: Analytic accounts must respect `company_id`. Use
   `analytic.plan` (18.0) to separate cost flows per entity.
2. **Rework / negative progress**: Task progress should never decrease without
   a documented change order. Add a `project.task.change_order` model if needed.
3. **Timesheet on closed tasks**: Default Odoo allows it. Add a server action or
   constraint to block timesheets on tasks with `stage_id.fold = True`.
4. **Currency mismatch**: Service SO in USD, timesheets costed in PHP. Ensure
   analytic lines use the company currency; currency conversion happens at SO level.
5. **Resource over-allocation**: No native capacity check in CE. Planning module is
   EE-only. No `project_forecast` OCA module exists. Requires custom implementation.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Timesheet approval gate | OCA `hr_timesheet_sheet` with manager approval workflow |
| Budget ceiling enforcement | `account.analytic.account` with `crossovered_budget` lines |
| Change order audit trail | `mail.tracking.value` on task fields (hours, deadline, stage) |
| Segregation of duties | PM approves timesheets, Finance approves invoices (separate groups) |
| SOX-style project close | Custom stage with checklist: deliverables signed, timesheets approved, final invoice sent |

---

## Odoo/OCA Implementation Surfaces

| Module | Source | Purpose |
|--------|--------|---------|
| `project` | Core | Project and task management |
| `hr_timesheet` | Core | Timesheet entry on tasks |
| `sale_timesheet` | Core | Link SO lines to projects/tasks, T&M invoicing |
| `sale_project` | Core | Project creation from sales orders |
| `analytic` | Core | Cost tracking and reporting |
| `project_timeline` | OCA | Gantt-style date range on tasks |
| `project_task_code` | OCA | Auto-generated task reference codes |
| `project_milestone_status` | OCA | Milestone status tracking |
| `hr_timesheet_sheet` | OCA | Timesheet approval sheets |
| `project_template` | OCA | Reusable project templates |
| `project_task_default_stage` | OCA | Default stages per project type |
| `ipai_project_ev` | Custom | Earned value computation and dashboard |

---

## Azure/Platform Considerations

- **Databricks**: Pull analytic line data via JDBC for portfolio-level EV dashboards
  and trend analysis across 50+ projects. Materialized views refresh nightly.
- **Power BI**: Connect to Databricks lakehouse for executive portfolio health
  scorecards (CPI/SPI heatmaps, burn-rate trends, resource utilization).
- **Azure DevOps**: Sync project tasks to ADO work items for engineering teams
  via `ipai_devops_sync` (webhook-based, not polling).
- **Document Intelligence**: Extract SOW deliverables from signed PDFs into
  milestone task lists automatically.

---

## Exercises

### Exercise 1: T&M Project Setup
Create a service product "Consulting Hours" with `service_tracking='task_in_project'`
and `service_policy='delivered_timesheet'`. Create a sale order for 100 hours at
PHP 5,000/hr. Confirm. Verify: project auto-created, analytic account linked,
task exists. Log 8 hours of timesheet. Create invoice. Verify invoice amount = PHP 40,000.

### Exercise 2: Milestone Billing
Create 3 SO lines: "Discovery" (PHP 200,000), "Build" (PHP 500,000), "UAT" (PHP 150,000).
Set `service_policy='delivered_manual'`. Confirm SO. Mark "Discovery" as delivered
(`qty_delivered=1`). Invoice. Verify only PHP 200,000 invoiced. Mark "Build" delivered.
Invoice again. Verify cumulative PHP 700,000.

### Exercise 3: Earned Value Report
Set up a project with 5 tasks, each with `planned_hours`. Log partial timesheets.
Write a SQL query or spreadsheet formula that computes PV, EV, AC, CPI, SPI from
`account_analytic_line` and `project_task`. Verify CPI < 1.0 when actual hours exceed plan.

### Exercise 4: Timesheet Approval Flow
Install `hr_timesheet_sheet`. Configure weekly sheets. Submit a sheet as employee.
Approve as manager. Verify approved timesheets cannot be edited. Attempt to invoice
unapproved timesheets and confirm they are excluded.

---

## Test Prompts for Agents

1. "Create a fixed-price project with 3 milestones from a sales order. The client
   is ACME Corp, total value PHP 850,000. Show me the project, tasks, and analytic account."

2. "The project PRJ-042 is 60% complete but we have spent 80% of the budget.
   Calculate the CPI and SPI and recommend corrective action."

3. "Block timesheet entries on tasks that are in the Done or Cancelled stage.
   Implement as a Python constraint on account.analytic.line."

4. "Generate a portfolio summary showing all active projects with their budget
   utilization percentage, sorted by CPI ascending (worst-performing first)."

5. "A client wants to switch from T&M to fixed-price mid-project. What is the
   migration path in Odoo? Handle the partially-invoiced timesheets."
