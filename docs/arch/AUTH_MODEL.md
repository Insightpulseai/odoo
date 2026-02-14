# Authentication & Authorization Model

## Overview

**Single Identity Provider**: Supabase Auth manages all authentication
**Authorization**: PostgreSQL RLS policies + JWT claims
**Tenancy**: Every user belongs to exactly one tenant
**Roles**: `owner` > `admin` > `finance` > `ops` > `viewer`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Supabase Auth (Identity)                  │
│  • Email/password, magic link, OAuth (future)                │
│  • JWT tokens with custom claims (tenant_id, role)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL RLS (Authorization)              │
│  • Row-level security enforces tenant isolation              │
│  • Policies check JWT claims: tenant_id, role                │
│  • Service-role bypasses RLS (use with caution)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  Browser Apps    │  OCR Service  │  n8n       │  Superset   │
│  (anon + JWT)    │  (user JWT)   │  (service) │  (read-only)│
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Core Tables

```sql
-- Tenants: Root entity for multi-tenancy
app.tenants (
  id uuid primary key,
  slug text unique,                -- URL-safe identifier
  name text,
  settings jsonb,                  -- Features, limits, branding
  is_active boolean
)

-- Profiles: Maps auth.users to app context
app.profiles (
  user_id uuid primary key → auth.users(id),
  tenant_id uuid → app.tenants(id),
  role text,                       -- owner|admin|finance|ops|viewer
  display_name text,
  metadata jsonb
)

-- Service Tokens: Rotatable API keys
ops.service_tokens (
  id uuid primary key,
  name text,
  token_hash text,                 -- bcrypt, never plaintext
  tenant_id uuid → app.tenants(id),
  scopes text[],                   -- read:receipts, write:receipts, etc.
  is_active boolean
)

-- Audit Log: Security events
ops.audit_log (
  id uuid primary key,
  tenant_id uuid,
  user_id uuid,
  action text,                     -- profile.role_changed, user.invited
  resource_type text,
  resource_id text,
  metadata jsonb
)
```

## JWT Claims

After authentication, Supabase Auth injects custom claims via `custom_access_token_hook()`:

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "tenant_id": "tenant-uuid",
  "role": "admin",
  "tenant_slug": "acme-corp",
  "display_name": "John Doe"
}
```

### Helper Functions

```sql
-- Extract claims from JWT
app.current_tenant_id()  -- Returns tenant_id from JWT
app.current_role()       -- Returns role from JWT
app.current_user_id()    -- Returns sub (user_id) from JWT
app.is_tenant_active()   -- Checks if tenant is active
```

## Role Hierarchy

| Role | Permissions |
|------|------------|
| `owner` | Full control: manage users, update tenant settings, delete data |
| `admin` | Manage users (except owners), configure features |
| `finance` | Financial operations, BIR compliance, expense approvals |
| `ops` | Operational tasks, OCR processing, task management |
| `viewer` | Read-only access to tenant data |

### Role Enforcement

- **Database Level**: RLS policies check `app.current_role()`
- **Application Level**: UI gates and API route guards
- **Audit Trail**: All role changes logged to `ops.audit_log`

## RLS Policies

### Tenant Isolation

Every business table has `tenant_id` column and SELECT policy:

```sql
create policy {table}_select_tenant on {schema}.{table}
  for select
  using (tenant_id = app.current_tenant_id());
```

### Role-Based Updates

Only admins/owners can modify certain data:

```sql
create policy profiles_update_admin on app.profiles
  for update
  using (
    tenant_id = app.current_tenant_id()
    and app.current_role() in ('owner', 'admin')
  );
```

### Service Token Validation

Services using API keys must validate token and inject tenant context:

```sql
create or replace function ops.validate_service_token(token text)
returns table(tenant_id uuid, scopes text[])
language plpgsql
security definer
as $
  -- Verify token hash and return tenant_id + scopes
$;
```

## Service Integration Patterns

### Browser Apps (Scout, Control Room)

**Authentication**: `supabase-js` with anon key
**Authorization**: User JWT automatically sent with requests

```typescript
// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email,
  password,
});

// Access token contains tenant_id + role claims
const session = await supabase.auth.getSession();
console.log(session.user.user_metadata); // { tenant_id, role }

// Queries automatically scoped by RLS
const { data: receipts } = await supabase
  .from('bronze_receipts')
  .select('*');
