# Supabase Platform Kit — ops-console Integration

> **Runbook for using the Supabase Management API as an embedded control plane
> inside `apps/ops-console`.**
>
> Scope: **internal org only** — we manage our own Supabase projects.
> Not customer-OAuth / multi-tenant SaaS.

---

## Architecture

```
Browser (ops-console UI)
  ↓  calls
/api/supabase-proxy/[...path]  (Next.js server route, server-only)
  ↓  forwards with Bearer token
https://api.supabase.com  (Supabase Management API)
```

The proxy at `apps/ops-console/app/api/supabase-proxy/[...path]/route.ts` already
handles all Methods (GET, POST, PUT, PATCH, DELETE) and injects the management API
token from `process.env.SUPABASE_MANAGEMENT_API_TOKEN`.

The typed client is `apps/ops-console/lib/management-api.ts` — it points all calls
to `/api/supabase-proxy`, so no Management API token ever reaches the browser.

---

## Token Security (non-negotiable)

| Rule | Detail |
|------|--------|
| `SUPABASE_MANAGEMENT_API_TOKEN` is **server-only** | Set in Vercel env (Production + Preview), never `NEXT_PUBLIC_*` |
| Never log the token | Proxy route must not echo it in error messages |
| Rotate quarterly | Or immediately on team member departure |
| Scope | Supabase dashboard → Account → Access tokens → create with minimal scope |

---

## Surfaces to expose in ops-console (`/platform` route)

The `/platform` page surfaces three tabs backed by Management API endpoints:

### Tab 1: Projects

| Surface | Management API endpoint | Notes |
|---------|------------------------|-------|
| List all projects | `GET /v1/projects` | Shows name, region, status |
| Project health | `GET /v1/projects/{ref}/health` | DB, auth, storage, edge function health |
| Create project | `POST /v1/projects` | Scoped to our org |

### Tab 2: Branches (DEV → Prod workflow)

| Surface | Management API endpoint | Notes |
|---------|------------------------|-------|
| List branches | `GET /v1/projects/{ref}/branches` | |
| Create DEV branch | `POST /v1/projects/{ref}/branches` | Ephemeral DB snapshot for staging |
| Run migrations on branch | `POST /v1/projects/{ref}/database/migrations` | Apply schema changes safely |
| Merge branch to prod | `POST /v1/branches/{branch-ref}/merge` | Commits schema + data to production |
| Delete branch | `DELETE /v1/branches/{branch-ref}` | After merge or abandon |

### Tab 3: Logs & Security

| Surface | Management API endpoint | Notes |
|---------|------------------------|-------|
| Query logs | `GET /v1/projects/{ref}/analytics/endpoints/logs.all` | Filter by service/level |
| Security advisor | `GET /v1/projects/{ref}/advisors/security` | Run before every prod deploy |
| PITR restore | `POST /v1/projects/{ref}/database/backups/restore-pitr` | Disaster recovery only — causes data loss for rows written after restore point |

---

## DEV Branch → Merge workflow (Supabase branching as "staging DB")

```
1. Developer opens PR with schema migration
2. CI creates Supabase DEV branch for the PR
   POST /v1/projects/{ref}/branches
3. CI runs the migration against the DEV branch
   POST /v1/projects/{ref}/database/migrations
4. App deploy (staging / Vercel Preview) targets the DEV branch DB
5. QA validates on Preview URL + DEV branch DB (full prod-data parity)
6. PR merged → CI merges DEV branch into production DB
   POST /v1/branches/{branch-ref}/merge
7. Branch deleted
   DELETE /v1/branches/{branch-ref}
```

This is the Supabase equivalent of Odoo.sh's "staging duplicates production DB" behavior.

---

## Security advisor gate

Run before every production Supabase change:

```
GET /v1/projects/{ref}/advisors/security
```

Returns a list of security findings (e.g., tables without RLS, exposed functions).
**Block prod deploy if severity ≥ HIGH is returned.**

The CI preflight should call this endpoint; ops-console surfaces the live report.

---

## What the existing proxy already handles

The proxy at `/api/supabase-proxy/[...path]` passes through any path segment to
`https://api.supabase.com`. All Platform Kit operations (projects, branches, logs,
security) are covered without new API routes.

To add a new surface: add a new client call in the component using the typed client
in `lib/management-api.ts`. The path segments map directly to Management API paths.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/ODOO_SH_EQUIVALENT_MATRIX.md` | Full capability comparison including Platform Kit |
| `docs/ops/SUPABASE_METRICS.md` | Prometheus metrics endpoint (separate from Management API) |
| `docs/ops/SUPABASE_VERCEL.md` | Env var sync between Supabase and Vercel |
| `docs/ops/SUPABASE_N8N.md` | DB Webhooks → n8n automation plane |
