# CI/CD Runtime Topology

> Canonical reference for pipeline ownership, execution, and evidence contracts.
> Last updated: 2026-03-29

---

## Pipeline Inventory by Domain

| ID | Pipeline | YAML Path | Domain | Trigger |
|----|----------|-----------|--------|---------|
| 7 | `ipai-landing-deploy` | `web/ipai-landing/azure-pipelines.yml` | Web | `web/ipai-landing/**` |
| 13 | `prismalab-deploy` | `azure-pipelines.yml` (Prismaconsulting repo) | Web | `*` |
| 8 | `odoo-container-deploy` | `azure-pipelines/odoo-container-deploy.yml` | Odoo | `addons/ipai/**`, Dockerfile |
| 9 | `ci-validation` | `azure-pipelines-ci.yml` | Repo-wide | All except `infra/azure/**` |
| 4 | `azure-infra-deploy` | `infra/ci/azure-pipelines.yml` | Infra | `infra/azure/**`, `ssot/azure/**` |
| 5 | `databricks-bundles-ci` | `azure-pipelines/databricks-bundles-ci.yml` | Data | `databricks/**` |
| 6 | `databricks-bundles-promote` | `azure-pipelines/databricks-bundles-promote.yml` | Data | Manual |
| — | `foundry-runtime-ci` | `platform/ci/foundry-runtime-ci.yml` | Platform | `platform/**`, `packages/**`, `apps/**` |
| — | `foundry-runtime-pr` | `platform/ci/foundry-runtime-pr.yml` | Platform | PR only |
| — | `evals-validation` | `agents/ci/evals-validation.yml` | Agents | `agents/**` |
| 3 | `docs-pages-deploy` | `azure-pipelines.yml` (docs repo) | Docs | docs repo |
| 12 | `ipai-landing-upgrade` | `web/ipai-landing/azure-pipelines.upgrade.yml` | **DEPRECATED** | — |
| 10 | `agent-platform-ci` | `agent-platform/azure-pipelines.yml` | **DEPRECATED** | Redirects to `platform/ci/` |
| 11 | `agent-platform-pr` | `agent-platform/azure-pipelines-pr.yml` | **DEPRECATED** | Redirects to `platform/ci/` |

## Ownership Map

| Domain | Owns | Does NOT own |
|--------|------|-------------|
| `platform/` | Foundry runtime, governance, integration, deploy | Agent prompts, skills, evals |
| `agents/` | Prompts, skills, judges, evals, golden sets | Runtime infra, Foundry projects |
| `data-intelligence/` | Databricks bundles, DLT pipelines, DAB deploys | Non-Databricks compute |
| `infra/` | Bicep/Terraform IaC, DNS, Front Door, Key Vault | Application code |
| `web/` | Site/app deploy entrypoints (landing, PrismaLab) | Backend services |
| `addons/ipai/` | Odoo custom modules, Odoo container deploy | Non-Odoo services |

## Shared Template Spine

All templates live in `azure-pipelines/templates/`:

```
azure-pipelines/templates/
├── extends/
│   ├── base-ci.yml          # Policy-enforced CI skeleton
│   └── base-deploy.yml      # Build → Deploy → Smoke → Evidence
└── jobs/
    ├── build-container.yml   # ACR build + push
    ├── deploy-bicep.yml      # Bicep deployment
    ├── deploy-containerapp.yml # ACA update + revision verify
    ├── foundry-eval.yml      # Eval gate with threshold checks
    ├── databricks-bundle-validate.yml
    ├── databricks-bundle-promote.yml
    ├── smoke-http.yml        # HTTP health + content checks
    └── publish-evidence.yml  # Audit artifact
```

### Consumption pattern

Entrypoint pipelines should be **thin** — trigger + parameters + `extends` or `template` reference:

```yaml
# Thin entrypoint example
extends:
  template: ../../azure-pipelines/templates/extends/base-deploy.yml
  parameters:
    imageName: ipai-website
    containerAppName: ipai-website-dev
    smokeUrl: https://insightpulseai.com
```

## Execution Preconditions

1. **Hosted parallelism grant**: Required for all `vmImage: ubuntu-latest` pipelines. Request at `https://aka.ms/azpipelines-parallelism-request`.
2. **Service connection `azure-ipai`**: ARM connection to the Azure subscription.
3. **AzDO environments**: `platform-staging`, `databricks-staging`, `databricks-prod` (create in AzDO UI for approval gates).
4. **Variable groups**: `azure-ipai-config`, `prismalab-secrets`.

## Evidence Contract

Every deploy lane must end with evidence:
- Build image digest
- Container app revision ID
- Smoke test HTTP status + content match
- Pipeline artifact with all of the above

## Transition Notes

### `agent-platform` removal

`agent-platform/` is **not a canonical boundary**. Per project architecture:
- Foundry runtime/governance → `platform/`
- Agent assets (prompts, skills, evals) → `agents/`

The old `agent-platform/*.yml` files are now thin redirects. To complete the transition:
1. Update AzDO pipeline ID 10 to point to `platform/ci/foundry-runtime-ci.yml`
2. Update AzDO pipeline ID 11 to point to `platform/ci/foundry-runtime-pr.yml`
3. Delete the `agent-platform/` directory

### Dead pool replacement

All `ipai-build-pool` references have been replaced with `vmImage: ubuntu-latest`. The self-hosted pool had no agents running.
