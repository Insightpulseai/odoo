# Examples — odoo-data-migration-script

## Example 1: Add required field with default backfill

**Input**: Add required `margin_pct` field to `project.project`, backfill existing records

**Output** — migrations/18.0.1.1.0/pre-migrate.py:
```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    _logger.info("Pre-migrating ipai_finance_ppm to 18.0.1.1.0")
    cr.execute("""
        ALTER TABLE project_project
        ADD COLUMN IF NOT EXISTS margin_pct FLOAT DEFAULT 0.0
    """)
    cr.execute("""
        ALTER TABLE project_project
        ADD COLUMN IF NOT EXISTS is_over_budget BOOLEAN DEFAULT FALSE
    """)
```

**Output** — migrations/18.0.1.1.0/post-migrate.py:
```python
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Post-migrating ipai_finance_ppm to 18.0.1.1.0")
    projects = env['project.project'].search([
        ('budget_amount', '>', 0),
        ('margin_pct', '=', 0),
    ])
    for project in projects:
        project._compute_margin_pct()
    _logger.info("Backfilled margin_pct for %d projects", len(projects))
```

- Forward migration: PASS (50 existing projects backfilled)
- Fresh install: PASS (skipped, no version)
- Idempotency: PASS (IF NOT EXISTS, search filter prevents double-compute)

## Example 2: Rename model (table rename in pre-migration)

**Input**: Rename `ipai.old.model` to `ipai.new.model`

**Output** — pre-migrate.py:
```python
def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        ALTER TABLE IF EXISTS ipai_old_model
        RENAME TO ipai_new_model
    """)
    cr.execute("""
        UPDATE ir_model SET model = 'ipai.new.model'
        WHERE model = 'ipai.old.model'
    """)
    cr.execute("""
        UPDATE ir_model_data SET name = REPLACE(name, 'ipai_old_model', 'ipai_new_model')
        WHERE model = 'ir.model' AND name LIKE '%ipai_old_model%'
    """)
```

## Example 3: Rejected — cr.commit() in migration

**Input**: Migration script calls `cr.commit()` after SQL

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: `cr.commit()` in migration scripts is prohibited — the framework manages transactions
- Recommendation: Remove `cr.commit()` call; Odoo commits after successful migration automatically
