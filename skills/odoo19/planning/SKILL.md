---
name: planning
description: Employee and resource scheduling with shift management, roles, auto-planning, and Sales/Project integration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# planning -- Odoo 19.0 Skill Reference

## Overview

Odoo Planning manages team schedules by dispatching shifts to resources (employees or materials). Shifts are organized by roles, can be linked to projects and sales orders, and support recurring schedules. The module features auto-planning based on roles, working hours, and availability. Planning integrates with Sales (sold services mapped to roles), Project (project-specific shifts), Timesheets (progress tracking), and HR (time off, contracts). Used by operations managers, team leads, and scheduling coordinators.

## Key Concepts

- **Shift**: A scheduled time block assigned to a resource, with a role, project, and optional sales order link.
- **Resource**: An entity that can be assigned shifts -- either an **Employee** (human) or a **Material** (equipment like cranes, vehicles).
- **Role**: A job function (e.g., chef, receptionist, driver) assigned to resources. Roles determine which shifts a resource can be assigned.
- **Default Role**: The primary role for a resource, given priority during auto-planning.
- **Shift Template**: A reusable shift configuration with start hour, duration, and role.
- **Open Shift**: A shift with no resource assigned; can be auto-assigned or claimed by employees.
- **Auto Plan**: Automatic assignment of open shifts and sales-order-linked shifts to resources based on roles, availability, and working hours.
- **Published Schedule**: A confirmed schedule that has been communicated to employees via email. Unpublished shifts appear with diagonal stripes.
- **Material**: A non-human resource (equipment) that can be scheduled with shifts and working hours.
- **Property Fields**: Custom fields linked to roles that appear on all shifts for that role (e.g., accreditation, location, language).

## Core Workflows

### 1. Configure Roles and Resources

1. Navigate to **Planning > Configuration > Roles**, click **New**.
2. Enter the role **Name** (e.g., Bartender, Forklift Operator).
3. Assign **Resources** (employees and/or materials) who can perform this role.
4. Optionally link **Services** (from Sales app) to the role.
5. For employees: go to **Planning > Configuration > Employees**, open an employee, go to **Work Information** tab.
6. Set **Working Hours** and assign one or more **Planning Roles** with a **Default Role**.

### 2. Create and Manage Shifts

1. Open any schedule view (My Planning, Schedule by Resource/Role/Project).
2. Click **New** to open the shift form.
3. Select a **Template** (if available) to pre-fill details.
4. Set: **Resource** (leave empty for open shift), **Role**, **Project**, **Sales Order Item**, **Date/Time**.
5. Optionally enable **Repeat** for recurring shifts (configures frequency and end date).
6. Click **Publish & Save** to confirm and notify the assigned employee.

### 3. Auto-Plan Open Shifts

1. Ensure open shifts exist (shifts with no resource assigned) and/or sales orders with services linked to roles.
2. Click **Auto Plan** on any schedule view.
3. Odoo assigns shifts based on: matching roles, default role priority, conflict avoidance (no overlaps), time off, working hours, and active contracts.
4. Review the auto-assigned schedule.
5. Click **Publish** to confirm and notify employees.

### 4. Employee Self-Service: Switch or Unassign

1. **Switch shifts** (default): Employee clicks **Ask to switch** on an unwanted shift. Other employees with the same role see the shift and can click **I take it**.
2. **Unassignment** (optional): Enable in **Planning > Configuration > Settings > Allow Unassignment**. Employees can click **I am unavailable** to revert a shift to an open shift.

### 5. Copy Schedules Between Weeks

1. On a schedule view, use the **Copy Previous** button to duplicate last week's shifts to the current week.
2. Copied shifts appear as planned (unpublished) with diagonal stripes.
3. Adjust as needed, then click **Publish** to finalize.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `planning.slot` | Shifts (scheduled time blocks) |
| `planning.role` | Roles for resources |
| `planning.slot.template` | Shift templates |
| `resource.resource` | Resources (employees or materials) |
| `hr.employee` | Employees (inherits resource) |

### Key Fields on `planning.slot`

| Field | Type | Description |
|-------|------|-------------|
| `resource_id` | Many2one | Assigned resource (empty = open shift) |
| `role_id` | Many2one | Role for this shift |
| `project_id` | Many2one | Linked project |
| `sale_line_id` | Many2one | Linked sales order item |
| `start_datetime` | Datetime | Shift start |
| `end_datetime` | Datetime | Shift end |
| `allocated_hours` | Float | Allocated time |
| `allocated_percentage` | Float | Percentage of working hours |
| `template_id` | Many2one | Shift template |
| `repeat` | Boolean | Is recurring |
| `repeat_interval` | Integer | Recurrence interval |
| `repeat_unit` | Selection | Recurrence unit |
| `state` | Selection | `draft`, `published` |
| `employee_id` | Many2one | Employee (if resource is human) |

### Schedule Visual Elements

| Element | Meaning |
|---------|---------|
| Full color | Planned and published |
| Diagonal stripes | Planned but unpublished |
| Grayed-out background | Employee on time off |
| Progress bar | Ongoing shift with linked timesheets |

### Configuration Settings

| Setting | Description |
|---------|-------------|
| Allow Unassignment | Let employees unassign from shifts (replaces switch) |
| Unassignment days limit | Max days before shift that unassignment is allowed |
| Recurring Shifts | Time frame for auto-creating recurring shifts (default: 6 months) |

### Menu Paths

- My Planning: `Planning > My Planning`
- Schedule by Resource: `Planning > Schedule by Resource`
- Schedule by Role: `Planning > Schedule by Role`
- Schedule by Project: `Planning > Schedule by Project`
- Schedule by Sales Order: `Planning > Schedule by Sales Order`
- Configuration: `Planning > Configuration > Roles / Employees / Materials / Shift Templates / Settings`

## API / RPC Patterns

<!-- TODO: Planning-specific external API examples not found in docs -->

Standard ORM access:

```python
# Search open shifts for a specific role
env['planning.slot'].search([('resource_id', '=', False), ('role_id', '=', role_id)])

# Create a shift
env['planning.slot'].create({
    'resource_id': resource_id,
    'role_id': role_id,
    'start_datetime': '2026-02-20 09:00:00',
    'end_datetime': '2026-02-20 17:00:00',
})
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- **Materials** concept allows scheduling non-human resources (equipment).
- **Property Fields** on roles allow custom data per shift (e.g., required accreditation, location).
- Split shifts tool (scissors icon) allows splitting long shifts into segments directly in the Gantt view.
- Switching shifts and unassignment are mutually exclusive features; enabling unassignment disables switching.

## Common Pitfalls

- **Auto Plan requires roles on employees**: Employees with no roles assigned cannot be auto-planned. The Auto Plan feature skips them entirely.
- **Flexible hours block Auto Plan**: Employees with blank **Working Hours** (flexible hours) cannot be auto-planned because Odoo cannot calculate their allocated time.
- **Switching vs. unassignment are mutually exclusive**: Enabling "Allow Unassignment" replaces the shift switching feature. You cannot have both active simultaneously.
- **Recurring shifts created in advance**: By default, recurring shifts are only planned 6 months ahead. Shifts beyond that window are created gradually. This can confuse teams planning far in advance.
- **Unpublished shifts are invisible to employees**: Employees only see shifts after they are published. Forgetting to publish causes scheduling gaps.