// Returns only receipts from user's tenant
```

### OCR Service

**Authentication**: Accept user JWT from frontend
**Authorization**: Validate JWT and extract tenant_id

```typescript
// OCR API endpoint
async function processReceipt(req: Request) {
  // 1. Extract JWT from Authorization header
  const jwt = req.headers.get('Authorization')?.replace('Bearer ', '');

  // 2. Validate JWT with Supabase
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const { data: { user }, error } = await supabase.auth.getUser(jwt);

  if (error || !user) {
    return new Response('Unauthorized', { status: 401 });
  }

  // 3. Extract tenant_id from JWT claims
  const tenantId = user.user_metadata.tenant_id;

  // 4. Write to bronze_receipts with tenant_id
  const { data, error: insertError } = await supabase
    .from('bronze_receipts')
    .insert({
      tenant_id: tenantId,
      user_id: user.id,
      ocr_result: { /* ... */ },
    });

  return new Response(JSON.stringify(data));
}
```

### n8n Workflows

**Authentication**: Use service-role key (trusted internal service)
**Authorization**: Pass tenant_id explicitly to RPC functions

```json
{
  "nodes": [
    {
      "type": "Supabase",
      "parameters": {
        "operation": "executeFunction",
        "function": "process_bir_filing",
        "parameters": {
          "tenant_id": "{{ $json.tenant_id }}",
          "filing_type": "1601-C",
          "period": "2025-12"
        }
      }
    }
  ]
}
```

**RPC Function with Tenant Check**:

```sql
create or replace function app.process_bir_filing(
  p_tenant_id uuid,
  p_filing_type text,
  p_period text
)
returns jsonb
language plpgsql
security definer
as $
  -- Verify tenant_id is valid and active
  -- Execute filing logic
  -- Log audit event
$;
```

### Apache Superset

**Authentication**: Read-only PostgreSQL credentials
**Authorization**: Query gold-layer views with tenant_id filter

```sql
-- Create read-only role
create role superset_reader with login password 'secure-password';
grant usage on schema gold to superset_reader;
grant select on all tables in schema gold to superset_reader;

-- Gold views are pre-filtered by tenant_id
create view gold.expense_analytics as
select
  tenant_id,
  category,
  sum(amount) as total
from silver_expenses
group by tenant_id, category;

-- Superset queries must include tenant_id filter
select * from gold.expense_analytics
where tenant_id = 'current-tenant-uuid';
```

**Alternative**: Implement Superset SSO with JWT validation (more complex).

## Authentication Flows

### 1. Tenant Bootstrap (First-Time Setup)

**Endpoint**: `POST /functions/v1/auth-bootstrap`

**Request**:
```json
{
  "tenant": {
    "slug": "acme-corp",
    "name": "ACME Corporation",
    "settings": { "features": ["ocr", "bir_compliance"] }
  },
  "owner": {
    "email": "owner@acme.com",
    "password": "secure-password",
    "display_name": "Jane Doe"
  }
}
```

**Response**:
```json
{
  "success": true,
  "tenant": { "id": "...", "slug": "acme-corp" },
  "user": { "id": "...", "email": "owner@acme.com", "role": "owner" },
  "session": { "access_token": "...", "refresh_token": "..." }
}
```

**Implementation**:
1. Create `app.tenants` row
2. Create `auth.users` row via Supabase Admin API
3. Create `app.profiles` row with role="owner"
4. Generate session tokens
5. Log audit event

### 2. User Invitation

**Endpoint**: `POST /functions/v1/tenant-invite`

**Headers**: `Authorization: Bearer <admin_jwt>`

**Request**:
```json
{
  "email": "newuser@acme.com",
  "role": "finance",
  "display_name": "Bob Smith",
  "send_email": true
}
```

**Response**:
```json
{
  "success": true,
  "user": { "id": "...", "email": "newuser@acme.com", "role": "finance" },
  "invitation_sent": true
}
```

**Implementation**:
1. Verify inviter is admin/owner
2. Create `auth.users` row (or link existing user)
3. Create `app.profiles` row in inviter's tenant
4. Send invitation email via Supabase
5. Log audit event

### 3. Login

**Frontend**:
```typescript
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@acme.com',
  password: 'password',
});

// JWT now contains tenant_id + role claims
const session = data.session;
```

**Backend (JWT Validation)**:
```typescript
const { data: { user }, error } = await supabase.auth.getUser(jwt);

