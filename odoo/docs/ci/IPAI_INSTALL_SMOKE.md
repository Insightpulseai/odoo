# IPAI Odoo Install Smoke Test

## Overview

The IPAI Install Smoke Test validates that all IPAI modules and their dependencies can be hydrated, planned for installation, and verified in ephemeral CI databases without affecting production or staging environments.

**Note:** This test performs hydration validation and install-plan simulation, not live Odoo module installation.

This is a **Phase 0** validation gate that runs on every PR touching:
- `addons/ipai/**`
- `ssot/odoo/ipai-install-baseline.yaml`
- CI validation scripts
- The workflow itself

## Purpose

Phase 0 requires that the Odoo/OCA/IPAI substrate exists and can be verified deterministically before any Pulser behavior, MCP wiring, or agent integration depends on it.

This workflow proves:
1. ✅ All IPAI modules exist in the codebase
2. ✅ All modules have valid `__manifest__.py` files
3. ✅ All declared dependencies are satisfied
4. ✅ No deprecated modules are used in CI-required groups
5. ✅ Install planning never targets production/staging databases
6. ✅ Evidence is generated for audit and replay

## Architecture

### Files and Responsibilities

```
ssot/odoo/ipai-install-baseline.yaml
├─ Defines install groups (core_minimal, pulser_chat, bir_tax_compliance, etc.)
├─ Lists approved modules per group
├─ Declares module metadata (status, dependencies, deprecation)
└─ Sets CI database name allowlist/blocklist

scripts/ci/validate_odoo_addons_hydration.py
├─ Reads ipai-install-baseline.yaml
├─ Verifies all modules exist
├─ Validates __manifest__.py syntax
├─ Checks dependency closure
├─ Rejects deprecated modules in required groups
└─ Outputs: hydration-report.json

scripts/ci/install_ipai_modules.py
├─ Validates database name against allowlist
├─ Blocks access to forbidden databases (production/staging/default)
├─ Simulates install plan for specified module group (no actual Odoo invocation)
├─ Builds dependency graph
├─ Generates install evidence (install-report.json, module-dependency-graph.json)
└─ All operations are CI-safe (no database mutations)

.github/workflows/ipai-odoo-install-smoke.yml
├─ Runs on: PR, push to main/develop, merge_group
├─ Hydration job: Validates module structure
├─ Install jobs: Simulates install plan for core_minimal, pulser_chat, bir_tax_compliance
├─ Evidence gate: Ensures all reports generated, no forbidden DB names
└─ Artifacts: Retained for 30 days, downloadable from Actions
```

### Install Groups

#### `core_minimal` (CI-required)
- **Modules:** `ipai_finops_compliance_core`, `ipai_environment_guard`
- **Purpose:** Minimal IPAI runtime substrate; blocks all other groups
- **Order:** 1 (runs first)
- **Why:** Policy authority, action registry, namespace boundaries

#### `pulser_chat` (CI-required)
- **Modules:** `ipai_finops_compliance_core`, `ipai_pulser_chat`
- **Purpose:** User-facing agentic ERP interface (UI-only)
- **Order:** 2
- **Why:** Pulser chat right-rail requires policy authority

#### `bir_tax_compliance` (CI-required)
- **Modules:** `ipai_finops_compliance_core`, `ipai_l10n_ph_bir`, `ipai_bir_compliance`, `ipai_tax_review`, `ipai_tax_intelligence`
- **Purpose:** Philippine BIR tax compliance (evidence, extraction, filing)
- **Order:** 3
- **Why:** Phase 0 requires first BIR evidence workflow validation

#### `finance_close`, `expense_liquidation` (Optional)
- For future validation; not currently in CI-required path

#### `full_dev_smoke` (Manual dispatch only)
- Dynamically includes all non-deprecated IPAI modules
- Label-triggered or manual workflow dispatch
- Comprehensive smoke test; not part of default PR runs

