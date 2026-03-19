# Finance PPM Go-Live Checklist

## Overview

Production go-live checklist for Finance PPM modules

- **Technical Name:** `ipai_finance_ppm_golive`
- **Version:** 18.0.1.0.0
- **Category:** Finance
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Finance PPM Go-Live Checklist Module
====================================

Complete production readiness checklist for Finance PPM system with:
- 9 section groups (Data, Module, AFC, STC, Control Room, Notion, Audit, Operational, Go-Live)
- 60+ granular checklist items
- Approval workflow (Finance Supervisor → Senior Supervisor Finance → Director)
- Dashboard with completion % tracking
- PDF export for Director sign-off
- Integration with Finance PPM modules

Author: Jake Tolentino (InsightPulse...

## Functional Scope

### Data Models

- **ipai.finance.ppm.golive.checklist** (Model)
  - Finance PPM Go-Live Checklist
  - Fields: 20 defined
- **ipai.finance.ppm.golive.item** (Model)
  - Go-Live Checklist Item
  - Fields: 10 defined
- **ipai.finance.ppm.golive.section** (Model)
  - Go-Live Checklist Section
  - Fields: 8 defined

### Views

- Tree: 5
- Form: 1
- Kanban: 1

### Menus

- `menu_golive_root`: Go-Live Checklist
- `menu_golive_dashboard`: Dashboard
- `menu_golive_checklists`: Checklists
- `menu_golive_config`: Configuration
- `menu_golive_sections`: Sections
- ... and 1 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_finance_ppm_golive --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_finance_ppm_golive --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*6 access rules defined in ir.model.access.csv*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_ppm_golive'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_finance_ppm_golive")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/checklist_sections.xml`
- `data/checklist_items.xml`
- `views/golive_checklist_views.xml`
- `views/golive_section_views.xml`
- `views/golive_item_views.xml`
- `views/golive_dashboard_views.xml`
- `views/menus.xml`
- `reports/golive_cfo_signoff.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
