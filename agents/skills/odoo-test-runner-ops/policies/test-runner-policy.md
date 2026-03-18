# Test Runner Policy

## Database Rules

- Always use disposable databases: test_<module_name>
- Never use canonical databases (odoo_dev, odoo_staging, odoo) for tests
- Drop test databases after test completion
- Create fresh database for each test run (no reuse)

## Evidence Requirements

- Every test run must produce evidence in docs/evidence/<YYYYMMDD-HHMM>/<module>/test.log
- Evidence must include: module name, database used, test count, pass/fail count
- Error tracebacks must be captured in full
- Never claim "all tests pass" without citing the evidence log path

## Failure Classification Rules

- Every failure must be classified using the 5-category matrix
- Classification must be documented alongside the test evidence
- "passes locally" is the only classification that means "ready"
- "init only" means the module installs but has no tests — cannot claim tested
- "env issue" requires documentation of the specific environment problem
- "migration gap" must be reported upstream if it is in OCA code
- "real defect" requires a fix or a filed issue

## Batch Testing

- Batch test results must include per-module pass/fail
- Failed modules must be individually classified
- Do not report aggregate pass rate without per-module detail

## CI Integration

- Test runner scripts should exit with appropriate codes (0=pass, 1=fail, 2=timeout)
- CI workflows should use these scripts, not ad-hoc test commands
- Test evidence should be uploaded as CI artifacts
