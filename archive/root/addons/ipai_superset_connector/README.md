# IPAI Superset Connector

## Overview

Apache Superset integration with managed dataset sync

- **Technical Name:** `ipai_superset_connector`
- **Version:** 18.0.1.0.0
- **Category:** Reporting/BI
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

IPAI Superset Connector
=======================

Enterprise-grade Apache Superset integration for Odoo 18 CE.
Replaces Power BI Connector ($400) with zero licensing cost.

Architecture
------------
This module uses a **Direct PostgreSQL + Managed Views** approach:

1. **Read Replica Connection** (Recommended)
   - Superset connects directly to Odoo's PostgreSQL read replica
   - Zero ETL latency, real-time dashboards
   - Requires PostgreSQL streaming replication setup

2. **Managed SQL Views**
...

## Functional Scope

### Data Models

- **superset.connection** (Model)
  - Superset Connection
  - Fields: 25 defined
- **superset.analytics.view** (Model)
  - Pre-built Analytics View
  - Fields: 10 defined
- **res.config.settings** (TransientModel)
  - Fields: 5 defined
- **superset.dataset** (Model)
  - Superset Dataset
  - Fields: 23 defined
- **superset.dataset.column** (Model)
  - Superset Dataset Column
  - Fields: 11 defined
- **superset.dataset.wizard** (TransientModel)
  - Create Superset Dataset
  - Fields: 10 defined
- **superset.bulk.dataset.wizard** (TransientModel)
  - Bulk Create Superset Datasets
  - Fields: 3 defined

### Views

- Form: 3
- : 1
- Tree: 4
- Search: 1

### Menus

- `menu_superset_create_dataset`: Create Dataset
- `menu_superset_bulk_create`: Bulk Create
- `menu_superset_datasets`: Datasets
- `menu_superset_analytics_views`: Analytics Views
- `menu_superset_root`: Superset
- ... and 1 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `sale` (CE Core)
- `account` (CE Core)
- `stock` (CE Core)
- `hr` (CE Core)
- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_superset_connector --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_superset_connector --stop-after-init
```

## Configuration

### System Parameters

- `ipai_superset_connector.auto_sync`: False
- `ipai_superset_connector.sync_interval`: daily
- `ipai_superset_connector.enable_rls`: True

### Scheduled Actions

- **Superset: Sync Datasets** (Inactive)

## Security

### Security Groups

- `group_superset_user`: Superset User
- `group_superset_manager`: Superset Manager
- `group_superset_admin`: Superset Administrator

### Access Rules

*13 access rules defined in ir.model.access.csv*

## Integrations

- Apache Superset (BI/Analytics)
- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_superset_connector'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_superset_connector")]).state)'
```

## Data Files

- `security/superset_security.xml`
- `security/ir.model.access.csv`
- `data/superset_config.xml`
- `data/analytics_views.xml`
- `views/superset_dataset_views.xml`
- `views/superset_connection_views.xml`
- `views/res_config_settings_views.xml`
- `wizards/dataset_wizard_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
