---
name: time_off
description: "Manage employee time off requests, allocations, accrual plans, public holidays, and mandatory days."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Time Off — Odoo 19.0 Skill Reference

## Overview

The **Time Off** app is the centralized hub for leave management. Employees request time off and view balances; managers allocate time, approve requests, and monitor team availability. The app supports multiple time off types with configurable approval chains, accrual plans for earned leave, public holidays, mandatory days, and negative balance caps. It integrates with Payroll (work entry types), Attendances (extra hours deduction), and Timesheets.

## Key Concepts

- **Time Off Type** — A category of leave (Paid Time Off, Sick Time Off, Unpaid, Compensatory Days, Extra Hours). Each type defines approval rules, allocation rules, and payroll work entry type. Preconfigured: PTO, Sick, Unpaid, Compensatory Days, Extra Hours.
- **Allocation** — A grant of time off to employees. Can be Regular (immediate) or Accrual (earned over time). Supports single-employee or bulk allocation (by employee, company, department, or tag).
- **Accrual Plan** — Rules for earning time off over time. Configures accrual period, carry-over policy, milestones, and caps.
- **Milestone (Rule)** — A tier within an accrual plan defining accrual rate, frequency, caps, carry-over limits, and start delay.
- **Time Off Request** — An employee's request to use allocated time off for a specific period.
- **Approval Chain** — Who must approve requests/allocations: No Validation, Time Off Officer, Employee's Approver, or both.
- **Time Off Officer** — User designated per time off type to approve requests and allocations.
- **Public Holiday** — Non-working day configured globally or per working schedule. Reflected across Calendar, Planning, Manufacturing, etc.
- **Mandatory Day** — Day when time off is blocked for specific departments or the entire company.
- **Negative Cap** — Allows employees to go negative on a time off type up to a maximum excess amount.
- **Deduct Extra Hours** — Setting on a time off type that subtracts approved overtime before consuming leave balance.
- **Kind of Time Off** — Worked Time (counts toward accruals) vs. Absence (does not count).
- **Carry-Over** — Policy for rolling unused time off to the next year: None (reset to 0), All, or with a maximum.

## Core Workflows

### 1. Configure Time Off Types

