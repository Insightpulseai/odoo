# IPAI Equipment Management

**Version**: 18.0.1.0.0
**Category**: Inventory
**License**: AGPL-3
**Author**: InsightPulseAI

Cheqroom-style equipment catalog, bookings, and incident tracking for Odoo CE 18.0 + OCA.

---

## Overview

The **IPAI Equipment Management** module provides a comprehensive system for managing physical assets, equipment bookings, and incident reporting. It enables organizations to track equipment availability, manage reservations, and monitor equipment condition throughout its lifecycle.

## Features

### Core Capabilities

- **Equipment Catalog**: Maintain a complete inventory of equipment assets
- **Booking Management**: Reserve and check out equipment with conflict detection
- **Incident Tracking**: Report and track equipment issues and damage
- **Smart Buttons**: Quick navigation between assets, bookings, and incidents
- **Condition Tracking**: Monitor equipment condition (New, Good, Used, Damaged)
- **Status Management**: Track availability (Available, Reserved, Checked Out, Maintenance)

### Equipment Asset Management

| Field | Description |
|-------|-------------|
| Name | Asset identifier |
| Product | Linked product from inventory |
| Category | Product category classification |
| Serial Number | Unique equipment identifier |
| Storage Location | Where equipment is stored |
| Condition | Physical condition status |
| Status | Availability status |
| Image | Equipment photo |

### Booking Workflow

```
Draft → Reserved → Checked Out → Returned
           ↓           ↓
       Cancelled    Cancelled
```

- **Conflict Detection**: Prevents double-booking of equipment
- **Overdue Tracking**: Automatic flagging of overdue checkouts
- **Project Linkage**: Associate bookings with projects/jobs

### Incident Management

- **Severity Levels**: Low, Medium, High
- **Status Tracking**: Open → In Progress → Resolved
- **Booking Linkage**: Link incidents to specific bookings

---

## Installation

### Prerequisites

This module depends on:
- `stock` (Odoo Inventory)
- `maintenance` (Odoo Maintenance)
- `project` (Odoo Project)

### Install

1. Place the module in your Odoo addons directory
2. Update the apps list: `Settings → Apps → Update Apps List`
3. Search for "IPAI Equipment Management"
4. Click **Install**

---

## Usage

### Managing Equipment

1. Navigate to: **Inventory → Equipment → Assets**
2. Click **Create** to add new equipment
3. Fill in equipment details:
   - Name and serial number
   - Link to product catalog (optional)
   - Set initial condition and status
   - Upload equipment image
4. Use smart buttons to view related bookings and incidents

### Creating Bookings

1. Navigate to: **Inventory → Equipment → Bookings**
2. Click **Create**
3. Select the equipment asset
4. Set borrower and project (optional)
5. Define start and end datetime
6. Click **Reserve** to confirm booking

### Booking Actions

| Action | Description |
|--------|-------------|
| Reserve | Confirm booking, mark asset as reserved |
| Check Out | Equipment handed to borrower |
| Return | Equipment returned, mark asset as available |
| Cancel | Cancel booking, release asset |

### Reporting Incidents

1. Navigate to: **Inventory → Equipment → Incidents**
2. Click **Create**
3. Select the affected asset
4. Link to booking (if applicable)
5. Set severity level and description
6. Track resolution progress

---

## Data Model

### Equipment Asset (`ipai.equipment.asset`)

```python
Fields:
- name: Equipment name (required)
- product_id: Linked product
- category_id: Product category
- serial_number: Unique identifier
- location_id: Storage location
- condition: new / good / used / damaged
- status: available / reserved / checked_out / maintenance
- image_1920: Equipment image
- company_id: Multi-company support
- booking_count: Computed booking count
- incident_count: Computed incident count
```

### Equipment Booking (`ipai.equipment.booking`)

```python
Fields:
- name: Reference (auto-generated sequence)
- asset_id: Equipment being booked
- borrower_id: User checking out equipment
- project_id: Associated project
- start_datetime: Booking start
- end_datetime: Booking end
- state: draft / reserved / checked_out / returned / cancelled
- is_overdue: Computed overdue flag
```

### Equipment Incident (`ipai.equipment.incident`)

```python
Fields:
- name: Incident title
- booking_id: Related booking
- asset_id: Affected equipment
- reported_by: User reporting incident
- severity: low / medium / high
- description: Incident details
- status: open / in_progress / resolved
```

---

## Security

Access control is managed through `security/ir.model.access.csv`:

| Group | Assets | Bookings | Incidents |
|-------|--------|----------|-----------|
| User | Read | Read/Create | Read/Create |
| Manager | Full CRUD | Full CRUD | Full CRUD |

---

## Technical Details

### File Structure

```
ipai_equipment/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── equipment.py
├── views/
│   ├── ipai_equipment_menus.xml
│   └── ipai_equipment_views.xml
└── security/
    └── ir.model.access.csv
```

### Dependencies

- Python: Standard library only
- Odoo modules: `stock`, `maintenance`, `project`

---

## Support

- **Author**: InsightPulseAI
- **Website**: https://insightpulseai.net
- **License**: AGPL-3

---

## Changelog

### Version 18.0.1.0.0

- Initial release
- Equipment asset management
- Booking workflow with conflict detection
- Incident tracking system
- Smart button navigation
- Overdue booking detection
