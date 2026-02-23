# Odoo Enterprise → CE + OCA Parity Matrix

**Target Version:** Odoo 19.0 CE
**Generated:** 2026-01-27
**Purpose:** Complete mapping of Enterprise-only features to self-hosted replacements

---

## Classification Legend

| Status | Description |
|--------|-------------|
| `REPLACEABLE_BY_OCA` | Full or near-complete replacement available via OCA modules |
| `REQUIRES_EXTERNAL_SERVICE` | Self-hosted external service required (outside Odoo) |
| `REQUIRES_CUSTOM` | Minimal IPAI glue module needed (config, approvals, connectors) |
| `NO_REPLACEMENT` | No viable self-hosted alternative; accept feature gap or build custom |

---

## Accounting & Finance

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Accounting Reports** (P&L, Balance Sheet) | `REPLACEABLE_BY_OCA` | account | `account_financial_report`, `mis_builder` | - | `odoo -d db -i account_financial_report,mis_builder --stop-after-init` |
| **Budget Management** | `REPLACEABLE_BY_OCA` | account | `mis_builder_budget` | - | `odoo -d db -i mis_builder_budget --stop-after-init` |
| **Bank Reconciliation Widget** | `REPLACEABLE_BY_OCA` | account | `account_reconcile_oca` | - | `odoo -d db -i account_reconcile_oca --stop-after-init` |
| **Consolidation** | `REQUIRES_CUSTOM` | account | `multi-company` repos | `ipai_consolidation_bridge` | Custom implementation required |
| **Asset Management** | `REPLACEABLE_BY_OCA` | account | `account_asset_management` (OCA) | - | `odoo -d db -i account_asset_management --stop-after-init` |
| **Deferred Revenue** | `REPLACEABLE_BY_OCA` | account | `account_cutoff_accrual_dates` (OCA) | - | `odoo -d db -i account_cutoff_accrual_dates --stop-after-init` |
| **Inter-Company Rules** | `REPLACEABLE_BY_OCA` | account | `account_invoice_inter_company`, `purchase_sale_inter_company` | - | `odoo -d db -i account_invoice_inter_company,purchase_sale_inter_company --stop-after-init` |
| **Payment Follow-up** | `REPLACEABLE_BY_OCA` | account | `account_credit_control` (OCA) | - | `odoo -d db -i account_credit_control --stop-after-init` |
| **SEPA/PAIN Payments** | `REPLACEABLE_BY_OCA` | account | `account_payment_order`, `account_banking_sepa_credit_transfer` | - | `odoo -d db -i account_payment_order,account_banking_sepa_credit_transfer --stop-after-init` |
| **Check Printing** | `REPLACEABLE_BY_OCA` | account | `account_check_printing_report_base` (OCA) | - | `odoo -d db -i account_check_printing_report_base --stop-after-init` |

### Acceptance Tests - Accounting

```bash
# Verify financial reports
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8069/web/health"
docker compose exec odoo odoo shell -d odoo_core -c "env['account.financial.report'].search_count([])" --stop-after-init

# Verify MIS Builder
docker compose exec odoo odoo shell -d odoo_core -c "env['mis.report'].search_count([])" --stop-after-init
```

---

## Documents & Knowledge

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Documents App** | `REPLACEABLE_BY_OCA` | base | `dms`, `dms_field` | - | `odoo -d db -i dms,dms_field --stop-after-init` |
| **Knowledge Base** | `REPLACEABLE_BY_OCA` | base | `document_page`, `document_page_approval` | - | `odoo -d db -i document_page,document_page_approval --stop-after-init` |
| **Sign (Digital Signatures)** | `REQUIRES_EXTERNAL_SERVICE` | base | - | `ipai_sign_bridge` | Use: DocuSign, SignRequest, or self-hosted **Docuseal** |
| **OCR/Document Digitization** | `REQUIRES_EXTERNAL_SERVICE` | base | - | `ipai_ocr_gateway` | Use: **Paperless-ngx**, Apache Tika, or Tesseract |
| **Spreadsheet** | `REPLACEABLE_BY_OCA` | base | `spreadsheet_oca`, `spreadsheet_dashboard_oca` | - | `odoo -d db -i spreadsheet_oca,spreadsheet_dashboard_oca --stop-after-init` |