## Running Locally

### Validate Hydration

```bash
cd odoo
python3 scripts/ci/validate_odoo_addons_hydration.py .
```

Output: `evidence/ci/ipai-install/hydration-report.json`

### Simulate Installation

```bash
cd odoo
python3 scripts/ci/install_ipai_modules.py \
    --odoo-root . \
    --install-group core_minimal \
    --db-name ci_odoo_test_core
```

Outputs:
- `evidence/ci/ipai-install/install-report.json`
- `evidence/ci/ipai-install/module-dependency-graph.json`

### Full CI-like Run

```bash
# Hydration
python3 scripts/ci/validate_odoo_addons_hydration.py .

# Install each group
python3 scripts/ci/install_ipai_modules.py \
    --odoo-root . \
    --install-group core_minimal \
    --db-name ci_odoo_core_minimal

python3 scripts/ci/install_ipai_modules.py \
    --odoo-root . \
    --install-group pulser_chat \
    --db-name ci_odoo_pulser_chat

python3 scripts/ci/install_ipai_modules.py \
    --odoo-root . \
    --install-group bir_tax_compliance \
    --db-name ci_odoo_bir_compliance
```

## Evidence Structure

Each run generates JSON evidence in `evidence/ci/ipai-install/`:

### `hydration-report.json`

```json
{
  "timestamp": "2026-04-27T...",
  "odoo_root": "/path/to/odoo",
  "config_path": "ssot/odoo/ipai-install-baseline.yaml",
  "validation_results": {
    "modules": {
      "ipai_finops_compliance_core": {
        "status": "found",
        "path": "/path/to/addons/ipai/ipai_finops_compliance_core",
        "manifest_status": "valid",
        "manifest": {
          "name": "Financial Operations Compliance Core",
          "version": "18.0.1.0.0",
          "depends": []
        }
      }
    },
    "install_groups": { ... },
    "dependencies": { ... }
  },
  "summary": {
    "total_modules": 15,
    "found_modules": 15,
    "missing_modules": 0,
    "manifest_errors": 0,
    "deprecated_in_required": 0
  }
}
```

### `install-report.json`

```json
{
  "timestamp": "2026-04-27T...",
  "environment": "ci",
  "install_group": "core_minimal",
  "database": "ci_odoo_core_minimal",
  "requested_modules": ["ipai_finops_compliance_core", "ipai_environment_guard"],
  "success": true,
  "errors": []
}
```

### `module-dependency-graph.json`

```json
{
  "dependency_graph": {
    "ipai_finops_compliance_core": {
      "name": "ipai_finops_compliance_core",
      "status": "active",
      "declared_dependencies": [],
      "transitive": []
    },
    "ipai_pulser_chat": {
      "name": "ipai_pulser_chat",
      "status": "active",
      "declared_dependencies": ["ipai_finops_compliance_core"],
      "transitive": ["ipai_finops_compliance_core"]
    }
  }
}
```

## CI Acceptance Criteria

✅ **Must pass all of:**
- Hydration validation succeeds (all modules found, manifests valid)
- Install group `core_minimal` smoke-installs (no missing dependencies)
- Install group `pulser_chat` smoke-installs
- Install group `bir_tax_compliance` smoke-installs
- Evidence JSON files are generated
- No forbidden database names in evidence (no `odoo`, `odoo_prod`, `odoo_staging`, `defaultdb`)
- No production/staging/default database mutation possible

❌ **Fails if any of:**
- Module missing or not found
- `__manifest__.py` invalid or missing
- Dependency closure incomplete
- Deprecated module in CI-required group
- Evidence not generated
- Forbidden database name appears in evidence

## Integration with Phase 0 Execution

This smoke test validates the **substrate** before any Pulser behavior depends on it.

