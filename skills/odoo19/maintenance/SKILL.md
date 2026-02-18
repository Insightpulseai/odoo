---
name: maintenance
description: Equipment and work center maintenance scheduling, tracking, and preventive/corrective maintenance requests.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Maintenance — Odoo 19.0 Skill Reference

## Overview

Odoo Maintenance helps companies schedule and track corrective and preventive maintenance on warehouse equipment and work centers. It tracks maintenance teams, individual equipment with failure metrics (MTBF, MTTR), maintenance requests through Kanban stages, and provides a calendar view for scheduling. Integrates with Manufacturing for work center equipment tracking. Used by maintenance managers, technicians, equipment operators, and warehouse supervisors.

## Key Concepts

- **Equipment**: Any machine, tool, or device used in operations (production lines, computers, power tools). Registered with metadata: category, vendor, serial number, warranty, work center assignment.
- **Equipment Category**: Groups equipment by type (e.g., Computers, Machinery, Tools). Has a responsible user and optional email alias.
- **Maintenance Team**: A group of users (technicians) responsible for handling maintenance requests.
- **Technician**: An individual team member responsible for servicing specific equipment or requests.
- **Maintenance Request**: A task to perform corrective or preventive maintenance on equipment or a work center. Tracked through Kanban stages: New Request, In Progress, Repaired, Scrap.
- **Maintenance Type**: `Corrective` (fix an existing issue) or `Preventive` (prevent future issues).
- **MTBF (Mean Time Between Failure)**: Average days between equipment failures. Auto-calculated from completed corrective maintenance.
- **MTTR (Mean Time To Repair)**: Average days to repair equipment. Auto-calculated from maintenance request duration.
- **Expected MTBF**: Manually configurable expected days between failures. Used to estimate next failure date.
- **Estimated Next Failure**: Auto-calculated as Latest Failure Date + MTBF.
- **Effective Date**: Date equipment was first put in use; basis for MTBF calculations.
- **Work Center (Maintenance context)**: Equipment can be assigned to manufacturing work centers, linking maintenance tracking to production capacity.
- **Block Workcenter**: Option on maintenance requests for work centers that prevents scheduling work orders during maintenance.
- **Maintenance Calendar**: Calendar view of scheduled and ongoing maintenance requests, filterable by technician.
- **Custom Maintenance Worksheets**: Optional templates for maintenance instructions (PDF, Google Slides, or text).

## Core Workflows

### 1. Add New Equipment

1. Navigate to `Maintenance > Equipment > Machines & Tools`, click `New`.
2. Enter `Equipment Name` and select `Equipment Category`.
3. Set `Used By` (Department, Employee, or Other).
4. Assign `Maintenance Team` and `Technician`.
5. (Optional) Set `Work Center` if the equipment is used in manufacturing.
6. Fill in the `Product Information` tab: Vendor, Model, Serial Number, Effective Date, Cost, Warranty Expiration Date.
7. In the `Maintenance` tab, set `Expected Mean Time Between Failure`.
8. Click `Save`.

### 2. Create a Maintenance Request

1. Go to `Maintenance > Maintenance > Maintenance Requests`, click `New`.
2. Enter a descriptive `Request` title.
3. Select `For`: Equipment or Work Center. Then select the specific item.
4. Set `Maintenance Type`: Corrective or Preventive.
5. (Optional) Link to a `Manufacturing Order` and `Work Order` if the issue arose during production.
6. Assign `Team` and `Responsible` technician.
7. Set `Scheduled Date`, `Duration`, and `Priority`.
8. Add details in `Notes` tab and instructions in `Instructions` tab.
9. Click `Save`. The request appears in the `New Request` Kanban stage.

### 3. Process a Maintenance Request

1. Open the maintenance request from `Maintenance > Maintenance > Maintenance Requests`.
2. Drag the request card to `In Progress` when work begins (or click the stage in the form).
3. Perform the maintenance work.
4. If successful, move to `Repaired` stage.
5. If the equipment cannot be repaired, move to `Scrap` stage.

### 4. Set Up Equipment Categories and Teams

1. Go to `Maintenance > Configuration > Equipment Categories`, click `New`.
2. Enter `Category Name`, assign `Responsible` user, optionally set `Email Alias`.
3. Go to `Maintenance > Configuration > Maintenance Teams`, click `New`.
4. Enter `Team Name`, assign `Team Members`.

