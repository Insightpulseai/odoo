# Odoo 18 Enterprise → CE/OCA Complete Parity Guide

## Executive Summary

This document provides a comprehensive mapping of **ALL** Odoo 18 Enterprise Edition features to their Community Edition (CE) + OCA module equivalents, identifying gaps that require custom `ipai_*` delta modules.

| Category | EE Modules | CE/OCA Covered | Gap (ipai_*) | Parity % |
|----------|------------|----------------|--------------|----------|
| Sales & CRM | 8 | 6 | 2 | 75% |
| Accounting & Finance | 12 | 10 | 2 | 83% |
| Inventory & MRP | 10 | 8 | 2 | 80% |
| Purchase | 5 | 5 | 0 | 100% |
| Human Resources | 9 | 6 | 3 | 67% |
| Project & Services | 7 | 5 | 2 | 71% |
| Marketing | 5 | 2 | 3 | 40% |
| Website & eCommerce | 6 | 5 | 1 | 83% |
| Productivity | 6 | 2 | 4 | 33% |
| **TOTAL** | **68** | **49** | **19** | **72%** |

**With ipai_* delta modules: 95%+ parity achievable**

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Full parity via CE core |
| 🟢 | Full parity via OCA module |
| 🟡 | Partial parity (70-90%) |
| 🔴 | No OCA equivalent - needs ipai_* |
| ⚪ | Low priority / Niche feature |

---

## 1. Sales & CRM

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **CRM** | `crm` (core) | ✅ 100% | Native CE |
| **Sales** | `sale` (core) | ✅ 100% | Native CE |
| **Point of Sale** | `point_of_sale` (core) | ✅ 95% | Native CE; some UX differences |
| **Subscriptions** | — | 🔴 0% | **GAP**: `ipai_subscription` needed |
| **Rental** | `rental_base` (OCA) | 🟢 80% | OCA/rental repository |
| **Amazon Connector** | — | ⚪ 0% | Third-party integrations exist |
| **eBay Connector** | — | ⚪ 0% | Third-party integrations exist |
| **eSign** | `sign` (OCA) | 🟡 70% | OCA/contract; less polished |

### OCA Modules for Sales

```yaml
OCA/sale-workflow:
  - sale_order_type
  - sale_order_line_sequence
  - sale_elaboration
  - sale_automatic_workflow
  - sale_exception

OCA/contract:
  - contract                    # Recurring contracts
  - contract_sale_invoicing

OCA/rental:
  - rental_base
  - rental_pricelist
```

### Required ipai_* Modules

```
ipai_subscription          NEW - Recurring billing, MRR tracking
ipai_esign                 NEW - Digital signature workflows
```

---

## 2. Accounting & Finance

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Invoicing** | `account` (core) | ✅ 100% | Native CE |
| **Accounting** | `account` (core) | ✅ 95% | Native CE |
| **Bank Reconciliation** | `account_reconcile_oca` | 🟢 95% | OCA full replacement |
| **Bank Synchronization** | `account_bank_statement_import_*` | 🟢 90% | OCA; manual import |
| **Assets** | `account_asset_management` | 🟢 95% | OCA full replacement |
| **Budget** | `account_budget_oca` | 🟢 90% | OCA available |
| **Consolidation** | — | 🔴 0% | **GAP**: `ipai_consolidation` |
| **Analytic Accounting** | `analytic` (core) | ✅ 100% | Native CE |
| **Payment Providers** | `payment` (core) | ✅ 90% | Native CE; fewer providers |
| **Expenses** | `hr_expense` (core) | ✅ 100% | Native CE |
| **Spreadsheet (BI)** | — | 🟡 60% | Use Apache Superset |
| **Documents** | `dms` (OCA) | 🟢 80% | OCA Document Management |

### OCA Modules for Accounting

```yaml
OCA/account-reconcile:
  - account_reconcile_oca           # Bank reconciliation UI
  - account_reconcile_model_oca     # Auto-matching rules
  - account_statement_import_ofx
  - account_statement_import_camt
  - account_statement_import_file_reconcile_oca

OCA/account-financial-tools:
  - account_asset_management        # Depreciation
  - account_cutoff_accrual_dates    # Deferred revenue
  - account_lock_date_update
  - account_move_name_sequence

OCA/account-financial-reporting:
  - account_financial_report        # P&L, Balance Sheet
  - account_tax_balance
  - mis_builder                     # Custom financial reports

OCA/account-closing:
  - account_fiscal_year_closing
  - account_cutoff_base

OCA/bank-payment:
  - account_payment_order
  - account_banking_pain_base       # SEPA payments
```

### Required ipai_* Modules

```
ipai_bir_compliance        ✓ EXISTS - Philippine BIR tax forms
ipai_consolidation         NEW      - Multi-company consolidation
ipai_loan_management       NEW      - Loan tracking & amortization
```

