---
name: attendances
description: "Employee time clock with kiosk check-in/out, overtime tracking, and attendance reporting."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Attendances — Odoo 19.0 Skill Reference

## Overview

The **Attendances** app functions as a time clock. Employees check in and out via a kiosk device (tablet, PC, phone) or directly from the database. Managers view real-time availability, track overtime, review attendance logs, and generate reports. The app feeds work entries into Payroll when the contract's Work Entry Source is set to Attendances.

## Key Concepts

- **Kiosk Mode** — Dedicated device interface for check-in/out. Supports Manual Selection, Barcode/RFID, or both.
- **Check-in / Check-out** — Timestamp pair recording an employee's work session.
- **Backend Attendance** — Database users can check in/out directly from the top-right attendance icon in any Odoo app.
- **Approver** — User assigned to review/manage an employee's attendance records (set on employee Settings tab → Attendance field).
- **Overtime (Extra Hours)** — Time worked beyond the employee's scheduled hours. Can be automatically approved or require manager approval.
- **Tolerance Time (Company)** — Minutes of extra time that are NOT counted as overtime.
- **Tolerance Time (Employee)** — Minutes of deficit that do NOT penalize the employee's hours.
- **Automatic Check-Out** — Automatically checks out employees after a configurable tolerance period past their scheduled end time.
- **Absence Management** — Logs absences not covered by time off requests on the attendance report.
- **PIN Identification** — Optional numeric PIN required at kiosk check-in/out.
- **RFID/Badge** — Barcode or RFID token used for quick kiosk check-in/out.

## Core Workflows

### 1. Configure Attendances

1. Navigate to `Attendances → Configuration → Settings`.
2. **Modes**: Enable `Attendances from Backend` to allow database check-in. Enable `Automatic Check-Out` with tolerance hours. Enable `Absence Management`.
3. **Kiosk Mode**: Select `Manual Selection`, `Barcode/RFID`, or both.
4. **Kiosk Settings**: Set Barcode Source (Scanner/Camera), Display Time (seconds), enable Employee PIN Identification.
5. **Extra Hours**: Set Tolerance Time In Favor Of Company (minutes), Tolerance Time In Favor Of Employee (minutes), Extra Hours Validation (Automatic/Manager), Display Extra Hours.
6. Save settings.

### 2. Set Up a Kiosk

1. Navigate to `Attendances → Configuration → Settings`.
2. Copy the Attendance Kiosk URL.
3. Open the URL on a dedicated device (tablet/PC). The user is automatically signed out of the database.
4. Alternatively, click `Kiosk Mode` in the Attendances top menu.

### 3. Employee Check-in/out at Kiosk

- **Badge**: Tap "Scan your badge" → scan barcode with configured scanner/camera.
- **RFID**: Scan RFID fob with connected reader.
- **Manual**: Tap "Identify Manually" → search/browse employee list → tap name. Optionally enter PIN.
- Confirmation message shows Welcome/Goodbye with hours logged.

### 4. Review and Manage Attendance Records

1. Navigate to `Attendances` app dashboard to see all employee check-in/out records.
2. Officers can view, create, and modify records for all employees.
3. Approvers can view/modify records only for assigned employees.
4. Use Attendance Logs for detailed record viewing.
5. Use Reporting for aggregate analysis (hours by employee, department, overtime).

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.attendance` | Individual attendance record (check-in/out pair) |
| `hr.employee` | Employee (attendance fields: `attendance_state`, `last_attendance_id`) |

### Key Fields

- `hr.attendance`: `employee_id`, `check_in` (datetime), `check_out` (datetime), `worked_hours` (computed float), `overtime_hours`

### Access Rights

| Level | Capabilities |
|-------|-------------|
| No access | Check in/out via kiosk or backend icon only; no app access |
| Officer | Full CRUD on all attendance records; no settings access |
| Administrator | Full access including configuration and reporting |

### Important Menu Paths

- `Attendances` — dashboard with real-time check-in status
- `Attendances → Kiosk Mode` — enters kiosk on current device
- `Attendances → Configuration → Settings`
- `Attendances → Reporting`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Automatic Check-Out feature with configurable tolerance period.
- Absence Management setting logs unplanned absences on attendance reports (excludes flexible schedules).
- Extra Hours Validation supports Automatically Approved or Approved by Manager modes.
- Kiosk URL is auto-generated and can be regenerated for security purposes.
- Approved extra hours can be deducted from time off requests via the Time Off app's Deduct Extra Hours setting.

## Common Pitfalls

- **Kiosk URL is unsecured.** Anyone with the URL can access the kiosk; regenerate the URL if compromised.
- **Entering Kiosk Mode signs out the user.** The device loses database access — this is a security feature, not a bug.
- **Tolerance settings are cumulative.** The company tolerance and employee tolerance work independently; misconfiguration can hide or inflate overtime.
- **Approver field is per-employee.** If no Attendance approver is set, only Administrators can view that employee's records.
- **RFID/Barcode does not require the Barcode app.** The kiosk handles barcode scanning natively.
