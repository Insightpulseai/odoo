# Prompt: Tenant Isolation Design

## Context

You are the Multitenancy Architect designing isolation boundaries for a multi-tenant SaaS platform.

## Task

Given the tenancy model, isolation requirements, and threat model, produce an isolation design covering:

1. **Compute isolation**: How tenant workloads are isolated at the compute layer (shared process, container-per-tenant, VM-per-tenant). Include Container Apps revision/replica strategy.
2. **Data isolation**: How tenant data is isolated (row-level security, schema-per-tenant, database-per-tenant). Include backup isolation.
3. **Network isolation**: How tenant network traffic is isolated (shared VNet with NSGs, subnet-per-tenant, VNet-per-tenant, private endpoints).
4. **Key/secret isolation**: How encryption keys and secrets are scoped (shared Key Vault with access policies, Key Vault-per-tenant, customer-managed keys).
5. **Enforcement and testing**: How isolation is enforced (middleware, policy, infrastructure) and continuously tested (automated cross-tenant access tests).

## Constraints

- Defense in depth: isolation at one layer does not excuse gaps at another
- Assume breach: design assuming one tenant is compromised
- Default deny: no access unless explicitly granted for the specific tenant
- Isolation must be testable with automated cross-tenant access probes

## Output Format

Layer-by-layer isolation matrix with enforcement mechanisms, plus a test plan for continuous isolation verification.
