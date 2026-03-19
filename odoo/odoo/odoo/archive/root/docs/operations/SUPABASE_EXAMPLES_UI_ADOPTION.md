# Supabase Examples + UI Library — Adoption Contract

> How we use Supabase reference examples, the Supabase UI Library,
> and Supabase UI Platform Kit in the ops-console and this monorepo.

---

## Three distinct things

| Resource | What it is | How we use it |
|----------|-----------|---------------|
| **Supabase examples** (`supabase/supabase/examples/*`) | Reference apps demonstrating auth, storage, edge functions, realtime | Cherry-pick minimal pattern slices — never fork full apps |
| **Supabase UI Library** | Official component library built on top of shadcn/ui | Default admin UI primitives for ops-console |
| **Supabase UI Platform Kit** | UI components specifically for Management API surfaces (projects, branches, logs, security advisor) | Only used for platform control-plane pages in ops-console |

---

## Supabase Examples — Harvest Rules

### What to harvest

| Pattern category | Where it lives in `supabase/supabase/examples/` | Minimal slice to copy |
|-----------------|------------------------------------------------|-----------------------|
| Next.js + Auth (SSR) | `with-nextjs/` | `middleware.ts`, `lib/supabase/server.ts`, `lib/supabase/client.ts` |
| Storage upload/download | `storage/` | `lib/storage.ts`, upload route handler |
| Edge Functions invocation | `edge-functions/` | `lib/edge-functions.ts`, fetch wrapper |
| Realtime subscriptions | `realtime/` | channel setup hook, cleanup pattern |
| Auth with MFA | `with-mfa/` | MFA enrollment flow, TOTP verification |

### Rules

1. **Lift minimal slices** — copy only the files that implement the specific pattern
2. **No full-template forks** — never copy an entire example app into ops-console
3. **No style overrides** — examples may have global CSS; strip it; use our token system
4. **Update the tracking table** below when you adopt a new pattern

### Currently adopted from Supabase examples

| Pattern | Source example | File(s) in ops-console | Adopted |
|---------|---------------|------------------------|---------|
| Supabase SSR session | `nextjs-with-supabase` | `lib/supabase/server.ts`, `middleware.ts` | 2026-02 |

---

## Supabase UI Library — Component Rules

Supabase UI Library is the **default admin UI component set** for ops-console because:
- Built on top of shadcn/ui (same primitives already in use)
- Matches Supabase's visual language for platform admin surfaces
- Maintained by Supabase for long-term compatibility

### Allowed components (current)

These components from Supabase UI are approved for use in ops-console:

| Component | Use case |
|-----------|---------|
| `<DataTable>` | Tabular data (projects, branches, logs) |
| `<StatusBadge>` | Resource health indicators |
| `<AlertBanner>` | Platform-level warnings |
| `<CodeBlock>` | Connection strings, schema output |
| `<CopyButton>` | Copy-to-clipboard patterns |

### How to add a Supabase UI component

1. Check that the component is in `@supabase/ui` (not just in their internal dashboard)
2. Add a wrapper in `apps/ops-console/components/supabase-ui/` — never import directly into pages
3. Document it in `apps/ops-console/components/supabase-ui/README.md`
4. Add to the "Allowed components" table above

---

## Supabase UI Platform Kit — Platform Surface Rules

Platform Kit components map directly to Management API surfaces. Use **only** for:

| Platform Kit component | Maps to Management API endpoint | ops-console page |
|------------------------|--------------------------------|------------------|
| Project health card | `GET /v1/projects/{ref}/health` | `/platform` |
| Branch list | `GET /v1/projects/{ref}/branches` | `/platform` |
| Log query panel | `POST /v1/projects/{ref}/analytics/endpoints/logs.all` | `/platform` |
| Security advisor | `GET /v1/projects/{ref}/advisors/security` | `/platform` |

**Do not** use Platform Kit components for non-Management-API pages (e.g., product feature UI,
marketing content, regular data tables).

---

## Security rules (applies to all three)

| Rule | Details |
|------|---------|
| `service_role` key never in browser | Only used in server routes / Edge Functions |
| `anon` key is the browser limit | `NEXT_PUBLIC_SUPABASE_ANON_KEY` is safe to expose |
| Management API token server-only | `SUPABASE_MANAGEMENT_API_TOKEN` — no `NEXT_PUBLIC_` prefix ever |
| RLS must be on | All tables accessed from client must have RLS policies |
| Auth tokens in `httpOnly` cookies | Never store Supabase JWT in `localStorage` |

---

## Component registry (where Supabase UI wrappers live)

```
apps/ops-console/
└── components/
    └── supabase-ui/
        ├── README.md          ← naming conventions + import guide
        ├── DataTable.tsx      ← wrapper around @supabase/ui DataTable
        ├── StatusBadge.tsx    ← wrapper around @supabase/ui StatusBadge
        └── index.ts           ← barrel export
```

All Supabase UI and Platform Kit wrappers live in `components/supabase-ui/`.
Import from the barrel: `import { DataTable } from '@/components/supabase-ui'`

---

## Related

| File | Purpose |
|------|---------|
| `apps/ops-console/components/supabase-ui/README.md` | Component wrappers: naming + imports |
| `docs/ops/SUPABASE_PLATFORM_KIT.md` | Management API runbook |
| `docs/ops/VERCEL_MONOREPO.md` | ops-console Vercel project |
| `docs/ops/VERCEL_TEMPLATES_EXAMPLES.md` | Vercel templates adoption rules |
