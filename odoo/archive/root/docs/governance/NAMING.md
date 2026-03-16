# Repository Naming Convention (Enforced)

This repo uses deterministic folder names to avoid collisions with Odoo terminology and to keep tooling predictable.

## Canonical folders
- `pkgs/` — workspace packages (shared libraries)
- `web/` — web applications (frontends)
- `docs/arch/` — architecture documentation
- `supabase/` — Supabase project directory (kept for CLI compatibility)
- `addons/ipai/` — IPAI custom modules (already well-namespaced with `ipai_*` prefix)

## Naming rationale
- `web/` over `apps/` - Avoids collision with Odoo "Apps" terminology (which means installable modules)
- `supabase/` kept - Supabase CLI tooling expects this directory structure
- `addons/ipai/` kept - Module names already use `ipai_*` prefix for namespacing

## Forbidden legacy references
CI blocks PRs that reintroduce these legacy patterns:
- `packages/` (use `pkgs/`)
- `apps/` (use `web/`)
- `docs/architecture/` (use `docs/arch/`)

## How to run the refactor
- Install config: copy `scripts/refactor/naming.env.example` → `scripts/refactor/naming.env`
- Execute: `scripts/refactor/run_naming_refactor.sh`
- Verify: `scripts/refactor/checks.sh`