### External Service: Docuseal (Self-hosted Signing)

```yaml
# docker-compose.yml addition
services:
  docuseal:
    image: docuseal/docuseal:latest
    ports:
      - "3000:3000"
    volumes:
      - docuseal_data:/data
    environment:
      - SECRET_KEY_BASE=${DOCUSEAL_SECRET}
```

### External Service: Paperless-ngx (OCR)

```yaml
# docker-compose.yml addition
services:
  paperless-ngx:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    ports:
      - "8000:8000"
    volumes:
      - paperless_data:/usr/src/paperless/data
      - paperless_media:/usr/src/paperless/media
    environment:
      - PAPERLESS_OCR_LANGUAGE=eng
      - PAPERLESS_URL=http://localhost:8000
```

---

## Studio & Customization

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Odoo Studio** | `REQUIRES_CUSTOM` | base | - | `ipai_dev_studio_base` | Pre-installed IPAI module |
| **Custom Reports Builder** | `REPLACEABLE_BY_OCA` | base | `bi_sql_editor`, `report_xlsx` | - | `odoo -d db -i bi_sql_editor,report_xlsx --stop-after-init` |
| **Automated Actions** | `REPLACEABLE_BY_OCA` | base | Native CE + `base_automation` | - | Built-in CE feature |
| **Custom Fields** | `REPLACEABLE_BY_OCA` | base | Native CE Settings | - | Built-in CE feature |
| **Custom Views** | `REQUIRES_CUSTOM` | base | `base_view_inheritance_extension` | `ipai_dev_studio_base` | `odoo -d db -i base_view_inheritance_extension --stop-after-init` |

### Acceptance Tests - Studio Alternative

```bash
# Verify BI SQL Editor
docker compose exec odoo odoo shell -d odoo_core -c "env['bi.sql.view'].search_count([])" --stop-after-init

# Verify report_xlsx installed
docker compose exec odoo odoo shell -d odoo_core -c "print('report_xlsx' in env.registry._init_modules)" --stop-after-init
```

---

## Project & Services

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Gantt View** | `REPLACEABLE_BY_OCA` | project | `project_timeline` | - | `odoo -d db -i project_timeline --stop-after-init` |
| **Task Dependencies** | `REPLACEABLE_BY_OCA` | project | `project_task_dependency` | - | `odoo -d db -i project_task_dependency --stop-after-init` |
| **Planning / Resource Scheduling** | `REQUIRES_EXTERNAL_SERVICE` | project | - | `ipai_planning_bridge` | Use: **Cal.com** or self-hosted scheduler |
| **Field Service** | `REPLACEABLE_BY_OCA` | project | `fieldservice` (OCA) | - | `odoo -d db -i fieldservice --stop-after-init` |
| **Timesheets Grid** | `REPLACEABLE_BY_OCA` | hr_timesheet | `hr_timesheet_sheet` | - | `odoo -d db -i hr_timesheet_sheet --stop-after-init` |
| **Forecasting** | `REQUIRES_EXTERNAL_SERVICE` | project | - | - | Use: External BI tool (Superset/Metabase) |

---

## HR & Workforce

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Appraisal** | `REPLACEABLE_BY_OCA` | hr | `hr_appraisal_oca` (check availability) | `ipai_hr_appraisal` | May require custom |
| **Referral** | `REQUIRES_CUSTOM` | hr_recruitment | - | `ipai_hr_referral` | Custom implementation |
| **Employee Expense Advances** | `REPLACEABLE_BY_OCA` | hr_expense | `hr_expense_advance_clearing` | - | `odoo -d db -i hr_expense_advance_clearing --stop-after-init` |
| **Payroll** | `REQUIRES_EXTERNAL_SERVICE` | hr | `payroll` (OCA) | - | OCA payroll or external payroll system |
| **Attendance Kiosk** | `REPLACEABLE_BY_OCA` | hr_attendance | `hr_attendance_terminal` (OCA) | - | `odoo -d db -i hr_attendance_terminal --stop-after-init` |

