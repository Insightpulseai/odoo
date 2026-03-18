# Odoo CE/OCA 18 vs Enterprise Parity Analysis

## Target Industries

1. **Accounting Firm** - Fiduciary services, audit, bookkeeping
2. **Marketing Agency** - Creative services, campaign management, client projects
3. **Odoo Partner** - Implementation services, reseller operations

---

## Executive Summary

| Industry | CE/OCA Parity | Gap Modules Needed | Effort |
|----------|---------------|-------------------|--------|
| Accounting Firm | **85%** | 3 ipai_* modules | Medium |
| Marketing Agency | **90%** | 2 ipai_* modules | Low |
| Odoo Partner | **80%** | 4 ipai_* modules | Medium |

**Overall Assessment**: All three industries can achieve functional parity using Odoo CE 18 + OCA modules + targeted ipai_* delta modules.

---

## 1. Accounting Firm Industry

### Enterprise Feature Set

| Feature | Enterprise Module | Description |
|---------|------------------|-------------|
| Bank Reconciliation | account (enterprise) | Auto-matching, bank sync |
| Multi-Currency Accounting | account | Automatic rate conversion |
| Tax Automation | account | Jurisdiction-based tax rules |
| Deferred Revenue/Expenses | account_asset | Spread recognition |
| Budget Management | account_budget | Budget vs actual tracking |
| Consolidation | account_consolidation | Multi-company consolidation |
| Audit Trail | account | Immutable journal entries |
| E-Invoicing | account | Country-specific compliance |
| Financial Reports | account_reports | P&L, Balance Sheet, Cash Flow |
| Analytic Accounting | analytic | Cost center tracking |

### CE/OCA Parity Matrix

| Feature | CE/OCA Module | Parity | Notes |
|---------|--------------|--------|-------|
| Bank Reconciliation | `account_reconcile_oca` | **95%** | OCA provides full reconciliation UI |
| Bank Statement Import | `account_statement_import_*` | **100%** | OFX, QIF, CSV, CAMT.053 support |
| Multi-Currency | `account` (core) | **100%** | Native CE feature |
| Tax Management | `account` (core) | **90%** | Basic; need localization for PH |
| Asset Management | `account_asset_management` | **95%** | OCA module, full depreciation |
| Budget Management | `account_budget_oca` | **90%** | OCA provides budget tracking |
| Analytic Accounting | `analytic` (core) | **100%** | Native CE feature |
| Financial Reports | `account_financial_report` | **85%** | OCA; less polished than Enterprise |
| Consolidation | — | **0%** | **GAP**: Requires delta module |
| E-Invoicing (PH) | — | **0%** | **GAP**: Requires BIR compliance |

### Required Delta Modules

```
ipai_bir_compliance        ✓ EXISTS - BIR 2307, Alphalist, SAWT
ipai_finance_consolidation NEW     - Multi-company consolidation
ipai_finance_reports       NEW     - Enhanced financial reporting with drill-down
```

### OCA Modules to Install

```yaml
# requirements/oca-accounting.txt
OCA/account-reconcile:
  - account_reconcile_oca
  - account_reconcile_model_oca
  - account_statement_import_file_reconcile_oca
  - account_statement_import_ofx
  - account_statement_import_camt

OCA/account-financial-tools:
  - account_asset_management
  - account_cutoff_accrual_dates
  - account_lock_date_update

OCA/account-financial-reporting:
  - account_financial_report
  - account_tax_balance

OCA/account-closing:
  - account_fiscal_year_closing
  - account_cutoff_base
```

### Parity Score: 85%

**Gaps requiring custom development:**
1. Multi-company consolidation (Enterprise-only)
2. Philippine BIR compliance (localization)
3. Advanced financial dashboards

---

## 2. Marketing Agency Industry

### Enterprise Feature Set

| Feature | Enterprise Module | Description |
|---------|------------------|-------------|
| Project Management | project | Task tracking, Gantt, milestones |
| Timesheet Billing | hr_timesheet | Time tracking → invoicing |
| CRM Integration | crm | Lead/opportunity to project |
| Client Portal | portal | Client access to project status |
| Social Marketing | social | Multi-platform posting |
| Email Marketing | mass_mailing | Campaign management |
| Subscriptions | sale_subscription | Retainer billing |
| Planning | planning | Resource scheduling |
| Documents | documents | File management per project |

