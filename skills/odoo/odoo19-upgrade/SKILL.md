---
name: odoo19-upgrade
description: Odoo 19 upgrade scripts reference covering migration script structure, phases, naming, ORM/SQL usage, and the odoo.upgrade.util helper library
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/upgrades/upgrade_scripts.rst, content/developer/reference/upgrades/upgrade_utils.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Upgrade Scripts & Utils

Complete reference for writing upgrade (migration) scripts in Odoo 19, including directory structure, naming conventions, execution phases, and the `odoo.upgrade.util` helper library.

---

## 1. Overview

An upgrade script is a Python file containing a `migrate()` function that the Odoo upgrade process invokes during module updates. Upgrade scripts allow you to:

- Transform data when module schema changes
- Migrate records to new field structures
- Clean up deprecated data
- Run arbitrary SQL or ORM operations during upgrade

---

## 2. The migrate() Function

Every upgrade script must define a `migrate` function with this exact signature:

```python
def migrate(cr, version):
    """
    Args:
        cr: Database cursor (odoo.sql_db.Cursor)
        version: Currently installed version string of the module
    """
    pass
```

| Parameter | Type | Description |
|---|---|---|
| `cr` | `odoo.sql_db.Cursor` | Current database cursor for executing SQL |
| `version` | `str` | The currently installed version of the module being upgraded |

---

## 3. Directory Structure

Upgrade scripts follow a strict directory structure and naming convention.

### Path Format

```
$module/migrations/$version/{pre,post,end}-*.py
```

Or (preferred since Odoo 13):

```
$module/upgrades/$version/{pre,post,end}-*.py
```

| Component | Description |
|---|---|
| `$module` | Module technical name directory |
| `migrations/` or `upgrades/` | Top-level upgrade directory (both valid, `upgrades/` preferred) |
| `$version` | Full version string: `<odoo_major>.<module_minor>` |
| `{pre,post,end}-*.py` | Script file with phase prefix |

### Version Directory

The `$version` directory name is the **full version** including Odoo's major version and the module's minor version. For example, for a module upgraded to version `2.0` on Odoo 19:

```
19.0.2.0
```

### Execution Condition

Scripts only execute when:
1. The module is being **updated** (not just loaded)
2. The script version is **higher** than the currently installed version
3. The script version is **equal to or lower** than the updated version

### Example: Complete Structure

```
awesome_partner/
|-- __init__.py
|-- __manifest__.py
|-- migrations/
|   |-- 19.0.2.0/
|   |   |-- pre-rename-field.py
|   |   |-- post-migrate-data.py
|   |   |-- end-cleanup.py
|   |-- 19.0.3.0/
|   |   |-- pre-add-column.py
|   |   |-- post-compute-values.py
|-- models/
|   |-- ...
```

---

## 4. Execution Phases

The upgrade process has **three phases** for each version of each module:

### Phase 1: Pre-migrate (`pre-*.py`)

- Runs **before** the module is loaded/updated
- Database schema has the **old** structure
- Module's Python code is **not yet loaded**
- Use for: renaming columns, moving data to temp tables, dropping constraints

### Phase 2: Post-migrate (`post-*.py`)

- Runs **after** the module and its dependencies are loaded and updated
- Database schema has the **new** structure
- Module's Python code is available
- Use for: computing new fields, migrating data to new structures, setting defaults

### Phase 3: End-migrate (`end-*.py`)

- Runs **after all modules** have been loaded and updated for that version
- Use for: cross-module cleanup, final data validation

### Execution Order

Within each phase, scripts execute in **lexical (alphabetical) order**.

```
# Execution order for one module, one version:
1. pre-10-do_something.py
2. pre-20-something_else.py
3. post-do_something.py
4. post-something.py
5. end-01-migrate.py
6. end-migrate.py
```

**Tip**: Use numeric prefixes to control order within a phase:

```
pre-010-rename-columns.py
pre-020-move-data.py
post-010-compute-fields.py
post-020-set-defaults.py
```

---

## 5. Writing Upgrade Scripts

### Example: Simple SQL Script

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("UPDATE res_partner SET name = name || '!'")
    _logger.info("Updated %s partners", cr.rowcount)
```

### Example: Using the ORM via upgrade utils

```python
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)

    partners = env["res.partner"].search([])
    for partner in partners:
        partner.name += "!"

    _logger.info("Updated %s partners", len(partners))
