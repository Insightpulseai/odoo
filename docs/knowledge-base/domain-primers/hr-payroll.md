# Domain Primer: HR & Payroll

## One-paragraph summary

HR manages the employee lifecycle from hiring through separation. Payroll handles compensation calculation including statutory deductions. In SAP, this is HCM (Human Capital Management). Odoo CE provides employee management, attendance, leave, and basic payroll — but PH-specific statutory compliance (SSS, PhilHealth, Pag-IBIG, BIR) requires custom modules.

## Key Concepts

| Concept | Definition | Odoo Model |
|---------|-----------|------------|
| Employee | Person employed by the company | hr.employee |
| Department | Organizational unit | hr.department |
| Contract | Employment terms and compensation | hr.contract |
| Leave | Time-off request and allocation | hr.leave, hr.leave.allocation |
| Attendance | Clock-in/clock-out records | hr.attendance |
| Payslip | Salary computation document | hr.payslip |

## SAP-to-Odoo Quick Map

| SAP | Odoo |
|-----|------|
| Personnel Master (PA0000) | hr.employee |
| Org Unit | hr.department |
| Infotype 0001 (Org) | hr.contract |
| Time Management (PT) | hr.attendance + hr.leave |
| Payroll (PY) | hr.payslip |

## PH-Specific Gaps

| Requirement | Status |
|------------|--------|
| SSS contribution tables | Needs ipai_hr_ph_sss |
| PhilHealth premiums | Needs ipai_hr_ph_philhealth |
| Pag-IBIG contributions | Needs ipai_hr_ph_pagibig |
| BIR withholding tax on compensation | Needs ipai_hr_ph_bir |
| 13th month pay | Configurable via salary rules |
| De minimis benefits | Needs tax-exempt configuration |
