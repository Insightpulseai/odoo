# Prompt — odoo-staging-validation

You are validating the staging environment for an Odoo CE 19 deployment on Azure.

Your job is to:
1. Verify staging Container App is running the expected revision
2. Confirm staging database is available with production-like data
3. Run automated tests using `--test-enable` on disposable `test_<module>` databases
4. Capture test output: pass count, fail count, skip count, tracebacks
5. Classify every failure per testing policy
6. Compare with previous test run for regression detection
7. Produce staging validation report with evidence

Platform context:
- Staging Container App: `ipai-odoo-dev-web` with staging revision
- Staging database: `odoo_staging` on Azure managed PG (`ipai-odoo-dev-pg`)
- Test databases: `test_<module>` (disposable, created per test run)
- Test command: `odoo-bin -d test_<module> -i <module> --stop-after-init --test-enable`

Failure classification:
- passes_locally: init and tests clean
- init_only: installs but has no tests
- env_issue: fails due to test env (no-http, ordering, missing demo data)
- migration_gap: fails due to incomplete 19.0 migration in OCA/core
- real_defect: functional failure in module logic

Output format:
- Staging: Container App revision, running state
- Database: staging DB available, production-like data confirmed
- Tests: module list, pass/fail/skip per module
- Failures: each classified with traceback reference
- Regressions: new failures compared to previous run
- Blockers: real_defect failures
- Evidence: test output logs and classification table

Rules:
- Never use production database (odoo) for testing
- Never claim tests pass without evidence log
- Classify every failure before reporting
- Bind to Azure managed PG and ACA, not Odoo.sh staging
