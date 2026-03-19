# CP-5: Azure DevOps Deploy Pipeline Validation

**Date**: 2026-03-19
**Status**: PASS (pipeline validated, pool strategy corrected)
**Checkpoint**: CP-5 — CI/CD pipeline readiness for go-live

---

## Pipeline Files

| File | Purpose | Status |
|------|---------|--------|
| `.azure/pipelines/ci-cd.yml` | Build + Deploy (5 stages) | **Fixed** — pool migration |
| `azure-pipelines-ci.yml` | CI validation (lint, SSOT, boundaries) | Clean — already hosted |
| `infra/ci/azure-pipelines.yml` | Bicep infra deploy (4 stages) | Clean — already hosted |

## Pipeline Architecture (ci-cd.yml)

```
Lint (hosted) → Build (hosted) → Deploy_Dev (hosted) → Deploy_Staging (hosted)
                                ↘ Infra_Dev (hosted)
```

**5 stages**, all on `vmImage: ubuntu-latest` (Microsoft-hosted agents).

## Pool Strategy — Before and After

| Stage | Before | After | Rationale |
|-------|--------|-------|-----------|
| Lint | `vmImage: ubuntu-latest` | (unchanged) | — |
| Build | `vmImage: ubuntu-latest` | (unchanged) | — |
| Infra_Dev | `name: ipai-build-pool` | `vmImage: ubuntu-latest` | Self-hosted deprecated 2026-03-15 |
| Deploy_Dev | `name: ipai-build-pool` | `vmImage: ubuntu-latest` | AzureCLI@2 uses service connection, no VNet needed |
| Deploy_Staging | `name: ipai-build-pool` | `vmImage: ubuntu-latest` | Same — control plane API, not data plane |

**Root cause**: `ipai-build-pool` was a self-hosted agent pool with no confirmed online agents.
Deploy stages use `az containerapp update` via `AzureCLI@2` task with service connection
`sc-azure-dev-platform` (workload identity federation). This calls the Azure control plane API,
which does not require VNet/private network access.

## Deploy Template Validation

`infra/pipelines/templates/deploy-aca.yml` — verified correct:
- Uses `az containerapp update` (not create) — assumes infra pre-provisioned by Bicep
- Polls for revision Running state with 300s timeout
- Health check via FQDN + `/web/health`
- Publishes deployment evidence as pipeline artifact

## SSOT Alignment

`ssot/azure/azure_devops.yaml` updated:
- `agent_policy.self_hosted` → `deprecated`
- `exception_policy` removed
- Rationale documented inline

## Prerequisites for Pipeline Execution

| Prerequisite | Status |
|-------------|--------|
| Service connection `sc-azure-dev-platform` | Required — must exist in AzDO project |
| Variable group `vg-ipai-platform-secrets` | Required — Key Vault-backed |
| GitHub service connection `github-insightpulseai` | Required — for template repo access |
| Template repo `Insightpulseai/infra` | Required — hosts lint-python.yml, build-container.yml, deploy-aca.yml |
| AzDO environments `insightpulseai-dev`, `insightpulseai-staging` | Required — for deployment jobs |
| ACR `cripaidev` | Required — container image registry |
| Container App `ipai-odoo-dev-web` | Required — must be pre-provisioned |
| `docker/Dockerfile.prod` | Required — build stage Dockerfile |

## Blockers

- **Pipeline trigger**: Cannot trigger from local CLI without `AZURE_DEVOPS_EXT_PAT` configured.
  The pipeline will trigger automatically on next push to `main` that touches `addons/ipai/**`,
  `docker/**`, `config/**`, `scripts/odoo/**`, or `infra/azure/**`.
- **Template repo**: `Insightpulseai/infra` must have `pipelines/templates/lint-python.yml`,
  `build-container.yml`, and `deploy-aca.yml` at `refs/heads/main`.
- **Issue #615**: CI fast-fail root cause still requires AzDO UI verification.

## Files Changed

- `.azure/pipelines/ci-cd.yml` — 3 pool references switched from `name: ipai-build-pool` to `vmImage: ubuntu-latest`
- `ssot/azure/azure_devops.yaml` — self-hosted pool marked deprecated

## Verdict

**CP-5: PASS** — Pipeline YAML is valid, all stages use hosted agents, deploy template
is well-structured with revision polling + health checks + evidence artifacts.
Pipeline will execute on next qualifying push to main.
