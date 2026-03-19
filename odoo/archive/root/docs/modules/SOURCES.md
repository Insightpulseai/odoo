# Catalog Sources

Authoritative source URLs for each catalog file.

---

## vercel.examples.catalog.json

**Source repo**: `github.com/vercel/next.js` — `/examples/` directory

Each example is a focused Next.js pattern (not a full app). These are the canonical reference
implementations maintained by the Vercel Next.js team.

**Browse**: https://github.com/vercel/next.js/tree/main/examples

**Scope**: Auth, storage, AI/streaming, multi-tenant, OTel, edge, monorepo patterns.

---

## vercel.templates.catalog.json

**Source**: `vercel.com/templates` (publicly browsable)

Templates are starter apps — larger than examples, meant to be cloned/forked.
We **harvest patterns** from templates, never fork them wholesale.

**Browse**: https://vercel.com/templates

**Scope**: Admin dashboards, SaaS starters, AI-enabled apps, enterprise Next.js baselines.

---

## supabase.examples.catalog.json

**Source repo**: `github.com/supabase/supabase` — `/examples/` directory

Supabase-maintained reference implementations for auth, storage, edge functions, realtime.

**Browse**: https://github.com/supabase/supabase/tree/master/examples

**Also see**: Agent playbooks in `/examples/prompts/` — useful for automating migrations
and other Supabase CLI operations.

**Scope**: Auth (SSR, MFA), storage upload/download, edge functions, realtime subscriptions.

---

## supabase.ui.catalog.json

**Source**: Two distinct Supabase products:

1. **Supabase UI Library** — `supabase.com/blog/supabase-ui-library`
   - Official component library built on shadcn/ui
   - Package: `@supabase/ui`
   - For: Admin and platform UI primitives

2. **Supabase UI Platform Kit** — `supabase.com/blog/supabase-ui-platform-kit`
   - Components for building platforms on top of Supabase Management API
   - For: ops-console `/platform` page (projects, branches, logs, security advisor)

**Governance**: See `docs/ops/SUPABASE_EXAMPLES_UI_ADOPTION.md`

---

## Out of scope (not catalogued here)

| Resource | Why out of scope |
|----------|-----------------|
| Community templates (not Vercel/Supabase official) | Unvetted quality; add to catalog individually if evaluated |
| OCA Odoo modules | Catalogued separately in `addons/oca/` and OCA search |
| DO App Platform examples | One-off references; see `docs/ops/DIGITALOCEAN_OBSERVABILITY.md` |
