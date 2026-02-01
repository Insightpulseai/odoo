# Multi-Tenant Platform Architecture

## Overview

InsightPulse AI platform uses **tenant-aware architecture** where:
- **TBWA = tenant/client** (not special codebase fork)
- **Platform = shared infrastructure** (Odoo CE + Supabase + Superset)
- **Isolation = database-level** (one Odoo DB per tenant + Supabase schema isolation)

## Architecture Principles

### 1. Separation of Concerns

```
odoo-ce (jgtolentino/odoo-ce)
├── Platform Odoo Core
│   ├── Odoo CE 18.0 + OCA modules
│   ├── ipai_* custom modules
│   └── Tenant provisioning engine
└── Infrastructure
    ├── CI/CD workflows
    ├── Deployment scripts
    └── Multi-tenant configuration

tbwa-agency-databank (jgtolentino/tbwa-agency-databank)
├── TBWA Tenant Data
│   ├── Supabase migrations (tbwa schema)
│   ├── Scout retail views
│   └── TBWA-specific seeds

superset (jgtolentino/superset)
├── BI Shell
│   ├── Superset Docker image
│   ├── Dataset configurations
│   └── Dashboard templates (all tenants)
```

### 2. Tenant Isolation Model

**One Platform Runtime, Multiple Tenant DBs**:

```
Odoo Host (Droplet/App Platform)
├── Odoo Container (ghcr.io/jgtolentino/odoo-ce:18)
│   └── Serves multiple databases
├── PostgreSQL (Supabase)
│   ├── odoo_platform (internal operations)
│   ├── odoo_tbwa (TBWA tenant)
│   └── odoo_<next> (future tenants)
└── Supabase Schemas
    ├── public (platform metadata)
    ├── tbwa (TBWA client data)
    ├── scout (shared retail intelligence)
    └── <next> (future tenant schemas)
```

## Tenant Metadata Model

### ipai.tenant (Platform Core)

Located in: `addons/ipai/ipai_tenant_core/`

**Purpose**: Track tenant configuration and route platform operations

**Key Fields**:
- `code` - Unique tenant identifier (e.g., "tbwa", lowercase alphanumeric)
- `db_name` - Odoo database name (e.g., "odoo_tbwa")
- `supabase_schema` - PostgreSQL schema in Supabase (e.g., "tbwa")
- `primary_domain` - Tenant access URL (e.g., "tbwa.erp.insightpulseai.com")
- `superset_workspace` - Superset folder for tenant dashboards
- `industry`, `country_id`, `admin_email` - Business metadata

**Seed Tenants** (from `data/tenant_seed_data.xml`):

| Code | Name | DB | Supabase Schema | Purpose |
|------|------|----|--------------------|---------|
| `platform` | InsightPulse AI Platform | `odoo_platform` | `public` | Internal operations |
| `tbwa` | TBWA Philippines | `odoo_tbwa` | `tbwa` | TBWA client operations |
| `scout` | Scout Retail Intelligence | `odoo_platform` | `scout` | Shared analytics |

## Tenant Provisioning Workflow

### Automated Provisioning

**Command**:
```bash
cd /path/to/odoo-ce
export ODOO_ADMIN_PASSWORD='secure_password'
export POSTGRES_URL='postgres://...' # Supabase pooler URL
export SUPABASE_SERVICE_ROLE_KEY='eyJ...'

# Provision TBWA tenant
make provision-tbwa

# Or provision any tenant
make provision-tenant CODE=tbwa
```

**What It Does** (see `scripts/provision_tenant.sh`):

1. **Check Tenant Exists**: Verify `ipai.tenant` record exists in platform DB
2. **Provision Supabase Schema**: Create PostgreSQL schema (e.g., `tbwa`)
3. **Create Odoo Database**: Initialize new Odoo DB (e.g., `odoo_tbwa`)
4. **Install Base Modules**: Install `ipai_tenant_core`, `ipai_bi_superset_embed`, etc.
5. **Set Admin Password**: Configure admin user credentials
6. **Provision Superset Workspace**: Create tenant folder in Superset

