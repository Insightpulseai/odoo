# Database Initialization & Maintenance

PostgreSQL database scripts for Odoo development and production environments.

## Directory Structure

```
db/
├── init/                   # First-time DB initialization (docker-entrypoint-initdb.d)
│   └── 10_unaccent_immutable.sql
├── sql/                    # On-demand SQL scripts (idempotent)
│   └── apply_unaccent_immutable.sql
└── README.md               # This file
```

## Initialization Scripts (`db/init/`)

**Purpose**: Automatically executed when PostgreSQL container initializes a **new** database.

**Behavior**:
- Scripts run **only once** during first database creation
- Executed in alphanumeric order (hence `10_` prefix)
- If database already exists, these scripts are **skipped**

**Mount Point**: `./db/init:/docker-entrypoint-initdb.d:ro`

**Example**:
```bash
# Fresh database - init scripts run automatically
docker-compose up -d db
# → 10_unaccent_immutable.sql executes
```

## On-Demand Scripts (`db/sql/`)

**Purpose**: Idempotent SQL scripts that can be applied to **existing** databases.

**Behavior**:
- Safe to run multiple times (CREATE OR REPLACE, IF NOT EXISTS patterns)
- Can be executed manually or via CI/automation
- Work on databases initialized before the script existed

**Mount Point**: `./db/sql:/sql:ro`

**Example**:
```bash
# Apply to existing database
docker-compose exec db psql -U odoo -d odoo_dev -f /sql/apply_unaccent_immutable.sql

# Or use helper script
./scripts/db/apply_unaccent_fix.sh odoo_dev
```

## Common Patterns

### Pattern 1: New Database Setup

```bash
# 1. Remove existing database (if needed)
docker-compose down -v

# 2. Start fresh - init scripts run automatically
docker-compose up -d db

# 3. Verify
docker-compose exec db psql -U odoo -d odoo_dev -c "\df public.unaccent_immutable"
```

### Pattern 2: Existing Database Hardening

```bash
# Database already exists, init scripts won't run
# Use on-demand script instead:

./scripts/db/apply_unaccent_fix.sh odoo_dev
```

### Pattern 3: CI/CD Deployment

```yaml
# .github/workflows/deploy.yml
- name: Apply DB hardening
  run: |
    docker-compose exec -T db psql -U odoo -d odoo_prod -f /sql/apply_unaccent_immutable.sql
```

## IMMUTABLE Wrapper Context

**Problem**: OCA modules create GIN/GiST indexes using `unaccent(text)`, but PostgreSQL requires index functions to be marked `IMMUTABLE`. The default `unaccent(text)` from the extension is `VOLATILE`.

**Solution**:
1. Create `unaccent_immutable(text)` wrapper with `IMMUTABLE` marking
2. Alter existing `unaccent(text)` to be `IMMUTABLE` (for OCA compatibility)

**Scripts**:
- `db/init/10_unaccent_immutable.sql` - Runs on new databases
- `db/sql/apply_unaccent_immutable.sql` - Runs on existing databases
- `scripts/db/apply_unaccent_fix.sh` - Helper script with verification

## Troubleshooting

### "functions in index expression must be marked IMMUTABLE"

**Cause**: Trying to install OCA module before IMMUTABLE wrapper is applied.

**Fix**:
```bash
# Apply the fix
./scripts/db/apply_unaccent_fix.sh

# Retry module installation
docker-compose exec odoo odoo -d odoo_dev -i hr_recruitment --stop-after-init
```

### Init scripts didn't run

**Cause**: Database already existed when container started.

**Fix**: Use on-demand script instead:
```bash
./scripts/db/apply_unaccent_fix.sh
```

### Verify function volatility

```bash
docker-compose exec db psql -U odoo -d odoo_dev -c "
SELECT
    p.proname,
    CASE p.provolatile
        WHEN 'i' THEN 'IMMUTABLE'
        WHEN 's' THEN 'STABLE'
        WHEN 'v' THEN 'VOLATILE'
    END as volatility
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND p.proname IN ('unaccent', 'unaccent_immutable');
"
```

Expected output:
```
      proname       | volatility
--------------------+------------
 unaccent           | IMMUTABLE
 unaccent_immutable | IMMUTABLE
```

## References

- PostgreSQL function volatility: https://www.postgresql.org/docs/current/xfunc-volatility.html
- OCA text search patterns: https://github.com/OCA/server-tools/tree/19.0
- Neon unaccent guide: https://neon.com/docs/extensions/unaccent
