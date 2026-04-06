# Management Accounting Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: CO (Controlling)

---

## Scope

Internal management reporting: cost centers, profit centers, analytic plans, budget vs
actual analysis, variance reporting, cost allocation, and KPI dashboards. Covers the
controlling backbone for enterprise decision-making on Odoo 18 CE, using analytic
accounting and OCA MIS Builder as the primary reporting engine.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| Cost Center | CO-CCA (Cost Center Accounting) | `account.analytic.account` within a plan |
| Profit Center | EC-PCA (Profit Center Accounting) | `account.analytic.account` (revenue-bearing plan) |
| Analytic Plan | CO Controlling Area | `account.analytic.plan` |
| Cost Element | Primary/Secondary Cost Element | `account.account` (P&L accounts) |
| Internal Order | CO Internal Order | `account.analytic.account` (project/campaign plan) |
| Budget | CO Budget (KO22) | OCA `mis_builder_budget` |
| Variance Analysis | CO-PC Variance (KKS2) | MIS Builder: actual vs budget columns |
| Allocation | CO Assessment/Distribution | Manual journal entries or `ipai_*` allocation engine |
| Activity-Based Costing | CO-OM-ABC | Analytic tags + MIS Builder formulas |
| Management Report | CO-PA (Profitability) | OCA `mis_builder` report instances |

---

## Must-Know Vocabulary

- **account.analytic.plan**: Odoo 18 multi-plan structure. Each plan is a dimension
  (e.g., Department, Project, Product Line). Replaces the flat analytic account model.
- **account.analytic.account**: An account within a plan. Can represent a cost center,
  profit center, project, or campaign depending on the plan it belongs to.
- **account.analytic.line**: Individual analytic posting. Created automatically when a
  journal entry line has analytic distribution. Contains amount, date, account, plan.
- **account.analytic.distribution.model**: Default analytic distribution rules applied
  automatically to journal entries based on conditions (account, partner, product).
- **Analytic distribution**: JSON field on `account.move.line` storing the percentage
  split across analytic accounts. Format: `{"analytic_account_id": percentage}`.
- **mis.report**: OCA MIS Builder report definition. Rows are KPIs defined as expressions
  (Python/SQL). Columns are periods or data sources.
- **mis.report.instance**: A configured execution of a MIS report with specific date
  ranges, comparison periods, and budget sources.
- **mis.budget**: OCA budget model. Stores planned amounts per analytic account per period.
- **mis.budget.item**: Individual budget line (account, analytic, period, amount).

---

## Core Workflows

### 1. Analytic Plan Setup
1. Define plans in `account.analytic.plan`:
   - **Department**: cost centers (Sales, Engineering, Admin, Operations).
   - **Project**: profit centers or project tracking.
   - **Product Line**: product-level profitability analysis.
2. Create `account.analytic.account` records under each plan.
3. Set `parent_id` to create child plans for hierarchical sub-dimensions.
   (`root_plan_id` on `account.analytic.account` is computed/read-only.)
4. Configure applicability: which plans appear on which document types
   (invoices, POs, timesheets, manual entries).

### 2. Analytic Distribution Configuration
1. Create `account.analytic.distribution.model` rules:
   - "All entries to account 600100 (Office Supplies) -> Department: Admin 100%"
   - "Product Category: Software -> Product Line: SaaS 100%"
   - "Partner: Client A -> Project: Project Alpha 60%, Project Beta 40%"
2. Rules auto-apply when matching conditions are met on journal entry lines.
3. Manual override allowed on individual entries.
4. Distribution percentages must total 100% per plan (Odoo validates).

### 3. Budget Creation (OCA MIS Builder)
1. Install `mis_builder` and `mis_builder_budget`.
2. Create `mis.budget` for fiscal year (e.g., "FY2026 Operating Budget").
3. Add `mis.budget.item` records:
   - Period (month or quarter), analytic account, GL account, planned amount.
4. Budget items map to MIS report KPI expressions for comparison.
5. Multiple budget versions supported (optimistic, conservative, board-approved).

