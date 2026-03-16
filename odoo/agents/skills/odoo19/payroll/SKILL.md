---
name: payroll
description: "Compute employee pay from contracts, work entries, and salary rules; generate payslips and pay runs."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Payroll — Odoo 19.0 Skill Reference

## Overview

The **Payroll** app calculates employee compensation by combining contract terms, work entries (from Attendances, Planning, or Timesheets), salary structures, and country-specific localization rules. Payroll officers create payslips individually or in batch pay runs, resolve work entry conflicts, and issue payments via wire transfer, NACHA/SEPA, or check. The app integrates tightly with Employees, Time Off, Attendances, Planning, and Accounting.

## Key Concepts

- **Contract** — Binding agreement defining salary, structure type, working schedule, and work entry source for an employee. Statuses: New, Running, Expired, Cancelled.
- **Salary Structure Type** — High-level classification (e.g., Employee, Worker) that groups salary rules applied to a contract.
- **Salary Structure** — Set of salary rules within a structure type that define how gross-to-net calculations work.
- **Salary Rule** — Individual computation line (base salary, tax, deduction, allowance) executed during payslip calculation.
- **Work Entry** — Granular timesheet record (Attendance, Sick Time Off, Training, Public Holiday, etc.) used to compute hours worked. Created from contract schedule, Attendances, or Planning.
- **Work Entry Type** — Category label for a work entry (e.g., `Attendance`, `Sick Time Off`). Each has a payroll code, color, and optional rounding. Nine default types ship with the app.
- **Payslip** — Individual payment record for one employee for one period. Statuses: Draft → Waiting → Done → Paid.
- **Pay Run (Batch)** — Group of payslips processed together. Statuses: Ready → Done → Paid.
- **Salary Adjustment (Salary Attachment)** — Recurring or one-time deduction/addition on a payslip (garnishment, child support, bonus installment). Types: Attachment of Salary, Assignment of Salary, Child Support.
- **Localization** — Country-specific module that preconfigures tax rules, salary structures, work entry types, and reporting. Must be installed before running payroll.
- **Payroll SEPA** — Option to create SEPA payment files for Euro-zone direct deposits.
- **NACHA** — ACH-compatible export format for US bank transfers.
- **YTD Reset Date** — Date when year-to-date accumulators reset (default Jan 1).
- **Deferred Time Off** — Mechanism to apply late time off to the next pay period instead of cancelling validated payslips.

## Core Workflows

### 1. Set Up Payroll

1. Install the correct country localization via `Payroll → Configuration → Settings → Payroll → Choose a Payroll Localization`.
2. Configure accounting settings: enable Payroll Entries, optionally enable Payroll SEPA and Batch Account Move Lines.
3. Set Contract Expiration Notice Period and Work Permit Expiration Notice Period (days).
4. Optionally set Deferred Time Off responsible person.
5. Create or verify Working Schedules under `Configuration → Working Schedules`.

### 2. Create an Employee Contract

1. Navigate to `Payroll → Contracts → Contracts` (or `Employees → Employees → Contracts`) and click **New**.
2. Fill required fields: Contract Reference, Employee, Contract Start Date, Working Schedule, Work Entry Source (Working Schedule / Attendances / Planning), Salary Structure Type.
3. In the **Salary Information** tab set Wage Type (Fixed/Hourly), Schedule Pay, Wage, and Yearly Cost.
4. In the **Details** tab configure Part Time settings if applicable, and select a Contract Template.
5. In the **Signatories** tab assign PDF templates for new and updated contracts.
6. Optionally attach salary adjustments via the Salary Attachments smart button.
7. Click **Generate Offer** → **Send By Email** to send the contract for signature.
8. Contract statuses progress: New → Partially Signed → Fully Signed.

### 3. Resolve Work Entry Conflicts & Generate Pay Run

1. Navigate to `Payroll → Work Entries → Work Entries`. The default Conflicting filter shows entries needing resolution.
2. Click an orange-triangle entry → **Edit** to view the conflict. For time off conflicts, click **Approve Time Off** or **Refuse Time Off**.
3. After resolving issues in source apps, click **Regenerate Work Entries** to rebuild entries for selected employees and date range.
4. Click **Generate Pay Run** on the Work Entries dashboard to create a batch with status Ready.

### 4. Process Payslips (Individual)

