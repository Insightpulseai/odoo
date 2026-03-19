# Odoo → Supabase Schema Mapping

This document maps Odoo 18 CE + OCA modules to our Supabase domain schemas.

---

## Mapping Format

| odoo_module | our_schema | our_tables | ipai_meta_module | coverage_status |
|-------------|------------|------------|------------------|-----------------|

---

## Core / Base

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| base | core | core.company, core.app_user | ipai_core | canonical |
| res_company | core | core.company | ipai_core | canonical |
| res_users | core | core.app_user, core.role | ipai_core | canonical |
| res_partner | crm | crm.partner | ipai_crm | partial |

---

## Sales & CRM

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| crm | crm | crm.partner, crm.lead, crm.activity | ipai_crm | partial |
| sale | sales | sales.order, sales.order_line, sales.pricelist | ipai_sales | partial |
| sale_subscription | saas | saas.plan, saas.subscription, saas.subscription_usage | ipai_saas | canonical |

---

## Finance / Accounting

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| account | finance | finance.account, finance.journal, finance.move, finance.move_line, finance.invoice | ipai_finance | partial |
| account_tax | finance | finance.tax_code, finance.tax_mapping | ipai_finance | partial |
| l10n_ph (BIR) | finance | finance.bir_filing_audit, finance.bir_schedule_template | ipai_finance_ph | partial |

---

## HR & Expense

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| hr | hr | hr.employee, hr.department, hr.contract | ipai_hr | partial |
| hr_expense | expense | expense.expense_report, expense.expense_line, expense.cash_advance | ipai_expense | canonical |
| hr_holidays | hr | hr.leave | ipai_hr | partial |
| hr_timesheet | projects | projects.timesheet | ipai_projects | partial |

---

## Projects / PPM

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| project | projects | projects.project, projects.task | ipai_projects | partial |
| project_budget | projects | projects.project_budget, projects.project_budget_line | ipai_ppm | partial |

---

## Purchase & Rates

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| purchase | rates | rates.rate_cards, rates.rate_card_items | ipai_rates | partial |
| product | inventory | inventory.product, inventory.product_category | ipai_inventory | partial |

---

## Inventory & Maintenance

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| stock | inventory | inventory.stock_location, inventory.stock_move, inventory.stock_quant | ipai_inventory | partial |
| maintenance | maintenance | maintenance.plan, maintenance.job | ipai_maintenance | partial |

---

## Helpdesk & Website

| Odoo Module | Our Schema | Our Tables | ipai Module | Coverage |
|-------------|------------|------------|-------------|----------|
| helpdesk | helpdesk | helpdesk.team, helpdesk.ticket, helpdesk.stage | ipai_helpdesk | planned |
| website | cms | cms.page, cms.menu, cms.form | ipai_cms | planned |

---

## Smart Delta Pattern

For each domain table, we extend Odoo base with:
- `tenant_id` (multi-tenant SaaS)
- `engine_source` (TE-Cheq, Retail-Intel, manual, API)
- `ai_explanation` (JSONB, LLM summary for anomalies)

### Example: expense.expense_reports

**Base**: OCA hr_expense sheet + account.move

**Smart Delta**:
- `tenant_id` (multi-tenant SaaS)
- `engine_source` (TE-Cheq, manual, API)
- `ai_explanation` (JSONB, LLM summary of anomalies)
- `policy_violations` (JSONB, automated policy check results)

---

## Odoo 18 CE / OCA Parity Checklist

- [x] expense.expense_reports ~= hr_expense + account_move mapping (OCA)
- [ ] projects.projects ~= project.project (OCA project)
- [ ] rates.rate_cards ~= sale_pricelist / sale_order_line price logic
- [ ] finance.bir_* aligned with account_tax / account_move in OCA Tax modules

**Breaking rule**: No engine may introduce a data model that cannot be mapped back to an OCA-compatible module.
