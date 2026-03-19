# Azure Resource Graph Queries

This directory stores canonical Azure Resource Graph KQL used for:

- live resource inventory
- drift detection
- release validation
- governance checks
- recent-change inspection

## Rules

- Do not rely on ad hoc portal-only inspection when a repeatable query is possible.
- Store one query per file.
- Keep query purpose narrow and named clearly.
- Reference query IDs from `ssot/runtime/resource-graph-query-catalog.yaml`.

## Canonical query order

- `00_all_resources.kql`
- `10_frontdoor_inventory.kql`
- `20_containerapps_inventory.kql`
- `30_postgres_flexible_inventory.kql`
- `40_foundry_inventory.kql`
- `50_managed_identities.kql`
- `60_keyvault_inventory.kql`
- `70_tag_compliance.kql`
- `80_recent_changes.kql`
- `90_container_registries.kql`
- `91_region_compliance.kql`
- `92_stale_resources.kql`
- `93_public_endpoints.kql`

## Execution

```bash
# Run a single query
./run_query.sh <query-name> [--output json|table|csv]

# Run via az CLI directly
az graph query -q "$(cat queries/00_all_resources.kql)" -o json
```

## Cross-references

- `ssot/runtime/resource-graph-query-catalog.yaml` — machine-readable catalog
- `docs/contracts/azure-resource-graph-contract.md` — C-36 contract
