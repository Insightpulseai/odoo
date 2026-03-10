# EE Parity Gate

Enterprise Edition parity assessment for the Odoo 19 CE + OCA platform.

> **Gate Status: ALL CAPABILITIES PASS. SHIP.**
>
> Assessment date: 2026-02-11

---

## Ship Verdicts

| Capability | Ship? | Gate |
|-----------|-------|------|
| Finance PPM (Clarity parity) | **YES** | PASS |
| OCR / Document Digitization | **YES** | PASS |
| Supabase Integration | **YES** | PASS |
| AI Agents (Joule parity) | **YES** | PASS |
| Zoho Mail SMTP | **YES** | PASS |
| Project CE (Work Management) | **YES** | PASS |

---

## EE Feature Coverage

### Covered by CE Native (~40%)

Sales, CRM, Invoicing, Accounting (basic), Purchase, Inventory, Manufacturing, Point of Sale, Project, Timesheets, Expenses, Website, eCommerce, Contacts, Calendar, Discuss, Employees, Recruitment, Time Off, Fleet, Maintenance, Repairs, Attendances, Surveys, Events.

### Covered by OCA (~35%)

Helpdesk, Field Service, Quality Management, Planning (partial), MRP II, PLM, Appraisal, Skills, Email Marketing, SMS, Appointments, Financial Reporting, Asset Management, Bank Reconciliation, Barcode, PWA/Mobile.

### Covered by ipai_* Delta (~20%)

Finance PPM, BIR Tax Compliance, Month-End Closing, OCR Gateway, AI Agent Builder, Supabase Ops Mirror, CRM Pipeline, Design System.

### Intentionally Not Built (~5%)

Studio, Native Mobile App, Odoo IAP services, Social Marketing (external tools via n8n).

---

## Replacement Hierarchy

```
Feature Request
    |
    v
1. CE_CONFIG      - Can CE settings/config solve it?
    | NO
    v
2. OCA_EQUIVALENT - Is there an OCA 18.0/19.0 module?
    | NO
    v
3. GAP_DELTA      - Small _inherit delta on existing models?
    | NO
    v
4. GAP_NEW_MODULE - New module (last resort, must be justified)
```

---

## Detailed Report

See [`docs/ee-parity-gate/EE_PARITY_GATE_REPORT.md`](https://github.com/Insightpulseai/odoo/blob/main/docs/ee-parity-gate/EE_PARITY_GATE_REPORT.md) for the full assessment with per-module analysis, OCA readiness matrix, and deployment architecture.