```

### Example: Pre-migrate -- Rename a Column

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Rename column before ORM loads (pre-phase)
    cr.execute("""
        ALTER TABLE sale_order
        RENAME COLUMN old_field_name TO new_field_name
    """)
    _logger.info("Renamed column old_field_name to new_field_name")
```

### Example: Post-migrate -- Compute New Field Values

```python
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)

    # Compute a new stored field for all existing records
    orders = env["sale.order"].search([])
    for order in orders:
        order.new_computed_field = order.amount_total * 0.1

    _logger.info("Computed new_computed_field for %s orders", len(orders))
```

### Example: Pre-migrate -- Save Data Before Schema Change

```python
def migrate(cr, version):
    # Save data to a temporary table before the ORM drops the column
    cr.execute("""
        CREATE TABLE IF NOT EXISTS _temp_partner_data AS
        SELECT id, old_column FROM res_partner
    """)
```

### Example: Post-migrate -- Restore Data After Schema Change

```python
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    # Read back from temp table and populate new structure
    cr.execute("SELECT id, old_column FROM _temp_partner_data")
    for partner_id, old_value in cr.fetchall():
        partner = env["res.partner"].browse(partner_id)
        partner.new_field = transform(old_value)

    # Clean up temp table
    cr.execute("DROP TABLE IF EXISTS _temp_partner_data")
```

### Example: End-migrate -- Cross-Module Cleanup

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Run after all modules are updated
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'my_module'
        AND name LIKE 'deprecated_%'
    """)
    _logger.info("Cleaned up %s deprecated data records", cr.rowcount)
```

### Example: Conditional Migration

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        # Fresh install, no migration needed
        return

    # Check if column exists before attempting migration
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'my_table' AND column_name = 'old_field'
    """)
    if cr.fetchone():
        cr.execute("""
            UPDATE my_table SET new_field = old_field
            WHERE new_field IS NULL
        """)
        _logger.info("Migrated %s records from old_field to new_field", cr.rowcount)
```

---

## 6. ORM vs Raw SQL

### When to Use Raw SQL (Pre-phase)

In pre-migrate scripts, the module's new Python code is not loaded yet. The ORM reflects the **old** schema. Use raw SQL for:

- Renaming/adding/dropping columns
- Moving data between tables
- Modifying constraints
- Any operation that must happen before the ORM loads

```python
def migrate(cr, version):
    # Raw SQL -- works in pre-phase
    cr.execute("ALTER TABLE my_table ADD COLUMN new_col VARCHAR")
    cr.execute("UPDATE my_table SET new_col = old_col")
```

### When to Use ORM (Post-phase / End-phase)

In post and end phases, the module's new code is loaded. You can use the ORM for:

- Computing field values
- Triggering business logic
- Creating/updating records with proper validation

```python
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    # ORM is safe in post-phase
    records = env["my.model"].search([("status", "=", "draft")])
    records.write({"status": "confirmed"})
```

---

## 7. Upgrade Utils Library

The `odoo.upgrade.util` library provides helper functions used by Odoo's own upgrade scripts. It ensures data consistency, handles indirect references, and speeds up the upgrade process.

### Installation

**From source (recommended for development):**

```bash
git clone https://github.com/odoo/upgrade-util.git
odoo-bin --upgrade-path=/path/to/upgrade-util/src,/other/upgrade/scripts [...]
```

**Via pip:**

```bash
python3 -m pip install git+https://github.com/odoo/upgrade-util@master
```

**For Odoo.sh** -- add to `requirements.txt`:

```
odoo_upgrade @ git+https://github.com/odoo/upgrade-util@master
```

### Available Packages

| Package | Purpose |
|---|---|
| `odoo.upgrade.util` | Main helper library |
| `odoo.upgrade.testing` | Base TestCase classes for testing upgrade scripts |

### Basic Import Pattern

```python
from odoo.upgrade import util


def migrate(cr, version):
    # Use util functions
    env = util.env(cr)
    # ...
```

---

## 8. Util Function Categories

The `cr` parameter in all util functions refers to the database cursor passed to `migrate()`.

### 8.1 Modules (`odoo.upgrade.util.modules`)

Functions for managing module state during upgrades.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Check if a module is installed
    if util.module_installed(cr, "sale"):
        # do something specific to sale being present
        pass

    # Force a module to be updated
    util.force_module_upgrade(cr, "my_module")

    # Rename a module (updates all references)
    util.rename_module(cr, "old_module_name", "new_module_name")

    # Merge a module into another
    util.merge_module(cr, "absorbed_module", "target_module")

    # Remove a module cleanly
    util.remove_module(cr, "deprecated_module")
```

