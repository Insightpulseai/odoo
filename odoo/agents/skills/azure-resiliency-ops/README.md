# azure-resiliency-ops

Validates HA/DR posture — zone redundancy, backup policies, failover routes, and health probes.

## When to use
- Pre-release audit for production deployment
- Disaster recovery drill
- New production service onboarded
- Backup policy change in a PR

## Key rule
Every production service must have zone redundancy, backup retention meeting policy minimum,
and a documented DR runbook. Single-zone deployments are blockers for production.
Never reduce backup retention below current policy minimum.

## Cross-references
- `docs/contracts/azure-resource-graph-contract.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
- `.claude/rules/infrastructure.md`
