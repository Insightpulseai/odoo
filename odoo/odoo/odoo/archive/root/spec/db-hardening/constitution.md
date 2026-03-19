# DB HARDENING CONSTITUTION (Spec-Driven)

## 1) Non-negotiables
- **No manual UI steps.** All behavior is reproducible via repo artifacts, scripts, and CI gates.
- **Idempotent by default.** All DB hardening routines must be safe to re-run.
- **Two-path enforcement:**
  1) **Init-time** (fresh DB bootstrap via container init hooks)
  2) **Apply-time** (existing DBs via on-demand scripts)
- **Evidence-first:** any hardening change must include:
  - verification query output (or deterministic check) documented in `db/README.md`
  - CI validation for artifact presence and wiring

## 2) Scope boundaries
- This bundle governs **PostgreSQL hardening primitives** required for Odoo + OCA installs.
- Out of scope: application feature schema (models/tables) and business data seeding.

## 3) Compatibility requirements
- Must support: `odoo_dev`, `odoo_staging`, `odoo_prod`.
- Must not require DB drop/recreate for remediation.

## 4) Security & safety
- Scripts must never echo secrets.
- Default mounts for SQL assets are **read-only**.
- If privileges are insufficient (managed PG), scripts must:
  - apply what they can (e.g., wrapper function)
  - clearly report what could not be applied (e.g., ALTER FUNCTION) without corrupting state.

## 5) CI gating
- PRs that touch DB hardening paths must trigger gates that validate:
  - artifact presence
  - compose wiring (mounts)
  - script executability
  - gitignore exceptions for tracked SQL
