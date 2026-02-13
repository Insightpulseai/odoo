# Odoo + Supabase Monorepo (OCA-style) — SSOT Layout

This repo is structured so **Odoo + OCA add-ons** and **Supabase (migrations/functions)** can ship together,
with infra SSOT (Cloudflare DNS) versioned alongside.

Recommended high-level layout:

- addons/                 # Odoo add-ons mounted via addons-path generator
  - ipai/                 # your custom SSOT modules
- external-src/           # OCA repos (submodules/subtrees), enumerated by generator
- infra/
  - cloudflare/           # DNS SSOT (Terraform)
- sandbox/                # dev/stage compose
- supabase/
  - migrations/           # SQL migrations (SSOT)
  - functions/            # Edge Functions (SSOT)
- scripts/
  - cf/                   # terraform plan/apply/verify wrappers
