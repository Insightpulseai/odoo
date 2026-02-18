---
name: stages
description: Configure Kanban pipeline stages — ordering, rotting detection, progress bars, email/SMS templates, and folding.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# stages — Odoo 19.0 Skill Reference

## Overview

Stages organize an application's Kanban pipeline and track the progress of cards (tickets, leads, tasks, etc.) through a workflow. They are used in apps like CRM, Helpdesk, and Project. Stages are customizable: administrators can create, rename, reorder, and assign them to teams. Features include rotting lead detection (highlighting stale cards), progress bars showing status breakdowns, automatic email/SMS templates triggered on stage transitions, and stage folding in Kanban view. Pipeline managers and administrators configure stages to match their team's workflow.

## Key Concepts

- **Stage**: A named step in a Kanban pipeline (e.g., New, In Progress, Won, Closed).
- **Card**: The record represented in a stage (e.g., a CRM lead, Helpdesk ticket).
- **Days to rot**: Threshold after which a card in a stage is highlighted in red, indicating it needs attention. Disabled when set to 0.
- **Progress bar**: Visual indicator above each stage showing the percentage breakdown of card statuses (e.g., In progress, Ready, Blocked) with color coding.
- **Email template**: A preconfigured email automatically sent to the customer when a card reaches a specific stage.
- **SMS template**: A preconfigured SMS automatically sent on stage transition (requires IAP credits).
- **Folded stage**: A stage whose cards are hidden in the Kanban view. Cards in a permanently folded stage are considered "closed".
- **Temporary fold**: Manually folding a stage from Kanban view; does not close the cards.
- **Team assignment**: Stages can be assigned to one or more teams; the same stage can appear in multiple team pipelines.

## Core Workflows

### 1. View and reorder stages

1. Enable developer mode.
2. Navigate to the desired app > Configuration > Stages.
3. The default list view shows stages in pipeline order.
4. Drag stages using the draggable icon to reorder.
5. Alternatively, drag and drop stage columns directly in the Kanban view.

### 2. Create a new stage

1. Configuration > Stages > click **New**.
2. Enter a **Name** for the stage.
3. Configure optional fields: Days to rot, Email Template, SMS Template, Teams, Folded in Kanban.
4. Save.

### 3. Set up rotting detection

1. In Kanban view, click the gear icon on a stage > **Edit**.
2. Enter the number of **Days to rot** (threshold before cards turn red).
3. Click **Save**.
4. Cards exceeding the threshold are highlighted red; the stage header shows the count of rotting cards.

### 4. Add email/SMS templates to a stage

1. Open the stage form (Configuration > Stages > select stage).
2. In the **Email Template** field, select an existing template or create a new one.
3. In the **SMS Template** field, select or create an SMS template.
4. When a card enters this stage, the email/SMS is automatically sent.

### 5. Fold a stage permanently

1. Open the stage form.
2. Tick the **Folded in Kanban** checkbox.
3. Save. Cards in this stage are considered "closed" and hidden in the Kanban view.

### 6. Fold a stage temporarily

1. In Kanban view, hover over the stage header.
2. Click the gear icon > **Fold**.
3. The stage collapses but cards are **not** considered closed.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `crm.stage` | CRM pipeline stages |
| `helpdesk.stage` | Helpdesk pipeline stages |
| `project.task.type` | Project task stages |

### Key Fields (varies by model)

| Field | Purpose |
|-------|---------|
| `name` | Stage name |
| `sequence` | Display order |
| `fold` | Folded in Kanban (boolean) |
| `team_id` / `team_ids` | Associated team(s) |
| `template_id` | Email template triggered on stage entry |
| `sms_template_id` | SMS template triggered on stage entry |
| `days_to_rot` | Rotting threshold (CRM) |

### Menu Paths

- Developer mode required: `[App] > Configuration > Stages`
- Kanban view: gear icon on stage header > Edit / Fold

### Progress Bar Statuses (Helpdesk example)

| Status | Color | Meaning |
|--------|-------|---------|
| In progress | (default) | Active work |
| Ready | Green | Ready for next step |
| Blocked | Red | Blocked / needs attention |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Developer mode required**: The Configuration > Stages menu is only accessible in developer mode.
- **Folded = closed**: Permanently folding a stage marks its cards as "closed". Do not fold stages with active work — this causes reporting and communication issues.
- **Temporary fold is not persistent**: Manually folding from the Kanban view reverts on page reload; it does not affect card status.
- **SMS requires IAP credits**: SMS templates triggered by stage transitions consume In-App Purchase credits. Running out of credits prevents sending.
- **Days to rot = 0 disables**: Setting Days to rot to zero disables the rotting feature for that stage.
