# IPAI CRM - Pipeline Clone

## Overview

Salesforce-like CRM pipeline experience

- **Technical Name:** `ipai_crm_pipeline`
- **Version:** 18.0.1.0.0
- **Category:** Sales/CRM
- **License:** LGPL-3
- **Author:** IPAI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI CRM Pipeline Clone
=======================

Delivers a Salesforce-like CRM pipeline experience on Odoo CRM.

Capability ID: crm.pipeline.board (P0)

Features:
- Enhanced kanban board with stage rules
- Quick action buttons (log call, schedule meeting, send email)
- Activity timeline improvements
- Stage validation rules
- Role-based dashboards

This module targets feature parity with Salesforce Sales Cloud
pipeline functionality while leveraging the IPAI design system.

## Functional Scope

### Data Models

- **crm.stage** (Model)
  - Fields: 6 defined
- **crm.lead** (Model)
  - Fields: 6 defined

### Views

- : 3

### Menus

- `ipai_crm_pipeline_menu`: IPAI Pipeline
- `ipai_crm_stage_config_menu`: Stage Rules

## Installation & Dependencies

### Dependencies

- `crm` (CE Core)
- `mail` (CE Core)
- `ipai_platform_workflow` (IPAI)
- `ipai_platform_theme` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_crm_pipeline --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_crm_pipeline --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

*No specific security configuration.*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_crm_pipeline'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_crm_pipeline")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/crm_lead_views.xml`
- `views/crm_stage_views.xml`
- `data/crm_stage_rules.xml`

## Static Validation Status

- Passed: 4
- Warnings: 1
- Failed: 0
