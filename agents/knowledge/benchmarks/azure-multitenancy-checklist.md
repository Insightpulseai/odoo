# Benchmark: Azure Multitenancy Checklist

> Source: Microsoft Azure Architecture multitenancy checklist
>
> Role: Tenant/isolation/operations benchmark checklist
>
> Structured around business considerations + five Well-Architected pillars

---

## Business Considerations

- **Define tenants**: A tenant is not the same as a user. Define what constitutes a tenant for your platform.
- **Pricing and tiers**: Design pricing model, define tiers, map features to tiers.
- **Tenancy models**: Shared infrastructure, dedicated infrastructure, or hybrid.
- **Marketplace**: Consider marketplace distribution if applicable.

---

## Reliability Pillar

- **Noisy neighbor mitigation**: Prevent one tenant from degrading others' experience
- **SLOs/SLAs**: Define per-tier service level objectives
- **Scale testing**: Validate behavior under multi-tenant load
- **Chaos testing**: Verify isolation under failure conditions

---

## Security Pillar

- **Zero trust / least privilege**: Assume breach, minimize blast radius
- **Tenant mapping**: Every request must be mapped to a tenant
- **Isolation testing**: Design AND test tenant isolation
- **Cross-tenant prevention**: Active measures against data leakage
- **Compliance**: Understand per-tenant compliance requirements
- **DNS safety**: Manage domain names to prevent subdomain takeover

---

## Cost Optimization Pillar

- **Per-tenant measurement**: Measure consumption per tenant
- **Cost correlation**: Map infrastructure costs to tenants
- **Billing antipatterns**: Avoid over-provisioning, under-metering, shared-cost hiding

---

## Operational Excellence Pillar

- **Tenant lifecycle automation**: Onboard, provision, configure, update, offboard
- **Control plane vs data plane**: Distinct responsibilities and scaling
- **Deployment strategy**: Tenant-aware deployment (ring, canary, blue-green)
- **Update strategy**: How updates roll out across tenants
- **Tenant-level monitoring**: Per-tenant metrics, logs, alerts
- **Resource organization**: Subscriptions, resource groups, naming for multi-tenant

---

## Performance Efficiency Pillar

- **Compute scaling**: Scale compute per tenant demand
- **Storage scaling**: Scale storage per tenant data
- **Networking scaling**: Scale network capacity per tenant traffic
- **Database strategy**: Shared pool vs dedicated per-tenant databases

---

## Global Guardrails

1. Tenants are not the same thing as users
2. Tenant context must be explicit in authorization
3. Tenant isolation must be designed and continuously tested
4. Per-tenant consumption must be measurable
5. Tenant lifecycle must be automated
6. Control plane and data plane must be distinguished
7. Noisy-neighbor risk must be actively mitigated

---

## Sources

- [Azure Multitenancy Checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