1. Navigate to `Time Off → Configuration → Time Off Types`.
2. Click **New**. Enter name (e.g., Vacation).
3. **Time Off Requests**: Set Approval (No Validation / By Time Off Officer / By Employee's Approver / Both).
4. **Allocation Requests**: Set Requires Allocation (Yes/No Limit), Employee Requests (Extra Days Allowed / Not Allowed), Approval chain.
5. **Configuration**: Set Notified Time Off Officer, Take Time Off In (Day/Half Day/Hours), Kind of Time Off, Company.
6. Optionally enable: Deduct Extra Hours, Public Holiday Included, Allow To Attach Supporting Document, Allow Negative Cap (with maximum excess).
7. **Payroll**: Select Work Entry Type.
8. **Display**: Set Color and Cover Image.

### 2. Create Accrual Plans

1. Navigate to `Time Off → Configuration → Accrual Plans`, click **New**.
2. Enter Name, Accrued Gain Time (start/end of period), Carry-Over Time (start of year / allocation date / other).
3. Optionally enable Based on Worked Time.
4. Click **New Milestone** to add rules:
   - Set accrual rate (X days/hours per frequency: hourly/daily/weekly/monthly/etc.).
   - Configure Cap accrued time, Start Accruing delay, Carry over policy (None/All/Maximum), Milestone cap, Carry Over Validity.
5. For 2+ rules, set Milestone Transition (Immediately / After current period).

### 3. Allocate Time Off

1. Navigate to `Time Off → Management → Allocations`, click **New**.
2. Enter Name, Time Off Type, Allocation Type (Regular/Accrual), Validity Period, Allocation amount, Employee.
3. For bulk allocation: click Actions gear → **Multiple Requests**. Select Mode (By Employee/Company/Department/Employee Tag).
4. Click **Create Allocations**.

### 4. Request Time Off (Employee)

1. Employee navigates to `Time Off → My Time → Dashboard`.
2. Click **New Time Off** or select dates on the calendar.
3. Select Time Off Type, dates, and optionally attach supporting documents.
4. Submit request for approval.

### 5. Approve Time Off (Manager)

1. Navigate to `Time Off → Management → Time Off`.
2. Review pending requests. Click **Approve** or **Refuse**.
3. For two-level approval (Employee's Approver + Time Off Officer), both must approve sequentially.

### 6. Configure Public Holidays

1. Navigate to `Time Off → Configuration → Public Holidays`, click **New**.
2. Enter Name, Start Date, End Date, optionally scope to specific Working Hours.
3. Select Work Entry Type for payroll integration.

### 7. Configure Mandatory Days

1. Navigate to `Time Off → Configuration → Mandatory Days`, click **New**.
2. Enter Name, Start Date, End Date, optionally scope to Departments.
3. Employees in selected departments cannot request time off on those days.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.leave` | Time off request |
| `hr.leave.type` | Time off type definition |
| `hr.leave.allocation` | Time off allocation |
| `hr.leave.accrual.plan` | Accrual plan |
| `hr.leave.accrual.plan.level` | Accrual plan milestone/rule |
| `resource.calendar.leaves` | Public holidays |
| `hr.leave.mandatory.day` | Mandatory day |

### Key Fields

- `hr.leave`: `employee_id`, `holiday_status_id` (time off type), `date_from`, `date_to`, `number_of_days`, `state` (draft/confirm/validate1/validate/refuse)
- `hr.leave.type`: `name`, `requires_allocation`, `allocation_validation_type`, `leave_validation_type`, `request_unit` (day/half_day/hour), `time_type` (leave/other), `create_calendar_meeting`, `work_entry_type_id`
- `hr.leave.allocation`: `name`, `holiday_status_id`, `allocation_type` (regular/accrual), `accrual_plan_id`, `date_from`, `date_to`, `number_of_days`, `employee_id`, `state`
- `hr.leave.accrual.plan`: `name`, `accrued_gain_time`, `carryover_date`, `is_based_on_worked_time`, `transition_mode`

### Important Menu Paths

- `Time Off → My Time → Dashboard` — personal overview with balances and calendar
- `Time Off → My Time → My Time Off` — personal requests
- `Time Off → My Time → My Allocations` — personal allocations
- `Time Off → Management → Time Off` — approve/refuse requests
- `Time Off → Management → Allocations` — manage allocations
- `Time Off → Overview` — team calendar view
- `Time Off → Configuration → Time Off Types`
- `Time Off → Configuration → Accrual Plans`
- `Time Off → Configuration → Public Holidays`
- `Time Off → Configuration → Mandatory Days`
- `Time Off → Reporting → by Time Off Type / by Department / by Employee`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Negative Cap feature allows employees to request more time off than allocated, up to a configurable Maximum Excess Amount.
- Carry Over Validity on accrual milestones sets a time limit for using rolled-over days.
- Accrual plan milestone supports Based on Worked Time — only actual worked days count toward accrual.
- Multiple Requests feature supports bulk allocation by Employee Tag in addition to Employee, Company, and Department.
- Accrual start date auto-adjusts to period boundaries based on Accrued Gain Time setting (start vs. end of period).

## Common Pitfalls

- **Accrual rule carry-over overrides plan carry-over.** If a milestone rule sets carry-over to "None (reset to 0)", it takes precedence over the accrual plan's Carry-Over Time setting.
- **Public holidays must be configured per company.** In multi-company databases, holidays are company-specific.
- **Mandatory days block time off silently.** Employees cannot submit requests for mandatory days; they receive no advance warning unless informed separately.
- **Allocation required vs. No Limit.** If a time off type is set to "No Limit", employees can request unlimited time off without prior allocation — use cautiously.
- **Time off type "Kind" affects accruals.** Types set to "Absence" do not count as worked time for accrual plans with Based on Worked Time enabled.
