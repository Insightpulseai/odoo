---
mode: agent
tools:
  - repo
  - tests
  - search
description: "Root-cause a failing CI test. Produces minimal fix or isolation strategy. Never deletes tests or adds noqa silencers without justification."
---

# Diagnose Test Failures

Use this prompt when CI reports a test failure and the log is cryptic,
a previously passing test now fails after an unrelated change, or a flaky test
needs root-cause analysis.

Fill in every bracketed section before invoking.

---

## Context

- **CI run or log excerpt**: [paste ≤50 lines of error + traceback, or link to run]
- **Test file**: [e.g. `addons/ipai/ipai_expense_automation/tests/test_expense_receipt.py`]
- **Failing test method**: [e.g. `test_ocr_receipt_creates_expense`]
- **Last breaking commit diff**:

```bash
git diff HEAD~1 HEAD -- <affected-file>
```

[paste output here]

- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- Never delete a failing test to make CI green
- Never add `# noqa`, `# type: ignore`, or `@unittest.skipIf` without a justification comment
- Never modify unrelated files — minimal diff only
- Fix the root cause, not the symptom
- PR-only; no direct push to `main`

## Task

1. Read the failing test file and the source file it tests.
2. Read the last breaking commit diff provided above.
3. Identify the root cause (not just "this line failed").
4. Propose the minimal change that makes the test pass without deleting or skipping it.
5. If flaky: propose `@unittest.skipIf` with a justification comment, or a fixture-level
   isolation change — never test deletion.

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files
odoo-bin --test-enable --stop-after-init --test-tags <ModuleName>   # if Odoo test
pytest <test-file> -v                                                # if pytest
```

## Acceptance Criteria

- [ ] Root cause identified and documented in the PR body
- [ ] Failing test now passes without deletion or unconditional skip
- [ ] No `# noqa` / `# type: ignore` added without a justification comment
- [ ] Only the failing test file and its direct source are modified
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/diagnose-tests/logs/diagnosis.txt`

## Rollback

```bash
git revert <commit-hash>    # revert the fix; re-investigate
```
