# Supabase ↔ Vercel Integration Contract

## Purpose

Automatic environment-variable wiring from Supabase → Vercel project settings.
The integration keeps Vercel's env vars in sync with the Supabase project so you
don't hand-copy secrets. It does **not** handle monorepo build-skipping (that's
`ignoreCommand` in `vercel.json`) and does **not** manage database migrations.

## What the integration provides

- Injects Supabase env vars into the Vercel project automatically:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY` (optional — see security rules below)
- Available via the Vercel Marketplace (unified billing / auth).
- If **Supabase Branching** is enabled, preview deployments are intended to connect
  to matching Supabase preview branches via env var updates. **Verify this mapping
  in your setup** — branch ↔ preview alignment has real-world sharp edges.

## Required vars for ops-console

| Variable | Scope | Source |
|----------|-------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | Browser + server | Integration (auto) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Browser + server | Integration (auto) |
| `SUPABASE_SERVICE_ROLE_KEY` | **Server-only** | Integration or manual |
| `SUPABASE_MANAGEMENT_API_TOKEN` | **Server-only** | Manual (Keychain / Vault) |

## Local development workflow

```bash
# After linking the Vercel project (once):
cd apps/ops-console
vercel env pull .env.local    # pulls from linked Vercel project
# .env.local is in .gitignore — never commit it
```

Alternatively, use the Keychain-backed generator:

```bash
./scripts/secrets/gen-env-local.sh
```

## Security rules (non-negotiable)

1. **Anon key only in browser code.** `NEXT_PUBLIC_SUPABASE_ANON_KEY` is safe to
   expose — it is scoped by RLS policies.
2. **Service role never in client bundle.** `SUPABASE_SERVICE_ROLE_KEY` bypasses
   RLS. Use it only in `app/api/*` server routes, never in `"use client"` files.
3. **Management token never in Vercel.** `SUPABASE_MANAGEMENT_API_TOKEN` is what
   accesses the Supabase control plane; it cannot live in Supabase Vault (circular).
   Store it in macOS Keychain locally and GitHub Actions secrets in CI.

## What the integration does NOT solve

- **Monorepo build skipping**: use `ignoreCommand` in `vercel.json`.
- **Branching ↔ preview env var sync** can be non-obvious; verify per-branch
  mapping before relying on it.
- **Migrations**: Supabase migrations run via `supabase db push` in CI, not
  via the Vercel integration.

## Cross-references

- `docs/ops/VERCEL_MONOREPO.md` — monorepo wiring, skip-unaffected builds
- `docs/ops/SUPABASE_N8N.md` — automation plane (DB Webhooks → n8n)
- `scripts/secrets/gen-env-local.sh` — Keychain-backed env generator
- `scripts/secrets/keychain-setup.sh` — initial Keychain provisioning