### 4. Budget vs Actual Reporting
1. Create `mis.report` with KPIs:
   - Revenue (sum of income accounts)
   - COGS (sum of cost accounts)
   - Gross Margin (Revenue - COGS)
   - Operating Expenses (by category)
   - Net Income
2. Create `mis.report.instance` with two columns:
   - Column 1: Actual (type=`actuals`, date range=current month/quarter)
   - Column 2: Budget (type=`budget`, source=budget record)
3. Add variance column: formula `(Actual - Budget)` and `(Actual - Budget) / Budget * 100`.
4. Filter by analytic account for department-level or project-level views.

### 5. Cost Allocation
1. **Direct allocation**: Analytic distribution on source transactions (invoices, timesheets).
2. **Step-down allocation**: Service departments (IT, HR) costs distributed to operating
   departments. Implemented as manual journal entries with analytic distribution.
3. **Activity-based**: Use analytic tags to classify cost drivers. MIS Builder formulas
   compute allocated costs based on driver volumes.
4. Monthly allocation entries:
   - Debit: receiving cost center analytic lines
   - Credit: sending cost center analytic lines
   - Net GL impact: zero (same GL account, different analytics)

### 6. Profitability Analysis
1. MIS Builder report by profit center (analytic account in Project or Product Line plan).
2. KPIs: Revenue, Direct Costs, Contribution Margin, Allocated Overhead, Net Margin.
3. Drill-down: from KPI cell to underlying `account.analytic.line` records.
4. Period comparison: current month, YTD, prior year, budget.
5. Export to XLSX for board reporting or push to Databricks for dashboards.

---

## Edge Cases

- **Missing analytic distribution**: Journal entries without analytic distribution are
  invisible to management reports. Enforce via `account.analytic.distribution.model`
  defaults and validation rules.
- **Cross-plan allocation**: An expense belongs to Department A but Project B. Odoo 18
  supports multi-plan distribution: one line can tag multiple plans simultaneously.
- **Budget overrun**: MIS Builder shows variance but does not block transactions. For
  hard budget control, implement validation in `account.move` create/write.
- **Intercompany analytic**: Analytic accounts are company-specific by default. For
  cross-company analysis, use shared analytic plans (`company_id=False`).
- **Timesheet costing**: `hr_timesheet` posts analytic lines with employee cost rate.
  If rates change mid-period, historical lines are not retroactively updated.
- **Rounding in allocation**: Percentage-based allocation across many accounts creates
  rounding differences. Handle with a catch-all "rounding" analytic account.
- **Plan applicability conflicts**: If a plan is not applicable to a document type,
  the distribution field is hidden. Users may skip required tagging.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Mandatory analytic tagging | `account.analytic.distribution.model` defaults + validation on `account.move` |
| Budget approval | Budget records require management sign-off before activation |
| Variance thresholds | MIS Builder conditional formatting. Alert on >10% unfavorable variance |
| Allocation documentation | Monthly allocation journal entries with narration explaining methodology |
| Analytic account lifecycle | Active/inactive flag. Archive completed projects. Never delete. |
| Access control | `analytic.group_analytic_accounting` group. Restrict budget edit to controllers |
| Audit trail | `account.analytic.line` is append-only. Corrections via new entries, not edits |
| Reconciliation | Monthly reconcile analytic totals to GL totals by account type |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `account.analytic.plan` -- dimension definitions (department, project, product line)
- `account.analytic.account` -- individual cost/profit centers within plans
- `account.analytic.line` -- analytic postings (auto-created from journal entries)
- `account.analytic.distribution.model` -- auto-distribution rules
- `account.move.line` -- `analytic_distribution` JSON field for multi-plan tagging
- `account.account` -- GL accounts serving as cost elements

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `mis_builder` | OCA/mis-builder | Flexible management reporting engine |
| `mis_builder_budget` | OCA/mis-builder | Budget data source for MIS reports |
| `mis_builder_demo` | OCA/mis-builder | Sample P&L/BS templates to start from |
| `account_analytic_parent` | OCA/account-analytic | Hierarchical analytic accounts |
| `account_analytic_sequence` | OCA/account-analytic | Auto-numbering for analytic accounts |
| `account_analytic_tag` | OCA/account-analytic | Analytic tagging framework |
| `account_analytic_line_commercial_partner` | OCA/account-analytic | Commercial partner field on analytic lines |
| `account_financial_report` | OCA/account-financial-reporting | Trial balance with analytic filter |

