# PostgreSQL Compatibility Issues and Fixes

## unaccent Function Immutability

### Symptom
```
psycopg2.errors.InvalidObjectDefinition: functions in index expression must be marked IMMUTABLE
```

Occurs during installation of Odoo modules that create functional indexes using `unaccent()` (e.g., `hr_recruitment`, `crm`, `sale`).

### Root Cause
PostgreSQL requires functions used in index expressions to be marked as `IMMUTABLE` (deterministic - same input always produces same output). The `unaccent` extension provides functions with `STABLE` volatility by default, which prevents their use in functional indexes.

Odoo modules create indexes like:
```sql
CREATE INDEX hr_applicant_name_unaccent
ON hr_applicant (unaccent(name));
```

PostgreSQL rejects this because `unaccent()` is marked `STABLE`, not `IMMUTABLE`.

### Fix
Applied via `scripts/db/patches/pg_immutable_index_fns.sql`:

1. Ensures `unaccent` extension exists
2. Alters `unaccent(text)` to `IMMUTABLE` volatility
3. Alters `unaccent(regdictionary, text)` to `IMMUTABLE` volatility

### Bootstrap Integration
Patch is automatically applied during database initialization via:
```bash
psql -f scripts/db/apply_patches.sql
```

### Risk Notes
- **Low Risk**: `unaccent()` function behavior is deterministic in practice (same input → same output)
- **PostgreSQL 16 Compatibility**: Tested on PostgreSQL 16 (Odoo 19 requirement)
- **Upstream Behavior**: PostgreSQL marks `unaccent()` as STABLE for technical reasons, but Odoo's usage pattern is safe for IMMUTABLE
- **Rollback**: If issues arise, revert with `ALTER FUNCTION public.unaccent(text) STABLE`

### Verification
```bash
# Check function volatility
psql -c "SELECT proname, provolatile FROM pg_proc WHERE proname = 'unaccent';"

# Expected output:
#  proname  | provolatile
# ----------+-------------
#  unaccent | i           (i = IMMUTABLE)
#  unaccent | i
```

### References
- PostgreSQL Function Volatility: https://www.postgresql.org/docs/16/xfunc-volatility.html
- Odoo Functional Indexes: Standard pattern in many Odoo modules for accent-insensitive search
- unaccent Extension: https://www.postgresql.org/docs/16/unaccent.html
