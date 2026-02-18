---
name: activities
description: Schedule, manage, and track follow-up activities (calls, emails, meetings, to-dos) on any record.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# activities — Odoo 19.0 Skill Reference

## Overview

Activities are follow-up tasks tied to records in an Odoo database. They enable users to schedule calls, emails, meetings, to-dos, document uploads, and signature requests directly from the chatter, Kanban, list, or activity views. Activities appear with color-coded due-date indicators (green = future, orange = today, red = overdue) and support chaining — one activity can automatically suggest or trigger the next. All Odoo users across CRM, Sales, Helpdesk, and other apps use activities to track action items and maintain workflow momentum.

## Key Concepts

- **Activity**: A scheduled follow-up task attached to a specific record.
- **Activity type**: Defines the category (To-Do, Email, Call, Meeting, Document, Signature, Grant Approval) and its behavior (e.g., Call opens calendar).
- **Chatter**: The discussion thread on a record where activities are displayed under "Planned Activities".
- **Activity view**: Dedicated grid view (clock icon in top-right) showing all records vs. activity types with color-coded cells.
- **Due date colors**: Green (future), Orange (today), Red (overdue) — consistent across all views.
- **Chaining type**: An activity type can **Suggest Next Activity** (proposes it) or **Trigger Next Activity** (auto-creates it) after completion.
- **Keep Done**: Activity type setting to keep completed activities visible in the activity view.
- **All scheduled activities**: Global activity list accessed via the clock icon in the header menu; organized by app and sub-section with Late/Today/Future counts.

## Core Workflows

### 1. Schedule an activity from the chatter

1. Open any record with a chatter.
2. Click the **Activity** button at the top of the chatter.
3. Select activity type (To-Do, Email, Call, Meeting, etc.).
4. Fill in Summary, Due Date, Assigned to, and Log a note.
5. Click **Save** to schedule, or **Mark Done** to log immediately.

### 2. Schedule from Kanban view

1. In Kanban view, click the clock icon at the bottom of a record card.
2. Click **+ Schedule An Activity**.
3. Fill out the Schedule Activity form and confirm.

### 3. Schedule from list view

1. In list view, reveal the **Activities** column if hidden (settings adjust icon).
2. Click the clock icon for a record.
3. Click **+ Schedule an activity** and complete the form.

### 4. Schedule a meeting activity

1. Select **Meeting** as the activity type.
2. Fill in summary and details, click **Schedule**.
3. The user's calendar opens; click desired date/time.
4. Complete the New Event form, click **Save & Close**.

### 5. Create a custom activity type

1. Settings > Discuss section > Activity Types.
2. Click **New**.
3. Set: Name, Action (Upload Document / Call / Meeting / Request Signature), Default User, Default Summary, Keep Done, Default Note.
4. Configure Next Activity section: Chaining Type (Suggest/Trigger), target activity, Schedule timing (Days/Weeks/Months after deadline or completion).

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `mail.activity` | Activity records |
| `mail.activity.type` | Activity type definitions |
| `mail.activity.mixin` | Mixin added to models that support activities |

### Key Fields on `mail.activity`

| Field | Purpose |
|-------|---------|
| `activity_type_id` | Link to activity type |
| `summary` | Short description |
| `date_deadline` | Due date |
| `user_id` | Assigned user |
| `note` | Additional details |
| `res_model_id` | Target model |
| `res_id` | Target record ID |

### Key Fields on `mail.activity.type`

| Field | Purpose |
|-------|---------|
| `name` | Activity type name |
| `category` | Action category (upload_file, phonecall, meeting, sign) |
| `default_user_id` | Auto-assigned user |
| `chaining_type` | suggest or trigger |
| `suggest_next_action_id` / `trigger_next_action_id` | Next activity in chain |
| `delay_count` / `delay_unit` / `delay_from` | Scheduling offset |
| `keep_done` | Keep visible after completion |

### Menu Paths

- `Settings > Discuss > Activity Types`
- Per-app: e.g., `CRM > Configuration > Activity Types`
- Global activity list: clock icon in header menu

### Activity Type Icons

| Icon | Type |
|------|------|
| Clock | Default |
| Phone | Call |
| Envelope | Email |
| Check | To-Do |
| Users | Meeting |
| Upload | Document |
| Pencil-square | Signature |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Activity type availability varies by installed apps**: Some types (e.g., Request Signature) require specific apps (Odoo Sign) to be installed.
- **Upload Document hides chaining**: The Chaining Type field does not appear when the action is Upload Document.
- **Default User is overridable**: The Default User and Default Summary on an activity type are pre-filled but can be changed before scheduling.
- **Color coding is universal**: Green/orange/red due-date colors are consistent across all views and apps; they cannot be customized.
