---
name: field_service
description: On-site intervention management with task scheduling, worksheets, product tracking, and map-based itinerary planning
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# field_service -- Odoo 19.0 Skill Reference

## Overview

Odoo Field Service manages on-site interventions and field tasks. Technicians can be dispatched to customer locations, record products used on-site, fill in worksheets (configurable reports), plan itineraries on a map, and invoice for time and materials. Field Service integrates with Project (task management), Timesheets (time tracking), Sales (invoicing), Inventory (product consumption), Helpdesk (ticket-to-task escalation), and Planning (resource scheduling). Used by field technicians, dispatchers, and service managers.

## Key Concepts

- **Field Service Task**: A project task representing an on-site intervention, with a customer address, planned date, and assigned technician.
- **Worksheet**: A configurable report template (built with Studio) that technicians fill in on-site to document work performed. Signed by the customer upon completion.
- **Worksheet Template**: A reusable template for worksheets, assigned per project or per task.
- **Product Catalog**: An interface for field workers to record products used during an intervention, which are then added to the invoice.
- **Default Warehouse**: A per-user warehouse setting that determines which stock location products are pulled from during field service tasks.
- **Map/Itinerary**: A map view showing all task locations for the day, with optional route planning via MapBox integration.
- **Time and Material Invoicing**: Billing customers for both time spent (via timesheets) and products used during the intervention.

## Core Workflows

### 1. Create a Field Service Task

**Manually:**
1. Navigate to **Field Service > All Tasks > All Tasks**, click **New**.
2. Enter the task title, **Customer** (must have a valid address for map), and optional fields (assignee, planned date, allocated hours).
3. Save.

**From a Sales Order:**
1. Create a SO with a service product configured with **Create on Order** = **Task** (in a Field Service project).
2. Confirm the SO. A Field Service task is auto-created.
3. Access via the **Tasks** smart button on the SO.

**From a Helpdesk Ticket:**
1. On a ticket with **Field Service** enabled, click **Plan Intervention**.
2. Set the task title, project, and optional worksheet template.
3. Click **Create Task** or **Create & View Task**.

### 2. Configure and Use Worksheets

1. Enable worksheets: **Field Service > Configuration > Settings > Worksheets** (this installs Studio).
2. Create templates: **Field Service > Configuration > Worksheet Templates**, click **New**.
3. Name the template, save, then click **Design Template** to open Studio.
4. Drag and drop fields (text, checkboxes, images, etc.) to build the worksheet.
5. Close Studio when complete.
6. Set a default template on the Field Service project: open the project, **Settings** tab > **Field Service** section > **Worksheet Template**.
7. On a task, the **Worksheet** smart button opens the worksheet for completion on-site.
8. Fields marked as **Required** must be filled before saving.

### 3. Record Products Used On-Site

1. Enable: **Field Service > Configuration > Settings > Time and Material Invoicing**.
2. On a field service task, click the **Products** smart button.
3. Click **Add** on product cards to add them. Adjust quantities with **+** and **-** buttons.
4. Products and their prices appear on the task's smart button.
5. Products are added to the linked sales order and reflected in the invoice.

### 4. Plan Itinerary with Map

1. Configure MapBox: obtain a token from mapbox.com, paste in **Settings > Integrations > Map Routes > Token**.
2. Navigate to **Field Service > My Tasks > Map**.
3. Tasks are sorted by **Planned Date** and displayed as pins on the map.
4. Click **View in Google Maps** to open the itinerary (includes current location as starting point).
5. Click individual pins or tasks in the left column for details; use **Navigate to** for directions.

### 5. Invoice Time and Materials

1. Ensure the task is linked to a Sales Order (automatically if created from SO or with **Time and Material Invoicing** enabled).
2. Log time via the **Timesheets** tab on the task.
3. Record products via the **Products** smart button.
4. Mark the task as Done.
5. On the linked SO, the **Delivered** quantities update for both time and products.
6. Click **Create Invoice** on the SO to bill the customer.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `project.task` | Field service tasks (same model as Project tasks, filtered by project type) |
| `project.project` | Field service project |
| `worksheet.template` | Worksheet template definitions |
| `sale.order` | Linked sales orders for invoicing |
| `sale.order.line` | SO lines for time and products |
| `product.product` | Products used during interventions |

### Key Fields on Field Service Tasks

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | Many2one | Field Service project |
| `partner_id` | Many2one | Customer (address used for map) |
| `user_ids` | Many2many | Assigned technicians |
| `date_deadline` | Date | Planned date |
| `worksheet_template_id` | Many2one | Worksheet template |
| `sale_order_id` | Many2one | Linked sales order |
| `timesheet_ids` | One2many | Time entries |
| `worksheet_count` | Integer | Number of worksheets completed |

### Configuration Settings

| Setting | Description |
|---------|-------------|
| Worksheets | Enable worksheet feature (installs Studio) |
| Time and Material Invoicing | Enable product catalog and time billing |
| Map Routes (in Settings app) | MapBox token for itinerary planning |

### User Default Warehouse

- Set per-user at: **Settings > Users > Manage users > [User] > Preferences > Inventory > Default Warehouse**.
- Or self-service: **Profile icon > My Profile > Preferences > Default Warehouse**.
- Products in field service SOs are pulled from this warehouse. Stock updates automatically when task is marked done.

### Menu Paths

- All Tasks: `Field Service > All Tasks > All Tasks`
- My Tasks: `Field Service > My Tasks`
- Map: `Field Service > My Tasks > Map`
- Products: `Field Service > Configuration > Products`
- Worksheet Templates: `Field Service > Configuration > Worksheet Templates`
- Settings: `Field Service > Configuration > Settings`

## API / RPC Patterns

<!-- TODO: Field Service-specific external API examples not found in docs -->

Standard ORM access:

```python
# Search field service tasks for today
from datetime import date
env['project.task'].search([
    ('project_id.is_fsm', '=', True),
    ('date_deadline', '=', date.today()),
])

# Create a field service task
env['project.task'].create({
    'name': 'HVAC Maintenance',
    'project_id': fsm_project_id,
    'partner_id': customer_id,
    'user_ids': [(6, 0, [technician_id])],
    'date_deadline': '2026-02-20',
})
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Worksheets require Studio, which is auto-installed when the Worksheets feature is enabled. This impacts pricing plans.
- The product catalog is a visual interface (not just order lines) for adding products on mobile devices during field work.
- MapBox integration is optional; without it, the map shows a static pin display without routing.
- Field Service tasks use the same `project.task` model as regular Project tasks, differentiated by the project's `is_fsm` flag.

## Common Pitfalls

- **Worksheet feature installs Studio**: Enabling Worksheets automatically installs Studio, which may change the pricing plan. Confirm cost implications before enabling.
- **Customer address required for map**: Tasks without a valid customer address do not appear on the map view. Ensure addresses are complete with street, city, and country.
- **Default warehouse not set**: If no default warehouse is configured for a field technician, products are pulled from the main warehouse, which may not reflect actual field inventory.
- **MapBox token required for routing**: Without a valid MapBox token, the map only shows static pins. Route/itinerary planning requires the token to be configured in Settings.
- **Products must be created in Field Service config**: Products used during field service need to be accessible from **Field Service > Configuration > Products**. Products not flagged appropriately will not appear in the product catalog.
