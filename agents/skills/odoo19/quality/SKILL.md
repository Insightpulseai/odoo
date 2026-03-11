---
name: quality
description: Quality control and assurance for manufacturing processes and inventory operations via checks, control points, and alerts.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Quality — Odoo 19.0 Skill Reference

## Overview

Odoo Quality ensures product quality throughout manufacturing processes and inventory movements. It automates quality check creation via configurable control points, supports multiple check types (instructions, pass/fail, measure, picture, worksheet, spreadsheet), and provides quality alerts for issue tracking. Integrates tightly with Manufacturing (work order steps) and Inventory (receipt/delivery inspections). Used by quality engineers, QA inspectors, production supervisors, and quality managers.

## Key Concepts

- **Quality Control Point (QCP)**: A rule that automatically creates quality checks at predetermined intervals for specific products, operations, or work orders.
- **Quality Check**: An individual inspection task created by a QCP (or manually). Must be completed before proceeding with the associated operation.
- **Quality Alert**: A notification to a quality team about a product defect or issue. Can be created from MOs, inventory orders, Shop Floor, or directly in the Quality app.
- **Quality Team**: A group of users responsible for managing quality checks and alerts.
- **Failure Location**: Specifies where a quality failure was detected (used for root cause analysis).
- **Check Types**:
  - `Instructions` — Provide step-by-step instructions (same as a work order step in Manufacturing).
  - `Pass - Fail` — Binary pass/fail criterion.
  - `Measure` — Requires a measurement within a specified tolerance of a norm value.
  - `Take a Picture` — Requires a photo upload for visual inspection.
  - `Register Production` — Prompts confirmation of produced quantity.
  - `Worksheet` — Interactive worksheet to fill out.
  - `Spreadsheet` — Interactive spreadsheet to fill out.
- **Control Per**: Determines check granularity — `Operation` (one per operation), `Product` (one per unique product in the operation), or `Quantity` (percentage-based).
- **Control Frequency**: Determines how often checks are created — `All` (every time), `Randomly` (percentage of operations), or `Periodically` (time-based interval).

## Core Workflows

### 1. Configure a Quality Control Point

1. Navigate to `Quality > Quality Control > Control Points`, click `New`.
2. Enter a `Title` for the QCP.
3. Select one or more `Products` (or `Product Categories`) to scope the check. Leave blank for all products.
4. Select one or more `Operations` (e.g., Manufacturing, Receipts, Delivery Orders).
5. (Optional) If Manufacturing is selected, specify a `Work Order Operation` for check on a specific work order step.
6. Set `Control Per` (Operation / Product / Quantity) and `Control Frequency` (All / Randomly / Periodically).
7. Set the `Type` (Instructions, Pass - Fail, Measure, Take a Picture, etc.).
8. Assign a `Team` and optionally a `Responsible` user.
9. Add instructions in the `Instructions` tab. Add failure instructions in `Message If Failure` tab.

### 2. Process a Quality Check

1. When an operation triggers a QCP, a quality check is auto-created.
2. On the operation (e.g., receipt, MO, work order), a quality check indicator appears.
3. Click the quality check to open it. Follow instructions based on the check type:
   - **Pass - Fail**: Click `Pass` or `Fail`.
   - **Measure**: Enter the measured value. Odoo compares against norm/tolerance and auto-determines pass/fail.
   - **Take a Picture**: Upload a photo.
   - **Instructions**: Read and confirm completion.
4. If the check fails, follow the failure instructions and optionally create a quality alert.

### 3. Create and Manage a Quality Alert

1. Navigate to `Quality > Quality Control > Quality Alerts`, click `New`.
2. Enter a `Title` summarizing the issue.
3. Select `Product`, `Work Center`, or `Picking` as applicable.
4. Assign a `Team` and `Responsible`.
5. Set `Root Cause` and `Priority`.
6. Fill in `Description`, `Corrective Actions`, and `Preventive Actions` tabs.
7. Alerts are displayed on a Kanban board. Drag to move between stages (New, In Progress, Done).

### 4. Add Quality Steps to Manufacturing Operations

1. Open a BoM, go to the `Operations` tab.
2. Click the list icon in the `Instructions` column of an operation.
3. On the `Steps` page, click `New` to create a quality control point.
4. Set `Type` to `Instructions` (or other check type) and add details.
5. Reorder steps by dragging. Steps appear as work order steps in Shop Floor.

## Technical Reference

### Key Models

| Model | Description |
|-------|-------------|
| `quality.point` | Quality Control Point |
| `quality.check` | Individual quality check instance |
| `quality.alert` | Quality alert |
| `quality.alert.team` | Quality team |
| `quality.alert.stage` | Quality alert Kanban stage |

### Key Fields

- `quality.point.title`: QCP title
- `quality.point.product_ids`: Products scope (Many2many)
- `quality.point.product_category_ids`: Product category scope
- `quality.point.picking_type_ids`: Operation types that trigger checks
- `quality.point.test_type_id`: Check type (Instructions, Pass-Fail, Measure, etc.)
- `quality.point.measure_frequency_type`: `'all'`, `'random'`, `'periodical'`
- `quality.point.measure_on`: `'operation'`, `'product'`, `'move_line'` (quantity)
- `quality.point.team_id`: Assigned quality team
- `quality.point.note`: Instructions text
- `quality.point.failure_message`: Message shown on failure
- `quality.check.quality_state`: `'none'`, `'pass'`, `'fail'`
- `quality.check.point_id`: Link to QCP
- `quality.alert.stage_id`: Kanban stage
- `quality.alert.priority`: `'0'`, `'1'`, `'2'`, `'3'`
- `quality.alert.reason_id`: Root cause

### Important XML IDs

- `quality.quality_point_action` — Quality Control Points action
- `quality.quality_alert_action_team` — Quality Alerts action

## API / RPC Patterns

<!-- TODO: not found in docs — Odoo 19 quality docs do not cover JSON-RPC or XML-RPC examples directly. -->

## Version Notes (19.0)

- **Instructions check type = work order step**: An `Instructions` QCP assigned to a manufacturing operation is stored as a work order step and displayed in Shop Floor.
- **Worksheet and Spreadsheet check types**: Quality checks can now use interactive worksheet or spreadsheet templates.

<!-- TODO: specific breaking changes between 18.0 and 19.0 not documented in quality RST source -->

## Common Pitfalls

- **QCP with no products/categories applies to all products**: Leaving `Products` and `Product Categories` blank creates checks for every instance of the specified operation, which may generate excessive checks.
- **Instructions checks overlap with work order steps**: An `Instructions` QCP for manufacturing is essentially a work order step. Creating both a manual step and a QCP for the same operation can cause duplicate steps.
- **Worksheet/Spreadsheet templates must be pre-created**: QCPs with Worksheet or Spreadsheet types require selecting a template from `Quality > Configuration > Quality Worksheet/Spreadsheet Templates`. Without a template, the check cannot be processed.
- **Quality checks block operation validation**: If a quality check is required for an operation, the operation cannot be validated until the check is completed. This can cause bottlenecks if quality teams are unaware of pending checks.
- **Quality app required for BoM operation instructions**: The detailed `Instructions` feature (adding step-by-step instructions to BoM operations) requires the Quality app to be installed.
