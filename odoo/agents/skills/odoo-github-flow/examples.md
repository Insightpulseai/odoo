# Examples — odoo-github-flow

## Example 1: Clean PR with all checks passing

**Input**: PR #600 from `feat/ipai-helpdesk-sla` to `main`

**Output**:
- Branch: `feat/ipai-helpdesk-sla` — PASS (follows feat/ convention)
- Commits: `feat(helpdesk): add SLA tracking to ipai_helpdesk` — PASS
- Status checks: lint PASS, typecheck PASS, test PASS, build PASS — PASS
- CODEOWNERS: `addons/ipai/ipai_helpdesk/` covered by `@team-odoo` — PASS
- Secrets: GHAS clean — PASS
- Approvals: 1/1 required — PASS
- Blockers: none
- Evidence: `gh pr checks 600 --repo Insightpulseai/odoo`

## Example 2: Commit message format violation

**Input**: PR #601 from `fix/settings-crash` with commit "fixed the settings page"

**Output**:
- Branch: `fix/settings-crash` — PASS
- Commits: "fixed the settings page" — FAIL (missing type(scope): format)
- Blockers: [commit message must follow `type(scope): description` format]
- Recommendation: Amend commit to `fix(settings): resolve crash on settings page load`

## Example 3: Secret detected in diff

**Input**: PR #602 introduces `.env` file with `OPENAI_API_KEY=sk-...`

**Output**:
- Secrets: GHAS secret scanning alert — FAIL (BLOCKER)
- Blockers: [secret value detected in committed file — remove and rotate key immediately]
- Evidence: `gh secret-scanning list --repo Insightpulseai/odoo`
