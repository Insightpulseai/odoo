# IPAI BIR Tax Compliance

## 1. Overview
Philippine BIR tax compliance - 36 eBIRForms support

**Technical Name**: `ipai_bir_tax_compliance`
**Category**: Accounting/Localizations
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

        Complete Philippine Bureau of Internal Revenue (BIR) tax compliance module.

        Supported Tax Types:
        - VAT (Forms 2550M, 2550Q)
        - Withholding Tax (Forms 1600, 1601-C, 1601-E, 1601-F, 1604-CF)
        - Income Tax (Forms 1700, 1701, 1702)
        - Excise Tax (Forms 2200A, 2200P, 2200T, 2200M, 2200AN)
        - Percentage Tax (Forms 2551M, 2551Q)
        - Capital Gains Tax (Forms 1706, 1707)
        - Documentary Stamp Tax (Forms 2000, 2000-OT)

        Features:
        - Automated tax computation from Odoo transactions
        - Filing deadline calendar with alerts
        - Form generation wizards
        - Compliance dashboard
        - TIN validation
        - Audit trail
    

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
- `bir.vat.line`
- `bir.alphalist.line`
- `bir.tax.return.line`
- `bir.filing.deadline`
- `bir.withholding.return`
- `bir.tax.return`
- `bir.vat.return`
- `bir.alphalist`
- `bir.withholding.line`

## 6. User Interface
- **Views**: 9 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_bir_tax_compliance --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_bir_tax_compliance --stop-after-init
```