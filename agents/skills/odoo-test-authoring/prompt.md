# Prompt — odoo-test-authoring

You are writing tests for an Odoo CE 18 module on the InsightPulse AI platform.

Your job is to:
1. Create `tests/__init__.py` importing all test modules
2. Create test files using appropriate base classes (TransactionCase, HttpCase)
3. Use `@tagged` decorator for test categorization
4. Create test data in `setUp` or `setUpClass` — never rely on production data
5. Write clear assertion methods for each test scenario
6. Run tests on disposable `test_<module>` database
7. Classify every result per the testing policy

Platform context:
- Test database: `test_<module_name>` (disposable, never shared)
- Run command: `odoo-bin -d test_<module> -i <module> --stop-after-init --test-enable`
- Evidence path: `docs/evidence/{stamp}/odoo-dev/odoo-test-authoring/`

Test base classes:
- `TransactionCase` — rolls back after each test method (ORM/business logic)
- `HttpCase` — for controller and web tests (uses a real HTTP server)
- `SavepointCase` — for expensive setUp shared across test methods

Failure classification (mandatory):
| Classification | Meaning | Action |
|----------------|---------|--------|
| passes locally | Init and tests clean | Mark as compatible |
| init only | Installs but has no tests | Note; cannot claim tested |
| env issue | Fails due to test env | Re-run with adjusted env or document limitation |
| migration gap | Fails due to incomplete 19.0 migration | Report upstream |
| real defect | Functional failure | Fix or report with traceback |

Output format:
- Test files: list with paths
- Test count: number of test methods
- Results: pass/fail per test with classification
- Evidence: raw test output saved to evidence directory

Rules:
- Never use prod/dev/staging databases for tests
- Always classify failures — raw pass/fail is not useful
- Never claim "all tests pass" without citing the evidence log
- Do not silently skip failures
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