---

## 3. Inventory & Manufacturing

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Inventory** | `stock` (core) | ✅ 100% | Native CE |
| **Purchase** | `purchase` (core) | ✅ 100% | Native CE |
| **Manufacturing** | `mrp` (core) | ✅ 95% | Native CE |
| **PLM** | `mrp_plm` (OCA) | 🟢 80% | OCA/manufacture |
| **Quality** | `quality_control` (OCA) | 🟢 85% | OCA/manufacture |
| **Maintenance** | `maintenance` (core) | ✅ 100% | Native CE |
| **Barcode** | `stock_barcodes` (OCA) | 🟢 85% | OCA/stock-logistics-barcode |
| **Batch/Serial Tracking** | `stock` (core) | ✅ 100% | Native CE |
| **MPS (Master Schedule)** | — | 🔴 30% | **GAP**: `ipai_mps` needed |
| **IoT Integration** | — | ⚪ 0% | Hardware-specific |

### OCA Modules for Inventory/MRP

```yaml
OCA/stock-logistics-warehouse:
  - stock_available
  - stock_demand_estimate
  - stock_warehouse_calendar

OCA/stock-logistics-workflow:
  - stock_picking_batch
  - stock_split_picking

OCA/stock-logistics-barcode:
  - stock_barcodes
  - stock_barcodes_gs1

OCA/manufacture:
  - mrp_bom_structure_xlsx
  - mrp_production_request
  - mrp_workorder_sequence
  - quality_control_oca
```

### Required ipai_* Modules

```
ipai_mps                   NEW - Master Production Schedule
ipai_shop_floor            NEW - Production floor tablet UI
```

---

## 4. Human Resources

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Employees** | `hr` (core) | ✅ 100% | Native CE |
| **Recruitment** | `hr_recruitment` (core) | ✅ 100% | Native CE |
| **Time Off** | `hr_holidays` (core) | ✅ 100% | Native CE |
| **Attendances** | `hr_attendance` (core) | ✅ 100% | Native CE |
| **Payroll** | `payroll` (OCA) | 🟢 75% | OCA/payroll; needs localization |
| **Appraisals** | `hr_appraisal` (OCA) | 🟢 80% | OCA/hr |
| **Referrals** | — | 🔴 0% | **GAP**: Low priority |
| **Fleet** | `fleet` (core) | ✅ 100% | Native CE |
| **Lunch** | `hr_lunch` (OCA) | 🟢 80% | OCA available |

### OCA Modules for HR

```yaml
OCA/hr:
  - hr_employee_document
  - hr_contract_types
  - hr_employee_calendar_planning

OCA/payroll:
  - payroll
  - payroll_account

OCA/hr-attendance:
  - hr_attendance_geolocation
  - hr_attendance_reason
```

### Required ipai_* Modules

```
ipai_payroll_ph            NEW - Philippine payroll (SSS, PhilHealth, Pag-IBIG)
ipai_appraisal_360         NEW - 360-degree feedback
```

---

## 5. Project & Services

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Project** | `project` (core) | ✅ 100% | Native CE |
| **Timesheets** | `hr_timesheet` (core) | ✅ 100% | Native CE |
| **Field Service** | `fieldservice` (OCA) | 🟢 80% | OCA/field-service |
| **Helpdesk** | `helpdesk_mgmt` (OCA) | 🟢 70% | OCA/helpdesk; alpha status |
| **Planning** | `resource_booking` (OCA) | 🟡 60% | **GAP**: `ipai_planning` |
| **Appointments** | `appointment` (OCA) | 🟢 75% | OCA/calendar |
| **Worksheets** | — | 🔴 0% | Part of Field Service |

### OCA Modules for Projects

```yaml
OCA/project:
  - project_template
  - project_timesheet_time_control
  - project_task_default_stage
  - project_status
  - project_milestone

OCA/timesheet:
  - hr_timesheet_sheet
  - sale_timesheet_line_exclude

OCA/helpdesk:
  - helpdesk_mgmt
  - helpdesk_mgmt_project
  - helpdesk_mgmt_timesheet

OCA/field-service:
  - fieldservice
  - fieldservice_account
  - fieldservice_project
```

### Required ipai_* Modules

```
ipai_clarity_ppm_parity    ✓ EXISTS - Clarity PPM features
ipai_helpdesk_plus         NEW      - Enhanced helpdesk
ipai_planning              NEW      - Resource planning/scheduling
```

---

## 6. Marketing

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Email Marketing** | `mass_mailing` (core) | ✅ 90% | Native CE |
| **Marketing Automation** | — | 🔴 0% | **GAP**: `ipai_marketing_auto` |
| **SMS Marketing** | `sms` (core) | 🟡 70% | Native CE; limited |
| **Social Marketing** | — | 🔴 0% | **GAP**: `ipai_social` |
| **Events** | `event` (core) | ✅ 100% | Native CE |
| **Surveys** | `survey` (core) | ✅ 100% | Native CE |

