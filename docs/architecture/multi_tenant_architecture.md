# InsightPulse AI - Multi-Tenant ERP SaaS Architecture

## Overview

This document describes the complete multi-tenant architecture for InsightPulse AI, enabling:

- **Self-hosted clients**: Each tenant gets their own isolated database
- **Clients becoming providers**: Recursive tenant hierarchy (white-label)
- **Automated provisioning**: Database creation, cloning, and configuration
- **Schema introspection**: Auto-generate DBML, ERD, and documentation
- **Superset integration**: Automatic BI workspace per tenant

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE (insightpulse_master)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   tenants   │  │   plans     │  │   jobs      │  │  metrics    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│  TENANT: tbwa-smp     │ │  TENANT: acme-corp    │ │  TENANT: client-xyz   │
│  (Provider)           │ │  (Client)             │ │  (Client)             │
│  ┌─────────────────┐  │ │  ┌─────────────────┐  │ │  ┌─────────────────┐  │
│  │ Odoo 18 CE      │  │ │  │ Odoo 18 CE      │  │ │  │ Odoo 18 CE      │  │
│  │ + ipai_* modules│  │ │  │ + ipai_* modules│  │ │  │ + ipai_* modules│  │
│  └─────────────────┘  │ │  └─────────────────┘  │ │  └─────────────────┘  │
│  ┌─────────────────┐  │ │  ┌─────────────────┐  │ │  ┌─────────────────┐  │
│  │ Superset        │  │ │  │ Superset        │  │ │  │ Superset        │  │
│  │ Workspace       │  │ │  │ Workspace       │  │ │  │ Workspace       │  │
│  └─────────────────┘  │ │  └─────────────────┘  │ │  └─────────────────┘  │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
         │
         │ (Provider can create sub-tenants)
         ▼
┌───────────────────────┐
│  SUB-TENANT: sub-acme │
│  (Client of Provider) │
└───────────────────────┘
```

## Tenant Types

| Type | Description | Can Create Tenants | Example |
|------|-------------|-------------------|---------|
| `platform_owner` | InsightPulse AI (you) | ✓ | insightpulse |
| `provider` | White-label partner | ✓ (sub-tenants) | tbwa-smp |
| `client` | End customer | ✗ | acme-corp |
| `internal` | Testing/demo | ✗ | demo-tenant |

## Files Included

| File | Purpose |
|------|---------|
| `insightpulse_canonical.dbml` | DBML schema for ERD visualization (dbdiagram.io) |
| `control_plane_schema.sql` | SQL DDL for control plane database |
| `tenant_automation.py` | Python module for tenant management |
| `n8n_tenant_provisioning.json` | n8n workflow for automated provisioning |

## Database Schema

### Control Plane Tables

```sql
-- Core tables in insightpulse_master database
tenants                 -- All tenant records with DB connection info
subscription_plans      -- Pricing tiers (starter, professional, enterprise, provider)
tenant_user_assignments -- Maps platform users to tenants with roles
provisioning_jobs       -- Background job queue for DB operations
database_templates      -- Templates for cloning new tenant DBs
tenant_invoices         -- Billing records
tenant_metrics          -- Daily usage metrics per tenant
superset_workspaces     -- Apache Superset workspace configuration
audit_logs              -- Platform-level audit trail
```

### Tenant Database Tables

```sql
-- Tables in each tenant database (cloned from template)
-- Standard Odoo tables plus:
tenant_config           -- Tenant-specific configuration
ipai_journal_entries    -- Extended journal entry metadata
ipai_month_end_checklist -- Finance SSC month-end tracking
ipai_documents          -- Document management with OCR
ipai_ai_conversations   -- AI chat history
ipai_ai_messages        -- Individual AI messages
ipai_ai_embeddings      -- Vector embeddings for RAG
analytics_finance_summary -- Pre-aggregated finance data
analytics_user_activity -- User activity metrics
ipai_audit_log          -- Tenant-level audit trail
```

## Automated Provisioning Flow

```
1. API Request (POST /tenant/create)
   ↓
2. Validate tenant code & generate credentials
   ↓
3. Insert tenant record (status: provisioning)
   ↓
4. Create PostgreSQL user
   ↓
5. CREATE DATABASE ... WITH TEMPLATE insightpulse_template
   ↓
6. Grant permissions
   ↓
7. Update tenant status (status: active)
   ↓
8. Create Superset database connection
   ↓
9. Send welcome email via Mailgun
   ↓
10. Notify Slack #provisioning channel
```

## Usage Examples

### Create a New Tenant (Python)

```python
from tenant_automation import TenantManager, TenantType

async with TenantManager() as manager:
    tenant = await manager.create_tenant(
        code="acme-corp",
        name="Acme Corporation",
        tenant_type=TenantType.CLIENT,
        plan_id="professional"
    )
    print(f"Created: {tenant.db_name}")
