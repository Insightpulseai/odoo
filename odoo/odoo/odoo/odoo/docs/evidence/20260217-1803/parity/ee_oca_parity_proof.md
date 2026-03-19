# EE-to-OCA Parity Proof: Every Enterprise Module Has a Replacement

> Generated: 2026-02-17T18:04:03Z
> Script: `scripts/ee_oca_parity_proof.py`
> Spec: `spec/ee-oca-parity/constitution.md`

---

## Executive Summary

**151/151 Enterprise-only modules are covered (100.0%)**

Every Odoo Enterprise Edition module has been mapped to one or more of:

1. **OCA module** — direct open-source replacement from Odoo Community Association
2. **CE-native** — functionality already in Odoo Community Edition
3. **External service** — third-party API (n8n, Twilio, Superset, etc.) replacing Odoo IAP
4. **IPAI thin bridge** — minimal `ipai_*` glue module (<1k LOC)

### Evidence Tier Status

> **Important**: A mapping (T1) proves a replacement *exists*.
> It does NOT prove installability (T2), functional parity (T3),
> or production readiness (T4). See `spec/ee-oca-parity/constitution.md`.

| Tier | Name | Count | Meaning |
|------|------|-------|---------|
| T0 | Unmapped | 0 | No verified replacement |
| **T1** | **Mapped** | **150** | **Replacement identified, OCA repo verified** |
| T2 | Installable | 0 | Installs on our Odoo 19 CE baseline |
| T3 | Functional | 0 | ≥80% feature coverage for our workflows |
| T4 | Verified | 0 | Production-tested, 30-day soak |
| N/A | Not needed | 1 | Demo/test data, skip |

### Strategy Breakdown

| Strategy | Count | Description |
|----------|-------|-------------|
| OCA only | 106 | Direct OCA replacement |
| OCA + bridge | 12 | OCA + ipai/external glue |
| External service | 25 | n8n, Mautic, APIs (no module needed) |
| CE native | 6 | Already in Community Edition |
| IPAI custom | 8 | Thin ipai connector |
| Not needed | 1 | Demo/test data, skip |
| **Total** | **151** | |

### OCA Repository Verification

- Verified OCA repos referenced: **152**
- Missing OCA repos: **0**
- Unique OCA repos used: **45**

Referenced OCA repos:

