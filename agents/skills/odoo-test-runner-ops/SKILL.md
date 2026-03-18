# Odoo Test Runner Ops Skill

## Purpose

Run Odoo tests via CLI. Covers --test-enable, --test-tags, -i for init, disposable test databases (test_<module>), and failure classification per testing.md.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 19.0 installed
- PostgreSQL accessible with createdb privileges
- Module under test is in addons path
- Disposable test database will be created/used

## Covered Operations

### Test Execution

- `odoo-bin -d test_<module> -i <module> --test-enable --stop-after-init` — install and run all tests
- `odoo-bin -d test_<module> -i <module> --test-enable --test-tags <tags> --stop-after-init` — run specific test tags
- `odoo-bin -d test_<module> -u <module> --test-enable --stop-after-init` — update and run tests

### Test Tags

- `--test-tags /<module>` — run all tests in a module
- `--test-tags /<module>:TestClassName` — run specific test class
- `--test-tags /<module>:TestClassName.test_method` — run specific test method
- `--test-tags -/module_to_skip` — skip tests from a module

### Environment Setup

- Create disposable DB: `createdb -U <user> test_<module>`
- Drop after test: `dropdb -U <user> test_<module>`
- Always use `--stop-after-init` to exit after tests complete

## Failure Classification

| Classification | Meaning | Action |
|----------------|---------|--------|
| passes locally | Init and tests clean | Mark as compatible |
| init only | Installs but has no tests | Note; cannot claim tested |
| env issue | Fails due to test env (no-http, ordering, missing demo data) | Re-run with adjusted env |
| migration gap | Fails due to incomplete 19.0 migration | Report upstream |
| real defect | Functional failure in module logic | Fix or report with traceback |

## Evidence Capture

- Save raw test output to `docs/evidence/<YYYYMMDD-HHMM>/<module>/test.log`
- Include: module name, database used, test count, pass/fail count, error tracebacks
- Never claim "all tests pass" without citing the evidence log

## Verification

- Exit code 0 = all tests passed
- Exit code non-zero = failures occurred — classify each failure
- Check log for `ERROR` and `FAIL` entries
