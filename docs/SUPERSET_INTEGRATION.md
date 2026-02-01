# Superset Integration Architecture

## Overview

This document describes the **cross-repo integration** between `odoo-ce` (platform + database authority) and `superset` (BI application repo).

## Architecture Principles

1. **Single Source of Truth**: `odoo-ce` owns all database schema, migrations, and views
2. **Superset as Consumer**: Superset repo only reads from Supabase PostgreSQL
3. **Automated Coordination**: Schema changes in odoo-ce automatically trigger Superset rebuild
4. **No Duplication**: Superset infra lives in `jgtolentino/superset`, not duplicated here

## Repository Separation

```
odoo-ce (jgtolentino/odoo-ce)
├── Database Authority
│   ├── supabase/migrations/       ← All schema changes
│   ├── db/                         ← SQL scripts
│   └── sql/                        ← Scout/retail views
├── Odoo Modules
│   └── addons/ipai/ipai_bi_superset_embed/
│       ├── models/                 ← Superset API client
│       ├── views/                  ← Embedded dashboard views
│       └── data/config_params.xml  ← Superset URLs + tokens
└── CI/CD
    └── .github/workflows/notify-superset.yml  ← Trigger Superset on schema change

superset (jgtolentino/superset)
├── BI Application
│   ├── Dockerfile                  ← Superset container
│   ├── infra/do-app-spec.yaml     ← DigitalOcean deployment
│   └── config/scout_retail_datasets.yaml
├── Dashboard Templates
│   └── examples/dashboards/scout_retail_intelligence.json
└── CI/CD
    └── .github/workflows/deploy.yml  ← Listen for schema_changed event
```

## Supabase Configuration

**Project**: Platform Database (`spdtwktxdalcfigzeqrz`)
**Region**: AWS us-east-1
**Architecture**: Multi-tenant with schema isolation

### Connection Details

```bash
# Supabase Project
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

# PostgreSQL Connection (via pooler - port 6543)
POSTGRES_URL=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x

# API Keys
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDY0NDAzNSwiZXhwIjoyMDc2MjIwMDM1fQ.Rhdi18B5EuUeaSGfdB4rqZ6UoPSrJ9IbzkN_YboyvhU
```

**Storage**: All credentials in `~/.zshrc` or platform secrets (DigitalOcean, GitHub Actions)

### Multi-Tenant Schema Isolation

**Platform uses schema-based tenant isolation:**

- **`public`**: Shared platform tables (tenant metadata, system config)
- **`tbwa`**: TBWA client data (Scout transactions, agencies, etc.)
- **`scout`**: Scout retail intelligence views (cross-tenant analytics)
- **Future tenants**: `afc_client`, `nextgen_agency`, etc.

**RLS Policies**: All tenant-specific tables enforce Row-Level Security filtering on `tenant_id`

## Cross-Repo CI Workflow

### Trigger Flow (odoo-ce → superset)

```
1. Developer commits schema change to odoo-ce
   ↓ (push to main/master/develop)
2. .github/workflows/notify-superset.yml detects changes in:
   - supabase/migrations/**
   - db/**
   - sql/**
   - packages/db/**
   ↓
3. Workflow triggers GitHub API repository_dispatch:
   POST /repos/jgtolentino/superset/dispatches
   Body: {"event_type": "schema_changed", "client_payload": {...}}
   ↓
4. Superset .github/workflows/deploy.yml receives event
   ↓
5. Superset rebuilds + redeploys with updated schema
```

### Required Secrets

**In odoo-ce repo** (GitHub Actions secrets):
- `GH_PAT_SUPERSET` - Personal Access Token with `repo` scope for `jgtolentino/superset`

**In superset repo** (GitHub Actions secrets):
- `OPEX_SUPABASE_ANON_KEY`
- `OPEX_SUPABASE_SERVICE_ROLE_KEY`
- `OPEX_POSTGRES_URL`
- `SUPERSET_ADMIN_USER`
- `SUPERSET_ADMIN_PASS`

## Odoo Module Integration

### ipai_bi_superset_embed

**Purpose**: Embed Superset dashboards in Odoo views via iframe/SDK

**Architecture**:

```python
# models/superset_dashboard.py
class SupersetDashboard(models.Model):
    _name = 'ipai.superset.dashboard'

    def get_guest_token(self):
        """Call Superset API to generate guest token for embedded dashboard"""
        api_url = self.env['ir.config_parameter'].sudo().get_param('superset.api_url')
        response = requests.post(f"{api_url}/api/v1/security/guest_token", ...)
        return response.json()['token']
```

**Views**: OWL components with iframe embedding:

