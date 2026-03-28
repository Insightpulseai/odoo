# Addon Discovery Debug Runbook

> How to prove addons_path resolution, manifest discovery, and module visibility
> when an addon is not found or not installable.

## Symptoms

- Module appears in filesystem but not in Odoo's Apps list
- `Module not found` error during `-i <module>` or `-u <module>`
- Module installed but views/data not loading (wrong module version picked up)
- `ImportError` or `ModuleNotFoundError` for an addon

## Step 1: Verify addons_path

Print the effective addons_path from the running Odoo instance:

```bash
# Production (ACA container)
kubectl exec -it <pod> -- grep addons_path /etc/odoo/odoo.conf

# Devcontainer
grep addons_path /etc/odoo/odoo.conf

# Local dev (CLI args)
ps aux | grep odoo-bin | grep addons-path
```

Or from Odoo shell:

```python
from odoo.tools import config
print(config['addons_path'])
```

Expected output (production):
```
/opt/odoo/addons,/workspaces/odoo/addons/oca,/workspaces/odoo/addons/ipai
```

**Check**: Each path must exist and be readable by the Odoo process user.

## Step 2: Verify Module Directory Exists

```bash
# Check that the module directory exists in one of the addons_path entries
ls -la /workspaces/odoo/addons/ipai/ipai_odoo_copilot/
ls -la /workspaces/odoo/addons/ipai/ipai_odoo_copilot/__manifest__.py
```

**Check**: Directory must contain `__manifest__.py` (not `__openerp__.py`).

## Step 3: Validate Manifest

```bash
python3 -c "
import ast, sys
with open('$MODULE_PATH/__manifest__.py') as f:
    manifest = ast.literal_eval(f.read())
print('name:', manifest.get('name'))
print('version:', manifest.get('version'))
print('installable:', manifest.get('installable', True))
print('depends:', manifest.get('depends', []))
"
```

**Check**:
- `installable` must be `True` (default if absent)
- `version` should start with `19.0.`
- `depends` must list only modules that are themselves discoverable

## Step 4: Check for Name Collisions

If a module name appears in multiple addons_path entries, the first one wins:

```bash
for path in /opt/odoo/addons /workspaces/odoo/addons/oca /workspaces/odoo/addons/ipai; do
  if [ -d "$path/<module_name>" ]; then
    echo "FOUND: $path/<module_name>"
  fi
done
```

**Check**: Module should appear in exactly one path. If duplicated, the first
match in addons_path order is used.

## Step 5: Check Module State in Database

```sql
SELECT name, state, latest_version
FROM ir_module_module
WHERE name = '<module_name>';
```

| State | Meaning |
|-------|---------|
| `uninstalled` | Known but not installed |
| `installed` | Active |
| `to upgrade` | Pending upgrade on next restart |
| `to install` | Pending install on next restart |
| `uninstallable` | Manifest says `installable: False` or missing deps |

If the module is not in `ir_module_module` at all, Odoo has not discovered it.
Run module update list:

```bash
odoo-bin -d <db> --update=base --stop-after-init
# or via Odoo shell:
self.env['ir.module.module'].update_list()
```

## Step 6: Check Dependency Chain

A module is uninstallable if any of its dependencies are uninstallable:

```python
# Odoo shell
module = self.env['ir.module.module'].search([('name', '=', '<module_name>')])
print(module.state, module.dependencies_id.mapped(lambda d: (d.name, d.state)))
```

**Check**: All dependencies must be in `installed` or `uninstalled` state (not
`uninstallable`).

## Step 7: Check OCA Submodule Status

For OCA modules, verify the submodule is checked out at the correct branch:

```bash
cd addons/oca/<repo>
git branch --show-current
git log --oneline -1
```

**Check**: Branch should be `19.0`. If detached or on wrong branch, update:

```bash
git submodule update --remote addons/oca/<repo>
```

## Step 8: Check File Permissions

```bash
ls -la /workspaces/odoo/addons/ipai/<module>/
# All files should be readable by the odoo user (uid 101 in container)
```

## Common Fixes

| Problem | Fix |
|---------|-----|
| Module not in addons_path | Add the parent directory to `addons_path` in `odoo.conf` or CLI args |
| `__manifest__.py` syntax error | Fix Python syntax in manifest file |
| `installable: False` | Set to `True` or remove (defaults to `True`) |
| Missing dependency | Install the dependency first, or add its path to addons_path |
| OCA module on wrong branch | `git submodule update --remote addons/oca/<repo>` |
| Name collision | Rename one of the modules or adjust addons_path order |
| Stale module list | Run `self.env['ir.module.module'].update_list()` in Odoo shell |
| File permissions | `chown -R odoo:odoo /workspaces/odoo/addons/ipai/<module>` |

## Verification

After fixing, confirm the module is discoverable:

```bash
odoo-bin -d <db> -i <module> --stop-after-init --test-enable 2>&1 | tail -20
```

Expected: module installs without error. If `--test-enable` is used, tests run
and results appear in output.