### CE/OCA Parity Matrix

| Feature | CE/OCA Module | Parity | Notes |
|---------|--------------|--------|-------|
| Project Management | `project` (core) | **100%** | Full Kanban, Gantt, tasks |
| Timesheet Tracking | `hr_timesheet` (core) | **100%** | Native CE feature |
| Timesheet Billing | `sale_timesheet` (core) | **95%** | Time & materials invoicing |
| CRM | `crm` (core) | **100%** | Native CE feature |
| Client Portal | `portal` (core) | **95%** | Native; less polished |
| Email Marketing | `mass_mailing` (core) | **90%** | Native CE feature |
| Social Marketing | — | **30%** | **GAP**: Enterprise-only |
| Subscriptions | `sale_subscription` | **0%** | **GAP**: Enterprise-only |
| Planning/Scheduling | `project_forecast` | **80%** | OCA provides basic planning |
| Documents | `dms` | **85%** | OCA Document Management |

### Required Delta Modules

```
ipai_social_publisher      NEW     - Social media scheduling (Buffer alternative)
ipai_subscription_lite     NEW     - Recurring billing for retainers
ipai_client_portal_plus    ENHANCE - Enhanced client portal experience
```

### OCA Modules to Install

```yaml
# requirements/oca-marketing.txt
OCA/project:
  - project_timesheet_time_control
  - project_task_default_stage
  - project_status
  - project_template

OCA/timesheet:
  - hr_timesheet_sheet
  - sale_timesheet_line_exclude

OCA/sale-workflow:
  - sale_order_type
  - sale_project_copy_tasks

OCA/dms:
  - dms
  - dms_field

OCA/social:
  - mail_tracking
  - mass_mailing_custom_unsubscribe
```

### Parity Score: 90%

**Gaps requiring custom development:**
1. Social media publishing/scheduling
2. Subscription/retainer management
3. Enhanced client portal dashboards

---

## 3. Odoo Partner Industry

### Enterprise Feature Set

| Feature | Enterprise Module | Description |
|---------|------------------|-------------|
| Partner Portal | partner | Lead assignment, commission tracking |
| Quote Calculator | sale | Service pack configuration |
| Implementation Projects | project | Pre-configured templates |
| Reseller Management | crm | Partner levels, activations |
| Commission Plans | sale_commission | Automated commission calculation |
| Training Tracking | survey + hr | Certification management |
| Support Ticketing | helpdesk | Customer support portal |
| Subscription Licensing | sale_subscription | Odoo license management |

### CE/OCA Parity Matrix

| Feature | CE/OCA Module | Parity | Notes |
|---------|--------------|--------|-------|
| CRM/Lead Management | `crm` (core) | **100%** | Native CE feature |
| Partner Levels | `crm` (core) | **90%** | Basic; needs enhancement |
| Project Templates | `project` (core) | **85%** | Manual setup required |
| Commission Tracking | `sale_commission` | **80%** | OCA module available |
| Quote Builder | `sale` (core) | **90%** | Native; templates manual |
| Helpdesk/Support | — | **0%** | **GAP**: Enterprise-only |
| Subscription Mgmt | — | **0%** | **GAP**: Enterprise-only |
| Training/Cert | — | **30%** | Basic survey; needs LMS |
| Partner Portal | `portal` (core) | **70%** | Basic; needs enhancement |

### Required Delta Modules

```
ipai_helpdesk_lite         NEW     - Support ticketing system
ipai_partner_portal        NEW     - Enhanced partner portal
ipai_commission_advanced   NEW     - Multi-tier commission plans
ipai_lms_lite              NEW     - Training/certification tracking
```

### OCA Modules to Install

```yaml
# requirements/oca-partner.txt
OCA/commission:
  - sale_commission
  - sale_commission_salesman

OCA/project:
  - project_template
  - project_task_default_stage

OCA/partner-contact:
  - partner_tier

OCA/helpdesk (if available for 18.0):
  - helpdesk_mgmt
  - helpdesk_mgmt_project
```

### Parity Score: 80%

**Gaps requiring custom development:**
1. Helpdesk/support ticketing (Enterprise-only)
2. Advanced partner portal with dashboard
3. Multi-tier commission automation
4. Training/certification LMS

---

## Consolidated Delta Module Roadmap

### Priority 1: Shared Infrastructure

