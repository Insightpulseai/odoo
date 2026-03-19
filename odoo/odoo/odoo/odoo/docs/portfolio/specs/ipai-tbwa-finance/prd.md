# IPAI TBWA Finance - Product Requirements Document

## Executive Summary

The IPAI TBWA Finance module provides a unified platform for managing TBWA Philippines' financial operations, specifically:

1. **Month-End Closing Automation** - Replacing SAP Advanced Financial Closing (AFC) with Odoo-native task management
2. **BIR Tax Compliance** - Managing Philippine Bureau of Internal Revenue statutory filings

## Problem Statement

TBWA Philippines currently manages financial close and tax compliance through:
- Manual spreadsheets for task tracking
- Separate calendars for deadlines
- Email-based approval workflows
- No integration between closing tasks and tax filings

This leads to:
- Missed deadlines and late filing penalties
- Duplicate effort between month-end and BIR prep
- No visibility into compliance status
- Audit trail gaps

## Solution Overview

A unified Odoo module that:
- Auto-generates tasks from templates each period
- Calculates deadlines using Philippine holiday calendar
- Enforces RACI workflow (Prep → Review → Approve)
- Provides Kanban dashboard for real-time status
- Blocks period close until all compliance checks pass

## User Stories

### US-1: Period Manager
> As a Finance Director, I want to open a new closing period so that all required tasks are automatically created with correct deadlines.

**Acceptance Criteria:**
- One-click period opening
- All month-end templates generate tasks
- BIR filing tasks generated based on frequency
- Deadlines calculated using holiday calendar

### US-2: Task Preparer
> As a Finance Staff (RIM), I want to see my assigned preparation tasks so that I can complete them before the deadline.

**Acceptance Criteria:**
- My Tasks view filtered by assigned user
- Clear due date display
- Attachment support for supporting documents
- Mark as done button

### US-3: Task Reviewer
> As a Finance Manager (BOM), I want to review completed tasks so that I can approve or return them.

**Acceptance Criteria:**
- Review queue showing pending reviews
- Side-by-side view of task and attachments
- Approve/Reject with comments
- Chatter for communication

### US-4: Compliance Officer
> As a Compliance Officer, I want to see all BIR filing statuses so that I ensure we file on time.

**Acceptance Criteria:**
- BIR Filing calendar view
- Status indicators (On Track, At Risk, Overdue)
- Reference number tracking after filing
- Penalty tracking for late filings

### US-5: Period Closer
> As a Finance Director, I want to close a period only when all checks pass so that we maintain compliance.

**Acceptance Criteria:**
- Pre-close validation checklist
- Block close if checks fail
- Period lock after closing
- Audit log of close action

## Features

### F1: Philippine Holiday Calendar
- 2025-2026 holidays pre-loaded
- Regular vs special non-working distinction
- Workday offset calculation
- Holiday CRUD for future years

### F2: Task Templates
- Month-end templates (20 tasks across 4 phases)
- BIR form templates (monthly, quarterly, annual)
- Template activation/deactivation
- OCA module reference for integration points

### F3: Task Management
- Unified task model for all task types
- RACI workflow enforcement
- State machine (Pending → In Progress → Review → Done)
- Overdue notifications via cron

### F4: Closing Period
- Period lifecycle (Draft → Open → In Progress → Closed)
- One-click task generation
- Compliance check framework
- Period locking

### F5: BIR Return Tracking
- VAT return preparation
- WHT return preparation
- Alphalist compilation
- Filing reference tracking

### F6: Dashboard & Reporting
- Kanban by phase/state
- Calendar by due date
- Aging analysis
- Period status summary

## Data Model

```
ph.holiday
├── name, date, holiday_type

finance.task.template
├── name, task_type, phase
├── bir_form_type, frequency
├── prep/review/approve_day_offset
├── odoo_model, oca_module

closing.period
├── name, date_start, date_end
├── state, company_id
├── task_ids, compliance_check_ids

finance.task
├── template_id, period_id
├── task_type, phase, bir_form_type
├── state, prep/review/approve workflow
├── assigned_user_id, due_date

compliance.check
├── period_id, check_type, name
├── status, result_notes

bir.return
├── period_id, task_id
├── return_type, form_number
├── filing_date, reference_number
```

## Success Metrics

| Metric | Target |
|--------|--------|
| On-time BIR filing rate | 100% |
| Month-end close cycle time | ≤ 5 working days |
| Task overdue rate | < 5% |
| Audit finding rate | Zero material findings |

## Rollout Plan

1. **Phase 1 (Week 1-2)**: Module installation, team training
2. **Phase 2 (Week 3-4)**: January 2025 close (pilot)
3. **Phase 3 (Week 5+)**: Production use, feedback iteration
