# azure-deployment-ops

Validates Azure deployment topology — Container Apps, Front Door, managed identity, and Key Vault binding.

## When to use
- New Azure Container App is provisioned
- Deployment configuration changes in a PR
- Infrastructure PR modifies Bicep or Terraform
- New custom domain binding is requested

## Key rule
Every Container App must have managed identity, Key Vault binding via identity (never connection strings),
and Front Door routing with a valid TLS certificate. Missing any of these is a blocker.

## Cross-references
- `docs/contracts/azure-resource-graph-contract.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
- `.claude/rules/infrastructure.md`