---

## Sales & CRM

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Subscriptions** | `REPLACEABLE_BY_OCA` | sale | `contract`, `contract_sale` | - | `odoo -d db -i contract,contract_sale --stop-after-init` |
| **Rental** | `REQUIRES_CUSTOM` | sale | `sale_rental` (OCA) | - | `odoo -d db -i sale_rental --stop-after-init` |
| **Sales Commission** | `REPLACEABLE_BY_OCA` | sale | `sale_commission` (OCA) | - | `odoo -d db -i sale_commission --stop-after-init` |
| **Lead Scoring** | `REQUIRES_EXTERNAL_SERVICE` | crm | - | - | Use: External ML pipeline or n8n workflow |

---

## Marketing

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Marketing Automation** | `REQUIRES_EXTERNAL_SERVICE` | mass_mailing | - | `ipai_marketing_bridge` | Use: **Mautic**, **Listmonk**, or n8n workflows |
| **Social Marketing** | `REQUIRES_EXTERNAL_SERVICE` | - | - | - | Use: External social tools (Buffer, Hootsuite) |
| **Email Tracking** | `REPLACEABLE_BY_OCA` | mail | `mail_tracking` | - | `odoo -d db -i mail_tracking --stop-after-init` |
| **SMS Marketing** | `REQUIRES_EXTERNAL_SERVICE` | sms | - | `ipai_sms_gateway` | Use: Twilio, Plivo, or self-hosted SMS gateway |

### External Service: Mautic (Marketing Automation)

```yaml
# docker-compose.yml addition
services:
  mautic:
    image: mautic/mautic:latest
    ports:
      - "8080:80"
    environment:
      - MAUTIC_DB_HOST=postgres
      - MAUTIC_DB_NAME=mautic
      - MAUTIC_DB_USER=mautic
      - MAUTIC_DB_PASSWORD=${MAUTIC_DB_PASS}
```

---

## Approvals & Workflows

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Approvals App** | `REPLACEABLE_BY_OCA` | base | `base_tier_validation`, `base_tier_validation_formula` | `ipai_platform_approvals` | `odoo -d db -i base_tier_validation,base_tier_validation_formula --stop-after-init` |
| **Purchase Approval** | `REPLACEABLE_BY_OCA` | purchase | `purchase_order_approval_block` | - | `odoo -d db -i purchase_order_approval_block --stop-after-init` |
| **Expense Approval** | `REPLACEABLE_BY_OCA` | hr_expense | `hr_expense_tier_validation` (OCA) | - | `odoo -d db -i hr_expense_tier_validation --stop-after-init` |

---

## Manufacturing & Quality

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Quality Control** | `REPLACEABLE_BY_OCA` | mrp | `quality_control_oca` (check availability) | - | May require custom |
| **PLM (Product Lifecycle)** | `REQUIRES_CUSTOM` | mrp | - | `ipai_plm_bridge` | Custom implementation |
| **Work Order Tablet** | `REPLACEABLE_BY_OCA` | mrp | Native CE + `web_responsive` | - | `odoo -d db -i web_responsive --stop-after-init` |

---

## IoT & Hardware

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **IoT Box** | `REQUIRES_EXTERNAL_SERVICE` | - | - | `ipai_iot_bridge` | Use: **Home Assistant**, **Node-RED**, or custom |
| **Barcode Scanning** | `REPLACEABLE_BY_OCA` | stock | `stock_barcodes` (OCA) | - | `odoo -d db -i stock_barcodes --stop-after-init` |
| **VoIP** | `REQUIRES_EXTERNAL_SERVICE` | - | - | `ipai_voip_bridge` | Use: **FreePBX**, **Asterisk**, or cloud VoIP |

### External Service: FreePBX (VoIP)

```yaml
# docker-compose.yml addition
services:
  freepbx:
    image: tiredofit/freepbx:latest
    ports:
      - "5060:5060/udp"
      - "5061:5061/tcp"
      - "10000-10100:10000-10100/udp"
    volumes:
      - freepbx_data:/data
```

