{
    "name": "IPAI Superset Connector",
    "version": "18.0.1.0.0",
    "category": "Reporting/BI",
    "summary": "Apache Superset integration with managed dataset sync",
    "description": """
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
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "sale",
        "account",
        "stock",
        "hr",
        "project",
    ],
    "data": [
        "security/superset_security.xml",
        "security/ir.model.access.csv",
        "data/superset_config.xml",
        "data/analytics_views.xml",
        "views/superset_dataset_views.xml",
        "views/superset_connection_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/dataset_wizard_views.xml",
    ],
    "external_dependencies": {
        "python": ["requests", "psycopg2"],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