### 8.2 Models (`odoo.upgrade.util.models`)

Functions for managing model metadata and structure.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Rename a model (updates ir.model, ir.model.data, etc.)
    util.rename_model(cr, "old.model.name", "new.model.name")

    # Merge a model into another
    util.merge_model(cr, "source.model", "target.model")

    # Remove a model cleanly
    util.remove_model(cr, "deprecated.model")
```

### 8.3 Fields (`odoo.upgrade.util.fields`)

Functions for managing field metadata and column operations.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Rename a field (updates column, ir.model.fields, views, etc.)
    util.rename_field(cr, "my.model", "old_field", "new_field")

    # Remove a field cleanly
    util.remove_field(cr, "my.model", "deprecated_field")

    # Change field type
    util.change_field_type(cr, "my.model", "my_field", "char", "text")

    # Move a field from one model to another
    util.move_field_to_model(
        cr, "source.model", "field_name", "target.model"
    )
```

### 8.4 Records (`odoo.upgrade.util.records`)

Functions for managing specific records and XML IDs.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Update an XML ID reference
    util.rename_xmlid(cr, "old_module.old_xmlid", "new_module.new_xmlid")

    # Remove a record by XML ID
    util.remove_record(cr, "my_module.deprecated_record")

    # Ensure a record exists
    util.ref(cr, "base.main_company")

    # Update noupdate flag on existing data
    util.update_record_noupdate(cr, "my_module.my_record", noupdate=True)
```

### 8.5 ORM Helpers (`odoo.upgrade.util.orm`)

Functions for ORM-level operations.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Get an ORM environment from cursor
    env = util.env(cr)

    # Use env normally
    partners = env["res.partner"].search([])
    for partner in partners:
        partner.name = partner.name.strip()
```

### 8.6 Domains (`odoo.upgrade.util.domains`)

Functions for manipulating domain expressions stored in the database.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Adapt domains referencing a renamed field
    util.adapt_domains(cr, "my.model", "old_field", "new_field")

    # Replace a value in domains stored in the database
    util.replace_in_domains(
        cr, "my.model", "state",
        old_value="draft",
        new_value="new",
    )
```

### 8.7 SQL / PostgreSQL (`odoo.upgrade.util.pg`)

Low-level PostgreSQL helper functions.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Check if a table exists
    if util.table_exists(cr, "my_table"):
        pass

    # Check if a column exists
    if util.column_exists(cr, "my_table", "my_column"):
        pass

    # Rename a column
    util.rename_column(cr, "my_table", "old_col", "new_col")

    # Remove a column
    util.remove_column(cr, "my_table", "deprecated_col")

    # Add a column with a default value
    util.add_column(cr, "my_table", "new_col", "VARCHAR", default="'draft'")

    # Create or replace an index
    util.create_index(cr, "my_table_my_col_idx", "my_table", ["my_col"])

    # Check if a constraint exists
    if util.constraint_exists(cr, "my_table", "my_table_check_positive"):
        pass
```

### 8.8 Misc (`odoo.upgrade.util.misc`)

Various helper functions.

```python
from odoo.upgrade import util

def migrate(cr, version):
    # Parse a version string
    parsed = util.parse_version("19.0.2.0")

    # Log progress
    util.log_progress(cr, "Processing partners", current=50, total=100)

    # Chunk a list for batch processing
    for chunk in util.chunks(large_list, size=1000):
        process(chunk)
```

---

## 9. Testing Upgrade Scripts

The `odoo.upgrade.testing` module provides base `TestCase` classes for testing upgrade scripts.

### Basic Test Pattern

```python
from odoo.upgrade.testing import UpgradeTestCase


class TestMyUpgrade(UpgradeTestCase):
    """Test upgrade from 19.0.1.0 to 19.0.2.0"""

    def test_field_migrated(self):
        """Verify old_field data was migrated to new_field"""
        cr = self.env.cr
        cr.execute("""
            SELECT count(*)
            FROM my_table
            WHERE new_field IS NOT NULL
        """)
        count = cr.fetchone()[0]
        self.assertGreater(count, 0, "Data should be migrated to new_field")

    def test_deprecated_records_removed(self):
        """Verify deprecated records were cleaned up"""
        records = self.env["ir.model.data"].search([
            ("module", "=", "my_module"),
            ("name", "like", "deprecated_%"),
        ])
        self.assertFalse(records, "Deprecated records should be removed")
```