```xml
<!-- views/superset_dashboard_views.xml -->
<template id="superset_embed_template">
    <iframe src="{superset.domain}/superset/dashboard/{dashboard_id}?standalone=2&amp;guest_token={token}" />
</template>
```

**Configuration** (data/config_params.xml):

```xml
<data>
    <record id="superset_domain" model="ir.config_parameter">
        <field name="key">superset.domain</field>
        <field name="value">https://superset.insightpulseai.com</field>
    </record>
    <record id="superset_api_url" model="ir.config_parameter">
        <field name="key">superset.api_url</field>
        <field name="value">https://superset.insightpulseai.com/api/v1</field>
    </record>
</data>
```

## Deployment Workflow

### Schema Change Scenario

```bash
# 1. Developer modifies Scout views in odoo-ce
cd /path/to/odoo-ce
git checkout -b feature/scout-new-metrics
psql "$OPEX_POSTGRES_URL" -f sql/V007__create_scout_performance_view.sql

# 2. Commit + push
git add sql/V007__create_scout_performance_view.sql
git commit -m "Add Scout performance metrics view"
git push origin feature/scout-new-metrics

# 3. Create PR → merge to main
# GitHub Actions automatically:
#   - Detects schema change in sql/
#   - Triggers jgtolentino/superset repository_dispatch
#   - Superset rebuilds with new view available

# 4. Verify in Superset
curl -sf https://superset.insightpulseai.com/api/v1/dataset/ | jq '.result[] | select(.table_name=="scout_performance_view")'
```

### Manual Superset Rebuild

If auto-trigger fails, manually dispatch from odoo-ce:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_PAT_SUPERSET" \
  https://api.github.com/repos/jgtolentino/superset/dispatches \
  -d '{"event_type":"schema_changed","client_payload":{"manual_trigger":true}}'
```

## Acceptance Gates

### Schema Changes (odoo-ce)

- ✅ All migrations applied successfully to Supabase
- ✅ Scout views created/updated (V00x__create_scout_retail_views.sql)
- ✅ RLS policies enforced on new tables
- ✅ Superset notification triggered (check GitHub Actions logs)

### Superset Deployment

- ✅ Docker image built and pushed to registry
- ✅ DigitalOcean App Platform deployment succeeded
- ✅ Superset health check: `curl -sf https://superset.insightpulseai.com/health`
- ✅ Scout datasets visible in Superset UI
- ✅ Guest token API responding: `POST /api/v1/security/guest_token`

### Odoo Embed Integration

- ✅ Module `ipai_bi_superset_embed` installed in Odoo
- ✅ Config parameters set (superset.domain, superset.api_url)
- ✅ Guest token generation working
- ✅ Dashboard iframe loads in Odoo view (SSIM ≥ 0.97 mobile, ≥ 0.98 desktop)

## Troubleshooting

### "Superset rebuild not triggered"

**Cause**: GitHub PAT expired or missing `repo` scope

**Fix**:
```bash
# Generate new PAT at https://github.com/settings/tokens
# Add to odoo-ce repo secrets:
gh secret set GH_PAT_SUPERSET --body="ghp_newtoken..."
```

### "Superset can't connect to Supabase"

**Cause**: Database credentials not set in Superset deployment

**Fix**:
```bash
# Update DigitalOcean App Platform secrets
doctl apps update <SUPERSET_APP_ID> \
  --env-vars "OPEX_POSTGRES_URL=postgresql://postgres.ublqmilcjtpnflofprkr:..."
```

### "Guest token API returns 401"

**Cause**: Superset admin credentials incorrect

**Fix**:
```bash
# Verify credentials in Superset container logs
doctl apps logs <SUPERSET_APP_ID> | grep "login"

# Update via App Platform console or doctl
```

## References

- Superset Repo: https://github.com/jgtolentino/superset
- Supabase Project: https://supabase.com/dashboard/project/ublqmilcjtpnflofprkr
- DigitalOcean App Platform: https://cloud.digitalocean.com/apps
- Scout Retail Intelligence: See `sql/V00*_scout_*.sql`

## Rollback Procedure

If Superset deployment fails after schema change:

```bash
# 1. Rollback odoo-ce schema (if needed)
cd /path/to/odoo-ce
psql "$OPEX_POSTGRES_URL" < backups/schema_$(date -v-1d +%Y%m%d).sql

# 2. Redeploy Superset to last known good deployment
cd /path/to/superset
doctl apps create-deployment <SUPERSET_APP_ID> \
  --deployment-id <LAST_GOOD_DEPLOYMENT_ID>

# 3. Verify rollback
curl -sf https://superset.insightpulseai.com/health
```

---

**Last Updated**: 2025-01-12
**Maintained By**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