Phase 0 sequence:
```
1. ✓ CI hydration/install validation (THIS WORKFLOW)
2. ⏳ ipai_pulser_chat right-rail behavior parity
3. ⏳ ipai_finops_compliance_core action registry
4. ⏳ PulserOdooMCPServer contract
5. ⏳ First BIR certificate review evidence path
6. ⏳ Foundry eval + Guardrails integration
```

## Adding New IPAI Modules to Phase 0

To add a new module to this smoke test:

1. **Create the module** under `addons/ipai/your_module_name/` with `__manifest__.py`
2. **Update `ssot/odoo/ipai-install-baseline.yaml`:**
   - Add module metadata under `modules:`
   - Add to one or more `install_groups:` if it should be CI-tested
   - Set `status: "active"` (or `"deprecated"` if old)
   - Declare `depends_on:` accurately
3. **Run validation locally:**
   ```bash
   python3 scripts/ci/validate_odoo_addons_hydration.py .
   ```
4. **Run install simulation:**
   ```bash
   python3 scripts/ci/install_ipai_modules.py \
       --odoo-root . \
       --install-group your_group \
       --db-name ci_odoo_test_your_group
   ```
5. **Verify evidence generated:**
   ```bash
   ls -la evidence/ci/ipai-install/
   ```

## Constraints (Hard)

🔒 **Non-negotiable:**
- No production database access
- No staging database access
- No database mutations outside ephemeral CI targets
- No deployment
- No tenant changes
- No Foundry resource changes
- No Partner Center changes
- No SDK installation
- No runtime behavior changes outside CI scripts/workflow

## Troubleshooting

### "Module not found" Error

**Symptom:** Hydration or install fails with "Module not found"

**Cause:** Module directory does not exist under `addons/oca/`, `addons/ipai/`, `addons/local/`, or standard addon path

**Fix:**
```bash
# Verify module exists
ls -la addons/ipai/your_module/

# Verify __manifest__.py exists
ls -la addons/ipai/your_module/__manifest__.py
```

### "Manifest syntax error" Error

**Symptom:** Hydration fails with "no valid __manifest__.py"

**Cause:** `__manifest__.py` is malformed (not valid Python dict or list syntax)

**Fix:**
```bash
# Validate manifest syntax
python3 -c "
import ast
with open('addons/ipai/your_module/__manifest__.py') as f:
    ast.literal_eval(f.read())
print('✓ Manifest syntax valid')
"
```

### "Dependency not found" Error

**Symptom:** Install fails with missing dependency

**Cause:** `depends_on` lists a module that doesn't exist

**Fix:**
```bash
# Check declared dependencies in ssot/odoo/ipai-install-baseline.yaml
# Verify each dependency module exists
# Update manifest `__manifest__.py` 'depends' field
```

### "Forbidden database name" Error

**Symptom:** Install fails or evidence validation rejects database name

**Cause:** Database name matches forbidden pattern (production/staging/default)

**Fix:** Use only CI-safe database names:
- `ci_odoo_*` (e.g., `ci_odoo_test_core`)
- `odoo_test_*` (e.g., `odoo_test_bir_compliance`)

## Maintenance

- **Review and update** `ipai-install-baseline.yaml` when:
  - New IPAI modules are added
  - Modules are deprecated
  - Dependencies change
  - Install groups change priority or members

- **Monitor evidence** for:
  - Repeated dependency resolution failures
  - Slow installs (>60s per group)
  - Manifest errors

- **Keep workflow green** by:
  - Running validation locally before pushing
  - Ensuring all manifest files are valid Python
  - Declaring all dependencies accurately
  - Not using forbidden database names in evidence

## Related Documentation

- [PULSER_ACCELERATOR_STACK.md](../../../docs/architecture/PULSER_ACCELERATOR_STACK.md) — Full packaging strategy
- [CLAUDE.md](../CLAUDE.md) — Project operating contract
- [ipai-install-baseline.yaml](../../ssot/odoo/ipai-install-baseline.yaml) — Install configuration
