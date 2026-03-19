# Odoo Developer Tools (Debug Mode) — IPAI Usage Guide

Reference for using Odoo's developer mode with the IPAI module stack.

## Official Documentation References

| Topic | URL |
|-------|-----|
| Developer mode overview | https://www.odoo.com/documentation/19.0/applications/general/developer_mode.html |
| Developer docs hub | https://www.odoo.com/documentation/18.0/developer.html |
| Frontend Assets (JS/CSS/SCSS) | https://www.odoo.com/documentation/18.0/developer/reference/frontend/assets.html |
| Backend Actions | https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html |
| Unit Tests | https://www.odoo.com/documentation/18.0/developer/tutorials/unit_tests.html |

## Enabling Developer Mode

### UI Method
Settings → Developer Tools → Click one of:
- Activate developer mode
- Activate developer mode (with assets)
- Activate developer mode (with tests assets)

### URL Method (Fast + Scriptable)

```bash
# Standard debug mode
https://erp.insightpulseai.com/odoo/web?debug=1

# With unminified assets (for JS/CSS debugging)
https://erp.insightpulseai.com/odoo/web?debug=assets

# With test bundles
https://erp.insightpulseai.com/odoo/web?debug=tests

# Turn off
https://erp.insightpulseai.com/odoo/web?debug=0
```

> **Note**: Put `?debug=...` **before** the `#` in deep URLs:
> `https://erp.insightpulseai.com/odoo/web?debug=assets#action=123`

## Debug Mode Comparison

| Mode | Flag | Use Case |
|------|------|----------|
| Standard | `debug=1` | Technical menus, model/view introspection, External IDs |
| With Assets | `debug=assets` | OWL/JS/SCSS debugging, unminified bundles, trace frontend errors |
| With Tests | `debug=tests` | QUnit tests, test-only JS assets, dev/test scenarios |

## IPAI Implementation Workflows

### 1. Validate Module Install/Upgrade (No UI Breakage)

Use **developer mode** (`debug=1`) to inspect runtime objects:

**Settings → Technical → User Interface:**
- Views: Confirm XML loaded, no parse errors, inheritance applied
- Menus: Confirm menu items exist and link to actions
- Actions: Confirm actions target correct models/views

**Settings → Technical → Database Structure:**
- Models/Fields: Confirm model registry contains expected objects

**CLI verification:**
```bash
# Install module with stop-after-init
odoo -c /etc/odoo/odoo.conf -d prod -i ipai_agent_core --stop-after-init 2>&1 | tee install.log

# Upgrade module
odoo -c /etc/odoo/odoo.conf -d prod -u ipai_platform_theme --stop-after-init 2>&1 | tee upgrade.log

# Check for errors
grep -E "(ERROR|CRITICAL|Traceback)" install.log
```

### 2. Debug Theme/WorkOS/Ask AI UI Issues

Use **developer mode with assets** (`debug=assets`) for:
- OWL console errors
- Missing JS modules
- SCSS token build issues
- Stale bundle caching after deploy

**Workflow:**
1. Load with assets: `?debug=assets`
2. Hard refresh (Ctrl+Shift+R)
3. Open DevTools Console + Network tab
4. Trace failing asset to source module

**Common issues:**
```
Module        | Symptom                    | Check
--------------|----------------------------|---------------------------
ipai_platform_theme | Tokens not applying   | tokens.scss in bundle
ipai_theme_tbwa_backend | Wrong colors     | Override order in assets.xml
ipai_ask_ai   | Chat panel not showing     | ask_ai_systray.js loading
ipai_workos_* | OWL component errors       | Component registration
```

### 3. Run Frontend Tests

Use **developer mode with tests** (`debug=tests`) for:
- QUnit test bundles
- Module test execution
- Dev/test scenario validation

**Running tests:**
```bash
# CLI test runner
odoo -c /etc/odoo/odoo.conf -d test_db --test-enable --test-tags /ipai --stop-after-init

# Specific module tests
odoo -c /etc/odoo/odoo.conf -d test_db --test-enable -i ipai_agent_core --stop-after-init
```

## IPAI Module Verification Checklist

For each ipai_* module, verify:

- [ ] **Manifest**: Valid Python dict, correct depends, no enterprise-only deps
- [ ] **Python**: No syntax errors (`python -m compileall`)
- [ ] **XML**: All views/data files parse without error
- [ ] **Security**: ir.model.access.csv exists and is valid
- [ ] **Install**: Module installs without traceback
- [ ] **Upgrade**: Module upgrades without traceback
- [ ] **UI**: Menu items visible, views render, actions work
- [ ] **Assets**: JS/CSS bundles load (check in debug=assets)

## Quick Reference Commands

```bash
# Enable debug mode via CLI (set in odoo.conf)
# Not recommended for production

# Check module state
psql -d prod -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;"

# Force asset regeneration
psql -d prod -c "DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';"

# View all custom fields (x_*)
psql -d prod -c "SELECT model, name, ttype FROM ir_model_fields WHERE name LIKE 'x_%' ORDER BY model, name;"
```

## Related Documentation

- [CE_OCA_EQUIVALENTS_AUDIT.md](./CE_OCA_EQUIVALENTS_AUDIT.md) - Enterprise vs OCA parity
- [ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md](./ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md) - Security review
- [artifacts/ipai_quality_gate.json](../artifacts/ipai_quality_gate.json) - Quality gate results