if (user) {
  const tenantId = user.user_metadata.tenant_id;
  const role = user.user_metadata.role;
  // Proceed with tenant-scoped operations
}
```

## Security Best Practices

### DO ✅

- **Always use RLS**: Enable on every table with business data
- **Validate tenant_id**: Extract from JWT, never trust client input
- **Rotate service tokens**: Use `ops.service_tokens`, not hardcoded keys
- **Audit sensitive operations**: Log role changes, data exports, deletions
- **Use service-role sparingly**: Only in trusted server environments
- **Enforce role hierarchy**: Check `app.current_role()` in policies
- **Soft delete**: Use `deleted_at` instead of hard deletes

### DON'T ❌

- **Never expose service-role key** to browser
- **Don't bypass RLS** without explicit security review
- **Don't trust client-provided tenant_id** - always use JWT claims
- **Don't hardcode tenant IDs** in application code
- **Don't create cross-tenant queries** without explicit permission
- **Don't use anon key** for server-to-server auth
- **Don't skip audit logging** for security-relevant events

## Verification Checklist

After deploying auth system, verify:

```bash
# 1. Apply migrations
psql "$POSTGRES_URL" -f supabase/migrations/5001_auth_foundation.sql
psql "$POSTGRES_URL" -f supabase/migrations/5002_auth_jwt_claims.sql
psql "$POSTGRES_URL" -f supabase/migrations/5003_rls_policies.sql

# 2. Enable custom access token hook
# Go to: Supabase Dashboard → Authentication → Hooks
# Enable: Custom Access Token
# Function: public.custom_access_token_hook

# 3. Create test tenant + owner
curl -X POST "$SUPABASE_URL/functions/v1/auth-bootstrap" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -d '{
    "tenant": {"slug": "test-tenant", "name": "Test Tenant"},
    "owner": {"email": "test@example.com", "password": "test1234"}
  }'

# 4. Login and verify JWT claims
curl -X POST "$SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -d '{"email": "test@example.com", "password": "test1234"}' \
  | jq '.user.user_metadata'

# Expected output:
# {
#   "tenant_id": "...",
#   "role": "owner",
#   "tenant_slug": "test-tenant"
# }

# 5. Test RLS policies
psql "$POSTGRES_URL" -c "
  set request.jwt.claims = '{\"tenant_id\": \"<tenant-uuid>\"}';
  select * from app.tenants;  -- Should return only current tenant
"

# 6. Test cross-tenant isolation
psql "$POSTGRES_URL" -c "
  set request.jwt.claims = '{\"tenant_id\": \"wrong-uuid\"}';
  select * from app.tenants;  -- Should return 0 rows
"
```

## Troubleshooting

### JWT Claims Not Appearing

**Symptom**: JWT doesn't contain `tenant_id` or `role`

**Solutions**:
1. Verify custom access token hook is enabled in Supabase Dashboard
2. Check `app.profiles` table has row for user
3. Check `custom_access_token_hook()` function exists and is callable
4. Verify function returns proper JSON structure

```sql
-- Test hook directly
select public.custom_access_token_hook(
  jsonb_build_object('user_id', '<user-uuid>')
);
```

### RLS Blocking All Queries

**Symptom**: All queries return 0 rows or permission denied

**Solutions**:
1. Verify JWT is being sent: `Authorization: Bearer <token>`
2. Check `request.jwt.claims` is set: `select current_setting('request.jwt.claims')`
3. Verify `tenant_id` in JWT matches `tenant_id` in table
4. Check RLS policies exist: `\d+ app.profiles`

```sql
-- Debug RLS policies
select * from pg_policies where tablename = 'profiles';
```

### Service Token Validation Failing

**Symptom**: API calls with service tokens return 401

**Solutions**:
1. Verify token is active: `select * from ops.service_tokens where is_active = true`
2. Check token hash matches: `select crypt('token', token_hash) = token_hash from ops.service_tokens`
3. Verify scopes are correct
4. Check token hasn't expired: `expires_at > now()`

## Future Enhancements

- **OAuth Providers**: Google, Microsoft, GitHub SSO
- **Multi-Factor Authentication**: TOTP, SMS, biometric
- **Session Management**: Active session listing, remote logout
- **API Rate Limiting**: Per-tenant rate limits in `ops.rate_limits`
- **Tenant Provisioning UI**: Self-service tenant creation
- **Advanced Audit**: Query audit logs via API, export to SIEM

## Related Documentation

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [JWT.io](https://jwt.io/) - JWT debugger
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Last Updated**: 2026-01-09
**Migration Files**: `5001_auth_foundation.sql`, `5002_auth_jwt_claims.sql`, `5003_rls_policies.sql`
**Edge Functions**: `auth-bootstrap`, `tenant-invite`
