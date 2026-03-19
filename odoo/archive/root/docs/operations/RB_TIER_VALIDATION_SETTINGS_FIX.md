# Runbook: base_tier_validation Settings Crash Fix

> **Symptom**: Opening Odoo Settings crashes with an OWL error referencing
> `module_base_tier_validation_formula` (field not found on model
> `res.config.settings`).
>
> **Root cause**: The field is defined in code but was missing from the DB
> registry because the module was installed **before** `res_config_settings.py`
> was added to the codebase. A module upgrade registers the new field.
>
> **Fix**: `odoo -d $ODOO_DB -u base_tier_validation --stop-after-init`

---

## Environment Variables (required — no hardcoded values)

Set these before running any command in this runbook:

```bash
# Odoo database name
export ODOO_DB="odoo_prod"           # or "odoo_dev" for local

# Container name (check with: docker ps --format '{{.Names}}' | grep odoo)
export ODOO_CONTAINER="odoo-server"  # adjust to actual name

# Config file path inside the container (check odoo.conf in container)
export ODOO_CONF="/etc/odoo/odoo.conf"

# Host running Docker (empty = localhost)
export DOCKER_HOST_SSH=""            # e.g. "root@178.128.112.214" for prod
```

---

## Pre-flight Checklist

Run these checks before applying the fix. Each must pass.

### 1. Confirm the module is installed (not just present on disk)

```bash
# Via XML-RPC (works from any machine with network access to Odoo)
python3 - <<'PY'
import os, xmlrpc.client
url = os.environ.get("ODOO_URL", "http://localhost:8069")
db  = os.environ.get("ODOO_DB", "odoo_prod")
uid = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common").authenticate(
        db, os.environ["ODOO_USER"], os.environ["ODOO_PASSWORD"], {})
m   = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
rows = m.execute_kw(db, uid, os.environ["ODOO_PASSWORD"],
        "ir.module.module", "search_read",
        [[("name", "=", "base_tier_validation")]],
        {"fields": ["name", "state", "installed_version"]})
for r in rows:
    print(r)
PY
```

Expected: `state: installed`. If `state: to install` or module missing — the
upgrade is not applicable; install the module instead (`-i base_tier_validation`).

### 2. Confirm the code file is present

```bash
# Local
ls addons/oca/server-ux/base_tier_validation/models/res_config_settings.py

# In container (use $DOCKER_HOST_SSH prefix for remote)
${DOCKER_HOST_SSH:+ssh $DOCKER_HOST_SSH} docker exec "$ODOO_CONTAINER" \
  ls /mnt/extra-addons/server-ux/base_tier_validation/models/res_config_settings.py
```

Expected: file exists and is non-empty. If missing — the addon source needs
to be updated on the server before the upgrade will help.

### 3. Confirm field is present in Python source

```bash
${DOCKER_HOST_SSH:+ssh $DOCKER_HOST_SSH} docker exec "$ODOO_CONTAINER" \
  grep -n "module_base_tier_validation_formula" \
    /mnt/extra-addons/server-ux/base_tier_validation/models/res_config_settings.py
```

Expected output (line numbers may vary):
```
11:    module_base_tier_validation_formula = fields.Boolean(string="Tier Formula")
```

### 4. Confirm the field is NOT yet in the DB

```bash
${DOCKER_HOST_SSH:+ssh $DOCKER_HOST_SSH} docker exec "$ODOO_CONTAINER" \
  psql -U odoo "$ODOO_DB" -c \
  "SELECT column_name FROM information_schema.columns
   WHERE table_name = 'res_config_settings'
   AND column_name LIKE '%tier_validation%';"
```

Expected (before fix): `0 rows` — field not yet registered.
If the column already exists → the fix was already applied, skip to verification.

---

## Apply the Fix

### Option A: Direct (container exec)

```bash
${DOCKER_HOST_SSH:+ssh $DOCKER_HOST_SSH} docker exec "$ODOO_CONTAINER" \
  odoo -d "$ODOO_DB" --config "$ODOO_CONF" \
    -u base_tier_validation --stop-after-init --no-http 2>&1 \
  | tee /tmp/btv_upgrade.log
```

### Option B: Via odoo-bin on host (non-Docker)

```bash
odoo -d "$ODOO_DB" --config "$ODOO_CONF" \
  -u base_tier_validation --stop-after-init --no-http 2>&1 \
| tee /tmp/btv_upgrade.log
```

### Option C: GitHub Actions (CI-triggered, no SSH access)

Trigger the manual workflow dispatch for module upgrades if one exists, or
add this to a workflow:

```yaml
- name: Upgrade base_tier_validation
  env:
    ODOO_DB: ${{ secrets.ODOO_DB }}
    ODOO_CONTAINER: ${{ secrets.ODOO_CONTAINER }}
    ODOO_CONF: ${{ secrets.ODOO_CONF }}
  run: |
    ssh ${{ secrets.DEPLOY_HOST }} \
      "docker exec $ODOO_CONTAINER odoo -d $ODOO_DB --config $ODOO_CONF \
        -u base_tier_validation --stop-after-init --no-http"
```

---

## Post-Fix Verification

### 1. Confirm the column now exists

```bash
${DOCKER_HOST_SSH:+ssh $DOCKER_HOST_SSH} docker exec "$ODOO_CONTAINER" \
  psql -U odoo "$ODOO_DB" -c \
  "SELECT column_name, data_type
   FROM information_schema.columns
   WHERE table_name = 'res_config_settings'
   AND column_name LIKE '%tier_validation%';"
```

Expected: `module_base_tier_validation_formula | boolean`

### 2. Confirm Settings renders without OWL error

Open `https://<odoo-url>/odoo/settings` in a browser. The page should load
without a JavaScript traceback. If using Playwright:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto(os.environ["ODOO_URL"] + "/web#action=base_setup.action_general_configuration")
    page.wait_for_selector(".o_form_view", timeout=15000)
    errors = page.evaluate("window.__console_errors__ || []")
    assert not any("tier_validation" in str(e) for e in errors), f"OWL error still present: {errors}"
    print("✅ Settings renders without OWL error")
    b.close()
PY
```

### 3. Check upgrade log for errors

```bash
grep -E "ERROR|Traceback|Exception" /tmp/btv_upgrade.log | head -20
```

Expected: no output (no errors).

---

## Rollback

The upgrade only adds a column (no data migration, no destructive change).
If something goes wrong:

1. Restart Odoo — the column addition is idempotent and harmless.
2. If the column causes a conflict (unlikely): drop it manually.
   ```sql
   -- Only if needed — this column is additive and safe to keep
   ALTER TABLE res_config_settings DROP COLUMN IF EXISTS module_base_tier_validation_formula;
   ```
3. The underlying code fix (`res_config_settings.py`) can be reverted in the
   submodule if needed.

---

## Notes

- **`addons/oca/` is gitignored** in the main repo. The `base_tier_validation`
  module lives in `addons/oca/server-ux/base_tier_validation/` which is its own
  independent git repo (not a tracked submodule). Deployment must ensure the
  correct version is present on the server.
- **`noupdate="1"` data files**: If this module has XML data files with
  `noupdate="1"`, a module upgrade will re-apply them only if they were
  previously not loaded. Safe in this case.
- **Production window**: This upgrade is fast (adds 1 boolean column + triggers
  a Settings view reload). No downtime window required for Odoo 19.
