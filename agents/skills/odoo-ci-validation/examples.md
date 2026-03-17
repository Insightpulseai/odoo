# Examples — odoo-ci-validation

## Example 1: All checks passing

**Input**: PR #605, all GitHub Actions workflows completed

**Output**:
- PR: #605 (`feat/ipai-helpdesk-sla`)
- Workflow runs: ci-odoo (pass), lint (pass), typecheck (pass), security (pass)
- Required checks: lint PASS, typecheck PASS, test PASS, build PASS
- Test results: 47 passed, 0 failed, 0 skipped
- Build: artifact `ipai-odoo:feat-helpdesk-sla-abc123` pushed to `cripaidev`
- Security: GHAS clean
- Blockers: none
- Evidence: `gh run list --repo Insightpulseai/odoo --branch feat/ipai-helpdesk-sla`

## Example 2: Test failure requiring classification

**Input**: PR #606, test workflow failed

**Output**:
- PR: #606 (`fix/invoice-rounding`)
- Required checks: lint PASS, typecheck PASS, test FAIL, build PASS
- Test results: 42 passed, 3 failed, 1 skipped
- Failure classification:
  1. `test_invoice_tax_rounding` — real_defect (assertion error on tax computation)
  2. `test_invoice_pdf_report` — env_issue (wkhtmltopdf not available in CI runner)
  3. `test_invoice_mail_send` — env_issue (no SMTP configured in test environment)
- Blockers: [1 real defect must be fixed before merge; 2 env issues are non-blocking]
- Evidence: `gh run view 12345 --repo Insightpulseai/odoo --log-failed`
