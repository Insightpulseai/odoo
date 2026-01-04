# IPAI Month-End Closing & BIR Tax Filing

## 1. Overview
SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance

**Technical Name**: `ipai_month_end_closing`
**Category**: Accounting/Accounting
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

IPAI Month-End Closing & BIR Tax Filing
=======================================

Complete month-end financial closing workflow based on SAP Advanced Financial
Closing (AFC) best practices, tailored for TBWA Finance operations.

Features
--------
* 36 pre-configured closing tasks organized by functional area
* Employee assignments mapped to TBWA Finance team (RIM, BOM, JPAL, LAS, JLI, RMQB, JAP, JRMO)
* Three-tier approval workflow: Preparation → Review → Approval
* Task dependencies matching SAP AFC workflow patterns
* BIR tax filing calendar with automated deadlines (1601-C, 1601-EQ, 2550Q, 1702-RT/EX, 1702Q)

Functional Areas
----------------
* Payroll & Personnel
* Tax & Provisions
* Rent & Leases
* Accruals & Expenses
* Prior Period Review
* Amortization & Corporate
* Insurance
* Treasury & Other
* Client Billings & WIP/OOP
* VAT & Taxes
* CA Liquidations
* AR/AP Aging
* Regional Reporting

BIR Compliance
--------------
* Monthly: 1601-C (Compensation), 0619-E (Creditable EWT)
* Quarterly: 1601-EQ (EWT), 2550Q (VAT), 1702Q (Income Tax)
* Annual: 1702-RT/EX (Income Tax Return)

Architecture: Smart Delta
-------------------------
This module follows the ipai_* Smart Delta pattern:
- Extends core Odoo project module
- No monkey-patching or forks
- OCA-compatible, marketplace-ready
- AGPL-3 licensed
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `project`
- `hr`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- No explicit new models detected (may inherit existing).

## 6. User Interface
- **Views**: 4 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_month_end_closing --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_month_end_closing --stop-after-init
```