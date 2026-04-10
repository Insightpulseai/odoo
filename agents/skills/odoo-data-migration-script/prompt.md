# Prompt — odoo-data-migration-script

You are writing a data migration script for an Odoo CE 18 module on the InsightPulse AI platform.

Your job is to:
1. Create the `migrations/<version>/` directory structure
2. Write `pre-migrate.py` for schema changes before ORM loads (raw SQL)
3. Write `post-migrate.py` for data transforms after ORM is available
4. Define `migrate(cr, version)` as the entry point function
5. Ensure idempotency (IF NOT EXISTS, WHERE NOT EXISTS, COALESCE defaults)
6. Test on disposable database with existing data
7. Verify both forward migration and fresh install work

Platform context:
- Migration directory: `<module>/migrations/<version>/`
- Version format: `19.0.x.y.z` (must match __manifest__.py)
- Test database: `test_<module>` (disposable, with seed data)

Pre-migration (before ORM loads):
```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return  # Fresh install, skip
    _logger.info("Pre-migrating ipai_module to %s", version)
    cr.execute("""
        ALTER TABLE my_table
        ADD COLUMN IF NOT EXISTS new_field VARCHAR DEFAULT 'draft'
    """)
```

Post-migration (ORM available):
```python
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return  # Fresh install, skip
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Post-migrating ipai_module to %s", version)
    records = env['my.model'].search([('new_field', '=', False)])
    for rec in records:
        rec.new_field = rec._compute_default_new_field()
```

Output format:
- Migration type: pre/post
- Version: from -> to
- Scripts: list with paths
- Idempotency: verified (pass/fail)
- Forward migration test: pass/fail on DB with existing data
- Fresh install test: pass/fail on empty DB
- Evidence: migration log output

Rules:
- Never use cr.commit() — framework handles transactions
- Pre-migration: raw SQL only (ORM not loaded)
- Post-migration: prefer ORM over raw SQL
- Migrations must be idempotent
- Test on disposable DB, never prod/dev/staging
- Handle both upgrade and fresh install paths
- Version in directory must match manifest version
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