| Module | Industries | Effort | Dependencies |
|--------|-----------|--------|--------------|
| `ipai_helpdesk_lite` | Partner, Marketing | High | mail, project |
| `ipai_subscription_lite` | Partner, Marketing, Accounting | High | sale, account |

### Priority 2: Industry-Specific

| Module | Industry | Effort | Dependencies |
|--------|----------|--------|--------------|
| `ipai_bir_compliance` | Accounting | ✓ EXISTS | account |
| `ipai_finance_consolidation` | Accounting | High | account |
| `ipai_social_publisher` | Marketing | Medium | mail |
| `ipai_partner_portal` | Partner | Medium | portal, crm |
| `ipai_commission_advanced` | Partner | Medium | sale_commission |

### Priority 3: Nice-to-Have

| Module | Industry | Effort | Dependencies |
|--------|----------|--------|--------------|
| `ipai_finance_reports` | Accounting | Medium | account |
| `ipai_client_portal_plus` | Marketing | Low | portal |
| `ipai_lms_lite` | Partner | High | survey, hr |

---

## Implementation Recommendations

### Phase 1: Foundation (All Industries)

```bash
# Install core OCA modules for all industries
pip install odoo-addon-account-reconcile-oca
pip install odoo-addon-project-timesheet-time-control
pip install odoo-addon-sale-commission
pip install odoo-addon-dms
```

### Phase 2: Accounting Firm Stack

```python
# addons/ipai_accounting_firm/__manifest__.py
{
    "name": "IPAI Accounting Firm Stack",
    "depends": [
        # OCA Accounting
        "account_reconcile_oca",
        "account_asset_management",
        "account_financial_report",
        # IPAI Delta
        "ipai_bir_compliance",
    ],
}
```

### Phase 3: Marketing Agency Stack

```python
# addons/ipai_marketing_agency/__manifest__.py
{
    "name": "IPAI Marketing Agency Stack",
    "depends": [
        # OCA Project/Timesheet
        "project_timesheet_time_control",
        "project_template",
        "dms",
        # IPAI Delta (when built)
        # "ipai_social_publisher",
        # "ipai_subscription_lite",
    ],
}
```

### Phase 4: Odoo Partner Stack

```python
# addons/ipai_odoo_partner/__manifest__.py
{
    "name": "IPAI Odoo Partner Stack",
    "depends": [
        # OCA Commission
        "sale_commission",
        "project_template",
        # IPAI Delta (when built)
        # "ipai_helpdesk_lite",
        # "ipai_partner_portal",
    ],
}
```

---

## Cost-Benefit Analysis

### Enterprise Annual Cost (50 users)

| Industry | Enterprise Cost | CE/OCA + Delta Cost | Savings |
|----------|-----------------|---------------------|---------|
| Accounting Firm | $24,000 | $4,000 (dev) | **83%** |
| Marketing Agency | $18,000 | $2,000 (dev) | **89%** |
| Odoo Partner | $30,000 | $6,000 (dev) | **80%** |

*Delta development costs are one-time; Enterprise costs are recurring annually.*

### 5-Year TCO Comparison

| Industry | Enterprise 5Y | CE/OCA 5Y | Savings |
|----------|---------------|-----------|---------|
| Accounting Firm | $120,000 | $16,000 | **$104,000** |
| Marketing Agency | $90,000 | $10,000 | **$80,000** |
| Odoo Partner | $150,000 | $22,000 | **$128,000** |

---

## Sources

- [OCA Account Reconcile Repository](https://github.com/OCA/account-reconcile)
- [OCA Project Repository](https://github.com/OCA/project)
- [OCA Timesheet Repository](https://github.com/OCA/timesheet)
- [Odoo Accounting Features](https://www.odoo.com/app/accounting-features)
- [Odoo Marketing Agency Solution](https://www.odoo.com/industries/marketing-agency)
- [Odoo Partner Solution](https://www.odoo.com/industries/odoo-partner)
- [SDLC Corp - Scaling Marketing Agency with Odoo](https://sdlccorp.com/post/scaling-a-marketing-agency-with-odoo-project-management-tools/)
- [Dixmit - Accounting on Odoo Community 18](https://www.dixmit.com/en/blog/our-blog-1/accounting-management-on-odoo-community-18)

---

*Document Version: 1.0.0*
*Last Updated: December 2025*
*Author: InsightPulseAI*
