# IPAI Superset Connector

**Odoo 18 CE ↔ Apache Superset Integration**  
Replaces Power BI Connector ($400) with zero licensing cost.

## Architecture Improvements over Original Spec

The original spec proposed a custom SQLAlchemy dialect to query Odoo directly. This is fundamentally flawed because **Odoo doesn't speak SQL** - it uses JSON-RPC/XML-RPC.

### What We Built Instead

| Approach | Original Spec | This Implementation |
|----------|--------------|---------------------|
| Data Access | Custom SQLAlchemy shim (fragile) | Direct PostgreSQL + SQL Views |
| Latency | High (API translation) | Low (native SQL) |
| Complexity | Very High | Medium |
| Reliability | Poor | Excellent |
| Superset Features | Limited | Full |

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  Apache         │────▶│  PostgreSQL      │◀────│  Odoo 18 CE     │
│  Superset       │ SQL │  (Read Replica)  │ ORM │                 │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               ▲
                               │
                        ┌──────┴──────┐
                        │   SQL Views  │
                        │   (Managed)  │
                        └─────────────┘
```

**Key Design Decisions:**

1. **Direct PostgreSQL Connection** - Superset connects to Odoo's PostgreSQL database directly
2. **Managed SQL Views** - Module creates optimized views that flatten Odoo's relational model
3. **No Middleware** - Zero ETL latency, real-time dashboards
4. **Row-Level Security** - Multi-tenant filtering via `company_id`

## Features

### Power BI Parity Matrix

| Feature | Power BI Connector | This Module | Notes |
|---------|-------------------|-------------|-------|
| Real-time Sync | ✓ via API | ✓ via SQL | Faster |
| Scheduled Refresh | ✓ | ✓ | Superset cron |
| Multiple Workspaces | ✓ | ✓ | Schemas |
| Table Relationships | ✓ | ✓ | SQL JOINs |
| Authentication | MSAL | PostgreSQL + RLS | Simpler |
| Custom Metrics | ✓ | ✓ | Superset metrics |
| **Cost** | **$400** | **$0** | Zero license |

### Pre-built Analytics Views

| View | Category | Description |
|------|----------|-------------|
| `superset_sales_order_analysis` | Sales | Orders with customer dimensions |
| `superset_account_move_analysis` | Finance | Journal entries with GL dimensions |
| `superset_trial_balance` | Finance | Account balances by period |
| `superset_bir_vat_analysis` | BIR | VAT I/O for 2550Q filing |
| `superset_stock_valuation` | Inventory | Stock levels with valuation |
| `superset_project_task_analysis` | Project | Tasks with status metrics |
| `superset_employee_analysis` | HR | Employee demographics |

## Installation

### Prerequisites

1. **Apache Superset** - Running instance
2. **PostgreSQL Read Replica** (recommended) - Or direct access to Odoo's database
3. **Odoo 18 CE** - With this module installed

### Install Module

```bash
# Copy to addons folder
cp -r ipai_superset_connector /mnt/extra-addons/

# Update and install
docker exec -it odoo-web odoo -d your_db -i ipai_superset_connector --stop-after-init
```

### Configure Connection

1. Go to **Superset → Connections → Create**
2. Enter Superset URL and credentials
3. Enter PostgreSQL connection details (Odoo's database)
4. Click **Test Connection**
5. Click **Create Database in Superset**

### Create Datasets

**Option A: Single Dataset**
1. Go to **Superset → Create Dataset**
2. Select an Odoo model
3. Choose fields to include
4. Click **Create Dataset**

**Option B: Bulk Create**
1. Go to **Superset → Bulk Create**
2. Select a preset (Sales, Finance, etc.)
3. Click **Create Datasets**

### Create Analytics Views

1. Go to **Settings → Superset**
2. Click **Create All Analytics Views**
3. Views are now available in Superset

## API Reference

### Superset Connection Model

```python
from odoo import api, models

# Get connection
conn = self.env['superset.connection'].browse(1)

# Test connection
conn.action_test_connection()

# Create database in Superset
conn.action_create_database_connection()

# Sync all datasets
conn.action_sync_all_datasets()

# API calls
result = conn._api_call('GET', '/api/v1/database/')
```

### Superset Dataset Model

```python
# Create dataset
dataset = self.env['superset.dataset'].create({
    'name': 'My Dataset',
    'technical_name': 'my_dataset',
    'connection_id': conn.id,
    'source_type': 'model',
    'model_id': self.env.ref('sale.model_sale_order').id,
    'include_all_fields': True,
})

# Generate SQL
dataset.action_generate_sql()

# Create view in PostgreSQL
dataset.action_create_view()

# Sync to Superset
dataset.action_sync_to_superset()
```

## PostgreSQL Setup

### Option 1: Read Replica (Recommended)

```sql
-- On primary server, create replication slot
SELECT pg_create_logical_replication_slot('superset_replica', 'pgoutput');

-- On replica, create read-only user
CREATE USER superset_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE odoo TO superset_reader;
GRANT USAGE ON SCHEMA public TO superset_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_reader;
```

### Option 2: Direct Access (Simpler)

```sql
-- Create read-only user on Odoo's database
CREATE USER superset_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE odoo TO superset_reader;
GRANT USAGE ON SCHEMA public TO superset_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_reader;

-- Grant access to future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_reader;
```

## Multi-Tenant / Row-Level Security

Enable RLS in dataset settings to filter by `company_id`:

```sql
-- Example: User can only see their company's data
CREATE POLICY company_isolation ON superset_sales_order_analysis
    FOR SELECT
    USING (company_id = current_setting('app.company_id')::integer);
```

In Superset, configure RLS rules per role.

## Comparison: Original Spec vs This Implementation

### Original Spec Issues

1. **Impossible Architecture** - SQLAlchemy dialect can't translate SQL to Odoo's JSON-RPC
2. **No Working Code** - Only pseudocode stubs
3. **Missing Connection Pooling** - Odoo's API is stateless
4. **No Error Handling** - Production-critical
5. **No Caching Strategy** - Performance issue

### This Implementation Fixes

1. **Direct PostgreSQL** - Works natively with Superset
2. **Complete Module** - Production-ready Odoo module
3. **SQL Views** - Optimized for BI queries
4. **Full Error Handling** - Try/except, logging, user feedback
5. **Managed Metadata** - Tracks sync status, last refresh

## Smart Delta Architecture

This module follows the `ipai_*` Smart Delta pattern:

- ✓ Extends core models via `_inherit`
- ✓ No monkey-patching or forks
- ✓ OCA-compatible manifest
- ✓ AGPL-3 licensed
- ✓ Marketplace-ready

## Roadmap

- [ ] Superset chart/dashboard creation from Odoo
- [ ] Webhook-based cache invalidation
- [ ] n8n workflow integration for ETL
- [ ] Materialized views for heavy aggregations
- [ ] Apache Druid integration for real-time analytics

## License

AGPL-3.0 (OCA-compatible)

## Author

InsightPulse AI - https://insightpulseai.net
