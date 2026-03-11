---
name: appraisals
description: "Schedule and conduct employee performance reviews with self-assessment, manager feedback, goals, 360 feedback, and skills tracking."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Appraisals — Odoo 19.0 Skill Reference

## Overview

The **Appraisals** app manages recurring and ad-hoc performance reviews. It supports employee self-assessment, manager feedback, 360-degree peer feedback (via Surveys), goal tracking, skill evaluation, and final ratings. Appraisals can be scheduled automatically via configurable appraisal plans or created manually for events like promotions or transfers.

## Key Concepts

- **Appraisal** — A performance review record linking an employee, manager, appraisal template, and date. Statuses: New → Confirmed → Done (can be Reopened).
- **Appraisal Plan** — Automatic scheduling rules defining review frequency (e.g., 6 months after hire, then annually).
- **Appraisal Template** — Form structure with sections for employee and manager feedback. A Default Template ships with the app.
- **Employee's Feedback** — Self-assessment sections: My Work, My Future, My Feelings. Hidden from manager until employee toggles "Visible to Manager".
- **Manager's Feedback** — Manager sections: Feedback, Evaluation, Improvements. Hidden from employee until manager toggles "Visible to Employee".
- **360 Feedback** — Peer feedback surveys sent to coworkers during the appraisal process. Managed via the Surveys app.
- **Goal** — Measurable objective assigned to an employee with progress tracking (0/25/50/75/100%), deadline, and tags.
- **Final Rating** — Manager's overall assessment. Default scale: Needs Improvement, Meets Expectations, Exceeds Expectations, Strongly Exceeds Expectations, Good. Configurable via Evaluation Scale.
- **Skills Tab** — Auto-populated from employee skills on confirmation; skill levels can be updated during review with justification.
- **Private Note** — Manager-only notes tab, invisible to the employee.
- **Appraisals Automation** — Setting to automatically schedule AND confirm appraisals per the plan.

## Core Workflows

### 1. Configure Appraisal Plans

1. Navigate to `Appraisals → Configuration → Settings`.
2. Under **Appraisals Plans**, set the schedule (default: 6 months, 6 months, then every 12 months).
3. Optionally enable **Appraisals Automation** to auto-confirm scheduled appraisals.

### 2. Manually Create an Appraisal

1. Navigate to `Appraisals` app, click **New**.
2. Select Employee (auto-fills Manager, Job Position, Department).
3. Adjust Appraisal Date if needed. Select Appraisal Template.
4. Click **Confirm** to activate the appraisal and notify the employee.

### 3. Conduct the Appraisal

1. **Employee** fills out Employee's Feedback, updates skills in the Skills tab, then toggles "Visible to Manager".
2. **Manager** reviews goals and requests 360 Feedback (click **Ask Feedback** → select recipients → **Send**).
3. **Manager** fills out Manager's Feedback; optionally toggles "Visible to Employee".
4. **Schedule meeting**: Click the Meeting smart button or use activity scheduling.
5. **Review meeting**: Discuss both feedback sections, review skills and goals, agree on next steps.

### 4. Complete the Appraisal

1. Manager adds Private Note (optional).
2. Manager selects **Final Rating** from the Evaluation Scale.
3. Click **Mark as Done**. Status changes to Done; form locks.
4. To edit after completion: click **Reopen** → **Confirm** → make changes → **Mark as Done**.

### 5. Manage Goals

1. Navigate to `Appraisals → Goals`, click **New**.
2. Enter Goal name, Employee, Progress (0-100%), Manager, Deadline, Tags.
3. Add description and optional checklist in the Description tab.
4. Update progress during reviews. Click **Mark as Done** when 100% complete.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.appraisal` | Appraisal record |
| `hr.appraisal.goal` | Employee goal |
| `hr.appraisal.goal.tag` | Goal tag |
| `hr.appraisal.note` | Private manager note |
| `survey.survey` | 360 feedback survey |

### Key Fields

- `hr.appraisal`: `employee_id`, `manager_id`, `department_id`, `date_close` (appraisal date), `state` (new/pending/done/cancel), `final_interview`, `employee_feedback_published`, `manager_feedback_published`
- `hr.appraisal.goal`: `name`, `employee_id`, `manager_id`, `deadline`, `progress` (selection: 0/25/50/75/100), `tag_ids`, `description`

### Important Menu Paths

- `Appraisals` — main dashboard with appraisal cards
- `Appraisals → Goals` — goal list grouped by employee
- `Appraisals → Configuration → Settings` — appraisal plans, automation
- `Appraisals → Configuration → 360 Feedback` — survey list
- `Appraisals → Configuration → Evaluation Scale` — rating options
- `Appraisals → Configuration → Tags` — goal tags
- `Appraisals → Configuration → Appraisal Templates`
- `Appraisals → Reporting → Appraisal Analysis`
- `Appraisals → Reporting → Skills Evolution`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Appraisals Automation setting auto-confirms scheduled appraisals without manual intervention.
- Visibility toggles for both employee and manager feedback sections ("Visible to Manager" / "Visible to Employee").
- Skills Evolution report added under Reporting.
- Default appraisal template includes structured sections: My Work, My Future, My Feelings (employee) and Feedback, Evaluation, Improvements (manager).
- Goal progress uses discrete steps (0%, 25%, 50%, 75%, 100%) rather than free-form percentage.

## Common Pitfalls

- **Appraisal must be Confirmed before editing.** Unconfirmed appraisals have locked feedback fields.
- **Skills tab only appears after confirmation.** Skills are copied from the employee record at confirmation time.
- **Changing Appraisal Plans updates all employees with empty Next Appraisal Date.** Be cautious when modifying the global schedule.
- **360 Feedback requires the Surveys app.** The Ask Feedback button sends surveys, which must be installed.
- **Mark as Done locks the form.** Use Reopen to make post-completion edits, but this requires re-confirming.