```

### Clone a Tenant (Python)

```python
async with TenantManager() as manager:
    # Clone for demo/testing (structure only)
    demo = await manager.clone_tenant(
        source_tenant_id="...",
        new_code="acme-demo",
        new_name="Acme Demo",
        include_data=False
    )
    
    # Clone with data (for migration)
    migrated = await manager.clone_tenant(
        source_tenant_id="...",
        new_code="acme-v2",
        new_name="Acme V2",
        include_data=True
    )
```

### Upgrade Client to Provider (Python)

```python
async with TenantManager() as manager:
    # Client can now create their own sub-tenants
    provider = await manager.upgrade_to_provider(tenant_id="...")
    print(f"Upgraded to: {provider.tenant_type}")  # provider
```

### Introspect Database Schema (Python)

```python
from tenant_automation import SchemaIntrospector, DocumentationGenerator

# Generate DBML for dbdiagram.io
async with SchemaIntrospector(dsn) as introspector:
    dbml = await introspector.generate_dbml()
    markdown = await introspector.generate_markdown()
    erd_json = await introspector.generate_erd_json()

# Generate all documentation formats
generator = DocumentationGenerator("./docs")
outputs = await generator.generate_all(dsn, "acme-corp")
# Creates: acme-corp_schema.dbml, acme-corp_schema.md, acme-corp_erd.json
```

### Create Tenant via n8n Webhook

```bash
curl -X POST https://n8n.insightpulseai.net/webhook/tenant/create \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "new-client",
    "name": "New Client Inc.",
    "email": "admin@newclient.com",
    "plan_code": "professional"
  }'
```

### Setup Superset Workspace (Python)

```python
from tenant_automation import SupersetManager, TenantManager

async with TenantManager() as manager:
    tenant = await manager.get_tenant_by_code("acme-corp")
    
    async with SupersetManager() as superset:
        result = await superset.setup_tenant_workspace(tenant)
        print(f"Superset DB ID: {result['database_id']}")
        print(f"Datasets created: {len(result['dataset_ids'])}")
```

## CLI Commands

```bash
# Create tenant
python tenant_automation.py create acme-corp "Acme Corporation" --type client

# List tenants
python tenant_automation.py list --type client --status active

# Introspect and document
python tenant_automation.py introspect acme-corp --format all --output ./docs

# Setup Superset workspace
python tenant_automation.py superset acme-corp
```

## Environment Variables

```bash
# Control Plane Database
MASTER_DB_HOST=localhost
MASTER_DB_PORT=5432
MASTER_DB_NAME=insightpulse_master
MASTER_DB_USER=postgres
MASTER_DB_PASSWORD=secret

# Template Database
TEMPLATE_DB_NAME=insightpulse_template

# Encryption
ENCRYPTION_KEY=your-32-byte-fernet-key

# Superset
SUPERSET_URL=http://localhost:8088
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=admin

# Mailgun (for welcome emails)
MAILGUN_API_URL=https://api.mailgun.net
MAILGUN_DOMAIN=mg.insightpulseai.net
MAILGUN_API_KEY=key-xxx

# Slack (for notifications)
SLACK_BOT_TOKEN=xoxb-xxx
```

## DBML Output Example

The introspector generates DBML compatible with [dbdiagram.io](https://dbdiagram.io):

```dbml
// Generated from insightpulse_acme_corp
// Introspected at 2026-01-13T08:00:00Z

Project insightpulse_acme_corp {
  database_type: 'PostgreSQL'
}

Enum tenant_status_enum {
  provisioning
  active
  suspended
  archived
}

Table public.ipai_journal_entries {
  id integer [pk, increment]
  odoo_move_id integer [not null]
  entry_type varchar(50) [not null]
  cost_center varchar(50)
  bir_form_type varchar(20)
  created_at timestamptz [default: `now()`]
  
  indexes {
    odoo_move_id [unique]
    entry_type
  }
}

// Foreign Key Relationships
Ref: public.ipai_journal_entries.odoo_move_id > public.account_move.id
```

## Cost Analysis

| Component | Monthly Cost | Purpose |
|-----------|--------------|---------|
| PostgreSQL (per tenant) | ~$5-15 | Isolated database |
| Superset workspace | $0 (shared) | BI dashboards |
| Provisioning automation | $0 (n8n self-hosted) | Tenant lifecycle |
| Total per tenant | ~$5-15 | Full isolation |

**Comparison to alternatives:**
- AWS RDS per tenant: $50-200/month
- Multi-tenant SaaS (shared DB): Lower isolation, compliance risk
- Managed multi-tenant solutions: $500+/month

## Security Considerations

1. **Database Isolation**: Each tenant has own PostgreSQL database
2. **Credential Encryption**: AES-256 (Fernet) for stored passwords
3. **Row-Level Security**: Optional RLS in control plane
4. **Audit Logging**: Both platform and tenant-level
5. **RBAC**: Role-based access (owner, admin, manager, member, viewer)

## Next Steps

1. Run `control_plane_schema.sql` to create master database
2. Create template database with Odoo 18 CE + ipai_* modules
3. Deploy n8n workflow for automated provisioning
4. Configure Superset for multi-tenant access
5. Set up Mailgun for transactional emails
6. Configure Slack notifications
