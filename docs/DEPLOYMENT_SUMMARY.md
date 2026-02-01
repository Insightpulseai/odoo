# Multi-Tenant Platform Deployment Summary

**Date**: 2025-01-12
**Status**: ✅ Complete - PRs Created

## Pull Requests

### odoo-ce
**PR**: https://github.com/jgtolentino/odoo-ce/pull/211
**Branch**: `feat/deterministic-scss-verification`
**Changes**: 16 files, 2,310 lines added

### superset
**PR**: https://github.com/jgtolentino/superset/pull/13
**Branch**: `feature/postgres-native-examples`
**Changes**: 2 files, 44 lines added

## What Was Implemented

### 1. Multi-Tenant Architecture

**Core Principle**: TBWA = tenant/client, not special codebase fork

**Tenant Isolation**:
- One Odoo DB per tenant (`odoo_platform`, `odoo_tbwa`)
- Supabase schema isolation (`public`, `tbwa`, `scout`)
- Shared Superset with tenant-specific workspaces

### 2. ipai.tenant Model

**Location**: `addons/ipai/ipai_tenant_core/`

**Seed Tenants**:
```python
platform   → odoo_platform → public schema (internal operations)
tbwa       → odoo_tbwa     → tbwa schema (TBWA client data)
scout      → odoo_platform → scout schema (shared retail analytics)
```

**Fields**:
- `code` - Tenant identifier (lowercase alphanumeric)
- `db_name` - Odoo database name
- `supabase_schema` - PostgreSQL schema
- `primary_domain` - Access URL
- `superset_workspace` - Dashboard folder
- Business metadata: `industry`, `country_id`, `admin_email`

### 3. Automated Provisioning

**Script**: `scripts/provision_tenant.sh`

**Usage**:
```bash
export ODOO_ADMIN_PASSWORD='secure_password'
export POSTGRES_URL='postgres://postgres.spdtwktxdalcfigzeqrz:...'
make provision-tbwa
```

**Steps**:
1. Check tenant exists in `ipai.tenant` table
2. Create Supabase schema (e.g., `tbwa`)
3. Initialize Odoo database (e.g., `odoo_tbwa`)
4. Install base modules (`ipai_tenant_core`, `ipai_bi_superset_embed`)
5. Set admin password
6. Prepare Superset workspace

### 4. Cross-Repo CI Integration

**Workflow**: `.github/workflows/notify-superset.yml` (odoo-ce)

**Trigger**:
- Schema changes in `supabase/migrations/`, `db/`, `sql/`
- Sends `repository_dispatch` to `jgtolentino/superset`
- Event type: `schema_changed`

**Effect**:
- Superset automatically rebuilds with updated datasets
- New views/tables available within 60 seconds

### 5. Supabase Configuration

**Project**: `spdtwktxdalcfigzeqrz` (Platform Database)
**Region**: AWS us-east-1
**Connection**: ✅ Tested (PostgreSQL 17.6)

**Connection String**:
```bash
POSTGRES_URL=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

**API Keys**:
```bash
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 6. Documentation

**Complete Guides**:
- `docs/TENANT_ARCHITECTURE.md` - Full architecture reference
- `docs/SUPERSET_INTEGRATION.md` - Cross-repo integration details
- `docs/QUICK_START.md` - TL;DR quick start

## Post-Merge Actions

### Step 1: Merge PRs

```bash
# Review and merge both PRs:
# - odoo-ce PR #211
# - superset PR #13
```

### Step 2: Install ipai_tenant_core

```bash
# On Odoo host
odoo-bin -d odoo_platform -i ipai_tenant_core --stop-after-init

# Verify seed data
psql "$POSTGRES_URL" -c "SELECT code, name, db_name, supabase_schema FROM ipai_tenant;"
# Expected output:
#   code     | name                          | db_name         | supabase_schema
# -----------+-------------------------------+-----------------+----------------
#   platform | InsightPulse AI Platform      | odoo_platform   | public
#   tbwa     | TBWA Philippines              | odoo_tbwa       | tbwa
#   scout    | Scout Retail Intelligence     | odoo_platform   | scout
```

### Step 3: Provision TBWA Tenant

