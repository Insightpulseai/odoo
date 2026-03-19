# Examples — odoo-dev-to-staging-promotion

## Example 1: Clean promotion

**Input**: Branch `feat/ipai-helpdesk-sla` merged to dev, CI green, ready for staging

**Output**:
- Source branch: `dev`, commit `abc1234`
- CI status: lint PASS, test PASS, build PASS — all green
- Developer evidence: `docs/evidence/20260317-1200/odoo-delivery/odoo-ci-validation/` — PASS
- Blockers: none
- Staging revision: `rev-staging-xyz789` deployed, health check 200
- Database: migration completed (1 new table, 2 altered columns)
- Rollback: previous revision `rev-staging-xyz788`, DB backup at 2026-03-17T11:55:00Z
- Evidence: `docs/evidence/20260317-1300/odoo-delivery/odoo-dev-to-staging-promotion/`

## Example 2: Blocked promotion

**Input**: Dev branch has failing CI check

**Output**:
- Source branch: `dev`, commit `def5678`
- CI status: lint PASS, test FAIL, build PASS
- Developer evidence: CI validation shows real_defect in `ipai_helpdesk`
- Blockers: [test failure classified as real_defect — must be fixed before promotion]
- Promotion: BLOCKED — do not proceed until blocker resolved