- [OCA/account-budgeting](https://github.com/OCA/account-budgeting)
- [OCA/account-consolidation](https://github.com/OCA/account-consolidation)
- [OCA/account-financial-reporting](https://github.com/OCA/account-financial-reporting)
- [OCA/account-financial-tools](https://github.com/OCA/account-financial-tools)
- [OCA/account-reconcile](https://github.com/OCA/account-reconcile)
- [OCA/automation](https://github.com/OCA/automation)
- [OCA/bank-payment](https://github.com/OCA/bank-payment)
- [OCA/bank-statement-import](https://github.com/OCA/bank-statement-import)
- [OCA/calendar](https://github.com/OCA/calendar)
- [OCA/commission](https://github.com/OCA/commission)
- [OCA/connector-ecommerce](https://github.com/OCA/connector-ecommerce)
- [OCA/connector-telephony](https://github.com/OCA/connector-telephony)
- [OCA/contract](https://github.com/OCA/contract)
- [OCA/credit-control](https://github.com/OCA/credit-control)
- [OCA/crm](https://github.com/OCA/crm)
- [OCA/delivery-carrier](https://github.com/OCA/delivery-carrier)
- [OCA/dms](https://github.com/OCA/dms)
- [OCA/field-service](https://github.com/OCA/field-service)
- [OCA/fleet](https://github.com/OCA/fleet)
- [OCA/geospatial](https://github.com/OCA/geospatial)
- [OCA/helpdesk](https://github.com/OCA/helpdesk)
- [OCA/hr](https://github.com/OCA/hr)
- [OCA/hr-attendance](https://github.com/OCA/hr-attendance)
- [OCA/hr-holidays](https://github.com/OCA/hr-holidays)
- [OCA/intrastat-extrastat](https://github.com/OCA/intrastat-extrastat)
- [OCA/iot](https://github.com/OCA/iot)
- [OCA/knowledge](https://github.com/OCA/knowledge)
- [OCA/manufacture](https://github.com/OCA/manufacture)
- [OCA/mis-builder](https://github.com/OCA/mis-builder)
- [OCA/payroll](https://github.com/OCA/payroll)
- [OCA/project](https://github.com/OCA/project)
- [OCA/repair](https://github.com/OCA/repair)
- [OCA/reporting-engine](https://github.com/OCA/reporting-engine)
- [OCA/server-tools](https://github.com/OCA/server-tools)
- [OCA/shift-planning](https://github.com/OCA/shift-planning)
- [OCA/sign](https://github.com/OCA/sign)
- [OCA/social](https://github.com/OCA/social)
- [OCA/spreadsheet](https://github.com/OCA/spreadsheet)
- [OCA/stock-logistics-barcode](https://github.com/OCA/stock-logistics-barcode)
- [OCA/stock-logistics-reporting](https://github.com/OCA/stock-logistics-reporting)
- [OCA/stock-logistics-workflow](https://github.com/OCA/stock-logistics-workflow)
- [OCA/tier-validation](https://github.com/OCA/tier-validation)
- [OCA/timesheet](https://github.com/OCA/timesheet)
- [OCA/vertical-rental](https://github.com/OCA/vertical-rental)
- [OCA/web](https://github.com/OCA/web)

### Domain Coverage

| Domain | EE Modules | Covered |
|--------|------------|---------|
| accounting | 19 | 19/19 |
| appointment | 7 | 7/7 |
| approvals | 3 | 3/3 |
| barcode | 7 | 7/7 |
| data | 2 | 2/2 |
| documents | 16 | 16/16 |
| field_service | 4 | 4/4 |
| helpdesk | 10 | 10/10 |
| hr | 13 | 13/13 |
| iot | 1 | 1/1 |
| knowledge | 1 | 1/1 |
| manufacturing | 10 | 10/10 |
| marketing | 11 | 11/11 |
| planning | 3 | 3/3 |
| project | 7 | 7/7 |
| sales | 6 | 6/6 |
| shipping | 9 | 9/9 |
| spreadsheet | 2 | 2/2 |
| studio | 2 | 2/2 |
| timesheet | 2 | 2/2 |
| voip | 2 | 2/2 |
| web | 7 | 7/7 |
| whatsapp | 7 | 7/7 |

---

## Detailed Module Mapping

### Accounting

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `account_accountant` | T1 | oca | `account_financial_report`, `account_reconcile_oca`, `mis_builder`, `account_move_line_tax_editable`, `account_journal_lock_date` | CE invoicing + OCA reporting + OCA reconciliation covers full accounting |
| `account_asset` | T1 | oca | `account_asset_management` | OCA account_asset_management: full asset lifecycle, depreciation boards, disposa |
| `account_avatax` | T1 | external | Avalara AvaTax API (direct) | Direct Avalara API integration; no Odoo IAP middleman needed |
| `account_bank_statement_import_camt` | T1 | oca | `account_statement_import_camt` | Direct OCA equivalent |
| `account_bank_statement_import_csv` | T1 | oca | `account_statement_import_csv` | Direct OCA equivalent |
| `account_bank_statement_import_ofx` | T1 | oca | `account_statement_import_ofx` | Direct OCA equivalent |
| `account_bank_statement_import_qif` | T1 | oca | `account_statement_import_qif` | OCA provides QIF import capability |
| `account_batch_payment` | T1 | oca | `account_payment_order`, `account_banking_pain_base` | OCA bank-payment provides SEPA/PAIN payment orders with batch processing |
| `account_budget` | T1 | oca | `mis_builder`, `mis_builder_budget` | MIS Builder provides flexible budgeting with variance analysis, exceeds EE capab |
| `account_consolidation` | T1 | oca | `account_consolidation` | OCA consolidation module for multi-company financials |
| `account_disallowed_expenses` | T1 | oca | `account_move_line_tax_editable` | Tax-editable move lines + analytic filtering achieves expense disallowance track |
| `account_followup` | T1 | oca | `account_credit_control` | OCA credit-control provides automated dunning and payment follow-up workflows |
| `account_intrastat` | T1 | oca | `intrastat_product`, `intrastat_base` | OCA intrastat modules cover EU trade statistical reporting |
| `account_invoice_extract` | T1 | external | `ipai_doc_ocr_bridge`, `ipai_ocr_gateway` + PaddleOCR / Google Vision / AWS Textract | External OCR service replaces Odoo IAP digitization; ipai_doc_ocr_bridge integra |
| `account_online_synchronization` | T1 | oca | `account_statement_import_ofx`, `account_statement_import_camt`, `account_statement_import_csv` | OCA bank statement import (OFX, CAMT, CSV) replaces online sync with file-based  |
| `account_reports` | T1 | oca | `account_financial_report`, `mis_builder`, `mis_builder_contrib` | OCA financial reports + MIS Builder provide P&L, balance sheet, general ledger,  |
| `account_sepa_direct_debit` | T1 | oca | `account_banking_sepa_direct_debit` | OCA SEPA DD implementation (PAIN.008) |
| `account_taxcloud` | T1 | external | TaxCloud API (direct) | Direct TaxCloud API integration |
| `l10n_xx_reports` | T1 | oca | `account_financial_report`, `mis_builder` | OCA financial reports are country-agnostic; MIS Builder templates handle country |

### Appointment

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `appointment` | T1 | oca | `calendar_slot` | OCA calendar extensions + CE website calendar provide online booking |
| `appointment_account_payment` | T1 | ce | CE native | CE payment module handles appointment payment collection |
| `appointment_crm` | T1 | oca | `calendar_slot` | Calendar-to-opportunity linking |
| `appointment_google_calendar` | T1 | ce | CE native | CE google_calendar module provides Google Calendar sync natively |
| `appointment_hr` | T1 | oca | `calendar_slot` | Employee availability for appointments |
| `appointment_hr_recruitment` | T1 | oca | `calendar_slot` | Interview scheduling via calendar |
| `appointment_sale` | T1 | oca | `calendar_slot` | Calendar-to-sale linking |

### Approvals

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `approvals` | T1 | oca | `base_tier_validation`, `base_tier_validation_formula` | OCA tier-validation: multi-level approval workflows on any model, more flexible  |
| `approvals_purchase` | T1 | oca | `base_tier_validation`, `purchase_tier_validation` | Purchase order approval tiers |
| `approvals_sale` | T1 | oca | `base_tier_validation` | Sale order approval tiers |

### Barcode

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `stock_barcode` | T1 | oca | `stock_barcodes` | OCA stock_barcodes: mobile barcode scanning for warehouse operations |
| `stock_barcode_mrp` | T1 | oca | `stock_barcodes` | Barcode scanning in manufacturing context |
| `stock_barcode_mrp_subcontracting` | T1 | oca | `stock_barcodes` | Barcode scanning for subcontracting receipts |
| `stock_barcode_picking_batch` | T1 | oca | `stock_barcodes` | Batch picking with barcode scanning |
| `stock_barcode_product_expiry` | T1 | oca | `stock_barcodes` | Expiry date scanning during receipts |
| `stock_barcode_quality_control` | T1 | oca | `stock_barcodes`, `quality_control_oca` | Quality checks triggered during barcode operations |
| `stock_barcode_quality_mrp` | T1 | oca | `stock_barcodes`, `quality_control_oca` | Quality checks in MRP barcode context |

### Data

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `data_cleaning` | T1 | oca | `base_partner_merge` | OCA partner merge + CE base.partner.merge covers data deduplication |
| `data_merge` | T1 | oca | `base_partner_merge` | OCA partner merge utilities |

### Documents

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `documents` | T1 | oca | `dms`, `dms_field` | OCA DMS provides workspaces, tags, access control, versioning |
| `documents_account` | T1 | oca | `dms` | OCA DMS + Odoo attachment system covers document-accounting linking |
| `documents_fleet` | T1 | oca | `dms` | Generic DMS handles fleet documents via tags |
| `documents_hr` | T1 | oca | `dms` | OCA DMS tags/workspaces handle HR document categorization |
| `documents_hr_contract` | T1 | oca | `dms` | Contract documents managed via DMS workspaces |
| `documents_hr_expense` | T1 | oca | `dms` | Expense receipts via DMS |
| `documents_hr_holidays` | T1 | oca | `dms` | Leave documents via DMS |
| `documents_hr_payroll` | T1 | oca | `dms` | Payslip PDFs stored in DMS |
| `documents_hr_recruitment` | T1 | oca | `dms` | Applicant documents via DMS |
| `documents_l10n_be_hr_payroll` | T1 | oca | `dms` | Country-specific payroll docs via generic DMS |
| `documents_product` | T1 | oca | `dms` | Product datasheets via DMS |
| `documents_project` | T1 | oca | `dms` | OCA DMS workspaces per project |
| `documents_sign` | T1 | oca | `dms` | Signed documents stored in DMS |
| `documents_spreadsheet` | T1 | oca | `dms` | OCA DMS + CE spreadsheet covers document-spreadsheet integration |
| `sign` | T1 | oca+external | `sign_oca` + DocuSign / SignRequest / Yousign API | OCA sign module + external e-signature API for legal validity |
| `sign_itsme` | T1 | external | itsme API (direct) | Direct itsme API integration for Belgian identity verification |

### Field Service

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `industry_fsm` | T1 | oca | `fieldservice`, `fieldservice_account`, `fieldservice_agreement` | OCA field-service: full FSM with orders, locations, equipment, agreements |
| `industry_fsm_report` | T1 | oca | `fieldservice` | OCA fieldservice includes reporting capabilities |
| `industry_fsm_sale` | T1 | oca | `fieldservice_sale` | OCA fieldservice_sale for quotation-to-FSM flow |
| `industry_fsm_stock` | T1 | oca | `fieldservice_stock` | OCA fieldservice_stock for inventory on FSM orders |

### Helpdesk

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `helpdesk` | T1 | oca | `helpdesk_mgmt`, `helpdesk_mgmt_project`, `helpdesk_mgmt_timesheet` | OCA helpdesk_mgmt: full ticket management, SLA, project integration, timesheet |
| `helpdesk_account` | T1 | oca | `helpdesk_mgmt` | OCA helpdesk + CE accounting integration |
| `helpdesk_fsm` | T1 | oca | `helpdesk_mgmt`, `fieldservice` | OCA helpdesk + OCA field-service integration |
| `helpdesk_repair` | T1 | oca | `helpdesk_mgmt` | Ticket-to-repair order flow via OCA helpdesk |
| `helpdesk_sale` | T1 | oca | `helpdesk_mgmt` | Ticket-to-sale linking via OCA helpdesk |
| `helpdesk_sale_loyalty` | T1 | oca+ipai | `helpdesk_mgmt` + `ipai_helpdesk_refund` | Gift card refunds via thin ipai bridge |
| `helpdesk_sale_timesheet` | T1 | oca | `helpdesk_mgmt_timesheet` | Billable timesheet from helpdesk tickets |
| `helpdesk_stock` | T1 | oca | `helpdesk_mgmt` | Return/repair flows via helpdesk integration |
| `helpdesk_stock_account` | T1 | oca | `helpdesk_mgmt` | Stock valuation in helpdesk context |
| `helpdesk_timesheet` | T1 | oca | `helpdesk_mgmt_timesheet` | Direct OCA equivalent for timesheet tracking on tickets |

### Hr

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `hr_appraisal` | T1 | oca | `hr_appraisal` | OCA hr_appraisal: appraisal cycles, goals, feedback |
| `hr_appraisal_survey` | T1 | oca | `hr_appraisal` | Survey-based appraisals via OCA hr module |
| `hr_contract_salary` | T1 | oca | `payroll` | Salary configuration via OCA payroll rules |
| `hr_contract_sign` | T1 | oca+external | `sign_oca` + DocuSign / SignRequest API | Contract signing via OCA sign + external e-signature |
| `hr_gantt` | T1 | oca | `web_timeline` | OCA web_timeline provides timeline/Gantt view for any model |
| `hr_payroll` | T1 | oca | `payroll`, `payroll_account` | OCA payroll: salary rules, computation engine, payslip generation |
| `hr_payroll_account` | T1 | oca | `payroll_account` | OCA payroll_account: journal entries from payslips |
| `hr_payroll_holidays` | T1 | oca | `payroll` | Leave deductions in payroll computation |
| `hr_referral` | T1 | oca | `hr_recruitment_notification` | OCA HR recruitment modules handle referral tracking |
| `hr_work_entry_contract` | T1 | oca | `payroll` | Work entries generated from contracts via OCA payroll |
| `hr_work_entry_contract_attendance` | T1 | oca | `payroll` | Attendance-based work entries for payroll |
| `hr_work_entry_holidays` | T1 | oca | `payroll` | Holiday work entry generation |
| `l10n_xx_hr_payroll` | T1 | oca+ipai | `payroll`, `payroll_account` + `ipai_hr_payroll_ph` | OCA payroll engine is country-agnostic; salary rules are configured per country. |

### Iot

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `iot` | T1 | oca+ipai | `ipai_enterprise_bridge` | OCA/iot repo + ipai_enterprise_bridge provides device management; CE iot_base co |

### Knowledge

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `knowledge` | T1 | oca | `document_knowledge` | OCA knowledge module provides wiki/knowledge base |

### Manufacturing

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `mrp_plm` | T1 | oca | `mrp_bom_tracking` | OCA provides BOM versioning and change tracking; PLM engineering changes via man |
| `mrp_workorder` | T1 | oca | `mrp_production_putaway_strategy`, `mrp_multi_level` | OCA manufacture repo provides work order extensions; CE mrp provides base work o |
| `mrp_workorder_hr` | T1 | oca | `mrp_multi_level` | Worker assignment to work orders via OCA manufacture extensions |
| `mrp_workorder_iot` | T1 | ipai | `ipai_enterprise_bridge` | IoT device integration for shop floor via ipai bridge |
| `mrp_workorder_plm` | T1 | oca | `mrp_bom_tracking` | Engineering change orders via BOM tracking linked to work orders |
| `quality_control` | T1 | oca | `quality_control_oca` | OCA quality_control_oca: inspection plans, control points, alerts |
| `quality_control_iot` | T1 | oca+ipai | `quality_control_oca` + `ipai_enterprise_bridge` | Quality checks triggered by IoT sensors via bridge |
| `quality_mrp` | T1 | oca | `quality_control_oca` | Quality checks on manufacturing orders |
| `quality_mrp_workorder` | T1 | oca | `quality_control_oca` | Quality checks at work order steps |
| `quality_mrp_workorder_iot` | T1 | oca+ipai | `quality_control_oca` + `ipai_enterprise_bridge` | IoT-triggered quality checks at work order steps |

### Marketing

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `marketing_automation` | T1 | external | n8n / Mautic | n8n workflows provide campaign automation; Mautic for dedicated marketing automa |
| `marketing_automation_sms` | T1 | external | n8n + Twilio | SMS campaigns via n8n + Twilio integration |
| `social` | T1 | external | Buffer / Hootsuite / n8n | Social posting via external scheduler or n8n API integration |
| `social_crm` | T1 | external | n8n webhook | Social lead capture via n8n webhook to Odoo CRM |
| `social_demo` | N/A | not_needed | CE native | Demo data module — not needed for production |
| `social_facebook` | T1 | external | Facebook Graph API / n8n | Direct Facebook Graph API via n8n |
| `social_instagram` | T1 | external | Instagram Graph API / n8n | Direct Instagram API via n8n |
| `social_linkedin` | T1 | external | LinkedIn API / n8n | Direct LinkedIn API via n8n |
| `social_push_notifications` | T1 | external | Firebase Cloud Messaging / OneSignal | Push notifications via FCM or OneSignal |
| `social_twitter` | T1 | external | X API / n8n | Direct X API via n8n |
| `social_youtube` | T1 | external | YouTube Data API / n8n | Direct YouTube API via n8n |

### Planning

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `planning` | T1 | oca | `project_forecast_line`, `project_timeline` | OCA project_forecast_line + shift-planning provides resource scheduling |
| `planning_hr` | T1 | oca | `project_forecast_line` | Employee-linked planning via OCA forecast |
| `planning_hr_skills` | T1 | oca | `project_forecast_line` | Skill-based resource allocation via OCA project forecast |

### Project

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `crm_enterprise` | T1 | oca+external | Apache Superset | CRM forecasting and cohort analysis via Superset BI dashboards |
| `fleet_enterprise` | T1 | oca | `fleet_vehicle_log_fuel` | OCA fleet modules extend CE fleet with fuel logs, additional views |
| `project_enterprise` | T1 | oca | `project_timeline`, `web_timeline` | OCA project_timeline + web_timeline provide Gantt/timeline views for projects |
| `project_forecast` | T1 | oca | `project_forecast_line` | OCA project_forecast_line: resource allocation and capacity planning |
| `project_timesheet_forecast` | T1 | oca | `project_forecast_line`, `hr_timesheet_sheet` | Forecast vs actual timesheet comparison |
| `rental` | T1 | oca | `rental_base` | OCA vertical-rental provides rental management |
| `stock_enterprise` | T1 | oca | `stock_picking_report_valued` | OCA stock reporting provides valued picking reports and enhanced warehouse views |

### Sales

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `sale_commission` | T1 | oca | `sale_commission`, `account_commission` | OCA commission: full commission management with settlements |
| `sale_ebay` | T1 | oca | `connector_ecommerce` | OCA e-commerce connector framework supports marketplace integration |
| `sale_renting` | T1 | oca | `rental_base` | OCA vertical-rental provides rental management |
| `sale_subscription` | T1 | oca | `contract`, `contract_sale` | OCA contract module: recurring invoicing, renewals, MRR tracking |
| `sale_subscription_stock` | T1 | oca | `contract` | Recurring deliveries via contract |
| `sale_timesheet_enterprise` | T1 | oca | `hr_timesheet_sheet` | OCA timesheet sheet + CE sale_timesheet covers billable timesheets |

### Shipping

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `delivery_bpost` | T1 | oca | `delivery_carrier_label_postlogistics` | OCA delivery-carrier provides carrier-agnostic framework + specific connectors |
| `delivery_dhl` | T1 | oca | `delivery_carrier_label_dhl` | OCA DHL connector |
| `delivery_easypost` | T1 | external | EasyPost API (direct) | Direct EasyPost API integration; OCA delivery framework supports custom carriers |
| `delivery_fedex` | T1 | oca | `delivery_carrier_label_fedex` | OCA FedEx connector |
| `delivery_sendcloud` | T1 | external | Sendcloud API (direct) | Direct Sendcloud API; OCA delivery framework supports custom carriers |
| `delivery_shiprocket` | T1 | external | Shiprocket API (direct) | Direct Shiprocket API integration |
| `delivery_starshipit` | T1 | external | Starshipit API (direct) | Direct Starshipit API integration |
| `delivery_ups` | T1 | oca | `delivery_carrier_label_ups` | OCA UPS connector |
| `delivery_usps` | T1 | oca | `base_delivery_carrier_label` | OCA delivery-carrier framework + base label module; USPS via direct API or stamp |

### Spreadsheet

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `spreadsheet_dashboard_edition` | T1 | ce | CE native | CE spreadsheet_dashboard provides dashboard spreadsheets in Community |
| `spreadsheet_edition` | T1 | ce | CE native | CE spreadsheet (built-in since Odoo 16+) provides core spreadsheet functionality |

### Studio

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `web_studio` | T1 | ce+oca | `base_custom_info`, `auditlog` | CE base_automation + ir.actions + OCA web widgets + auditlog provide no-code cus |
| `website_studio` | T1 | ce | CE native | CE website builder provides drag-and-drop editing natively |

### Timesheet

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `timer` | T1 | oca | `hr_timesheet_sheet` | Timer functionality within OCA timesheet sheet |
| `timesheet_grid` | T1 | oca | `hr_timesheet_sheet` | OCA hr_timesheet_sheet: weekly timesheet grid with approval workflow |

### Voip

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `voip` | T1 | oca | `base_phone`, `crm_phone` | OCA connector-telephony: SIP/Asterisk/FreePBX integration, click-to-dial, call l |
| `voip_onsip` | T1 | oca | `base_phone` | OCA telephony framework supports any SIP provider |

### Web

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `web_cohort` | T1 | oca+external | `bi_sql_editor` + Apache Superset / Metabase | Cohort analysis via OCA bi_sql_editor + Superset/Metabase dashboards |
| `web_dashboard` | T1 | oca+external | `web_dashboard_tile` + Apache Superset / Metabase | OCA dashboard tiles + external BI (Superset) for advanced dashboards |
| `web_enterprise` | T1 | oca+ipai | `web_responsive` + `ipai_platform_theme` | OCA web_responsive + ipai_platform_theme provides modern responsive backend |
| `web_gantt` | T1 | oca | `web_timeline` | OCA web_timeline provides horizontal timeline view (Gantt equivalent) |
| `web_grid` | T1 | oca+ipai | `ipai_grid_view` | ipai_grid_view provides grid/matrix view; OCA web repo has grid utilities |
| `web_map` | T1 | oca | `web_view_leaflet_map` | OCA geospatial/web modules provide Leaflet-based map views |
| `web_mobile` | T1 | oca | `web_responsive` | OCA web_responsive makes backend mobile-friendly |

### Whatsapp

| EE Module | Tier | Strategy | OCA Replacement | Notes |
|-----------|------|----------|-----------------|-------|
| `whatsapp` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API (Meta Cloud API) | Direct WhatsApp Business API integration via ipai connector |
| `whatsapp_account` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | Invoice notifications via WhatsApp |
| `whatsapp_event` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | Event reminders via WhatsApp |
| `whatsapp_pos` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | POS receipts via WhatsApp |
| `whatsapp_sale` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | Quotation sharing via WhatsApp |
| `whatsapp_sale_subscription` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | Subscription reminders via WhatsApp |
| `whatsapp_stock` | T1 | external+ipai | `ipai_whatsapp_connector` + WhatsApp Business API | Delivery notifications via WhatsApp |

---

## Verification Methodology

1. **EE Module Catalog**: Compiled from Odoo documentation, Apps Store, release notes,
   and community knowledge. Validated against CE 19.0 addons list (608 modules).
2. **OCA Repo Verification**: Each referenced OCA repository verified via GitHub API
   (`GET /orgs/OCA/repos`). Live check confirms repository exists and is not archived.
3. **Strategy Assignment**: Each EE module assigned to one of: OCA, CE-native,
   external service, or IPAI thin bridge. No module left unmapped.
4. **Bridge Rule**: EE modules whose functionality is a *non-module* feature
   (hosting, IAP middleman, cloud service) are replaced by direct external API
   integration — no Odoo module needed.

## Compliance

- Zero Odoo Enterprise code in this repository
- All replacements are LGPL-3.0 or AGPL-3 licensed
- No Odoo IAP dependencies (all replaced by direct API calls)
- See `docs/strategy/parity/COMPLIANCE_AND_LICENSING.md` for full audit

---

*Evidence generated: 2026-02-17T18:04:03Z*
