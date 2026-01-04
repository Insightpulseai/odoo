# Finance PPM Go-Live Checklist

## 1. Overview
Production go-live checklist for Finance PPM modules

**Technical Name**: `ipai_finance_ppm_golive`
**Category**: Finance
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

Finance PPM Go-Live Checklist Module
====================================

Complete production readiness checklist for Finance PPM system with:
- 9 section groups (Data, Module, AFC, STC, Control Room, Notion, Audit, Operational, Go-Live)
- 60+ granular checklist items
- Approval workflow (Finance Supervisor → Senior Supervisor Finance → Director)
- Dashboard with completion % tracking
- PDF export for Director sign-off
- Integration with Finance PPM modules

Author: Jake Tolentino (InsightPulse AI / TBWA)
License: AGPL-3
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.finance.ppm.golive.section`
- `ipai.finance.ppm.golive.item`
- `ipai.finance.ppm.golive.checklist`

## 6. User Interface
- **Views**: 8 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_finance_ppm_golive --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_finance_ppm_golive --stop-after-init
```