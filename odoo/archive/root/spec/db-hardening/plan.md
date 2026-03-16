# DB Hardening Plan

## Phase 0 — Baseline inventory
- Confirm current artifacts exist:
  - `db/init/10_unaccent_immutable.sql`
  - `db/sql/apply_unaccent_immutable.sql`
  - `scripts/db/apply_unaccent_fix.sh`
  - compose mount `./db/sql:/sql:ro`
  - `.gitignore` exception for `db/**/*.sql`

## Phase 1 — CI gating
- Add workflow: `.github/workflows/db-hardening-gate.yml`
- Enforce:
  - artifact presence
  - wiring checks (compose + gitignore)
  - executable bit on helper script

## Phase 2 — Runtime/dev preflight (optional but recommended)
- Add an idempotent preflight check (warn or fail-fast depending on env):
  - confirms `unaccent` extension exists
  - confirms `public.unaccent_immutable(text)` exists and is IMMUTABLE
- Integrate into existing repo preflight framework (do not create a new framework).

## Phase 3 — Documentation hardening
- Ensure `db/README.md` includes:
  - init vs apply model
  - how to verify volatility
  - troubleshooting for privilege errors

## Evidence
- Store verification outputs or deterministic checks in docs/evidence if the repo policy requires it.
