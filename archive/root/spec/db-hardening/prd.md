# DB Hardening PRD

## Problem
Odoo/OCA installs can fail on PostgreSQL due to function volatility constraints in index expressions (e.g., `unaccent()` not marked IMMUTABLE). When addressed only via `/docker-entrypoint-initdb.d`, fixes apply **only to new DBs** and regress into "drop DB to recover" workflows.

## Goals
1. **Eliminate DB-nuke workflows** by providing an idempotent, on-demand apply path for existing DBs.
2. Guarantee hardening artifacts remain present and correctly wired via **CI gates**.
3. Provide deterministic verification for:
   - required extensions (`pg_trgm`, `unaccent`)
   - immutable wrapper function presence and volatility

## Non-goals
- Broad database performance tuning or indexing strategy beyond the hardening fix.
- Managing Odoo module install order (handled by other specs).

## Users
- Platform engineers maintaining Odoo runtime environments
- CI/CD automation agents running preflights and gates

## Requirements

### Functional requirements
- **Init-time script** exists and is mounted for fresh DB initialization:
  - `db/init/10_unaccent_immutable.sql`
- **Apply-time script** exists for existing DBs:
  - `db/sql/apply_unaccent_immutable.sql`
- **Helper script** exists to apply + verify quickly:
  - `scripts/db/apply_unaccent_fix.sh [db_name]`
- **Compose wiring** mounts `./db/sql:/sql:ro` in the Postgres service.
- **gitignore policy** allows DB SQL artifacts to be tracked (exception rule).

### Verification requirements
- Verification query must confirm volatility:
  - `public.unaccent(text)` is IMMUTABLE (best-effort)
  - `public.unaccent_immutable(text)` is IMMUTABLE (required)

### CI requirements
- A workflow gate triggers on changes to:
  - `db/**`, `scripts/db/**`, `docker-compose.yml`, `.gitignore`
- Gate asserts:
  - artifacts exist
  - helper script executable
  - compose mount present and read-only
  - gitignore exception exists

## Success metrics
- Installing previously failing module (e.g., hr_recruitment) succeeds on an **existing** DB after running the apply script.
- CI blocks regressions that remove or de-wire hardening artifacts.

## Spec → Gate mapping

This section is the **enforcement contract**. Every requirement below must map to at least one deterministic gate.

| Requirement | Enforced by | Gate condition (deterministic check) |
|---|---|---|
| Init-time hardening script exists | `.github/workflows/db-hardening-gate.yml` | `test -f db/init/10_unaccent_immutable.sql` |
| Apply-time hardening script exists | `.github/workflows/db-hardening-gate.yml` | `test -f db/sql/apply_unaccent_immutable.sql` |
| Helper script exists | `.github/workflows/db-hardening-gate.yml` | `test -f scripts/db/apply_unaccent_fix.sh` |
| Helper script executable | `.github/workflows/db-hardening-gate.yml` | `test -x scripts/db/apply_unaccent_fix.sh` |
| Compose mount exposes SQL directory read-only | `.github/workflows/db-hardening-gate.yml` | `grep -qE '\./db/sql:/sql:ro' docker-compose.yml` |
| DB SQL artifacts remain tracked (gitignore exception) | `.github/workflows/db-hardening-gate.yml` | `grep -qE '^\!db/\*\*/\*\.sql' .gitignore` |
| On-demand apply path works on existing DBs | `scripts/db/apply_unaccent_fix.sh` | Applies `db/sql/apply_unaccent_immutable.sql` and exits non-zero on failure |
| Volatility verification is performed | `scripts/db/apply_unaccent_fix.sh` | Queries `pg_proc.provolatile` for `unaccent` + `unaccent_immutable` and validates expected values |
| Optional: fail-fast preflight in dev/staging | (existing preflight framework) | Must assert `unaccent` ext exists + `unaccent_immutable(text)` IMMUTABLE before module install |

## Rollback
- Re-running scripts is safe; rollback is typically unnecessary.
- If a managed PG disallows altering volatility of `public.unaccent(text)`, wrapper function remains the supported path.
