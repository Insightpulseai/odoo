---
mode: agent
tools:
  - repo
  - tests
description: "Generate or extend Odoo unit tests for a model or utility function. Uses TransactionCase only — no mocks."
---

# Unit Test Generation

Use this prompt when a model, utility function, or Edge Function has no test coverage,
or when a new method was added without an accompanying test.

Fill in every bracketed section before invoking.

---

## Context

- **File under test**: [e.g. `addons/ipai/ipai_expense_automation/models/expense_receipt.py`]
- **Existing test file** (if any): [e.g. `addons/ipai/ipai_expense_automation/tests/test_expense_receipt.py`]
- **Missing scenario**: [1–2 lines describing what is not tested]
- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- Use `odoo.tests.common.TransactionCase` — **no** `unittest.mock`
- Tests live in `addons/ipai/<module>/tests/test_<model>.py`
- No Enterprise-only imports (`odoo.addons.account_*` beyond CE is forbidden)
- Modify **only** the test file — never the source under test
- Minimal diff: add the missing test method(s) only
- PR-only; no direct push to `main`

## Task

Read the file under test, identify the untested scenario described above, and write a
new test method that exercises it via database state (create → act → assert).
If the test file does not exist, scaffold it with the class header and the new method.

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files
```

To run the new test locally (optional — CI will run it):
```bash
odoo-bin --test-enable --stop-after-init --test-tags <ModuleName>
```

## Acceptance Criteria

- [ ] New test method exists in the correct test file
- [ ] Test uses `TransactionCase` and calls `self.env[...]` or `self.registry`
- [ ] No mock objects, no `unittest.mock` imports
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/unit-tests/logs/test_run.txt`

## Rollback

```bash
git revert <commit-hash>    # revert the test file addition
```
