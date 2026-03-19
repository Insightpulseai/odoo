# DB Hardening Tasks

## P0 — Contract & artifacts
- [x] Ensure `db/init/10_unaccent_immutable.sql` exists and is correct.
- [x] Ensure `db/sql/apply_unaccent_immutable.sql` exists and matches init behavior.
- [x] Ensure `scripts/db/apply_unaccent_fix.sh` exists, is executable, and verifies volatility.
- [x] Ensure Postgres service mounts `./db/sql:/sql:ro`.
- [x] Ensure `.gitignore` permits tracking `db/**/*.sql`.

## P0 — CI gate
- [x] Add `.github/workflows/db-hardening-gate.yml` with path filters.
- [x] Gate asserts:
  - required files exist
  - helper script executable
  - compose mount present and read-only
  - gitignore exception present

## P1 — Runtime/dev preflight (optional)
- [x] Add a preflight check in existing framework:
  - verify `unaccent` extension
  - verify `public.unaccent_immutable(text)` is IMMUTABLE
- [x] Decide behavior by env:
  - dev/staging: fail-fast
  - prod: warn-only (unless you want strict)

## P1 — Docs
- [x] Update/confirm `db/README.md` includes:
  - why init scripts aren't enough
  - apply script usage patterns
  - verification queries + expected output
  - privilege troubleshooting
