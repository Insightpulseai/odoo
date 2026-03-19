# Constitution — Odoo.sh × Supabase Platform Kit

**Purpose**: Define non-negotiable rules for the OdooOps Console implementation.

---

## Non-Negotiables

### Architecture

1. **App Router Only**: Next.js App Router architecture with Server Components as default
2. **Client Boundary Enforcement**: ALL interactivity behind `"use client"` boundaries ([Next.js docs][1])
3. **No styled-jsx in Server Modules**: Use Tailwind CSS or CSS Modules only
4. **Async Params**: All dynamic route params/searchParams must be awaited `Promise<{ ... }>`

[1]: https://nextjs.org/learn/dashboard-app/adding-search-and-pagination

### Security

1. **Zero Client Secrets**: Supabase Management API token NEVER exposed to client
2. **Server-Side Proxy**: All Platform Kit operations via `/api/supabase-proxy/[...path]`
3. **AuthZ on Every Request**: Tenant membership validation before proxy forwarding
4. **Audit Trail**: Every privileged action logged to `ops.audit_log`

### Data Integrity

1. **Deterministic Environments**: `dev / staging / prod` with identical schema
2. **RLS Enforcement**: All `ops.*` tables deny cross-tenant access
3. **Immutable Audit**: `ops.audit_log` is append-only, admin read-all
4. **Migration-First**: Schema changes via Supabase migrations only

### Platform Constraints (Odoo.sh-Class)

1. **CPU/Memory Fairness**: Workers may recycle; no long-lived processes
2. **No Daemonized Services**: Disallow sidecars/background daemons
3. **Scheduled Actions Timeboxed**: Auto-disable with operator notification
4. **System Packages Immutable**: No apt/OS package installs at runtime
5. **SMTP Port Restrictions**: Only 465/587 for external SMTP (port 25 blocked)
6. **No PostgreSQL Extensions**: Treat DB as plain Postgres
7. **Connection Durability**: No long-lived external connections
8. **DB Object Cap**: ≤10k total tables+sequences

---

## Quality Gates

### CI Requirements (All Must Pass)

1. ✅ `pnpm lint` — Zero linting errors
2. ✅ `pnpm typecheck` — Zero TypeScript errors
3. ✅ `pnpm build` — Clean Next.js production build
4. ✅ RLS tests — Cross-tenant denial verified
5. ✅ Proxy authZ tests — Unauthorized requests rejected

### Code Standards

1. **Type Safety**: Strict TypeScript, no `any` without justification
2. **Server/Client Separation**: Clear boundaries, no prop drilling of handlers
3. **Accessibility**: WCAG 2.1 AA minimum for all UI components
4. **Performance**: <3s load on 3G, <500ms API responses

---

## Deployment

### Build Verification

```bash
# Required green before merge
pnpm -r typecheck && pnpm -r build
```

### Environment Parity

- **Dev**: Local + DevContainer, matches staging schema
- **Staging**: DO App Platform, pre-prod validation
- **Prod**: DO App Platform, blue-green deploys only

---

**Effective Date**: 2026-02-15
**Last Updated**: 2026-02-15
**Status**: Active