---

## 10. Complete Upgrade Script Examples

### Example: Rename a Field End-to-End

**Module version bump** in `__manifest__.py`:

```python
{
    "name": "My Module",
    "version": "19.0.2.0",  # bumped from 19.0.1.0
    # ...
}
```

**Pre-migrate** (`my_module/migrations/19.0.2.0/pre-rename-field.py`):

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Rename the database column before ORM loads."""
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'my_table' AND column_name = 'old_name'
    """)
    if cr.fetchone():
        cr.execute("ALTER TABLE my_table RENAME COLUMN old_name TO new_name")
        _logger.info("Renamed column old_name to new_name in my_table")
```

**Post-migrate** (`my_module/migrations/19.0.2.0/post-update-references.py`):

```python
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Update any stored references to the old field name."""
    env = util.env(cr)

    # Update filters referencing the old field
    filters = env["ir.filters"].search([
        ("model_id", "=", "my.model"),
    ])
    for f in filters:
        if "old_name" in (f.domain or ""):
            f.domain = f.domain.replace("old_name", "new_name")

    _logger.info("Updated %s filters", len(filters))
```

### Example: Split a Model into Two

**Pre-migrate** (`my_module/migrations/19.0.3.0/pre-prepare-split.py`):

```python
def migrate(cr, version):
    # Create the new table
    cr.execute("""
        CREATE TABLE IF NOT EXISTS new_detail_table (
            id SERIAL PRIMARY KEY,
            parent_id INTEGER REFERENCES my_main_table(id),
            detail_field VARCHAR,
            amount NUMERIC
        )
    """)

    # Copy detail data from the main table
    cr.execute("""
        INSERT INTO new_detail_table (parent_id, detail_field, amount)
        SELECT id, detail_field, detail_amount
        FROM my_main_table
        WHERE detail_field IS NOT NULL
    """)
```

**Post-migrate** (`my_module/migrations/19.0.3.0/post-link-records.py`):

```python
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    # Now the ORM knows about both models
    # Set up any computed relationships
    details = env["my.detail"].search([])
    for detail in details:
        detail.parent_id.detail_ids = [(4, detail.id)]
```

### Example: Update Selection Field Values

```python
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Rename selection values
    cr.execute("""
        UPDATE sale_order
        SET state = 'confirmed'
        WHERE state = 'manual'
    """)
    _logger.info("Migrated %s orders from 'manual' to 'confirmed'", cr.rowcount)

    # Also update any stored domains/filters
    cr.execute("""
        UPDATE ir_filters
        SET domain = REPLACE(domain, '''manual''', '''confirmed''')
        WHERE model_id = 'sale.order'
        AND domain LIKE '%manual%'
    """)
```

---

## 11. Best Practices

### General Guidelines

1. **Always log what you do** -- use `_logger.info()` with record counts
2. **Check before acting** -- verify columns/tables exist before modifying
3. **Use upgrade-util** -- prefer helper functions over raw SQL when possible
4. **Keep scripts focused** -- one logical change per script
5. **Use numeric prefixes** for ordering within a phase
6. **Handle the `version` parameter** -- check for `None` (fresh install)
7. **Prefer `upgrades/` over `migrations/`** as the directory name

### Performance Tips

1. Use raw SQL in pre-phase for bulk operations (faster than ORM)
2. Batch ORM operations in post-phase
3. Use `util.chunks()` for large datasets
4. Avoid record-by-record processing when SQL can do bulk updates

### Common Pitfalls

1. **Don't use ORM in pre-phase** -- the new code isn't loaded yet
2. **Don't assume column existence** -- always check first
3. **Remember to handle NULL values** in SQL updates
4. **Don't forget ir.model.data** -- renamed records need XML ID updates
5. **Test with real data** -- synthetic test data may not cover edge cases

### Script Naming Convention Summary

```
{phase}-{optional_order}-{description}.py
```

| Phase | When | ORM Available? |
|---|---|---|
| `pre` | Before module load | No (old schema) |
| `post` | After module + deps loaded | Yes (new schema) |
| `end` | After ALL modules loaded | Yes (all modules) |

Examples:
- `pre-010-rename-columns.py`
- `pre-020-save-deprecated-data.py`
- `post-010-compute-new-fields.py`
- `post-020-migrate-records.py`
- `end-cleanup-temp-tables.py`