1. Navigate to `Payroll → Payslips → To Pay` or `All Payslips`, click **New**.
2. Select Employee (auto-fills Contract, Structure). Adjust Period dates.
3. Review **Worked Days & Inputs** tab; add Other Inputs (deductions, reimbursements) as needed.
4. Click **Compute Sheet** to populate the Salary Computation tab.
5. Click **Create Draft Entry** → confirm → journal entry draft is created; status changes to Done.
6. Post the journal entry via the Journal Entry smart button.
7. Click **Create Payment Report** → select export format (NACHA/CSV) and bank journal → **Generate**.
8. Click **Pay** → configure payment method → **Create Payments**.
9. Once funds are confirmed, click **Mark as paid**.

### 5. Process a Pay Run (Batch)

1. Open the pay run from `Payroll → Payslips → Pay Runs`.
2. Click **Create Draft Entry** → confirm. Status changes to Done.
3. Click **Payment Report** → select format and date → **Generate** → download file.
4. Click **Mark as paid** to finalize all payslips in the batch.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.payslip` | Individual payslip |
| `hr.payslip.run` | Pay run / batch |
| `hr.contract` | Employee contract |
| `hr.work.entry` | Work entry record |
| `hr.work.entry.type` | Work entry type definition |
| `hr.salary.rule` | Salary computation rule |
| `hr.payroll.structure` | Salary structure |
| `hr.payroll.structure.type` | Salary structure type |
| `hr.salary.attachment` | Salary adjustment / attachment |
| `hr.contract.type` | Contract type (Permanent, Temporary, etc.) |

### Key Fields

- `hr.payslip`: `employee_id`, `contract_id`, `struct_id`, `date_from`, `date_to`, `state` (draft/verify/done/paid/cancel), `payslip_run_id`, `worked_days_line_ids`, `input_line_ids`, `line_ids`
- `hr.contract`: `employee_id`, `state` (draft/open/close/cancel), `date_start`, `date_end`, `wage`, `structure_type_id`, `work_entry_source`, `resource_calendar_id`
- `hr.work.entry`: `employee_id`, `work_entry_type_id`, `date_start`, `date_stop`, `duration`, `state` (draft/validated/conflict/cancelled)
- `hr.work.entry.type`: `name`, `code`, `color`, `round_days`, `round_days_type`

### Important Views / Menu Paths

- `Payroll → Dashboard` — warnings for missing contracts, bank accounts, etc.
- `Payroll → Work Entries → Work Entries` — Gantt view of all work entries
- `Payroll → Payslips → To Pay` / `All Payslips` — list views
- `Payroll → Payslips → Pay Runs` — batch list grouped by status
- `Payroll → Contracts → Contracts` — contract list grouped by status
- `Payroll → Employees → Salary Adjustments` — salary attachment list
- `Payroll → Configuration → Settings` — accounting, localization, time off, payroll settings
- `Payroll → Configuration → Work Entries → Work Entry Types`
- `Payroll → Configuration → Other Input Types` — salary adjustment types
- `Payroll → Configuration → Templates` — contract templates (requires `hr_contract_salary`)

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Work Entry Source field on contracts allows selection between Working Schedule, Attendances, and Planning as the source for work entry generation.
- Salary Attachments renamed to Salary Adjustments in UI; model remains `hr.salary.attachment`.
- `hr_contract_salary` and `hr_contract_salary_payroll` modules required for contract template features and PDF signatories.
- Payslip PDF Display setting added to show/hide PDF on validation.
- YTD Reset Date setting added in Payroll configuration.
- Batch Account Move Lines setting creates a single anonymized journal entry per period.

## Common Pitfalls

- **Work entry conflicts block payslip generation.** All conflicts for the current pay period must be resolved before creating payslips or pay runs.
- **Missing bank account or untrusted bank.** Employees must have a bank account marked as Trusted in their Personal tab; otherwise the Pay button throws an error.
- **Only one running contract per employee.** Multiple active contracts cause payslip errors. Ensure previous contracts are expired or cancelled.
- **Localization must be installed first.** Without the correct country localization, salary structures and tax rules are missing, producing incorrect payslips.
- **Deferred time off.** If time off is taken after payslips are validated, configure a Deferred Time Off responsible to handle the adjustment in the next period rather than cancelling payslips.
