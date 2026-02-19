# Supabase SDK vs Supabase Platform Kit (Do Not Confuse)

## Overview

This document clarifies the critical distinction between Supabase's **data plane SDK** and **control plane Platform Kit**, as they serve completely different purposes and have different installation methods.

## Supabase Client SDK (Data Plane)

**Purpose**: Application data access (Auth/RLS/DB/Storage/Realtime) for end-user applications.

**Use when your app needs to:**
- Authenticate users (Supabase Auth)
- Query Postgres with RLS enforcement
- Access Storage buckets
- Use Realtime subscriptions
- Perform database CRUD operations

**Packages:**
- `@supabase/supabase-js` - Core client library
- `@supabase/ssr` - Next.js server-side helpers (recommended for SSR/RSC)

**Installation:**
```bash
npm install @supabase/supabase-js @supabase/ssr
```

**Typical usage:**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Query with RLS enforcement
const { data, error } = await supabase
  .from('ops.runs')
  .select('*')
  .eq('status', 'running')
```

---

## Supabase Platform Kit (Control Plane)

**Purpose**: Embedded Supabase management UI for platform/ops consoles. Provides project management capabilities via Management API proxy.

**Use when your app needs to:**
- Manage Supabase projects programmatically (DB/Auth/Storage/Users/Secrets/Logs/Perf)
- Embed the "Supabase Manager" dialog/drawer UI
- Proxy Management API calls server-side (token never exposed to client)
- Provide ops/admin interface for Supabase project management

**Installation method:**
Platform Kit is installed via **shadcn's generator workflow**, NOT npm install:

```bash
# Navigate to your canonical Platform Kit host app
cd web/ai-control-plane/

# Install Platform Kit via shadcn generator
npx shadcn@latest add @supabase/platform-kit-nextjs
```

**What gets installed:**
- UI components (dialog/drawer manager interface)
- Hooks and utilities for Management API interactions
- Server routes for **Management API proxy**: `app/api/supabase-proxy/[...path]/route.ts`
- Optional AI SQL route: `app/api/ai/sql/route.ts`

**Typical usage:**
```typescript
// Platform Kit provides embedded Supabase manager UI
import { SupabaseManagerDialog } from '@/components/supabase/manager'

export function OpsConsole() {
  return (
    <div>
      <h1>Platform Operations</h1>
      <SupabaseManagerDialog projectRef={projectRef} />
    </div>
  )
}
```

---

## Key Differences

| Aspect | Client SDK | Platform Kit |
|--------|-----------|--------------|
| **Purpose** | Data plane (app data access) | Control plane (project management) |
| **Installation** | `npm install @supabase/supabase-js` | `npx shadcn@latest add @supabase/platform-kit-nextjs` |
| **API Surface** | Supabase Database/Auth/Storage APIs | Supabase Management API |
| **Token Type** | Anon key (client) or Service Role (server) | Management API token (server-only) |
| **Target Apps** | End-user portals, apps, dashboards | Ops/admin consoles only |
| **Security Model** | RLS-enforced queries | Management token never in client |
| **SSOT/SOR Alignment** | SSOT data access (ops.*, mdm.*, ai.*) | SSOT management (project config) |

---

## Canonical Host App for Platform Kit

**Declared canonical host:** `web/ai-control-plane/`

**Policy:**
- Platform Kit MUST be installed in exactly one Next.js app
- This app serves as the ops/platform console for Supabase project management
- Do NOT install Platform Kit into end-user portals or non-ops apps
- Do NOT confuse Platform Kit install (shadcn generator) with Supabase Client SDK install

**Rationale:**
- Platform Kit is *management* (SSOT control plane), not end-user functionality
- Keeps Management API token surface contained and auditable
- Avoids accidental spread into unrelated web apps
- Follows principle of least privilege for control-plane operations

---

## Security

### Client SDK Security
- Use anon key for client-side operations (RLS-enforced)
- Use service role key ONLY server-side for elevated operations
- All service role operations MUST emit `ops.runs/run_events/artifacts` for audit trail
- Never expose service role key to client

### Platform Kit Security
- Management API token is **server-only** (never sent to client)
- Proxy routes MUST enforce `projectRef` permissions (deny-by-default)
- All Management API operations should be logged in `ops.run_events`
- Access to Platform Kit UI should require elevated authentication (admin/ops role)

**Example proxy route security:**
```typescript
// app/api/supabase-proxy/[...path]/route.ts
export async function POST(req: Request) {
  const session = await getServerSession()

  // Enforce admin role
  if (!session?.user?.role === 'admin') {
    return new Response('Unauthorized', { status: 401 })
  }

  // Enforce projectRef whitelist
  const { projectRef } = await req.json()
  if (!ALLOWED_PROJECT_REFS.includes(projectRef)) {
    return new Response('Forbidden project', { status: 403 })
  }

  // Proxy to Management API with server-side token
  // ... proxy logic ...
}
```

---

## Installation Checklist

### For Client SDK (Data Plane)
- [ ] Install `@supabase/supabase-js` and `@supabase/ssr`
- [ ] Set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` env vars
- [ ] Initialize client with `createClient()` or `createBrowserClient()`
- [ ] Implement RLS policies in Supabase for all tables
- [ ] Document which schemas/tables are accessed
- [ ] Follow SSOT/SOR boundary (no writes to Odoo-owned domains)

### For Platform Kit (Control Plane)
- [ ] Navigate to canonical host app: `cd web/ai-control-plane/`
- [ ] Run `npx shadcn@latest add @supabase/platform-kit-nextjs`
- [ ] Set `SUPABASE_MANAGEMENT_API_TOKEN` env var (server-only)
- [ ] Implement proxy route security (role check + projectRef whitelist)
- [ ] Add audit logging for all Management API operations
- [ ] Restrict UI access to admin/ops roles only
- [ ] Document management operations in `ops.run_events`

---

## Common Mistakes to Avoid

❌ **Using `npm install` for Platform Kit**
- Platform Kit is NOT installed via `npm install @supabase/platform-kit-nextjs`
- Use `npx shadcn@latest add @supabase/platform-kit-nextjs` instead

❌ **Confusing shadcn's role**
- shadcn is used as a **distribution/installation mechanism** for Platform Kit
- It's not "installing a Supabase client" - it's scaffolding management UI + proxy routes

❌ **Installing Platform Kit in multiple apps**
- Platform Kit should live in exactly ONE canonical ops console app
- Installing in multiple apps spreads Management API token surface

❌ **Exposing Management API token to client**
- Management API token MUST remain server-side only
- Use proxy routes to mediate all Management API calls

❌ **Using Platform Kit for end-user data access**
- Platform Kit is for project management, not app data access
- Use Client SDK (`@supabase/supabase-js`) for end-user features

---

## References

- [Supabase Client SDK Docs](https://supabase.com/docs/reference/javascript)
- [Supabase Management API](https://supabase.com/docs/reference/api)
- [Platform Kit Repository](https://github.com/supabase/platform-kit)
- Canonical host app: `web/ai-control-plane/`
- SSOT/SOR policy: `spec/odoo-ee-parity-seed/constitution.md`
