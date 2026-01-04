# IPAI Superset Connector

## 1. Overview
Apache Superset integration with managed dataset sync

**Technical Name**: `ipai_superset_connector`
**Category**: Reporting/BI
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

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
   - Creates optimized SQL views for common analytics needs
   - Flattens Odoo's relational model for BI consumption
   - Handles multi-company security via RLS

3. **Dataset Registry**
   - Tracks which Odoo models are exposed to Superset
   - Generates Superset dataset definitions via API
   - Manages column metadata and relationships

Features
--------
* Direct PostgreSQL connection (no middleware)
* Pre-built analytics views for Sales, Finance, HR, Inventory
* Row-Level Security (RLS) based on Odoo's ir.rule
* Automated dataset refresh via Superset API
* Multi-tenant support (company_id filtering)
* BIR compliance views for Philippine tax reporting

Power BI Parity
---------------
✓ Real-time data sync (via read replica)
✓ Scheduled refresh (via Superset cron)
✓ Multiple workspaces (via Superset schemas)
✓ Table relationships (via SQL views)
✓ Authentication (via PostgreSQL + RLS)
✓ Custom metrics (via Superset metrics)

NOT Implemented (by design):
✗ KQL/Kusto queries (use SQL instead)
✗ Microsoft Fabric (use Superset + PostgreSQL)
✗ Eventhouse (use materialized views)

Architecture: Smart Delta
-------------------------
This module follows ipai_* patterns:
- Extends core models via _inherit
- No monkey-patching or forks
- OCA-compatible, AGPL-3 licensed
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `sale`
- `account`
- `stock`
- `hr`
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `tableself.view_name if self.source_type in (model, view) else self.technical_name`
- `viewfields.Char(`
- `rec.viewFalse`
- `superset.dataset`
- `db_connectionfields.Char(`
- `tablemodel._table`
- `technicalfields.Char(`
- `superset.dataset.column`
- `modelfields.Char(`
- `cleanre.sub(r[^a-z0-9_], _, rec.technical_name.lower())`
- `rec.viewfsuperset_{clean_name}`
- `fieldfield.name`
- `superset.connection`
- `superset.analytics.view`
- `self.technicalself.model_id.model.replace(., _)`
- `technicalfields.Char(string=Technical Name, required=True)`

## 6. User Interface
- **Views**: 7 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_superset_connector --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_superset_connector --stop-after-init
```