---

## Azure/Platform Considerations

- **MIS Builder performance**: Complex KPI expressions with deep analytic filtering can
  be slow on large datasets. Optimize with PostgreSQL indexes on
  `account_analytic_line(plan_id, account_id, date)`.
- **Budget data entry**: For large budgets (hundreds of cost centers x 12 months), provide
  XLSX import via OCA `mis_builder_budget` import wizard or custom `ipai_*` loader.
- **Dashboard integration**: Extract MIS report data via Odoo `xmlrpc` or direct SQL
  into Databricks for Power BI / Grafana dashboards.
- **Scheduled reports**: Azure Container Apps cron to generate monthly MIS reports and
  email to management via Zoho SMTP.
- **Multi-company controlling**: Shared analytic plans across companies for group-level
  management reporting. Ensure `company_id` handling in MIS expressions.

---

## Exercises

### Exercise 1: Analytic Plan Architecture
Design and implement a three-plan structure: Department (5 cost centers), Project (3
active projects), Product Line (4 lines). Create distribution models that auto-tag:
(a) salary expenses by department, (b) consulting revenue by project, (c) product
sales by product line.

### Exercise 2: Operating Budget
Using MIS Builder, create a 12-month operating budget for FY2026. Define budget items
for: revenue (by product line), COGS, salaries (by department), rent, utilities,
marketing. Total budget: PHP 50M. Verify budget loads correctly in MIS report instance.

### Exercise 3: Budget vs Actual Variance Report
Create a MIS report instance for Q1 2026 with columns: Actual, Budget, Variance (absolute),
Variance (%). Filter by Department plan. Generate the report and identify the top 3
unfavorable variances. Drill down to the underlying transactions.

### Exercise 4: Cost Allocation
IT Department (cost center) spent PHP 500K in March. Allocate to operating departments:
Sales 40%, Engineering 35%, Operations 25%. Create the allocation journal entry with
proper analytic distribution. Verify the receiving departments' cost reports update.

### Exercise 5: Project Profitability
Create a profitability report for Project Alpha using MIS Builder. KPIs: billable revenue,
direct labor (from timesheets), direct expenses, allocated overhead (15% of direct costs),
net margin. Compare against project budget. Determine if the project is profitable.

---

## Test Prompts for Agents

1. "Create an analytic plan called 'Business Unit' with four accounts: Retail, Wholesale,
   E-commerce, and Corporate. Set up distribution models so all sales journal entries
   auto-tag based on the customer's assigned business unit."

2. "Build a MIS Builder report showing departmental P&L: Revenue, Direct Costs, Contribution
   Margin, Allocated Overhead, Net Margin. Configure for Q1 2026 with prior-year comparison."

3. "Enter the FY2026 budget for the Marketing department: PHP 200K/month for digital ads,
   PHP 100K/month for events, PHP 50K/month for content. Show budget vs actual for January."

4. "Allocate shared office rent (PHP 300K/month) across 5 departments based on headcount:
   Sales 12, Engineering 20, Admin 5, Operations 8, Finance 5. Create the monthly entry."

5. "Show the profitability of Product Line A for Q1 2026: revenue, COGS, gross margin,
   allocated SG&A (based on revenue share), net margin. Compare to Product Line B."

6. "Which cost center exceeded its Q1 budget by more than 15%? Show the specific line
   items causing the overrun and suggest corrective actions."

7. "Create a waterfall analysis: start with budgeted net income, show each variance
   (revenue, COGS, opex categories) that bridges to actual net income for March 2026."
