Query Azure Resource Graph for all live resources and reconcile against architecture SSOT.

## What This Does

1. Queries Azure Resource Graph for every resource in the subscription
2. Compares live state against `ssot/architecture/services.yaml`, `infra/ssot/azure/service-matrix.yaml`, and `infra/dns/subdomain-registry.yaml`
3. Classifies each resource by platform plane (compute, database, AI, identity, etc.)
4. Reports errors (retired service still running, missing resources, broken DNS routes)
5. Saves snapshot + evidence

## Execution

```bash
# Step 1: Query Resource Graph (requires az login)
az graph query -q "Resources | project name, type, resourceGroup, location | order by resourceGroup asc" --first 200 -o json > /tmp/azure-rg-snapshot.json

# Step 2: Run reconciliation
python3 scripts/ci/azure_resource_reconcile.py --snapshot /tmp/azure-rg-snapshot.json
```

If `az` is not logged in, tell the user to run `! az login` first.

## Output

Present results as:

### Azure Resource Inventory

| Plane | Count | Resources |
|-------|-------|-----------|
| compute | N | list... |
| ... | | |

### Reconciliation

| Check | Status | Detail |
|-------|--------|--------|
| Retired services not running | PASS/FAIL | ... |
| Active services have resources | PASS/FAIL | ... |
| DNS routes have backends | PASS/FAIL | ... |

### Drift Detected (if any)

For each error, state:
1. What the SSOT says
2. What Resource Graph shows
3. Which file to fix

Then fix the drift — update the SSOT files to match reality. Resource Graph is truth.

## Rules

- Resource Graph is the source of truth for what exists in Azure
- SSOT YAML files must match Resource Graph, not the other way around
- If a doc says "Exists" but Resource Graph disagrees, fix the doc
- If a doc says "Not deployed" but Resource Graph shows it, fix the doc
- Save the snapshot to `infra/ssot/azure/resource-graph-snapshot.json` after every query
