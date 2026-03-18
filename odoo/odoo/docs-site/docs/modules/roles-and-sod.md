# Roles and separation of duties

This document defines the 9-role framework for financial operations at InsightPulse AI, including per-role permissions, RACI matrices, separation of duties (SoD) conflicts, and automated anomaly detection.

## Role framework

### AP Clerk

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Enter vendor bills, match POs to invoices, prepare payment batches |
| **CAN** | Create draft vendor bills, submit for approval, view AP aging |
| **CANNOT** | Approve payments, post journal entries, modify chart of accounts |
| **Odoo groups** | `account.group_account_invoice` |
| **KPIs** | Invoice processing time < 2 days, matching accuracy >= 99% |

### AR Clerk

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Issue customer invoices, apply payments, manage collections |
| **CAN** | Create customer invoices, record payments, generate AR aging reports |
| **CANNOT** | Issue credit notes without approval, write off receivables, modify payment terms |
| **Odoo groups** | `account.group_account_invoice` |
| **KPIs** | DSO < 45 days, collection rate >= 95% |

### GL Accountant

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Post journal entries, reconcile accounts, prepare trial balance |
| **CAN** | Create and post journal entries, perform bank reconciliation, run reports |
| **CANNOT** | Approve payments, modify fiscal periods, change tax configurations |
| **Odoo groups** | `account.group_account_user` |
| **KPIs** | Reconciliation completion by Day 5, unreconciled items < 2% |

### Fixed Asset Accountant

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Manage asset lifecycle, compute depreciation, track disposals |
| **CAN** | Create asset records, run depreciation schedules, record disposals |
| **CANNOT** | Approve asset purchases, modify depreciation methods after approval, delete asset records |
| **Odoo groups** | `account.group_account_user`, `account_asset.group_account_asset` |
| **KPIs** | Depreciation posted by Day 3, asset register accuracy >= 99.5% |

### Payroll Specialist

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Process payroll, compute contributions, generate payslips |
| **CAN** | Run payroll batches, compute final pay, generate BIR forms |
| **CANNOT** | Approve salary changes, modify pay structures, access bank disbursement |
| **Odoo groups** | `hr_payroll.group_hr_payroll_user` |
| **KPIs** | Payroll processed by cutoff, zero payslip corrections post-release |

### Tax Compliance Officer

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Prepare tax returns, manage withholding, ensure BIR compliance |
| **CAN** | Generate BIR forms (2550M, 2550Q, 1601C, 1701Q), compute tax provisions |
| **CANNOT** | File returns without Finance Manager approval, modify tax rates, post adjustments |
| **Odoo groups** | `account.group_account_user`, `l10n_ph.group_tax_compliance` |
| **KPIs** | Filing on or before deadline, zero BIR penalties |

### Finance Manager

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Review and approve transactions, manage close process, financial reporting |
| **CAN** | Approve journal entries, approve payments, close periods, generate financial statements |
| **CANNOT** | Create own transactions and approve them (SoD), modify system configuration |
| **Odoo groups** | `account.group_account_manager` |
| **KPIs** | Close completed by Day 10, variance analysis delivered by Day 12 |

### Finance Director

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Strategic oversight, policy approval, final sign-off on statements |
| **CAN** | Approve financial statements, authorize exceptional transactions, set fiscal policy |
| **CANNOT** | Enter transactions, process payroll, perform day-to-day bookkeeping |
| **Odoo groups** | `account.group_account_manager`, `base.group_erp_manager` |
| **KPIs** | Board reporting on time, audit findings < 3 per year |

### External Auditor

| Attribute | Detail |
|-----------|--------|
| **Responsibilities** | Review financial records, verify compliance, issue audit opinion |
| **CAN** | Read all financial data, export reports, view audit trail |
| **CANNOT** | Create, modify, or delete any records; approve any transactions |
| **Odoo groups** | `account.group_account_readonly` |
| **KPIs** | N/A (external party) |

## RACI matrices

### Month-end close

| Phase | AP Clerk | AR Clerk | GL Acct | FA Acct | Payroll | Tax | Fin Mgr | Fin Dir | Ext Auditor |
|-------|----------|----------|---------|---------|---------|-----|---------|---------|-------------|
| 1. Sub-ledger cutoff | R | R | A | R | R | I | A | I | I |
| 2. Reconciliation | C | C | R | R | I | I | A | I | I |
| 3. Adjusting entries | I | I | R | R | I | R | A | I | I |
| 4. Financial statements | I | I | R | I | I | C | R | A | I |
| 5. Review and sign-off | I | I | C | I | I | C | R | A | R |

**Legend**: R = Responsible, A = Accountable, C = Consulted, I = Informed

## Odoo security group mapping

| Role | `group_account_invoice` | `group_account_user` | `group_account_manager` | `group_account_readonly` | `group_hr_payroll_user` | `group_tax_compliance` | `group_account_asset` | `group_erp_manager` | `group_system` |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| AP Clerk | x | | | | | | | | |
| AR Clerk | x | | | | | | | | |
| GL Accountant | | x | | | | | | | |
| Fixed Asset Acct | | x | | | | | x | | |
| Payroll Specialist | | | | | x | | | | |
| Tax Compliance | | x | | | | x | | | |
| Finance Manager | | | x | | | | | | |
| Finance Director | | | x | | | | | x | |
| External Auditor | | | | x | | | | | |

## Separation of duties (SoD) conflicts

!!! danger "Critical SoD controls"
    These 7 conflicts must never coexist in a single user. The system enforces these through Odoo security group exclusions and automated monitoring.

| # | Conflict | Risk | Mitigation |
|---|----------|------|------------|
| 1 | Create vendor bill + approve payment | Fictitious vendor fraud | Different users for AP entry and payment approval |
| 2 | Create journal entry + approve journal entry | Unauthorized adjustments | Maker-checker on all manual journal entries |
| 3 | Manage employee master data + process payroll | Ghost employee fraud | HR maintains employee records, Payroll processes pay |
| 4 | Create customer invoice + apply payment + write off | Lapping scheme | AR Clerk creates invoices, Finance Manager approves write-offs |
| 5 | Modify chart of accounts + post journal entries | Account manipulation | Only Finance Director modifies COA; GL Accountant posts entries |
| 6 | Manage fixed assets + approve disposals | Asset theft / ghost assets | FA Accountant manages records, Finance Manager approves disposals |
| 7 | File tax returns + modify tax configuration | Tax fraud / misreporting | Tax Officer prepares, Finance Manager approves, Finance Director signs |

## Anomaly detection

Automated alerts trigger when the system detects potential SoD violations or unusual activity.

| # | Trigger | Threshold | Alert recipients |
|---|---------|-----------|-----------------|
| 1 | Same user creates and approves a journal entry | Any occurrence | Finance Manager, Finance Director |
| 2 | Payment approved without matching vendor bill | Any occurrence | Finance Manager |
| 3 | Journal entry posted outside business hours | Weekends, 10 PM - 6 AM | Finance Manager |
| 4 | User accesses payroll data without payroll role | Any occurrence | HR Director, IT Admin |
| 5 | Credit note issued exceeding PHP 50,000 | Per transaction | Finance Director |
| 6 | Vendor master data modified and payment created same day | Same user, same day | Finance Manager |
| 7 | Bulk write-off exceeding PHP 100,000 | Per batch | Finance Director, External Auditor |

These alerts are implemented via `base.automation` rules in Odoo with notifications sent through both Odoo chatter and Slack (`#finance-alerts` channel).