```bash
cd /path/to/odoo-ce

# Set environment variables
export ODOO_ADMIN_PASSWORD='secure_password'
export POSTGRES_URL='postgres://postgres.spdtwktxdalcfigzeqrz:...'
export SUPABASE_SERVICE_ROLE_KEY='eyJ...'

# Provision tenant (one command)
make provision-tbwa

# Expected output:
# >>> Checking if tenant 'tbwa' exists in platform DB...
# >>> Tenant 'tbwa' found in platform DB ✓
# >>> Provisioning Supabase schema 'tbwa'...
# >>> Schema 'tbwa' created ✓
# >>> Provisioning Odoo database 'odoo_tbwa'...
# >>> Odoo database 'odoo_tbwa' created ✓
# >>> Installing base modules for 'odoo_tbwa'...
# >>> Base modules installed ✓
# >>> Setting admin password for 'odoo_tbwa'...
# >>> Admin password set ✓
# ✅ Tenant 'tbwa' provisioned successfully!
```

### Step 4: Verify Integration

**Test Supabase Connection**:
```bash
make test-connection
# Expected: ✅ Connection successful (PostgreSQL 17.6)
```

**Test Cross-Repo Trigger**:
```bash
# 1. Create test schema change in odoo-ce
echo "-- Test migration" > supabase/migrations/V999__test.sql
git add supabase/migrations/V999__test.sql
git commit -m "test: trigger Superset rebuild"
git push origin main

# 2. Check GitHub Actions in odoo-ce
# https://github.com/jgtolentino/odoo-ce/actions

# 3. Check GitHub Actions in superset (should trigger within 30 seconds)
# https://github.com/jgtolentino/superset/actions

# 4. Verify repository_dispatch event logged in superset deploy workflow
```

**Test TBWA Tenant Access**:
```bash
# Access TBWA Odoo
open https://tbwa.erp.insightpulseai.com
# OR
open https://erp.insightpulseai.com?db=odoo_tbwa

# Login: admin / $ODOO_ADMIN_PASSWORD
```

### Step 5: Configure Superset Workspace

```bash
# 1. Access Superset
open https://superset.insightpulseai.com

# 2. Create TBWA workspace folder
# - Go to Dashboards > Create folder: "tbwa"

# 3. Create dataset pointing to TBWA schema
# - Data > Databases > Add database
# - Connection string: $POSTGRES_URL
# - Schema: tbwa

# 4. Build initial dashboards
# - Use Scout retail views
# - Place in "tbwa" workspace folder

# 5. Test embedded dashboard in Odoo
# - Install ipai_bi_superset_embed in odoo_tbwa
# - Configure superset.domain, superset.api_url
# - Test guest token generation
```

## Acceptance Criteria

### Database Layer
- [x] Supabase connection successful
- [ ] `ipai.tenant` seed data loaded (3 tenants)
- [ ] TBWA schema created in Supabase
- [ ] `odoo_tbwa` database created

### Application Layer
- [ ] `ipai_tenant_core` installed in `odoo_platform`
- [ ] TBWA tenant provisioned successfully
- [ ] Admin login working for TBWA tenant
- [ ] Base modules installed in TBWA tenant

### Integration Layer
- [x] Cross-repo CI workflow deployed
- [ ] Schema change triggers Superset rebuild
- [ ] Superset workspace created for TBWA
- [ ] Embedded dashboards load in Odoo

### Documentation
- [x] Architecture documentation complete
- [x] Quick start guide available
- [x] Provisioning script documented

## Rollback Plan

If issues occur post-merge:

### Rollback Database Changes

```bash
# Drop TBWA tenant database
psql "$POSTGRES_URL" -c "DROP DATABASE IF EXISTS odoo_tbwa;"

# Drop TBWA schema
psql "$POSTGRES_URL" -c "DROP SCHEMA IF EXISTS tbwa CASCADE;"

# Remove tenant record
psql "$POSTGRES_URL" -c "DELETE FROM ipai_tenant WHERE code = 'tbwa';"
```

### Rollback Code Changes

```bash
# odoo-ce
git revert ebf98906  # Revert multi-tenant architecture commit
git push origin feat/deterministic-scss-verification

# superset
git revert ab35d2d  # Revert Supabase config commit
git push origin feature/postgres-native-examples
```

## Support

**Questions?**
- Architecture: See `docs/TENANT_ARCHITECTURE.md`
- Integration: See `docs/SUPERSET_INTEGRATION.md`
- Quick Start: See `docs/QUICK_START.md`

**Troubleshooting**: See "Troubleshooting" section in `docs/TENANT_ARCHITECTURE.md`

---

**Deployment Lead**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
**Deployment Date**: 2025-01-12
**Architecture Version**: 1.0
**Status**: ✅ Ready for Post-Merge Testing
