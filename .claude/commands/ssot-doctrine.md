Enforce architecture consistency by reconciling SSOT docs against Azure Resource Graph truth.

## What This Does

1. **Query Azure Resource Graph** for all live resources (the ground truth)
2. **Reconcile** against architecture SSOT files
3. **Fix drift** — update docs to match reality, not the other way around
4. **Report** errors, warnings, and resource summary

## Default Behavior

Every time you touch architecture docs, infra SSOT, or DNS config — run the Resource Graph query first. Resource Graph is truth. Docs follow.

## Execution

```bash
# Query Resource Graph (requires az login)
# Reference: https://learn.microsoft.com/en-us/azure/governance/resource-graph/first-query-azurecli
az graph query -q "Resources | project name, type, resourceGroup, location | order by resourceGroup asc" --first 200 -o json > /tmp/azure-rg-snapshot.json

# Run reconciliation
python3 scripts/ci/azure_resource_reconcile.py --snapshot /tmp/azure-rg-snapshot.json

# Save snapshot as SSOT artifact
cp /tmp/azure-rg-snapshot.json infra/ssot/azure/resource-graph-snapshot.json
```

If `az` is not logged in, tell the user to run `! az login` first.

## Useful Resource Graph Queries

```bash
# All resources by RG
az graph query -q "Resources | summarize count() by resourceGroup | order by count_ desc" -o table

# Container Apps only
az graph query -q "Resources | where type =~ 'microsoft.app/containerapps' | project name, resourceGroup" -o table

# AI services
az graph query -q "Resources | where type contains 'cognitiveservices' or type contains 'machinelearning' | project name, type, resourceGroup" -o table

# Resources created in last 7 days
az graph query -q "Resources | where properties.creationTime > ago(7d) | project name, type, resourceGroup" -o table

# Cost-bearing resources (exclude MIs, NSGs, etc.)
az graph query -q "Resources | where type !contains 'managedidentity' and type !contains 'networksecurity' and type !contains 'networkwatcher' | project name, type, resourceGroup" -o table
```

## Core Doctrine (Current)

**Entra authenticates. Foundry thinks. Document Intelligence reads. Odoo records.**

| Plane | Owner | SSOT File |
|-------|-------|-----------|
| Identity | Entra ID | `ssot/contracts/identity.yaml` |
| Edge | Front Door + Cloudflare DNS | `infra/dns/subdomain-registry.yaml` |
| ERP | Odoo CE 19 | `ssot/architecture/services.yaml` |
| AI | Foundry + OpenAI | `ssot/contracts/foundry_tools.yaml` |
| OCR | Document Intelligence | `ssot/contracts/document_ocr.yaml` |
| Data | Databricks + Unity Catalog | `ssot/contracts/analytics_pipeline.yaml` |
| Reporting | Power BI | (planned) |
| Secrets | Azure Key Vault | Key Vault resources |

## Reconciliation Files

| File | What It Tracks |
|------|---------------|
| `ssot/architecture/services.yaml` | Active vs retired services |
| `infra/ssot/azure/service-matrix.yaml` | Per-service status + ACA mapping |
| `infra/dns/subdomain-registry.yaml` | DNS subdomain lifecycle |
| `infra/ssot/azure/resource-graph-snapshot.json` | Last Resource Graph snapshot |
| `docs/architecture/AZURE_BILL_OF_MATERIALS.md` | Resource inventory + target alignment |

## Drift Protocol

When drift is detected:

1. **Resource Graph wins** over docs — update the doc, not Azure
2. **State the drift**: what the doc says vs what Resource Graph shows
3. **Fix the doc** immediately
4. **Re-run reconciliation** to confirm PASS
5. If FAIL persists, report the remaining gaps as actionable items

## Violation Protocol

If a change would violate doctrine:
1. **STOP** — do not proceed
2. **EXPLAIN** — which rule is violated
3. **PROPOSE** — compliant alternative
