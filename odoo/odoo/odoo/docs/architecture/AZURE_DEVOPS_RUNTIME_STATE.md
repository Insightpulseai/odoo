# Azure DevOps Runtime State

> Snapshot of Azure DevOps org state. SSOT: `ssot/azure/azure_devops.yaml`
> Last verified: 2026-03-17

---

## Organization

| Item | Value |
|------|-------|
| Org URL | `https://dev.azure.com/insightpulseai` |
| Tenant | `ceoinsightpulseai.onmicrosoft.com` |
| Subscription | Azure subscription 1 (Enabled) |

## Projects

| Project | Status | Notes |
|---------|--------|-------|
| `ipai-platform` | **Active** | 2 pipelines, 2 service connections, 1 variable group |
| `lakehouse` | **Empty** | No repos, no pipelines. Rename to `data-intelligence` or remove. |

## Pipelines

| Pipeline | YAML | Pool | Status |
|----------|------|------|--------|
| `azure-infra-deploy` (ID 1) | `azure-pipelines.yml` | `ipai-build-pool` (self-hosted) | **Blocked** — pool offline since 2026-03-11 |
| `ci-validation` (ID 2) | `azure-pipelines-ci.yml` | `ubuntu-latest` (hosted) | **Failing** — PR #600 (4 consecutive failures) |

### Pipeline Pool Analysis

`ci-validation` already uses hosted agents (`vmImage: ubuntu-latest`) in all stages. No change needed.

`azure-infra-deploy` uses `name: ipai-build-pool` in all 4 stages:
- Validate (lint + what-if)
- DeployDev
- DeployProd
- ValidateCutover

The Validate stage requires `AzureCLI@2` for what-if, which needs the `azure-ipai` service connection. This works on both hosted and self-hosted agents. **No private-network requirement exists** — all stages can run on hosted agents.

## Agent Pools

| Pool | Type | Agents | Status |
|------|------|--------|--------|
| Azure Pipelines (ID 9) | Hosted | N/A | Active |
| ipai-build-pool (ID 10) | Self-hosted | 1 (`ipai-build-pool 1`, v4.269.0) | **Offline** |

## Service Connections

| Name | Type | Ready |
|------|------|-------|
| `azure-ipai` | Azure RM | Yes |
| `github-insightpulseai` | GitHub | Yes |

## Variable Group: `azure-ipai-config`

| Variable | Value | Issue |
|----------|-------|-------|
| `AZURE_LOCATION` | `southeastasia` | OK |
| `AZURE_RESOURCE_GROUP_DEV` | `rg-ipai-dev` | OK — RG exists |
| `AZURE_RESOURCE_GROUP_PROD` | `rg-ipai-shared-prod` | **WRONG** — RG does not exist |
| `BICEP_TEMPLATE_PATH` | `infra/azure/main.bicep` | OK |
| `BICEP_VERSION` | `latest` | OK |
| `FD_PARAMS_PATH` | `infra/azure/parameters/front-door-prod.parameters.json` | OK |
| `ODOO_PARAMS_PATH` | `infra/azure/parameters/odoo-runtime-prod.parameters.json` | OK |

### Resource Group Reconciliation

Live Azure RGs (verified 2026-03-17):

| Resource Group | Region | Exists |
|----------------|--------|--------|
| `rg-ipai-dev` | southeastasia | Yes |
| `rg-ipai-shared-dev` | southeastasia | Yes |
| `rg-ipai-ai-dev` | southeastasia | Yes |
| `rg-ipai-agents-dev` | southeastasia | Yes |
| `rg-ipai-data-dev` | southeastasia | Yes |
| `rg-ipai-devops` | southeastasia | Yes |
| `rg-ipai-shared-staging` | southeastasia | Yes |
| `rg-ipai-shared-prod` | southeastasia | Yes |
| `rg-ipai-shared-prod` | — | **Does not exist** |

**Action**: Update `AZURE_RESOURCE_GROUP_PROD` in variable group and pipeline YAML from `rg-ipai-shared-prod` to `rg-ipai-shared-prod`.

## Environments

No environments are currently materialized in Azure DevOps.

**Target**:
- `dev` — auto-deploy, no approval gates
- `prod` — manual approval for destructive/topology changes

## Gaps

1. Self-hosted pool offline — `azure-infra-deploy` permanently stuck
2. Prod RG naming mismatch — pipeline would fail even if pool came online
3. No environments — no deployment gate model
4. `lakehouse` project is stale topology
5. `ci-validation` failing on PR #600 — merge path blocked

## Next Steps

1. Patch `azure-pipelines.yml` to use hosted pool (Validate stage at minimum)
2. Fix prod RG name in pipeline YAML and variable group
3. Create `dev` and `prod` environments in Azure DevOps
4. Rename or delete `lakehouse` project
5. Investigate and fix `ci-validation` failures on PR #600
