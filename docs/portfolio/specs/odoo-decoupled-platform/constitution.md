# Constitution: Odoo Decoupled Platform

> Non-negotiable rules and constraints for the decoupled Odoo + Supabase architecture.

## Core Principles

### 1. Auth Separation
- **App Auth is Supabase Auth** - Supabase Auth is the identity provider for all app users
- **Odoo uses service integration** - Odoo authenticates via service accounts, not user sessions
- **No Odoo-issued user tokens** - Odoo never directly issues authentication tokens to end users
- **JWT passthrough optional** - Advanced integrations may validate Supabase JWTs in Odoo middleware

### 2. Schema Ownership
- **Single source of truth per entity** - Each table/entity is owned by exactly one system (Odoo OR App)
- **No shared writes** - If Odoo owns an entity, app writes go through Odoo API; if App owns it, Odoo syncs read-only
- **Migrations are canonical** - All schema changes via `supabase/migrations/*.sql`
- **No implicit schema** - All schema must be explicit, versioned, and gated in CI

### 3. RLS as Authorization Layer
- **All exposed tables have RLS** - No table in API-exposed schemas without Row Level Security
- **Policies before code** - Authorization logic lives in Postgres RLS policies, not app code
- **Multi-tenant by default** - org_id/user_id isolation via RLS, not application-level filtering

### 4. Odoo as Domain Service
- **API contract first** - Odoo exposes stable API contracts (REST/JSON-RPC/GraphQL)
- **Event-driven sync** - Changes propagate via events/webhooks, not direct DB access
- **Worker mediation** - All Odoo↔App data flow goes through worker/edge functions
- **No direct client calls** - Browser/mobile never calls Odoo directly

### 5. CI Gates as Enforcement
- **Migrations gate** - CI fails if migrations don't exist or fail lint
- **RLS gate** - CI fails if exposed tables lack RLS
- **Secrets gate** - CI fails if service_role keys appear in client code
- **Spec gate** - CI fails if required spec files are missing

## Forbidden Patterns

1. ❌ Odoo as identity provider for app users
2. ❌ Direct browser→Odoo API calls
3. ❌ Shared write access to same table from Odoo and App
4. ❌ Service role key in client-side code
5. ❌ Tables exposed to API without RLS policies
6. ❌ Schema changes outside migration files
7. ❌ Auth logic in application code instead of RLS

## Required Artifacts

Every deployment must include:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Auth roles spec | `spec/auth/roles.yaml` | Role definitions + permissions |
| Schema spec | `spec/schema/entities.yaml` | Entity ownership mapping |
| API spec | `spec/api/openapi.yaml` | API contract documentation |
| RLS policies | `supabase/migrations/*_rls_*.sql` | Row-level security policies |
| Odoo bridge | `supabase/migrations/*_odoo_*.sql` | Odoo integration tables |
