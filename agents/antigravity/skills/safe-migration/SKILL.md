---
name: safe-migration
description: Use when adding/changing DB schema, migrations, RLS/policies, or data backfills. Enforce idempotence, reversibility, and verification.
---

# Safe Migration Skill

## Goal

Ensure database migrations are:

- **Idempotent**: Can run multiple times safely
- **Reversible**: Can be rolled back if needed
- **Verified**: Proven to work with tests and queries

## When to activate

Activate for:

- "Add a column to users table"
- "Create a new table"
- "Change column type"
- "Add index"
- "Migrate data from old to new schema"
- "Add foreign key constraint"
- "Update Odoo model fields"

Do NOT activate for:

- Simple data updates (use SQL directly)
- Read-only queries
- Reporting queries

## Guardrails

### 1. Idempotence

Migrations must be safe to run multiple times:

**SQL**:

```sql
-- ✅ Idempotent
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- ❌ Not idempotent (fails on second run)
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

**Odoo**:

```python
# ✅ Idempotent
def migrate(cr, version):
    if not column_exists(cr, 'res_partner', 'x_custom_field'):
        cr.execute("""
            ALTER TABLE res_partner
            ADD COLUMN x_custom_field VARCHAR(100)
        """)
```

### 2. Reversibility

Provide rollback for risky changes:

```sql
-- Migration: Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Rollback
ALTER TABLE users DROP COLUMN IF EXISTS phone;
```

### 3. Verification

Test migrations before production:

- Schema diff (before/after)
- Row counts (data migrations)
- Application smoke tests

## Process

### 1. Identify Impacted Tables/Views

- Which tables are affected?
- What are the dependencies (foreign keys, views, triggers)?
- What application code uses these tables?

**For Odoo**:

- Which models are affected?
- What computed fields depend on changed fields?
- What views/reports use these fields?

### 2. Produce Migration Scripts

**SQL Migration**:

```sql
-- migrations/001_add_user_phone.sql
BEGIN;

-- Add column
ALTER TABLE users
ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Add index (if needed)
CREATE INDEX IF NOT EXISTS idx_users_phone
ON users(phone);

-- Backfill data (if needed)
UPDATE users
SET phone = '+1-555-0000'
WHERE phone IS NULL AND country = 'US';

COMMIT;
```

**Odoo Migration** (`migrations/19.0.1.0.0/pre-migrate.py`):

```python
def migrate(cr, version):
    """Add custom field to res.partner"""

    # Check if column exists
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='res_partner'
        AND column_name='x_custom_field'
    """)

    if not cr.fetchone():
        # Add column
        cr.execute("""
            ALTER TABLE res_partner
            ADD COLUMN x_custom_field VARCHAR(100)
        """)

        # Backfill data
        cr.execute("""
            UPDATE res_partner
            SET x_custom_field = 'default_value'
            WHERE x_custom_field IS NULL
        """)
```

### 3. Create Verification Queries

**Schema verification**:

```sql
-- Verify column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'phone';

-- Verify index exists
SELECT indexname
FROM pg_indexes
WHERE tablename = 'users' AND indexname = 'idx_users_phone';
```

**Data verification**:

```sql
-- Check row counts
SELECT COUNT(*) FROM users;
-- Before: 1000
-- After: 1000 (should match)

-- Check data quality
SELECT COUNT(*) FROM users WHERE phone IS NULL;
-- Should be 0 if backfill worked

-- Check constraints
SELECT COUNT(*) FROM users WHERE phone !~ '^\+?[0-9-]+$';
-- Should be 0 (valid phone format)
```

### 4. Test Locally/CI

Run migration on test database:

```bash
# Create test database
createdb myapp_test
pg_restore -d myapp_test latest_backup.dump

# Run migration
psql -d myapp_test -f migrations/001_add_user_phone.sql

# Verify
psql -d myapp_test -f migrations/verify.sql

# Test application
python manage.py test
```

### 5. Provide Rollback Path

**SQL Rollback**:

```sql
-- rollback/001_add_user_phone.sql
BEGIN;

-- Drop index
DROP INDEX IF EXISTS idx_users_phone;

-- Drop column
ALTER TABLE users DROP COLUMN IF EXISTS phone;

COMMIT;
```

**Odoo Rollback**:

```python
# migrations/19.0.1.0.0/end-migrate.py
def rollback(cr, version):
    """Rollback custom field addition"""
    cr.execute("""
        ALTER TABLE res_partner
        DROP COLUMN IF EXISTS x_custom_field
    """)
```

## Output Format

### Migration Plan

```markdown
## Migration Plan: Add Phone to Users

### Impact

- Table: `users`
- New column: `phone VARCHAR(20)`
- New index: `idx_users_phone`
- Backfill: Set default for US users

### Dependencies

- None (new column, no FK)

### Risks

- **Low**: Adding nullable column is safe
- **Medium**: Backfill updates 1000 rows (test on staging first)

### Estimated Downtime

- None (online migration)
```

### Migration SQL

```sql
-- migrations/001_add_user_phone.sql
BEGIN;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

CREATE INDEX IF NOT EXISTS idx_users_phone
ON users(phone);

UPDATE users
SET phone = '+1-555-0000'
WHERE phone IS NULL AND country = 'US';

COMMIT;
```

### Verification SQL

```sql
-- migrations/verify_001.sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'phone';
-- Expected: phone | character varying | YES

SELECT COUNT(*) FROM users WHERE phone IS NULL AND country = 'US';
-- Expected: 0
```

### Rollback SQL

```sql
-- rollback/001_add_user_phone.sql
BEGIN;

DROP INDEX IF EXISTS idx_users_phone;
ALTER TABLE users DROP COLUMN IF EXISTS phone;

COMMIT;
```

### Deploy Steps

```bash
# 1. Backup database
pg_dump -Fc myapp_prod > backup_$(date +%Y%m%d_%H%M%S).dump

# 2. Run migration
psql -d myapp_prod -f migrations/001_add_user_phone.sql

# 3. Verify
psql -d myapp_prod -f migrations/verify_001.sql

# 4. Test application
curl http://localhost:3000/health
# Expected: {"status": "ok"}

# 5. Monitor logs
tail -f logs/app.log
# Watch for errors
```

### Rollback Steps

```bash
# If migration causes issues:
psql -d myapp_prod -f rollback/001_add_user_phone.sql

# Restore from backup (last resort):
pg_restore -d myapp_prod -c backup_20240211_100000.dump
```

## Verification

- [ ] Migration is idempotent (uses IF NOT EXISTS)
- [ ] Rollback script provided
- [ ] Verification queries included
- [ ] Tested on local/staging database
- [ ] Application tests pass
- [ ] Deploy steps documented
- [ ] Rollback steps documented
- [ ] Backup taken before deploy

## Odoo-Specific Checklist

- [ ] Migration in correct version folder (`migrations/19.0.x.y.z/`)
- [ ] `pre-migrate.py` for schema changes
- [ ] `post-migrate.py` for data updates
- [ ] `end-migrate.py` for cleanup
- [ ] Module version bumped in `__manifest__.py`
- [ ] Tested with `odoo-bin -u module_name`
- [ ] No direct SQL for Odoo ORM tables (use ORM when possible)
