# Checklist: Tenant Isolation Design

## Compute Isolation

- [ ] Compute isolation model documented per tenant tier
- [ ] Process/container/VM boundary defined and enforced
- [ ] Resource limits (CPU, memory) set per tenant workload
- [ ] Container Apps revision strategy prevents cross-tenant code execution
- [ ] Managed identity scoped per tenant where applicable

## Data Isolation

- [ ] Data isolation model documented per tenant tier
- [ ] Row-level security policies defined and tested (shared DB)
- [ ] Schema separation implemented and verified (schema-per-tenant)
- [ ] Database-per-tenant provisioned and accessible only to owner (dedicated)
- [ ] Backup isolation ensured (tenant cannot access another's backup)
- [ ] Data encryption at rest with tenant-scoped keys where required

## Network Isolation

- [ ] Network isolation model documented per tenant tier
- [ ] NSG rules prevent cross-tenant network access
- [ ] Private endpoints configured for sensitive services
- [ ] DNS resolution scoped appropriately
- [ ] Egress controls prevent data exfiltration across tenant boundaries

## Key/Secret Isolation

- [ ] Key Vault access policies scoped per tenant
- [ ] Customer-managed keys supported for enterprise tier
- [ ] Secret rotation does not affect other tenants
- [ ] Key Vault diagnostic logs enabled for audit

## Enforcement and Testing

- [ ] Middleware enforces tenant context on every request
- [ ] Automated cross-tenant access tests run in CI/CD
- [ ] Isolation test covers all layers (compute, data, network, keys)
- [ ] Test results tracked and any failure blocks deployment
- [ ] Annual penetration test includes cross-tenant scenarios
