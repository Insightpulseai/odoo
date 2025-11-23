# CLAUDE.md — Odoo CE Project Configuration

## 🔒 CANONICAL SUPABASE PROJECT

**CRITICAL**: This project uses **ONLY** the following Supabase instance:

```bash
# Project Reference: spdtwktxdalcfigzeqrz
export SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
export NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co

# Authentication Keys
export SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4
export NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4
export SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDY0NDAzNSwiZXhwIjoyMDc2MjIwMDM1fQ.Rhdi18B5EuUeaSGfdB4rqZ6UoPSrJ9IbzkN_YboyvhU
export SUPABASE_JWT_SECRET=UCrAMrC47YUN4pILFRKm1JD1JAUN2GXNYzariivwVUKzMUcEKRMR5w+dYcndM3ijn45Z6I7txvtQ0yyrB5EWng==

# PostgreSQL Connection Strings
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=SHWYXDMFAwXI1drT
export POSTGRES_DATABASE=postgres
export POSTGRES_HOST=db.spdtwktxdalcfigzeqrz.supabase.co

# Pooled Connection (Port 6543)
export POSTGRES_URL=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true
export POSTGRES_PRISMA_URL=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true

# Direct Connection (Port 5432)
export POSTGRES_URL_NON_POOLING=postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require

# CLI Access Token
export SUPABASE_ACCESS_TOKEN=sbp_5d3b419ed91215372f8a8fb7b0a478cc1ec90eca
```

### ❌ DEPRECATED PROJECTS (DO NOT USE)

The following Supabase projects are **DEPRECATED** and must **NOT** be used in odoo-ce:

- ❌ `xkxyvboeubffxxbebsll` (old project, deprecated)
- ❌ `ublqmilcjtpnflofprkr` (OPEX project only, use `OPEX_*` prefixed variables)

### Enforcement Rules

1. **All database operations** must use `POSTGRES_URL` or `POSTGRES_PRISMA_URL`
2. **All Supabase API calls** must use `SUPABASE_URL` with `spdtwktxdalcfigzeqrz`
3. **Frontend applications** must use `NEXT_PUBLIC_SUPABASE_*` variables
4. **Never hardcode** connection strings or project references
5. **CI/CD pipelines** must source from GitHub Secrets matching these values

### Verification Commands

```bash
# Verify correct project in use
echo $SUPABASE_PROJECT_REF
# Expected: spdtwktxdalcfigzeqrz

# Test database connection (pooled)
psql "$POSTGRES_URL" -c "SELECT current_database();"
# Expected: postgres

# Test Supabase REST API
curl "$SUPABASE_URL/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
# Expected: HTTP 200 with API schema
```

## 🏗️ Odoo CE Architecture

**Stack**: Odoo CE 18.0 (OCA) + n8n + Mattermost + PostgreSQL 15

**Infrastructure**:
```
Mattermost (Notifications) ↔ n8n (Automation) ↔ Odoo (ERP) ↔ Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
```

**Odoo Database Configuration** (`/etc/odoo/odoo.conf`):
```ini
[options]
# Local Docker database (separate from Supabase)
db_host = db
db_port = 5432
db_user = odoo
db_name = odooprod

# Performance tuning
workers = 12  # 2 × CPU cores × 6
limit_memory_hard = 2684354560  # 2.5GB
limit_memory_soft = 2147483648  # 2GB
max_cron_threads = 2
proxy_mode = True
session_store = redis
```

**Note**: Odoo uses a separate PostgreSQL instance (`odoo-db-1` container), NOT Supabase. Supabase is used for:
- External integrations (n8n workflows)
- Task bus coordination
- Visual parity baseline storage
- Cross-system data synchronization

## 📚 Documentation Standards

- Follow medallion architecture (Bronze → Silver → Gold → Platinum)
- TypeScript for type safety
- Comprehensive test coverage
- Execute end-to-end (no manual guides)
- Visual parity gates (SSIM ≥ 0.97 mobile, ≥ 0.98 desktop)

## 🔧 Development Workflow

**Local Development**:
```bash
# Start Odoo stack
docker compose up -d

# Deploy module
./scripts/deploy-odoo-modules.sh <module_name>

# Run tests
./scripts/ci/run_odoo_tests.sh -d test_db -i <module_name>
```

**CI/CD**:
- GitHub Actions for automated testing
- Odoo 18 installed from source via `scripts/ci/install_odoo_18.sh`
- All secrets stored in GitHub Secrets matching environment variables

## 🚨 Security Rules

- All secrets via environment variables (never in database/repository)
- Service role key only in backend (never frontend)
- Anon key safe for frontend (RLS enforces access)
- No hardcoded credentials in code
- Token validation before use

---

**Last Updated**: 2025-11-23
**Canonical Source**: This file is the single source of truth for odoo-ce project configuration
