# IPAI Month-End Closing

## 1. Overview
SAP AFC replacement - Month-end closing automation

**Technical Name**: `ipai_month_end`
**Category**: Accounting
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

        Month-end closing automation with SAP Advanced Financial Closing (AFC) feature parity.

        Features:
        - Template-driven task management
        - RACI workflow (Prep → Review → Approve)
        - Holiday-aware workday scheduling (Philippines)
        - Overdue notifications
        - Progress tracking dashboards

        Replaces SAP AFC at zero licensing cost.
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `account`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.month.end.task.template`
- `ipai.month.end.closing`
- `ipai.ph.holiday`
- `ipai.month.end.task`

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
odoo-bin -d <db> -i ipai_month_end --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_month_end --stop-after-init
```