### Manual Steps (Post-Provisioning)

1. **Configure Tenant Modules**:
   - Install TBWA-specific modules (e.g., `ipai_finance_ppm`)
   - Configure BIR compliance settings
   - Set up multi-agency workflows

2. **Create Superset Dashboards**:
   - Go to: https://superset.insightpulseai.com
   - Create datasets pointing to `tbwa` schema
   - Build dashboards in `tbwa` workspace folder

3. **Configure Domain Routing** (if using custom domain):
   - Update DNS: `tbwa.erp.insightpulseai.com` → Odoo host IP
   - Configure Odoo `--db-filter` for tenant routing

## Data Flow Architecture

### Tenant Data Isolation

```
TBWA User Request
   ↓ (https://tbwa.erp.insightpulseai.com)
Odoo Platform (--db-filter=^odoo_tbwa$)
   ↓ (connects to odoo_tbwa DB)
Odoo Business Logic
   ↓ (queries/inserts via ORM)
Supabase PostgreSQL
   ├── tbwa schema (TBWA client data)
   ├── scout schema (shared retail views)
   └── public schema (platform metadata)
```

**RLS Enforcement**:
- All `tbwa.*` tables have RLS policies filtering on `tenant_id = 'tbwa'`
- Platform operations use `public` schema with no tenant filtering
- Shared analytics (`scout`) aggregates across tenants with proper RLS

### Superset Integration

```
TBWA User (Odoo UI)
   ↓
ipai_bi_superset_embed Module
   ↓ (calls Superset API)
Guest Token Generation
   ↓ (POST /api/v1/security/guest_token)
Embedded Dashboard (iframe)
   ↓ (queries Supabase)
Tenant-Specific Data (tbwa schema)
```

**Configuration** (in Odoo `ir.config_parameter`):
- `superset.domain` → `https://superset.insightpulseai.com`
- `superset.api_url` → `https://superset.insightpulseai.com/api/v1`
- `superset.workspace` → `tbwa` (tenant-specific)

## Cross-Repo CI/CD Integration

### Schema Change Trigger (odoo-ce → superset)

**Workflow**: `.github/workflows/notify-superset.yml`

```yaml
on:
  push:
    paths:
      - "supabase/migrations/**"
      - "db/**"
      - "sql/**"

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Superset pipeline
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.GH_PAT_SUPERSET }}" \
            https://api.github.com/repos/jgtolentino/superset/dispatches \
            -d '{"event_type":"schema_changed"}'
```

**Effect**: Schema changes in odoo-ce automatically rebuild Superset with updated datasets

### Superset Rebuild (superset)

**Workflow**: `.github/workflows/deploy.yml`

```yaml
on:
  repository_dispatch:
    types: [schema_changed]

jobs:
  dev:
    runs-on: ubuntu-latest
    steps:
      - name: Log schema change event
        if: github.event_name == 'repository_dispatch'
        run: |
          echo "🔄 Triggered by odoo-ce schema change"
```

**Effect**: Superset redeploys when schema changes are detected

## Supabase Configuration

### Project Details

**Project ID**: `spdtwktxdalcfigzeqrz`
**Region**: AWS us-east-1
**Pooler**: Port 6543 (connection pooling enabled)

### Connection Strings

**Pooled Connection** (recommended):
```bash
POSTGRES_URL=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x
```

