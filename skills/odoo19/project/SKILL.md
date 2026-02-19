---
name: project
description: Project and task management with Kanban pipelines, milestones, profitability tracking, and collaboration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# project -- Odoo 19.0 Skill Reference

## Overview

Odoo Project provides Kanban-based project management for organizing tasks, tracking progress, and measuring profitability. Projects are broken into tasks organized by stages, with support for milestones, dependencies, recurring tasks, sub-tasks, and time tracking via Timesheets. It integrates tightly with Sales (billable projects), Accounting (profitability), and Planning (resource allocation). Used by project managers, team leads, and service delivery teams.

## Key Concepts

- **Project**: A container for tasks, with its own Kanban board, settings, and optional analytic account for profitability tracking.
- **Task**: A unit of work within a project, assigned to one or more users, with a status and optional deadline.
- **Stage**: A column in the Kanban view (e.g., New, In Progress, Done). Custom per-project or shared across projects.
- **Task Status**: Five fixed statuses independent of stages: In Progress, Changes Requested, Approved, Canceled, Done. "Done" and "Canceled" close the task.
- **Milestone**: A key checkpoint in a project with a deadline and delivered percentage; used for milestone-based invoicing.
- **Task Dependency**: A predecessor/successor relationship between tasks; successor tasks get "Waiting" status until predecessors are Done/Canceled/Approved.
- **Recurring Task**: A task configured to auto-create a new copy when the current one is marked Done or Canceled.
- **Sub-task**: A child task nested under a parent task for breaking down work.
- **Top Bar**: Customizable navigation bar within a project providing quick access to timesheets, sales orders, invoices, documents, and dashboards.
- **Project Profitability**: Dashboard tracking revenues (timesheets, materials, subscriptions) vs. costs (timesheets, purchases, expenses).
- **Visibility**: Access control for a project -- Private (invited internal), All Internal, or Public (portal + internal).

## Core Workflows

### 1. Create and Configure a Project

1. Open the **Project** app, click **Create**.
2. Enter a project **Name**, click **Create Project**.
3. Click the vertical ellipsis on the project card, select **Settings**.
4. Configure: Customer, Project Manager, Planned Date, Allocated Hours, Tags.
5. Under the **Settings** tab, enable features: Milestones, Task Dependencies, Recurring Tasks, Timesheets.
6. Set **Visibility** (Private, All Internal, or Public).

### 2. Create and Manage Tasks

1. Open a project to view the Kanban board.
2. Click the **+** button to create a new task; enter title and assignees, click **Add**.
3. Open the task to set: Deadline, Allocated Time, Tags, Customer, Sales Order Item, Milestone.
4. Drag tasks between stages as work progresses.
5. Set task status using the status buttons: In Progress, Changes Requested, Approved, Done, Canceled.
6. Use keyboard shortcuts in task title: `30h` (allocate time), `#tag`, `@user`, `!` (high priority).

### 3. Configure Milestones

1. On the project card, click the vertical ellipsis > **Milestones**.
2. Click **New**, enter the milestone **Name** and optional **Deadline**.
3. Optionally set **Quantity (%)** for milestone-based invoicing.
4. On tasks, set the **Milestone** field to link tasks to milestones.
5. When all linked tasks are Done/Canceled, the milestone is auto-marked as Reached.

### 4. Set Up Task Dependencies

1. Enable **Task Dependencies** in project settings.
2. On a task form, go to the **Blocked by** tab, click **Add a line** to add predecessor tasks.
3. Alternatively, in Gantt view, drag from one task to another to create a dependency arrow.
4. Successor tasks automatically get the "Waiting" status until predecessors are resolved.

### 5. Track Project Profitability

1. On the project card, click the vertical ellipsis > **Dashboard** (or add Dashboard to the top bar).
2. The profitability dashboard shows Revenues (timesheets, materials, invoices, subscriptions, down payments, expenses) vs. Costs (timesheets, purchase orders, materials, expenses, vendor bills, manufacturing orders).
3. Columns: Expected, To Invoice/To Bill, Invoiced/Billed.
4. All records must be linked to the project's analytic account to appear.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `project.project` | Projects |
| `project.task` | Tasks |
| `project.task.type` | Task stages |
| `project.milestone` | Project milestones |
| `project.tags` | Task tags |
| `project.collaborator` | External collaborators |

