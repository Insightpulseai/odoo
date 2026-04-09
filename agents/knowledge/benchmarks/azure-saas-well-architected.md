# Benchmark: Azure SaaS Well-Architected

> Source: Microsoft Azure Well-Architected SaaS workload documentation
>
> Role: SaaS platform benchmark doctrine
>
> This is a benchmark --- not an integration contract. It becomes an integration only when an explicit contract is created in docs/contracts/.

---

## Structure

Microsoft organizes SaaS guidance around:

### Design Areas (Technical)
- **Resource organization**: subscription, resource group, naming, tagging for multi-tenant
- **Identity and access**: tenant identity, user identity, authorization, zero trust
- **Compute**: app hosting model, scaling, isolation boundaries
- **Networking**: ingress, DNS, CDN, private connectivity
- **Data**: tenant data isolation, shared vs dedicated databases, data residency

### Design Areas (Operational)
- **Billing and cost management**: pricing models, metering, cost attribution
- **Governance**: compliance, policy enforcement, audit
- **DevOps practices**: CI/CD for multi-tenant, deployment strategies, testing
- **Incident management**: tenant-aware alerting, blast radius, escalation

### Journey
- **Assessment**: current state evaluation
- **SaaS journey**: migration from single-tenant to multi-tenant

---

## Key Principles

1. **Design for tenancy from the start** --- retrofitting multi-tenancy is expensive
2. **Separate control plane from data plane** --- control plane manages tenants, data plane serves them
3. **Design billing into the architecture** --- not as an afterthought
4. **Tenant-aware observability** --- every metric, log, and trace should include tenant context
5. **Assume breach** --- design isolation assuming a compromised tenant

---

## Sources

- [Azure SaaS Well-Architected](https://learn.microsoft.com/en-us/azure/well-architected/saas/)
