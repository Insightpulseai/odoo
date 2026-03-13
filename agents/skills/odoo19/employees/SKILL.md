---
name: employees
description: "Centralized employee records with personal info, contracts, skills, equipment, onboarding, and offboarding."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Employees — Odoo 19.0 Skill Reference

## Overview

The **Employees** app is the central HR registry. Each employee record holds general information, work details, resume/skills, personal data, payroll configuration, and settings for integrations with Attendances, Time Off, Payroll, Fleet, Appraisals, and Planning. The app manages departments, onboarding/offboarding programs, equipment tracking, certifications, badges, and learning. Real-time presence status (attendance or system login) appears on the dashboard.

## Key Concepts

- **Employee Record** — Master profile with tabs: Work, Resume, Certifications, Personal, Payroll, Salary Adjustments, Settings.
- **Department** — Organizational unit with a manager; drives org chart display.
- **Skill Type** — Category grouping skills (e.g., Languages, Soft Skills). Contains skills, levels (with progress percentages), and a default level.
- **Skill** — Specific competency within a skill type (e.g., Python under Programming).
- **Skill Level** — Proficiency tier (Beginner/Intermediate/Expert) with a percentage.
- **Certification** — Skill type marked as certification; tracked with validity dates on employee records.
- **Badge** — Achievement/recognition award granted to employees.
- **Equipment** — Tracked assets assigned to employees (laptop, phone, etc.).
- **Onboarding** — Customizable program of tasks for new hires.
- **Offboarding** — Customizable program of tasks when employees leave.
- **Presence Display** — Employee availability indicator, based on either Attendances check-in or system login status.
- **Advanced Presence Control** — Presence derived from email send rate or IP address.
- **Work Location** — Where the employee works each day (Home, Office, Other); displayed on Kanban card.
- **Approvers** — Per-employee designation of who approves Expenses, Time Off, Timesheets, and Attendance.

## Core Workflows

### 1. Create a New Employee

1. Navigate to `Employees` app, click **New**.
2. Enter Employee Name, work email, phone, tags, and photo.
3. **Work tab**: Set Company, Department, Job Position, Job Title, Manager, Work Address, Work Location. Configure Usual Work Location per weekday.
4. **Resume tab**: Add resume lines (experience, education, training). Add skills via Pick a Skill → select Category, Skill, Skill Level.
5. **Certifications tab**: Add certifications with validity dates (only for skill types marked as certification).
6. **Personal tab**: Enter private contact, bank account (mark as Trusted for payroll), emergency contact, citizenship, family, visa/work permit, education.
7. **Payroll tab**: Review contract overview, employer costs, configure Work Entry Source and Working Hours.
8. **Settings tab**: Link to database User, set Timezone, configure Approvers (HR Responsible, Expense, Time Off, Timesheet, Attendance), set PIN/RFID for kiosk access.

### 2. Configure Skill Types

1. Navigate to `Employees → Configuration → Skill Types`.
2. Click **New**. Enter Skill Type name, color, and optionally toggle Certification.
3. Add Skills via **Add a line** (e.g., Python, Java).
4. Add Levels via **Add a line** with Name and Progress percentage. Set one as Default Level.

### 3. Add a Bank Account

1. On employee Personal tab, type account number in Bank Accounts field → **Create and edit...**
2. Enter Account Number, Clearing Number, select or create Bank.
3. Click **Send Money** toggle to mark as Trusted (required for Payroll direct deposits).

### 4. Run Onboarding / Offboarding

1. Configure onboarding/offboarding plans under `Employees → Configuration`.
2. When a new employee is created (or an employee leaves), the plan generates a checklist of tasks.
3. Responsible parties complete and mark tasks as done.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.employee` | Employee record |
| `hr.department` | Department |
| `hr.skill.type` | Skill type / category |
| `hr.skill` | Individual skill |
| `hr.skill.level` | Proficiency level within a skill type |
| `hr.employee.skill` | M2M link between employee and skill |
| `hr.employee.category` | Employee tag |
| `hr.work.location` | Work location definition |
| `equipment.equipment` | Equipment record |

### Key Fields

- `hr.employee`: `name`, `work_email`, `work_phone`, `department_id`, `job_id`, `job_title`, `parent_id` (manager), `address_id` (work address), `resource_calendar_id` (working hours), `user_id` (linked user), `attendance_state`, `employee_skill_ids`, `certificate` (education level), `marital`, `bank_account_id`, `pin`, `barcode`
- `hr.department`: `name`, `manager_id`, `parent_id`, `company_id`
- `hr.skill.type`: `name`, `color`, `skill_ids`, `skill_level_ids`, `certification` (bool)

### Important Menu Paths

- `Employees` — main Kanban dashboard with presence status
- `Employees → Employees → Contracts` — shared with Payroll
- `Employees → Configuration → Settings` — Presence Display, Skills Management, Working Hours
- `Employees → Configuration → Skill Types`
- `Employees → Configuration → Work Locations`
- `Employees → Reporting → Retention Report`

### Settings

- **Presence Display**: Based on attendances or user status in system.
- **Advanced Presence Control**: Based on emails sent per hour or corporate IP addresses.
- **Skills Management**: Enables Resume tab on employee profiles.
- **Company Working Hours**: Default working schedule.
- **Contract/Work Permit Expiration Notice Period**: Days before expiration to notify.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Usual Work Location section added to Work tab — specify per-weekday location (Home/Office/Other), reflected on employee Kanban card.
- Advanced Presence Control via email count and IP address filtering.
- Certifications tab appears only when at least one skill type is marked as certification.
- Salary Adjustments tab added to employee form (previously only accessible from Payroll).
- Work Entry Source field on employee Payroll tab allows Working Schedules, Attendances, or Planning selection.

## Common Pitfalls

- **Bank account must be Trusted for payroll.** Untrusted accounts cause errors when processing direct deposits.
- **Skills can only be added from preconfigured Skill Types.** New skills cannot be created inline from the employee form; they must be added to the Skill Type first.
- **Working Hours are company-specific.** In multi-company databases, each company must have its own working schedules configured.
- **Employees are not users by default.** Creating an employee does not consume a subscription seat; linking them to a user does.
- **Department manager auto-populates Manager field.** Selecting a department overrides the Manager field with the department's configured manager.