### Key Fields on `project.task`

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | Many2one | Parent project |
| `stage_id` | Many2one | Kanban stage |
| `user_ids` | Many2many | Assignees |
| `partner_id` | Many2one | Customer |
| `date_deadline` | Date | Deadline |
| `allocated_hours` | Float | Planned hours |
| `milestone_id` | Many2one | Linked milestone |
| `depend_on_ids` | Many2many | Predecessor tasks (blocked by) |
| `dependent_ids` | Many2many | Successor tasks (blocking) |
| `parent_id` | Many2one | Parent task (for sub-tasks) |
| `child_ids` | One2many | Sub-tasks |
| `recurring_task` | Boolean | Is recurring |
| `repeat_interval` | Integer | Recurrence interval |
| `repeat_unit` | Selection | Recurrence unit (day, week, month, year) |
| `sale_order_id` | Many2one | Linked sales order |
| `sale_line_id` | Many2one | Linked SO line |
| `priority` | Selection | `0` (normal), `1` (high) |

### Key Fields on `project.project`

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Project name |
| `partner_id` | Many2one | Customer |
| `user_id` | Many2one | Project manager |
| `privacy_visibility` | Selection | `followers`, `employees`, `portal` |
| `allow_milestones` | Boolean | Milestones enabled |
| `allow_task_dependencies` | Boolean | Dependencies enabled |
| `allow_recurring_tasks` | Boolean | Recurring tasks enabled |
| `allow_timesheets` | Boolean | Timesheets enabled |
| `analytic_account_id` | Many2one | Analytic account for profitability |

### Task Statuses (Fixed)

| Status | Meaning | Closes Task? |
|--------|---------|--------------|
| `In Progress` | Default; work ongoing | No |
| `Changes Requested` | Revisions needed | No |
| `Approved` | Ready for next stage | No |
| `Canceled` | Task canceled | Yes |
| `Done` | Task completed | Yes |

Note: "Changes Requested" and "Approved" reset to "In Progress" when a task moves to another Kanban stage.

### Menu Paths

- All Projects: `Project > All Projects`
- My Tasks: `Project > My Tasks`
- Configuration: `Project > Configuration > Stages / Tags / Settings`

## API / RPC Patterns

<!-- TODO: Project-specific external API examples not found in docs -->

Standard ORM access:

```python
# Create a project
project = env['project.project'].create({'name': 'Website Redesign', 'user_id': manager_id})

# Create a task
task = env['project.task'].create({
    'name': 'Design mockups',
    'project_id': project.id,
    'user_ids': [(6, 0, [user_id])],
    'allocated_hours': 20,
})

# Mark task as done
task.write({'stage_id': done_stage_id})  # Move to Done stage
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Task stages are no longer provided by default; users create custom stages per project.
- The **Top Bar** is a new navigation feature allowing quick access to related records (timesheets, invoices, documents) from within a project.
- Task statuses (In Progress, Changes Requested, Approved, Done, Canceled) are fixed and cannot be customized.
- Milestones are displayed in Gantt view with color-coded vertical lines (blue = on track, red = overdue).

## Common Pitfalls

- **Stages vs. statuses confusion**: Stages are customizable Kanban columns; statuses are fixed lifecycle states. Moving a task to a different stage resets "Changes Requested"/"Approved" back to "In Progress".
- **Milestones not auto-enabled**: Milestones must be explicitly enabled per project in settings. They are only auto-enabled for projects created from milestone-invoiced SOs.
- **Profitability requires analytic account**: Records (invoices, timesheets, purchases) must be linked to the project's analytic account to appear on the profitability dashboard.
- **Task dependencies block progress**: Successor tasks in "Waiting" status cannot be moved to "In Progress" until all predecessors are Done/Approved/Canceled. This can confuse teams not aware of the dependency.
- **Recurring tasks only trigger on Done/Canceled**: A recurring task creates the next instance only when its status is set to Done or Canceled, not when it moves to a particular stage.
