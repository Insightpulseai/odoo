# azure-optimization-ops

Validates cost and performance optimization — SKU right-sizing, idle resource detection, scaling rules, and reserved capacity.

## When to use
- Monthly cost review cycle
- Stale or idle resource detected via Resource Graph
- SKU change proposed in a PR
- Scaling rule modification

## Key rule
Never downgrade a SKU or reduce capacity without 30-day usage evidence and stakeholder approval.
Zero-traffic resources are flagged, not auto-deleted. Every recommendation includes a rollback path.

## Cross-references
- `docs/contracts/azure-resource-graph-contract.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