**Direct Connection** (migrations only):
```bash
POSTGRES_URL_NON_POOLING=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

### API Keys

**Anonymous Key** (public client access):
```bash
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4
```

**Service Role Key** (server-side operations, bypasses RLS):
```bash
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDY0NDAzNSwiZXhwIjoyMDc2MjIwMDM1fQ.Rhdi18B5EuUeaSGfdB4rqZ6UoPSrJ9IbzkN_YboyvhU
```

### Schema Organization

**Platform Schemas**:
- `public` - Platform metadata (`ipai.tenant`, system config)
- `auth` - Supabase auth (user accounts)
- `storage` - Supabase storage (files, attachments)

**Tenant Schemas**:
- `tbwa` - TBWA Philippines client data (agencies, expenses, BIR forms)
- `scout` - Scout retail intelligence (cross-tenant analytics)

**Future Tenants**:
- `afc_client` - AFC client operations
- `nextgen_agency` - NextGen agency operations

## Tenant Onboarding Checklist

### Pre-Provisioning

- [ ] Create `ipai.tenant` record in platform Odoo
  - Set `code`, `db_name`, `supabase_schema`
  - Configure `primary_domain`, `superset_workspace`
- [ ] Prepare Supabase migrations for tenant schema
  - Create `tbwa-agency-databank/supabase/migrations/*.sql`
  - Include RLS policies with `tenant_id` filtering

### Provisioning

- [ ] Run `make provision-tenant CODE=tbwa`
- [ ] Verify Supabase schema created: `SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'tbwa';`
- [ ] Verify Odoo database created: `SELECT datname FROM pg_database WHERE datname = 'odoo_tbwa';`
- [ ] Test admin login: `https://tbwa.erp.insightpulseai.com`

### Post-Provisioning

- [ ] Install tenant-specific Odoo modules
- [ ] Configure BIR compliance settings (if applicable)
- [ ] Create Superset datasets pointing to tenant schema
- [ ] Build initial dashboards in Superset workspace
- [ ] Configure Odoo `ipai_bi_superset_embed` for tenant
- [ ] Test embedded dashboards in Odoo views

### Acceptance Gates

- [ ] Tenant can login to Odoo at custom domain
- [ ] Tenant data isolated in Supabase schema
- [ ] Superset dashboards load in Odoo views
- [ ] Guest token API returns valid tokens
- [ ] RLS policies enforce tenant isolation

## Troubleshooting

### "Tenant code not found in ipai.tenant table"

**Cause**: Tenant record not created in platform DB

**Fix**:
```bash
# Create tenant record in Odoo UI
# Or insert via SQL:
psql "$POSTGRES_URL" -c "
INSERT INTO ipai_tenant (code, name, db_name, supabase_schema, active, create_date, write_date)
VALUES ('tbwa', 'TBWA Philippines', 'odoo_tbwa', 'tbwa', true, NOW(), NOW());
"
```

### "Database 'odoo_tbwa' already exists"

**Cause**: Tenant database was partially provisioned

**Fix**:
```bash
# Option 1: Drop and recreate
psql "$POSTGRES_URL" -c "DROP DATABASE odoo_tbwa;"
make provision-tenant CODE=tbwa

# Option 2: Skip database creation, continue provisioning
# Edit scripts/provision_tenant.sh to skip DB creation step
```

### "Schema 'tbwa' already exists"

**Cause**: Supabase schema was manually created or from previous provisioning

**Fix**: This is safe - provisioning script skips schema creation if exists

### "Superset can't connect to Supabase"

**Cause**: Connection string or credentials incorrect

**Fix**:
```bash
# Verify credentials in Superset deployment
doctl apps update $SUPERSET_APP_ID --env-vars "POSTGRES_URL=..."

# Test connection
psql "$POSTGRES_URL" -c "SELECT current_database(), current_schema();"
```

## References

- **Odoo Tenant Core**: `addons/ipai/ipai_tenant_core/`
- **Provisioning Script**: `scripts/provision_tenant.sh`
- **Makefile Targets**: `Makefile`
- **Superset Integration**: `docs/SUPERSET_INTEGRATION.md`
- **Supabase Project**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz

---

**Last Updated**: 2025-01-12
**Architecture Version**: 1.0
**Maintained By**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
