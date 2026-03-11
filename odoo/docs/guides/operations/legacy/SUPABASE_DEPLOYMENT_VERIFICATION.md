# Supabase Deployment Verification Report

**Project:** spdtwktxdalcfigzeqrz
**Status:** Run `./scripts/verify_supabase_deploy.sh` to generate results

## Overview

This document tracks the verification status of the Supabase deployment for the InsightPulse AI platform. The verification script performs comprehensive checks on migrations, RLS, JWT hooks, and Edge Functions.

## Quick Start

```bash
# Set required environment variables
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="<your-anon-key>"
export SUPABASE_SERVICE_ROLE_KEY="<your-service-role-key>"
export POSTGRES_URL_NON_POOLING="<your-postgres-connection-string>"

# Run verification
./scripts/verify_supabase_deploy.sh
```

## Verification Categories

### A) Migrations Verification

| Check | Description |
|-------|-------------|
| `migrations_table_exists` | Verifies `supabase_migrations.schema_migrations` table exists |
| `migrations_applied` | Counts and lists all applied migrations |
| `key_migrations` | Confirms presence of security-critical migrations |
| `repo_migrations_match` | Compares repo migrations with applied |

**Key Migrations:**
- `5001_auth_foundation.sql` - Core schemas (app, ops), tables (tenants, profiles, service_tokens, audit_log)
- `5002_auth_jwt_claims.sql` - JWT hook and helper functions
- `5003_rls_policies.sql` - RLS policies for tenant isolation

### B) Auth + JWT Hook Verification

| Check | Description |
|-------|-------------|
| `schemas_exist` | Confirms app, ops, public schemas exist |
| `jwt_hook_exists` | Verifies `public.custom_access_token_hook` function |
| `helper_functions` | Checks app.current_user_id(), app.current_tenant_id(), app.current_role() |

**JWT Hook Flow:**
1. User authenticates via Supabase Auth
2. Supabase calls `custom_access_token_hook()`
3. Function looks up user profile and adds claims
4. JWT now contains: `{ sub, email, tenant_id, role, ... }`
5. RLS policies extract claims via `current_setting('request.jwt.claims')`

### C) RLS Enforcement Verification

| Check | Description |
|-------|-------------|
| `rls_enabled` | Confirms RLS enabled on app.tenants, app.profiles, ops.service_tokens, ops.audit_log |
| `rls_policies_exist` | Counts policies on each table |
| `rls_policies_list` | Enumerates all policies |

**Security Model:**
- Tenant Isolation: Users can only access data from their tenant
- Role Hierarchy: owner > admin > finance > ops > viewer
- Service Authentication: service-role bypasses RLS (use carefully)

### D) Edge Functions Verification

| Check | Description |
|-------|-------------|
| `edge_functions_deployed` | Lists all functions in repo |
| `required_functions` | Confirms auth-bootstrap and tenant-invite exist |
| `auth_bootstrap_cors` | Tests CORS preflight response |
| `auth_bootstrap_validation` | Tests input validation (expects 400) |
| `tenant_invite_auth` | Tests auth requirement (expects 401 without auth) |

**Required Functions:**
- `auth-bootstrap` - Creates new tenant with owner
- `tenant-invite` - Invites users to existing tenant

### E) Storage & API Verification

| Check | Description |
|-------|-------------|
| `storage_buckets` | Lists configured storage buckets |
| `api_app_schema` | Verifies app schema exposed via REST |
| `api_ops_schema` | Verifies ops schema NOT exposed via REST |
| `seed_tenants` | Checks for bootstrap tenant data |

## Schema Exposure Policy

| Schema | PostgREST | Reason |
|--------|-----------|--------|
| `public` | RPC only | Helper functions, hooks |
| `app` | Yes | Tenant/profile data with RLS |
| `gold` | Yes | Analytics-ready, safe views |
| `silver` | Views only | Cleaned data (optional) |
| `ops` | **No** | Tokens, audit, internals |
| `bronze` | **No** | Raw uploads, payloads |
| `auth` | **No** | Supabase-managed |

Configure in `supabase/config.toml`:
```toml
[api]
schemas = ["public", "app", "gold"]
extra_search_path = ["public", "app", "gold"]
```

## Output Files

| File | Description |
|------|-------------|
| `docs/ops/SUPABASE_DEPLOYMENT_VERIFICATION.md` | Human-readable report (this file) |
| `artifacts/supabase_verify/report.json` | Machine-readable JSON report |

## Remediation Commands

### Apply Missing Migrations

```bash
# Using Supabase CLI
supabase db push

# Or manually apply specific migration
psql "$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5001_auth_foundation.sql
psql "$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5002_auth_jwt_claims.sql
psql "$POSTGRES_URL_NON_POOLING" -f supabase/migrations/5003_rls_policies.sql
```

### Deploy Edge Functions

```bash
# Deploy all functions
supabase functions deploy

# Deploy specific functions
supabase functions deploy auth-bootstrap
supabase functions deploy tenant-invite
```

### Enable Custom Access Token Hook

1. Go to Supabase Dashboard > Authentication > Hooks
2. Enable "Custom Access Token Hook"
3. Select function: `public.custom_access_token_hook`

### Verify RLS Manually

```sql
-- Check RLS status
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname IN ('app', 'ops');

-- Enable RLS if needed
ALTER TABLE app.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.service_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.audit_log ENABLE ROW LEVEL SECURITY;

-- List all policies
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname IN ('app', 'ops')
ORDER BY schemaname, tablename;
```

## Verification Tests (Manual)

### Test JWT Claims

```sql
-- After login, verify JWT claims:
SELECT
  app.current_user_id() as user_id,
  app.current_tenant_id() as tenant_id,
  app.current_role() as role,
  app.is_tenant_active() as tenant_active;
```

### Test Tenant Isolation

```sql
-- Should only return current user's tenant
SELECT * FROM app.tenants;

-- Should only return profiles from current user's tenant
SELECT * FROM app.profiles;
```

### Test Role Escalation Prevention

```sql
-- As a 'viewer', this should fail:
UPDATE app.profiles SET role = 'admin' WHERE user_id = auth.uid();
```

---

*Generated by verify_supabase_deploy.sh - Run the script to update with actual results*
