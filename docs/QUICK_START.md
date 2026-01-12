# Quick Start: Multi-Tenant Platform Setup

## TL;DR

**TBWA = tenant, not special fork. Platform = shared infra.**

## Prerequisites

```bash
# Required environment variables in ~/.zshrc
export POSTGRES_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4"
export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDY0NDAzNSwiZXhwIjoyMDc2MjIwMDM1fQ.Rhdi18B5EuUeaSGfdB4rqZ6UoPSrJ9IbzkN_YboyvhU"
export ODOO_ADMIN_PASSWORD="your_secure_password"
export GH_PAT_SUPERSET="ghp_your_github_pat"
```

## Provision TBWA Tenant (One Command)

```bash
cd /path/to/odoo-ce
make provision-tbwa
```

**What This Does**:
1. Creates Supabase schema: `tbwa`
2. Creates Odoo database: `odoo_tbwa`
3. Installs base modules
4. Sets admin password
5. Prepares Superset workspace

## Architecture at a Glance

```
Repos:
- odoo-ce          → Platform + Tenant Engine
- tbwa-agency-databank → TBWA Data (Supabase migrations)
- superset         → BI Shell (reads all tenants)

Databases:
- odoo_platform    → Internal operations
- odoo_tbwa        → TBWA client operations

Supabase Schemas:
- public           → Platform metadata
- tbwa             → TBWA client data
- scout            → Shared retail intelligence

Superset Workspaces:
- platform         → Internal dashboards
- tbwa             → TBWA dashboards
- scout            → Cross-tenant analytics
```

## Cross-Repo Integration

**Schema changes in odoo-ce automatically trigger Superset rebuild**:

```bash
# 1. Push schema change to odoo-ce
git add supabase/migrations/V008__new_scout_view.sql
git commit -m "Add new Scout performance view"
git push origin main

# 2. GitHub Actions automatically:
#    - Detects schema change
#    - Triggers jgtolentino/superset repository_dispatch
#    - Superset rebuilds with new view available

# 3. Verify in Superset (30-60 seconds later)
curl -sf https://superset.insightpulseai.net/api/v1/dataset/ | \
  jq '.result[] | select(.table_name=="scout_performance_view")'
```

## Access Points

**Platform Odoo**: https://erp.insightpulseai.net
**TBWA Odoo**: https://tbwa.erp.insightpulseai.net (or filtered via `--db-filter`)
**Superset**: https://superset.insightpulseai.net
**Supabase Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz

## Tenant Onboarding (Any New Client)

```bash
# 1. Create tenant record in platform Odoo
#    Go to: Platform > Tenants > Create
#    Set: code=afc, db_name=odoo_afc, supabase_schema=afc

# 2. Provision tenant
make provision-tenant CODE=afc

# 3. Done! Tenant ready at https://afc.erp.insightpulseai.net
```

## Key Files

| File | Purpose |
|------|---------|
| `addons/ipai/ipai_tenant_core/` | Tenant metadata model |
| `scripts/provision_tenant.sh` | Automated tenant provisioning |
| `Makefile` | One-command operations |
| `docs/TENANT_ARCHITECTURE.md` | Complete architecture guide |
| `docs/SUPERSET_INTEGRATION.md` | Superset cross-repo integration |
| `.github/workflows/notify-superset.yml` | Auto-trigger Superset rebuild |

## Troubleshooting

**Connection test**:
```bash
make test-connection
```

**View logs**:
```bash
make odoo-logs        # Odoo
make superset-logs    # Superset
```

**Manual Superset trigger**:
```bash
make ci-notify-superset
```

## Next Steps

1. ✅ Install tenant-specific modules (e.g., `ipai_finance_ppm`)
2. ✅ Create Superset dashboards in tenant workspace
3. ✅ Configure Odoo `ipai_bi_superset_embed` for embedded dashboards
4. ✅ Test end-to-end data flow: Odoo → Supabase → Superset

---

**Questions?** See `docs/TENANT_ARCHITECTURE.md` for detailed documentation.
