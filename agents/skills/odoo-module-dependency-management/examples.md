# Examples — odoo-module-dependency-management

## Example 1: Clean dependency chain

**Input**: Validate `ipai_helpdesk` module dependencies

**Output**:
- Module: `ipai_helpdesk` v19.0.1.0.0
- Direct dependencies: `base`, `mail`, `portal`, `rating`, `ipai_workspace_core`
- Transitive chain: base -> mail -> portal -> rating -> ipai_workspace_core (all resolved)
- Missing: none
- Circular: none
- Enterprise violations: none
- Manifest alignment: present in addons.manifest.yaml — PASS
- Evidence: `addons/ipai/ipai_helpdesk/__manifest__.py` depends list

## Example 2: Enterprise dependency detected

**Input**: New module `ipai_gantt_view` depends on `web_gantt`

**Output**:
- Module: `ipai_gantt_view` v19.0.1.0.0
- Direct dependencies: `base`, `project`, `web_gantt`
- Enterprise violations: `web_gantt` is an Enterprise module — FAIL (BLOCKER)
- Blockers: [Enterprise dependency `web_gantt` violates CE-only policy]
- Recommendation: Use `web_timeline` from OCA/web or build custom gantt with ipai_* module

## Example 3: Missing OCA dependency

**Input**: Module depends on `account_reconcile_oca` but OCA repo not in addons path

**Output**:
- Missing: `account_reconcile_oca` not found in addons/oca/
- Root cause: OCA repo `account-reconcile` not listed in `.gitmodules`
- Recommendation: Add submodule `git submodule add -b 19.0 https://github.com/OCA/account-reconcile addons/oca/account-reconcile`
