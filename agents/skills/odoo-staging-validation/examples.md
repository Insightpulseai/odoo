# Examples — odoo-staging-validation

## Example 1: Clean staging validation

**Input**: Staging revision `rev-def456` deployed with `ipai_helpdesk` v18.0.1.1.0

**Output**:
- Staging: `ipai-odoo-dev-web` revision `rev-def456`, running
- Database: `odoo_staging` available, 1.2GB, production-like data confirmed
- Tests:
  - `ipai_helpdesk`: 23 passed, 0 failed, 0 skipped — passes_locally
  - `ipai_workspace_core`: 15 passed, 0 failed, 0 skipped — passes_locally
- Regressions: none (previous run: 38 passed, 0 failed)
- Blockers: none
- Evidence: `docs/evidence/20260317-1430/odoo-delivery/odoo-staging-validation/test.log`

## Example 2: Staging with classified failures

**Input**: Full regression test on staging after OCA submodule update

**Output**:
- Tests: 12 modules tested
  - 9 modules: passes_locally
  - 1 module (`account_reconcile_oca`): migration_gap — `AttributeError: 'list' object` in 18.0 port
  - 1 module (`web_favicon`): env_issue — incompatible with Odoo 18 (tracked in OCA18_COMPATIBILITY_EXCEPTIONS.md)
  - 1 module (`ipai_bir_tax_compliance`): init_only — installs but has no test methods
- Regressions: `account_reconcile_oca` is new failure (was passing in previous run)
- Blockers: [account_reconcile_oca regression — investigate OCA update]
- Evidence: `docs/evidence/20260317-1500/odoo-delivery/odoo-staging-validation/test.log`
