# Delivery Readiness

> Machine-readable SSOT: `ssot/release/release_contract.yaml`
> Last reviewed: 2026-03-27

## Deployable Surfaces

| Surface | Pipeline | ACR Image | Container App | Public URL | Status |
|---------|----------|-----------|---------------|------------|--------|
| Web Landing | `web-landing-deploy.yml` | `ipai-website:latest` | `ipai-website-dev` | `www.insightpulseai.com` | Ready |
| Odoo ERP | `odoo-deploy.yml` | `ipai-odoo:19.0-copilot` | `ipai-odoo-dev-web` | `erp.insightpulseai.com` | Ready |
| Databricks | `databricks-deploy.yml` | N/A (bundle deploy) | N/A | Workspace URL | Ready |
| BI Layer | `bi-deploy-promote.yml` | N/A (SQL + Fabric) | N/A | N/A | Ready |

## Pipeline Stages (Required per Surface)

Every deploy pipeline follows the four-stage contract:

```
Build/Validate -> Deploy -> Smoke -> Evidence
```

| Stage | Purpose | Failure Behavior |
|-------|---------|-----------------|
| Build/Validate | ACR build or bundle validate | Blocks all downstream |
| Deploy | ACA update or bundle deploy | Blocks smoke |
| Smoke | HTTP/API health + content check | Marks release as failed |
| Evidence | Publish artifact with SHA, image, timestamp | Always runs (succeededOrFailed) |

## Smoke Criteria

| Surface | Check | Pass Criteria |
|---------|-------|---------------|
| Web Landing | `curl https://www.insightpulseai.com` | HTTP 200, body contains "InsightPulse" |
| Odoo ERP | `curl https://erp.insightpulseai.com/web/login` | HTTP 200, body contains "Odoo", no "Internal Server Error" |
| Databricks | `databricks api post /api/2.0/sql/statements` | Warehouse returns SUCCEEDED |
| BI Layer | Count serving views in gold schema | >= 9 views |

## Evidence Artifact

Each pipeline publishes a JSON artifact with:

```json
{
  "surface": "web-landing",
  "timestamp": "2026-03-27T12:00:00Z",
  "build_number": "20260327.1",
  "commit_sha": "abc1234...",
  "image_ref": "acripaiodoo.azurecr.io/ipai-website:latest",
  "smoke_url": "https://www.insightpulseai.com",
  "pipeline": "web-landing-deploy"
}
```

Artifacts are retained for 90 days in Azure DevOps.

## Promotion Policy

| Transition | Gate | Requirements |
|------------|------|-------------|
| Dev -> Staging | Manual approval | All stages pass, evidence published, smoke green |
| Staging -> Prod | Manual approval | Staging smoke green, evidence published, no critical alerts |

## Reusable Templates

All templates live in `azure-pipelines/templates/jobs/`:

| Template | Purpose |
|----------|---------|
| `build-container.yml` | ACR build + push with build-number tag |
| `deploy-containerapp.yml` | ACA revision update + activation check |
| `smoke-http.yml` | curl-based HTTP status + content check with retries |
| `publish-evidence.yml` | JSON evidence artifact + human-readable summary |
| `validate-bicep.yml` | Bicep syntax check + optional what-if |
| `databricks-bundle-validate.yml` | Bundle validate + optional tests |
| `databricks-bundle-promote.yml` | Bundle deploy + optional smoke |

## Prerequisites

- **Hosted parallelism**: Must be granted on Azure DevOps org before pipelines can run on `ubuntu-latest`
- **Service connection**: `azure-ipai` (workload identity federation)
- **ACR**: `acripaiodoo` (authenticated via service connection)
- **AzDO Environments**: `odoo-dev`, `odoo-staging`, `odoo-prod` (for approval gates)
- **Databricks auth**: Service principal or PAT configured in pipeline variables

## Local Smoke Tests

Committed scripts for local/CI execution:

| Script | Surface |
|--------|---------|
| `tests/smoke/web/test_landing.sh` | Web landing page |
| `tests/smoke/odoo/test_erp.sh` | Odoo ERP login |
| `tests/smoke/databricks/test_warehouse.sh` | Databricks SQL Warehouse |
