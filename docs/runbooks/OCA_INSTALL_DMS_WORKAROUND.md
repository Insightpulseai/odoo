# Runbook: OCA Install — DMS Storage Auto-Directory Collision

## Problem

When installing OCA modules that create `res.partner` records (e.g., demo data, test fixtures), the DMS module's `ir.attachment.create()` monkey-patch attempts to auto-create directories for each partner. If two partners share the same `display_name`, the `_check_name` constraint on `dms.directory` raises:

```
ValidationError: A directory with the same name already exists.
```

This blocks installation of any module that creates partner records.

## Trigger

- DMS storage record has a linked model via `dms_storage_ir_model_rel`
- The linked model is `res.partner` (or any model where `display_name` can collide)
- A module being installed creates records on that model with duplicate display names

## Root Cause

`addons/oca/dms/models/ir_attachment.py:27` hooks `ir.attachment.create()`. When a new attachment is created for a record linked to a DMS storage, `_dms_directories_create()` fires and calls `dms.directory.create(name=model_item.display_name)`. The `_check_name` constraint enforces unique sibling names within the same parent directory.

## Workaround

### Step 1: Temporarily unlink the model from DMS storage

```sql
-- Identify the problematic storage-model link
SELECT s.id, s.name, m.model
FROM dms_storage s
JOIN dms_storage_ir_model_rel rel ON rel.dms_storage_id = s.id
JOIN ir_model m ON m.id = rel.ir_model_id
WHERE m.model = 'res.partner';

-- Remove the link (note the storage ID for restoration)
DELETE FROM dms_storage_ir_model_rel WHERE dms_storage_id = <storage_id>;
```

### Step 2: Install/update modules

```bash
~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
  -d odoo_dev \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  -i <module_list> \
  --stop-after-init --no-http \
  --addons-path=<full_addons_path>
```

### Step 3: Restore the model link

```sql
-- Re-link the model to the DMS storage
INSERT INTO dms_storage_ir_model_rel (dms_storage_id, ir_model_id)
SELECT <storage_id>, id FROM ir_model WHERE model = 'res.partner';
```

### Step 4: Verify

```sql
-- Confirm link is restored
SELECT s.name, m.model
FROM dms_storage s
JOIN dms_storage_ir_model_rel rel ON rel.dms_storage_id = s.id
JOIN ir_model m ON m.id = rel.ir_model_id;

-- Confirm DMS directories still exist
SELECT count(*) FROM dms_directory;
```

## Rollback

If the install itself fails after unlinking:

```sql
-- Restore the link even if the install failed
INSERT INTO dms_storage_ir_model_rel (dms_storage_id, ir_model_id)
SELECT <storage_id>, id FROM ir_model WHERE model = 'res.partner'
ON CONFLICT DO NOTHING;
```

No data loss occurs from temporarily unlinking — existing DMS directories and files are preserved. Only the auto-creation hook is disabled during the unlinked period.

## Prevention

- When bulk-creating partner records (data imports, demo data), ensure `display_name` is unique within the scope of each DMS storage's parent directory
- Consider adding a deduplication suffix in `_dms_directories_create()` for a permanent fix
- Alternatively, avoid linking high-cardinality models (like `res.partner`) to DMS storage auto-directory creation

## Related

- DMS source: `addons/oca/dms/models/ir_attachment.py`
- Constraint: `addons/oca/dms/models/dms_directory.py` → `_check_name`
- First encountered: 2026-04-06, during OPRG OCA module batch install
