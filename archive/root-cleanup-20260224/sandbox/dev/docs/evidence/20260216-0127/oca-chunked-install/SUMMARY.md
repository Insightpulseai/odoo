# OCA Chunked Installation Evidence

**Date:** 2026-02-16 01:27
**Database:** odoo_dev
**Target Modules:** web_responsive, web_environment_ribbon, web_dialog_size, base_rest, base_rest_datamodel

## Installation Results

### ✅ Successfully Installed (3/5)

| Module | State |
|--------|-------|
| web_responsive | installed |
| web_environment_ribbon | installed |
| web_dialog_size | installed |

### ❌ Uninstallable (1/5)

| Module | State | Reason |
|--------|-------|--------|
| base_rest | uninstallable | Missing Python dependencies |

**Missing Dependencies for base_rest:**
- `apispec`
- `cerberus`
- `parse-accept-language`
- `pyquerystring`

### ⚠️ Not Found (1/5)

| Module | Notes |
|--------|-------|
| base_rest_datamodel | Module not found in current OCA repos or depends on base_rest |

## Overall Database State

```
     state     | count
---------------+-------
 installed     |   123
 uninstallable |    80
 uninstalled   |   649
```

## Validation Status

- ✅ **Chunked installation works:** 3 modules installed successfully in small batches
- ✅ **Timeout-resistant:** Each batch completed within agent execution limits
- ✅ **Idempotent:** Safe to rerun with `-u` flag
- ✅ **Evidence captured:** Module states and dependency analysis logged
- ⚠️ **REST framework needs deps:** Requires pip install in Odoo container

## Next Steps

To install base_rest, add Python dependencies to Odoo container:

```bash
docker-compose exec odoo pip install apispec cerberus parse-accept-language pyquerystring
docker-compose stop odoo
docker-compose run --rm odoo odoo -d odoo_dev --stop-after-init -u "base_rest"
```

## Artifacts

- `installer_output.log` - Installation command output
- `module_states.txt` - Final module states from ir_module_module
- `state_summary.txt` - Overall database state summary
- `external_deps_report.json` - Complete external dependencies analysis
