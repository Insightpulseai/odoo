# IPAI Finance PPM – TBWA Complete Configuration

## 1. Overview
Complete seed data for 8-employee Finance SSC with BIR compliance and month-end closing tasks

**Technical Name**: `ipai_finance_ppm_umbrella`
**Category**: Uncategorized
**Version**: 1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

TBWA Finance PPM Umbrella Configuration
========================================

Complete seed data for Finance SSC operations:

**8 Employees:**
- RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

**BIR Tax Forms (22 entries for 2026):**
- 1601-C / 0619-E (Monthly - 12 months)
- 2550Q (Quarterly VAT - 4 quarters)
- 1601-EQ (Quarterly EWT - 4 quarters)
- 1702-RT/EX (Annual Income Tax - 1 entry)
- 1702Q (Quarterly Income Tax - 1 entry)

**Month-End Closing Tasks (36 entries):**
- Payroll & Personnel
- Tax & Provisions
- Client Billings
- WIP/OOP Management
- AR/AP Aging
- Accruals & Reclassifications

**RACI Matrix:**
- Supervisor assignments per employee
- Reviewer: CKVC (Finance Supervisor), JPAL, RIM, BOM, LAS
- Approver: CKVC (Finance Director), RIM (Senior Finance Manager)

**Deadlines:**
- Preparation: BIR Deadline - 4 business days
- Review: BIR Deadline - 2 business days
- Approval: BIR Deadline - 1 business day
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `ipai_finance_ppm`
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- No explicit new models detected (may inherit existing).

## 6. User Interface
- **Views**: 5 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` not found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_finance_ppm_umbrella --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_finance_ppm_umbrella --stop-after-init
```