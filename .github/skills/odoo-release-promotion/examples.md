# odoo-release-promotion -- Worked Examples

## Example 1: Promotion Pipeline Overview

```
dev (odoo_dev)              staging (odoo_staging)          prod (odoo)
─────────────               ──────────────────              ──────────
1. Module dev + unit tests  4. Deploy image to staging ACA  7. Deploy image to prod ACA
2. Build image (ACR Task)   5. Run migration verify         8. Run migration verify
3. Scan image (Defender)    6. Smoke test + approval gate   9. Health check + traffic shift
                                                            10. Monitor 30 min, rollback if needed
```

## Example 2: Migration Verification Gate

```bash
# Run on staging before promoting to prod
# This verifies the module upgrade path without serving traffic

az containerapp exec \
  --name ipai-odoo-staging-web \
  --resource-group rg-ipai-staging-odoo-runtime \
  --command "odoo-bin -d odoo_staging -u ipai_finance_ppm --stop-after-init --no-http"

# Exit code 0 = migration clean
# Exit code non-zero = migration failure, DO NOT promote to prod
echo "Migration verify exit code: $?"
```

## Example 3: ACA Revision-Based Rollback

```bash
# List revisions for the Odoo web app
az containerapp revision list \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --output table

# Activate previous revision (rollback)
az containerapp revision activate \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --revision ipai-odoo-dev-web--prev-revision-name

# Shift 100% traffic to previous revision
az containerapp ingress traffic set \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --revision-weight ipai-odoo-dev-web--prev-revision-name=100
```

## Example 4: Azure DevOps Approval Gate (YAML)

```yaml
# azure-pipelines.yml snippet
stages:
  - stage: DeployStaging
    jobs:
      - deployment: DeployOdooStaging
        environment: staging
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    az containerapp update \
                      --name ipai-odoo-staging-web \
                      --image $(ACR_NAME).azurecr.io/odoo:$(Build.SourceVersion)
                - script: |
                    # Migration verification
                    az containerapp exec \
                      --name ipai-odoo-staging-web \
                      --command "odoo-bin -d odoo_staging -u all --stop-after-init --no-http"

  - stage: DeployProd
    dependsOn: DeployStaging
    condition: succeeded()
    jobs:
      - deployment: DeployOdooProd
        environment: production    # Has manual approval gate configured in AzDO
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    az containerapp update \
                      --name ipai-odoo-prod-web \
                      --image $(ACR_NAME).azurecr.io/odoo:$(Build.SourceVersion)
```

## Example 5: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Apps revision management blue green deployment")
Result: ACA supports multiple active revisions with traffic splitting.
        Deploy new revision, test with 0% traffic, then shift. Revisions
        are immutable -- rollback by activating a prior revision.

Step 2: microsoft_docs_search("Azure DevOps pipeline environment approval gates")
Result: AzDO environments support approval gates (manual or automated).
        Configure approvers per environment. Pipeline pauses until approved.
        Supports timeout and rejection policies.

Step 3: microsoft_docs_search("Azure Container Apps rollback previous revision")
Result: Deactivate failing revision, activate previous.
        az containerapp revision activate/deactivate commands.
        Traffic weights control which revision serves requests.
```