### 5. Schedule Preventive Maintenance

1. Create a maintenance request with `Maintenance Type` = `Preventive`.
2. Set the `Scheduled Date` for when maintenance should occur.
3. The request appears on the `Maintenance Calendar` (`Maintenance > Maintenance > Maintenance Calendar`).
4. Technicians can view their scheduled tasks in the calendar, filtered by technician in the sidebar.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `maintenance.equipment` | Equipment record |
| `maintenance.equipment.category` | Equipment category |
| `maintenance.request` | Maintenance request |
| `maintenance.team` | Maintenance team |
| `maintenance.stage` | Kanban stage for maintenance requests |
| `mrp.workcenter` | Work center (shared with Manufacturing) |

### Key Fields

- `maintenance.equipment.name`: Equipment name
- `maintenance.equipment.category_id`: Equipment category
- `maintenance.equipment.employee_id`: Assigned employee
- `maintenance.equipment.department_id`: Assigned department
- `maintenance.equipment.maintenance_team_id`: Responsible team
- `maintenance.equipment.technician_user_id`: Responsible technician
- `maintenance.equipment.workcenter_id`: Linked work center
- `maintenance.equipment.effective_date`: Date first put in use
- `maintenance.equipment.cost`: Acquisition cost
- `maintenance.equipment.warranty_date`: Warranty expiration
- `maintenance.equipment.mtbf`: Mean Time Between Failure (auto-calculated, days)
- `maintenance.equipment.mttr`: Mean Time To Repair (auto-calculated, days)
- `maintenance.equipment.expected_mtbf`: Expected MTBF (manually set, days)
- `maintenance.equipment.estimated_next_failure`: Estimated next failure date
- `maintenance.equipment.latest_failure_date`: Date of most recent failure
- `maintenance.request.name`: Request title
- `maintenance.request.request_date`: Date request was created
- `maintenance.request.schedule_date`: Scheduled maintenance date
- `maintenance.request.maintenance_type`: `'corrective'` or `'preventive'`
- `maintenance.request.stage_id`: Current Kanban stage
- `maintenance.request.equipment_id`: Linked equipment
- `maintenance.request.workcenter_id`: Linked work center
- `maintenance.request.maintenance_team_id`: Assigned team
- `maintenance.request.user_id`: Responsible user
- `maintenance.request.duration`: Expected duration
- `maintenance.request.priority`: `'0'`, `'1'`, `'2'`, `'3'`

### Important XML IDs

- `maintenance.hr_equipment_action` — Equipment list action
- `maintenance.hr_equipment_request_action` — Maintenance Requests action
- `maintenance.equipment_stage_0` — "New Request" stage
- `maintenance.equipment_stage_1` — "In Progress" stage
- `maintenance.equipment_stage_3` — "Repaired" stage
- `maintenance.equipment_stage_4` — "Scrap" stage

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 maintenance docs do not cover JSON-RPC or XML-RPC examples directly. -->

## Version Notes (19.0)

- **Custom Maintenance Worksheets**: Optional setting for attaching worksheet templates (PDF, Google Slides, or text) to maintenance requests.
- **Block Workcenter option**: Maintenance requests for work centers can block scheduling during maintenance.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in maintenance RST source -->

## Common Pitfalls

- **MTBF/MTTR are auto-calculated and not editable**: Only `Expected MTBF` can be manually set. The actual `MTBF` and `MTTR` values update automatically based on completed maintenance requests.
- **Equipment access requires follower or manager rights**: Non-manager users can only create maintenance requests for equipment they follow. Add users as followers on the equipment record, or grant `Equipment Manager` access rights.
- **Effective Date must be set for accurate MTBF**: The `Effective Date` field on equipment determines the time basis for MTBF calculations. If not set, metrics may be inaccurate.
- **Scrap stage means equipment cannot be repaired**: Moving a request to `Scrap` indicates the equipment must be replaced, not that it is pending further review. Use `In Progress` for ongoing work.
- **Work center link is optional but valuable**: Assigning equipment to a work center enables viewing equipment health alongside manufacturing capacity in `Maintenance > Equipment > Work Centers`.