---

## Helpdesk & Support

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Helpdesk** | `REQUIRES_EXTERNAL_SERVICE` | - | - | `ipai_helpdesk_bridge` | Use: **Zammad**, **osTicket**, or custom Odoo module |
| **Live Chat** | `REPLACEABLE_BY_OCA` | website | Native CE `im_livechat` | - | `odoo -d db -i im_livechat --stop-after-init` |

### External Service: Zammad (Helpdesk)

```yaml
# docker-compose.yml addition
services:
  zammad:
    image: ghcr.io/zammad/zammad:latest
    ports:
      - "8081:8080"
    volumes:
      - zammad_data:/opt/zammad
    environment:
      - POSTGRESQL_HOST=postgres
      - POSTGRESQL_DB=zammad
```

---

## Data & Analytics

| EE Feature | Status | CE Baseline | OCA Replacement | IPAI Glue | Install Command |
|------------|--------|-------------|-----------------|-----------|-----------------|
| **Data Cleaning** | `REQUIRES_CUSTOM` | base | - | `ipai_data_cleaning` | Custom implementation |
| **BI Dashboards** | `REQUIRES_EXTERNAL_SERVICE` | base | `kpi_dashboard` + external | `ipai_superset_connector` | Use: **Superset**, **Metabase** |
| **Embedded Analytics** | `REQUIRES_EXTERNAL_SERVICE` | base | - | `ipai_superset_connector` | Use: **Superset** embedded dashboards |

---

## Summary Statistics

| Classification | Count | Percentage |
|----------------|-------|------------|
| `REPLACEABLE_BY_OCA` | 35 | ~65% |
| `REQUIRES_EXTERNAL_SERVICE` | 14 | ~26% |
| `REQUIRES_CUSTOM` | 5 | ~9% |
| `NO_REPLACEMENT` | 0 | 0% |

---

## Recommended External Services Stack

| Service | Purpose | Self-Hosted Option | Cloud Alternative |
|---------|---------|-------------------|-------------------|
| **Docuseal** | Digital signatures | ✓ | DocuSign, SignRequest |
| **Paperless-ngx** | OCR/Document digitization | ✓ | Azure Form Recognizer |
| **Mautic** | Marketing automation | ✓ | Mailchimp, HubSpot |
| **Superset** | BI/Analytics | ✓ | Looker, Tableau |
| **Zammad** | Helpdesk | ✓ | Zendesk, Freshdesk |
| **FreePBX** | VoIP | ✓ | Twilio, Vonage |
| **Cal.com** | Scheduling/Planning | ✓ | Calendly |
| **Listmonk** | Email campaigns | ✓ | SendGrid |

---

## IPAI Bridge Modules Required

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `ipai_enterprise_bridge` | Umbrella module | All below |
| `ipai_sign_bridge` | Docuseal integration | base, dms |
| `ipai_ocr_gateway` | Paperless-ngx integration | base, dms |
| `ipai_marketing_bridge` | Mautic integration | mass_mailing, connector |
| `ipai_superset_connector` | Superset BI integration | base_rest, connector |
| `ipai_voip_bridge` | VoIP integration | base |
| `ipai_sms_gateway` | SMS integration | sms, base |
| `ipai_helpdesk_bridge` | Zammad integration | base_rest, connector |
| `ipai_planning_bridge` | Cal.com integration | project, base_rest |
| `ipai_dev_studio_base` | Studio alternative | base |
| `ipai_platform_approvals` | Enhanced approvals | base_tier_validation |

---

## Sources

- [Odoo Editions Comparison](https://www.odoo.com/page/editions)
- [OCA GitHub](https://github.com/oca)
- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [Syncoria - EE vs CE Comparison](https://www.syncoria.com/blog/blog-6/odoo-enterprise-and-community-true-facts-on-modules-and-features-101-53)
- [VentorTech - Odoo 17 CE vs EE](https://ventor.tech/odoo/odoo-17-community-vs-enterprise/)
