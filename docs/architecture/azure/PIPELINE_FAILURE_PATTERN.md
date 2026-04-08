# Azure DevOps pipeline failure pattern — 2026-03-18

## Observed surface

Project:
- `ipai-platform`

View:
- Azure DevOps → Pipelines → Runs
- Azure DevOps → Pipelines (definitions list)

## Pipeline definitions (confirmed from AzDO UI)

Only two pipeline definitions exist in `ipai-platform`:

| Pipeline | Last run | Trigger | Current status |
|----------|----------|---------|----------------|
| `ci-validation` | `#20260317.36` (PR #609) | Automatic (push/PR) | **Failing — this is the current incident** |
| `azure-infra-deploy` | Mar 11 | Manual | Separate concern |

The current fast-fail regression is specifically in `ci-validation`.
`azure-infra-deploy` is a separate problem and is not the immediate source of the blanket red runs.

## Evidence from run list

Observed characteristics:

- many consecutive recent runs of `ci-validation` failed
- failures span unrelated commit types:
  - docs
  - governance
  - dependencies
  - Azure/Odoo/Foundry config
  - architecture/spec changes
- most runs complete in `<1s`
- stage failure pattern appears highly uniform
- earlier runs around self-hosted pool / Foundry config changes show more mixed behavior than later blanket failures

## Root cause analysis

### Pipeline YAML audit

| File | Pool | External deps | Issue |
|------|------|---------------|-------|
| `azure-pipelines-ci.yml` | `ubuntu-latest` | None | OK — inline scripts only |
| `.azure/pipelines/ci-cd.yml` | `ipai-build-pool` (self-hosted) | `Insightpulseai/infra` templates via `github-insightpulseai` SC, `vg-ipai-platform-secrets` VG | **Divergent from SSOT** — pool + external deps |
| `infra/ci/azure-pipelines.yml` | `ubuntu-latest` | `azure-ipai-config` VG, `azure-ipai` SC | **Broken template path** |

### SSOT canonical configuration

`ssot/azure/azure_devops.yaml`:
- default pool: `ubuntu-latest`
- fallback: `self-hosted-if-vnet-required`

### Specific issues found

1. **Pool divergence**: `.azure/pipelines/ci-cd.yml` references `ipai-build-pool` (self-hosted) in 5 stages, contradicting SSOT `ubuntu-latest` default
2. **Template path**: `infra/ci/azure-pipelines.yml` references `pipelines/templates/deploy-bicep.yml` — resolves to `infra/ci/pipelines/templates/deploy-bicep.yml` which doesn't exist. Correct path: `../pipelines/templates/deploy-bicep.yml`
3. **External dependencies**: `ci-cd.yml` requires `github-insightpulseai` service connection and `vg-ipai-platform-secrets` variable group — if either is missing/broken, pipeline fails at parse time

## Interpretation

This pattern is most consistent with CI bootstrap/orchestration failure rather than commit-specific validation failure.

Primary fault domains:
1. Agent pool selection — self-hosted `ipai-build-pool` with no available agents
2. Shared pipeline template breakage — broken relative path for deploy templates
3. Missing variable group / secret / service connection
4. Early checkout/auth/bootstrap failure

## Fix applied

- `.azure/pipelines/ci-cd.yml`: migrated lint/build stages from `ipai-build-pool` to `vmImage: ubuntu-latest`; deploy stages use `$(deployPool)` variable (defaults to `ipai-build-pool`) to preserve VNet/private-network access if needed
- Corrected `infra/ci/azure-pipelines.yml` template path (2 locations)

The pool migration for lint/build stages is a recovery hypothesis, not a confirmed root cause fix. It should be treated as a staged mitigation until validated by:
- Milestone A: a docs-only run succeeds
- Milestone B: an addons/ipai run succeeds on hosted bootstrap
- Milestone C: a deploy-stage run proves whether hosted or self-hosted is required

## Primary unknown

**Which YAML file does the `ci-validation` pipeline definition point to?**

The most likely candidate is `azure-pipelines-ci.yml` (repo root) — name matches, triggers match. But this cannot be confirmed from the repo alone; it must be checked in the AzDO pipeline definition UI.

If `ci-validation` points to `azure-pipelines-ci.yml`, then:
- The pipeline uses `vmImage: ubuntu-latest` (no pool issue)
- The pipeline has no variable groups or external templates (no bootstrap dependency issue)
- The most likely failure point is the **GitHub service connection used for repo checkout** — if `github-insightpulseai` is broken, every run fails at checkout before any stage

If `ci-validation` points to `.azure/pipelines/ci-cd.yml` instead, then:
- The pool migration and `deployPool` variable changes are directly relevant
- The external template fetch and variable group dependencies are failure candidates

## Next diagnostic step

1. Open the `ci-validation` pipeline definition in AzDO
2. Confirm the YAML path
3. Open one failing docs/governance run
4. Inspect the first failing stage/job/task

Until that is known, repo-side fixes are speculative.

## Non-conclusions

This evidence does not identify the exact failing task from AzDO logs (screenshots only show run list, not job logs).

## Current status

- CI health: degraded → partial fix applied, pending validation
- Failing pipeline: `ci-validation` (confirmed)
- Primary unknown: YAML binding for `ci-validation`
- Validation trustworthiness: low until first failing task is inspected
- Code-quality signal from current runs: unreliable

## Related

- Issue #567: original Managed DevOps Pool authorization blocker
- `ssot/azure/azure_devops_ci_health.yaml`: machine-readable status
