# Constitution — Odoo 19 EE Surface Parity (Goal-Based)

## Purpose

Deliver **Enterprise-only surface parity** for **Odoo 19** using:

- Odoo Community + OCA modules (functional parity where applicable)
- Minimal custom glue (thin `ipai_*` only when unavoidable)
- External services (Supabase/Vercel/GitHub/etc.) for platform-level EE surfaces

This program explicitly **does not** treat “missing EE modules” as the goal. The goal is **operational and product outcomes**.

## Principles

1. **Goal-Based Parity**
   - Parity is measured by outcomes (e.g., “safe upgrades”, “CI builds”, “support workflow”), not by checking if an EE addon folder exists.
2. **OCA-First**
   - If a functional area exists in EE, assume an OCA-equivalent exists or can be composed from OCA building blocks.
3. **Thin Glue Only**
   - Custom code must be minimal, auditable, and replaceable. Prefer config + scripts + pipelines over bespoke addons.
4. **Deterministic + Reproducible**
   - All parity checks must be runnable in CI and produce machine-readable output.
5. **Surface Catalog SSOT**
   - The authoritative list of EE-only surfaces and what we care about is `docs/parity/EE_SURFACE_CATALOG.yaml`.
6. **Explicit Scope Control**
   - Each surface must declare: in-scope/out-of-scope, acceptance tests, and implementation strategy.

## Non-Goals

- Re-implementing proprietary Odoo services as 1:1 clones.
- UI-perfect cloning of EE-only UX where a workflow-equivalent is sufficient.
- Treating “module present” as proof of parity.

## Definition of Done

- Parity goals declared in `config/parity/PARITY_GOALS.yaml`
- `scripts/parity/parity_check.py` produces a pass/fail report and score
- CI gate can fail PRs if score falls below threshold or if Tier-0 goals regress
