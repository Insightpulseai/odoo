# IPAI Finance Monthly Closing

## 1. Overview
Structured month-end closing and BIR filing on top of Projects (CE/OCA-only).

**Technical Name**: `ipai_finance_monthly_closing`
**Category**: Accounting/Finance
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## 2. Functional Scope
No description provided.

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- No explicit new models detected (may inherit existing).

## 6. User Interface
- **Views**: 2 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_finance_monthly_closing --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_finance_monthly_closing --stop-after-init
```