### OCA Modules for Marketing

```yaml
OCA/social:
  - mail_tracking
  - mass_mailing_custom_unsubscribe
  - mass_mailing_list_dynamic

OCA/event:
  - event_registration_cancel_reason
  - event_sale_registration_multi_qty
```

### Required ipai_* Modules

```
ipai_marketing_automation  NEW - Drip campaigns, lead scoring
ipai_social_publisher      NEW - Social media scheduling
```

---

## 7. Website & eCommerce

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Website Builder** | `website` (core) | ✅ 95% | Native CE |
| **eCommerce** | `website_sale` (core) | ✅ 90% | Native CE |
| **Blog** | `website_blog` (core) | ✅ 100% | Native CE |
| **Forum** | `website_forum` (core) | ✅ 100% | Native CE |
| **Live Chat** | `im_livechat` (core) | ✅ 100% | Native CE |
| **eLearning** | `website_slides` (core) | ✅ 90% | Native CE |

### OCA Modules for Website

```yaml
OCA/website:
  - website_legal_page
  - website_cookiefirst
  - website_odoo_debranding

OCA/e-commerce:
  - website_sale_product_attribute_filter_visibility
  - website_sale_checkout_skip_payment
```

### Required ipai_* Modules

```
ipai_website_debranding    NEW - Remove Odoo branding
```

---

## 8. Productivity & Communication

| Enterprise Feature | CE/OCA Alternative | Parity | Notes |
|--------------------|-------------------|--------|-------|
| **Discuss** | `mail` (core) | ✅ 100% | Native CE |
| **Knowledge** | `knowledge` (OCA) | 🟢 70% | **or** `ipai_docs` ✓ EXISTS |
| **Approvals** | `tier_validation` (OCA) | 🟢 85% | OCA multi-tier approval |
| **Odoo Studio** | — | 🔴 0% | **GAP**: No-code builder |
| **VoIP** | — | ⚪ 0% | Third-party integration |
| **WhatsApp** | — | ⚪ 0% | Third-party integration |
| **IoT** | — | ⚪ 0% | Hardware-specific |
| **Mobile App** | — | 🟡 50% | PWA alternative |

### OCA Modules for Productivity

```yaml
OCA/server-tools:
  - base_tier_validation          # Approval workflows
  - base_tier_validation_formula

OCA/knowledge:
  - knowledge                     # Knowledge base

OCA/server-ux:
  - base_technical_features
  - date_range
```

### Required ipai_* Modules

```
ipai_docs                  ✓ EXISTS - Notion-style knowledge base
ipai_studio_lite           NEW      - Simple form customization
ipai_mobile_pwa            NEW      - Progressive Web App shell
```

---

## 9. Localization (Philippines)

| Requirement | CE/OCA Alternative | Parity | Notes |
|-------------|-------------------|--------|-------|
| **Chart of Accounts** | `l10n_ph` (core) | ✅ 100% | Native CE |
| **BIR Tax Forms** | — | 🔴 0% | **GAP**: `ipai_bir_compliance` ✓ |
| **SAWT/SLS/SLP** | — | 🔴 0% | Part of BIR compliance |
| **Withholding Tax** | `l10n_ph` (partial) | 🟡 60% | Needs enhancement |
| **SSS/PhilHealth/Pag-IBIG** | — | 🔴 0% | **GAP**: `ipai_payroll_ph` |

### Required ipai_* Modules

```
ipai_bir_compliance        ✓ EXISTS - BIR 2307, 1601-C, 2550Q, etc.
ipai_payroll_ph            NEW      - Philippine payroll deductions
ipai_ewt_ph                NEW      - Expanded withholding tax
```

---

## Complete ipai_* Module Roadmap

### Tier 1: Critical (High Business Value)

| Module | Replaces EE Feature | Effort | Priority |
|--------|---------------------|--------|----------|
| `ipai_subscription` | Subscriptions | High | P0 |
| `ipai_helpdesk_plus` | Helpdesk | High | P0 |
| `ipai_planning` | Planning | Medium | P0 |
| `ipai_bir_compliance` | (PH Localization) | ✓ EXISTS | — |
| `ipai_consolidation` | Consolidation | High | P1 |

### Tier 2: Important (Common Requirements)

| Module | Replaces EE Feature | Effort | Priority |
|--------|---------------------|--------|----------|
| `ipai_marketing_automation` | Marketing Automation | High | P1 |
| `ipai_social_publisher` | Social Marketing | Medium | P1 |
| `ipai_payroll_ph` | (PH Localization) | High | P1 |
| `ipai_mps` | MPS | Medium | P2 |
| `ipai_shop_floor` | Shop Floor | Medium | P2 |

