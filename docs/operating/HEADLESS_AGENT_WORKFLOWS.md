# Headless Agent Workflows

Non-interactive agent runs (CI, scheduled, background). IPAI's runtime is Azure Pipelines per CLAUDE.md; GHA is scoped-exception only for PR validation.

---

## Canonical workflows

| Workflow | Trigger | Surface | Authority |
|---|---|---|---|
| Issue triage | new GitHub Issue | GitHub Actions (scoped exception) or Azure Pipelines PR validation | [azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml) |
| PR review | PR opened | Azure Pipelines `azure-pipelines-pr.yml` | [CLAUDE.md§Engineering & Delivery Authority](../../CLAUDE.md) |
| Release note generation | tag push / release | Azure Pipelines | [ssot/release/release_contract.yaml](../../ssot/release/release_contract.yaml) |
| Blocker summarization | weekly | Azure Pipelines scheduled | [go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml) |
| Drift detection | daily | Azure Pipelines scheduled | [azure-resource-inventory.yaml](../../ssot/architecture/azure-resource-inventory.yaml) |
| Evidence pack generation | on demand | Azure Pipelines | `docs/evidence/` |
| SSO health check | hourly | Azure Pipelines | [odoo-sso-runtime-state.yaml](../../ssot/odoo/odoo-sso-runtime-state.yaml) |
| Eval gate | pre-release | `azure-pipelines-eval-gate.yml` | [ssot/agent-platform/agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml) |
| Contract checks | PR | `azure-pipelines-contract-checks.yml` | Import boundary + SSOT YAML load |

---

## Rules

1. **No interactive prompts** — headless runs never ask questions; they continue everything executable and report blockers
2. **Structured output only** — markdown with explicit `PASS` / `FAIL` + evidence lines
3. **Secrets from Azure Key Vault** via workload identity; never env vars with real values
4. **Azure Pipelines is canonical** — GHA only for scoped exceptions (see [CLAUDE.md](../../CLAUDE.md))
5. **Evidence written to `docs/evidence/<ts>/<scope>/`** with correlation id
6. **Fail closed** — any uncaught exception = exit non-zero + post to action group

---

## Issue triage workflow

**Trigger**: new GitHub Issue on `Insightpulseai/*`

**Steps**:
1. Parse issue title + body
2. Classify against 12 canonical Area Paths (see [azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml))
3. Suggest Epic binding + tag set
4. Post suggestion as Issue comment (one comment per PR, idempotent)
5. Never auto-assign; human owner required

**Forbidden**: auto-closing issues, auto-assigning humans, creating ADO work items without approval

---

## PR review workflow

**Trigger**: PR opened / updated

**Steps**:
1. Run ruff + mypy on changed files
2. Run pytest on affected test paths
3. Check for `agent_framework` imports outside `agent-platform/src/agent_platform/` (import boundary)
4. Check for secrets (grep for high-entropy strings, known secret patterns)
5. Check for deprecated services (Supabase / Vercel / Cloudflare Workers / n8n / etc.)
6. Post review summary to PR

**Forbidden**: auto-approving, auto-merging, bypassing branch protection

---

## Release note generation

**Trigger**: release tag push

**Steps**:
1. Read commits between previous tag and new tag
2. Group by conventional commit scope
3. Reference Epic/Issue IDs in description
4. Draft release notes to `docs/evidence/<ts>/release-notes/<tag>.md`
5. Post to ADO release as attachment (not auto-publish)

---

## Blocker summarization (weekly)

**Trigger**: cron weekly (Fri 15:00 Asia/Manila)

**Steps**:
1. Scan all `docs/evidence/<ts>/go-live-readiness-review/blocker-register.yaml` files
2. Aggregate open blockers by severity
3. Emit `docs/evidence/<ts>/weekly-blocker-summary.md`
4. Post summary to platform-architecture Slack (if Slack MCP allowlisted) or action group email

---

## Drift detection (daily)

**Trigger**: cron daily 02:00 UTC

**Steps**:
1. `az graph query` against current Azure state
2. Compare to [platform/ssot/azure/resource-inventory.dev.yaml](../../platform/ssot/azure/resource-inventory.dev.yaml)
3. Emit drift report to `docs/evidence/<ts>/azure-resource-inventory-drift/`
4. If drift detected, post to action group

**Forbidden**: auto-correcting drift (must surface for human review)

---

## SSO health check (hourly)

**Trigger**: cron hourly

**Steps**:
1. `curl -I https://erp.insightpulseai.com` expect HTTP 200/302
2. Verify OAuth endpoint reachable
3. Emit ok/fail to Log Analytics

**Forbidden**: actually attempting SSO login (needs human credentials)

---

## Evidence pack generation (on demand)

**Trigger**: manual invocation

**Steps**:
1. Read inputs (commit range, scope, evidence type)
2. Assemble evidence bundle under `docs/evidence/<ts>/<scope>/`
3. Include: summary.md + raw outputs + verification lines
4. No execution (read-only)

---

## Eval gate (pre-release)

**Trigger**: `azure-pipelines-eval-gate.yml`

**Steps**:
1. Run eval scenarios per [ssot/release/feature-ship-readiness-gates.yaml](../../ssot/release/feature-ship-readiness-gates.yaml)
2. Score against `ssot/eval/gates.yaml` (in `agent-platform/`)
3. Fail build if threshold not met
4. Emit scorecard to evidence

---

## Contract checks (PR)

**Trigger**: `azure-pipelines-contract-checks.yml` on PR

**Checks**:
- All YAML files under `ssot/`, `platform/ssot/`, `infra/ssot/` load cleanly
- Import boundary: `agent_framework` imports only under `agent-platform/src/agent_platform/`
- No hardcoded secrets (entropy + pattern scan)
- Deprecated service references flagged
- CLAUDE.md deprecation list enforced

**Fail build** on violation.

---

## Non-goals

- Not running deploys via GHA (Azure Pipelines is sole deploy authority)
- Not auto-approving or auto-merging
- Not auto-correcting drift
- Not using GHA minutes outside Azure-subscription billing (per CLAUDE.md scoped exception)
- Not storing secrets in workflow env vars (Key Vault + OIDC federation)

---

## Related

- [CLAUDE_CODE_OPERATING_STANDARD.md](CLAUDE_CODE_OPERATING_STANDARD.md)
- [SESSION_LIFECYCLE.md](SESSION_LIFECYCLE.md)
- [ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml)
- [ssot/governance/gha-scoped-exception.yaml](../../ssot/governance/gha-scoped-exception.yaml) (GHA allowed scope)
- [ssot/release/go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml)
