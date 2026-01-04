# IPAI TBWA Finance

## 1. Overview
Unified month-end closing + BIR tax compliance for TBWA Philippines

**Technical Name**: `ipai_tbwa_finance`
**Category**: Accounting
**Version**: 18.0.1.0.0
**Author**: IPAI / TBWA

## 2. Functional Scope

        Complete finance operations module for TBWA Philippines combining:

        1. MONTH-END CLOSING (SAP AFC Replacement)
           - Template-driven 36-task checklist across 4 phases
           - RACI workflow (Prep → Review → Approve)
           - Holiday-aware workday scheduling
           - Progress tracking dashboards

        2. BIR TAX COMPLIANCE (Philippine Statutory)
           - 36 eBIRForms support (VAT, WHT, Income, Excise)
           - Filing deadline calendar with alerts
           - Auto-compute from Odoo transactions
           - TIN validation

        SHARED COMPONENTS:
           - Philippine holiday calendar (2024-2027)
           - Unified task model with Kanban
           - Single team configuration (BOM, RIM, CKVC)
           - Integrated compliance dashboard

        Cost: Replaces SAP AFC ($500K-1M) + SAP Tax Compliance at zero licensing.
    

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
- `finance.task`
- `compliance.check`
- `closing.period`
- `finance.task.template`
- `ph.holiday`
- `bir.return`
- `bir.return.line`

## 6. User Interface
- **Views**: 12 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_tbwa_finance --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_tbwa_finance --stop-after-init
```