### Tier 3: Nice-to-Have

| Module | Replaces EE Feature | Effort | Priority |
|--------|---------------------|--------|----------|
| `ipai_studio_lite` | Odoo Studio | Very High | P3 |
| `ipai_mobile_pwa` | Mobile App | High | P3 |
| `ipai_esign` | eSign | Medium | P3 |
| `ipai_loan_management` | Loan Management | Medium | P3 |

### Already Built

| Module | Coverage |
|--------|----------|
| `ipai_bir_compliance` | BIR tax forms |
| `ipai_docs` | Knowledge base (Notion-style) |
| `ipai_expense` | Enhanced expenses |
| `ipai_equipment` | Equipment management |
| `ipai_clarity_ppm_parity` | Project portfolio management |
| `ipai_finance_ppm` | Finance PPM |
| `ipai_idp` | Intelligent document processing |

---

## OCA Repository Reference

### Essential Repositories (18.0 Branch)

| Repository | Purpose | URL |
|------------|---------|-----|
| account-reconcile | Bank reconciliation | github.com/OCA/account-reconcile |
| account-financial-tools | Asset management, cutoffs | github.com/OCA/account-financial-tools |
| account-financial-reporting | Financial reports | github.com/OCA/account-financial-reporting |
| project | Project enhancements | github.com/OCA/project |
| timesheet | Timesheet features | github.com/OCA/timesheet |
| hr | HR enhancements | github.com/OCA/hr |
| helpdesk | Helpdesk system | github.com/OCA/helpdesk |
| sale-workflow | Sales enhancements | github.com/OCA/sale-workflow |
| purchase-workflow | Purchase enhancements | github.com/OCA/purchase-workflow |
| stock-logistics-warehouse | Warehouse features | github.com/OCA/stock-logistics-warehouse |
| manufacture | MRP enhancements | github.com/OCA/manufacture |
| contract | Recurring contracts | github.com/OCA/contract |
| dms | Document management | github.com/OCA/dms |
| field-service | Field service | github.com/OCA/field-service |
| server-tools | Base utilities | github.com/OCA/server-tools |

---

## Cost Comparison

### Odoo Enterprise Annual Pricing (2024-2025)

| Users | Standard Plan | Custom Plan |
|-------|---------------|-------------|
| 10 | $2,880/year | $4,800/year |
| 25 | $7,200/year | $12,000/year |
| 50 | $14,400/year | $24,000/year |
| 100 | $28,800/year | $48,000/year |

### CE/OCA + ipai_* One-Time Development

| Component | Cost |
|-----------|------|
| OCA Module Integration | $5,000 - $10,000 |
| ipai_* Tier 1 Modules | $15,000 - $25,000 |
| ipai_* Tier 2 Modules | $10,000 - $20,000 |
| **Total One-Time** | **$30,000 - $55,000** |

### 5-Year TCO (50 Users)

| Edition | Year 1 | Years 2-5 | 5-Year Total |
|---------|--------|-----------|--------------|
| Enterprise (Custom) | $24,000 | $96,000 | **$120,000** |
| CE/OCA + ipai_* | $45,000 | $10,000 | **$55,000** |
| **Savings** | — | — | **$65,000 (54%)** |

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Install Odoo CE 18.0
- [ ] Configure PostgreSQL 16
- [ ] Set up OCA module repositories
- [ ] Install base OCA modules (account-reconcile, project, hr)

### Phase 2: Core Business
- [ ] Install industry-specific OCA modules
- [ ] Deploy existing ipai_* modules
- [ ] Configure multi-company if needed

### Phase 3: Gap Filling
- [ ] Develop priority ipai_* modules
- [ ] Integrate with external services (BI, OCR)
- [ ] User acceptance testing

### Phase 4: Production
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Go-live and training

---

## Sources

- [Odoo Editions Comparison](https://www.odoo.com/page/editions)
- [OCA Must-Have Modules](https://odoo-community.org/list-of-must-have-oca-modules)
- [OCA GitHub](https://github.com/OCA)
- [Odoo 18 Features](https://www.odoo.com/forum/help-1/new-features-of-odoo-18-roadmap-249773)
- [Odoo Pricing](https://www.odoo.com/pricing)
- [OCA Helpdesk](https://github.com/OCA/helpdesk)
- [Dixmit - Accounting on CE](https://www.dixmit.com/en/blog/our-blog-1/accounting-management-on-odoo-community-18)
- [iContechsoft - CE vs EE Comparison](https://icontechsoft.com/odoo-community-vs-enterprise/)

---

*Document Version: 1.0.0*
*Last Updated: December 2025*
*Maintainer: InsightPulseAI*
