# Prompt — odoo-upgrade-rehearsal

You are executing an upgrade rehearsal for an Odoo instance on a disposable database.

Your job is to:
1. Create or verify the disposable database copy exists
2. Run OpenUpgrade migration scripts against the disposable DB
3. Verify every module installs correctly post-migration
4. Check data integrity: record counts, key fields, relational consistency
5. Run automated tests on the migrated database
6. Classify every failure per testing policy
7. Produce a structured rehearsal report with evidence

Context:
- Disposable DB naming: `test_upgrade_{source_version}_to_{target_version}`
- Never use `odoo`, `odoo_dev`, `odoo_staging`, or `odoo_dev_demo`
- OpenUpgrade scripts: from `OCA/OpenUpgrade` target branch
- Custom migration scripts: from `addons/ipai/` modules

Output format:
- Source version: X.0
- Target version: Y.0
- Database: disposable DB name
- Migration execution: pass/fail with timing
- Module status: per-module pass/fail table
- Data integrity: record count comparison, key field validation
- Test results: pass/fail counts with failure details
- Failure classification: per testing policy categories
- Blockers: list of blocking issues
- Evidence: raw logs saved to evidence directory

Rules:
- NEVER run against production or canonical dev databases
- Classify every failure — no silent skips
- Save ALL raw output to evidence
- Do not claim success without data integrity verification
