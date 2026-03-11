---
name: recruitment
description: "Manage job positions, applicant pipelines, interviews, and hiring workflows."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Recruitment — Odoo 19.0 Skill Reference

## Overview

The **Recruitment** app manages the full hiring pipeline from job position creation and publishing through applicant tracking, interview scheduling, offer management, and contract signing. Applicants flow through a Kanban board of configurable stages. The app integrates with Website (job posting), Surveys (interview forms), Documents (resume storage), Sign (contract signing), and Employees (onboarding).

## Key Concepts

- **Job Position** — An open role with department, location, employment type, salary range, and expected skills. Published to the website for applicants.
- **Applicant Card** — Kanban card representing one candidate for a specific job position. Contains contact info, resume, interview results, and stage history.
- **Applicant Flow** — The progression of an applicant through pipeline stages (New → Initial Qualification → First Interview → Second Interview → Contract Proposal → Contract Signed).
- **Stage** — A Kanban column in the pipeline. Each stage can trigger an automatic email template, be marked as a Hired Stage, and be scoped to specific job positions.
- **Status (Kanban Color)** — Per-card indicator: Green (ready for next stage), Red (blocked), Gray (in progress).
- **Interview Form (Survey)** — A questionnaire/test sent to applicants via the Surveys app to evaluate fit. Configured per job position.
- **Resume Digitization (OCR)** — IAP-powered extraction of name, phone, and email from uploaded resumes. Options: Do not digitize, On demand, Automatically.
- **Resume Display** — Setting to show the CV inline on the applicant card (right side panel).
- **Salary Package Configurator** — Offer mechanism with configurable expiration days.
- **Source** — Channel through which an applicant discovered the job (job board, referral, direct).
- **Email Templates** — Preconfigured templates: Applicant Acknowledgement, Interest, Not Interested Anymore, Refuse, Schedule Interview.

## Core Workflows

### 1. Create and Publish a Job Position

1. Navigate to `Recruitment` dashboard, click **New**.
2. Enter Job Position name and Application email alias.
3. Click the job card's dropdown → **Configuration** to edit details.
4. Fill Recruitment tab: Department, Job Location, Employment Type, Working Schedule, Salary Range, Expected Skills, Recruiter, Interviewers, Interview Form, Contract Template.
5. Write the job description in the **Job Summary** tab.
6. Configure **Application Info** tab: Time to Answer, Process steps, Days to get an Offer.
7. Publish the position via the Website app.

### 2. Process Applicants Through the Pipeline

1. Applicants arrive in the **New** stage automatically (online application, email alias, or manual entry).
2. Review applicant card: resume, contact info, notes. Send Interview Survey if needed.
3. Move qualified applicants to **Initial Qualification** (drag-and-drop or status bar click).
4. Schedule first interview: use the **Schedule Interview** email template or manual calendar.
5. After interview, move to **First Interview** then **Second Interview** stages.
6. Send job offer: move to **Contract Proposal**, use the salary configurator to generate an offer.
7. Once contract is signed, move to **Contract Signed** (Hired Stage flag triggers hire date).
8. Create employee record from the applicant card.

### 3. Refuse an Applicant

1. Open the applicant card and click **Refuse**.
2. Select a refuse reason and optionally send the Recruitment: Refuse email template.
3. The applicant is archived.

### 4. Customize Pipeline Stages

1. In Kanban view, click the gear icon on a stage column → **Edit**.
2. Configure: Stage Name, Email Template (auto-send on entry), Folded in Kanban, Hired Stage, Job Specific, Show in Referrals (with points), Tooltip labels, Requirements.
3. To add a stage: click **+ Stage**, enter title, click **Add**.
4. To delete: gear icon → **Delete** (requires no applicants in stage).

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `hr.applicant` | Applicant record |
| `hr.job` | Job position |
| `hr.recruitment.stage` | Pipeline stage |
| `hr.recruitment.source` | Recruitment source/channel |
| `hr.candidate` | Candidate (person, may have multiple applications) |
| `survey.survey` | Interview form / survey |

### Key Fields

- `hr.applicant`: `partner_name` (candidate name), `email_from`, `partner_phone`, `job_id`, `stage_id`, `kanban_state` (normal/done/blocked), `user_id` (recruiter), `interviewer_ids`, `salary_proposed`, `salary_expected`, `priority`
- `hr.job`: `name`, `department_id`, `address_id`, `employment_type_id`, `no_of_recruitment` (target), `no_of_hired_employee`, `alias_id` (email alias), `website_published`
- `hr.recruitment.stage`: `name`, `sequence`, `template_id` (email template), `fold` (folded in kanban), `hired_stage`, `job_ids` (job-specific), `is_in_referral`

### Important Menu Paths

- `Recruitment` dashboard — job position Kanban cards
- `Recruitment → Applications → All Applications`
- `Recruitment → Configuration → Settings` — Interview Survey, Resume Digitization, Salary Package
- `Recruitment → Configuration → Stages`
- `Recruitment → Reporting → Applicant Analysis`, `Source Analysis`, `Velocity Analysis`, `Team Performance`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Resume Display setting allows inline CV viewing on applicant cards (right-side panel in full-screen).
- Resume Digitization (OCR) supports three modes: disabled, on-demand, automatic.
- Velocity Analysis and Team Performance reports added to Reporting menu.
- Stages apply globally unless explicitly scoped to specific job positions via the Job Specific field.

## Common Pitfalls

- **Stages are global by default.** Adding/deleting/modifying a stage affects all job positions unless the stage's Job Specific field is set.
- **Cannot delete a stage with applicants.** Applicants must be moved, archived, or deleted first.
- **Interview Survey requires Surveys app.** Enabling Send Interview Survey installs the Surveys module.
- **Resume OCR requires IAP credits.** The Digitize Automatically option consumes credits for each submitted resume.
- **Email alias must be unique per job position.** Duplicate aliases cause applications to route to the wrong position.
