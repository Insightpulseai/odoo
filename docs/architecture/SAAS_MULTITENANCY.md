# SaaS and Multitenancy — Canonical Benchmark

## Overview

The platform is benchmarked against Azure SaaS and multitenant best practices rather than
SAP product topology.

---

## Core principles

- SaaS is the delivery and operating model
- Multitenancy is the architecture model
- Tenant definition depends on the business model and workload
- Not every component must be shared
- Control plane, telemetry, and safe deployment are first-class design surfaces

---

## Preferred ERP/SaaS posture

- Single-cloud focus unless a multicloud business requirement is explicit
- Tenant-isolated transactional data where trust and compliance matter
- Deployment stamps to scale safely and reduce blast radius
- Resilient control plane for onboarding and fleet operations
- Feature flags and safe deployment for continuous innovation
- Strong operational standardization across tenants

---

## Tenant isolation model

| Component | Default posture | Rationale |
|-----------|----------------|-----------|
| Transactional DB (Odoo) | Isolated per tenant | ERP data requires strong trust/compliance boundary |
| Application runtime (ACA) | Shared fleet, isolated revisions | Cost-efficient with revision-safe rollout |
| Control plane | Shared | Fleet-wide operations need single view |
| AI/agent runtime (Foundry) | Shared project, scoped context | Model access is shared; data context is tenant-scoped |
| Storage/filestore | Isolated per tenant | Document/attachment data requires tenant boundary |
| Identity | Shared Entra tenant | Entra ID supports multi-org via access packages |
| Monitoring | Shared, tenant-tagged | Centralized with tenant-scoped queries |

---

## Control plane layers

### Service-level control plane

- Tenant onboarding and provisioning
- Environment lifecycle management
- Fleet-wide rollout coordination
- Health and quality checks across all tenants
- Cost, capacity, and deployment management
- Incident detection and mitigation

### Tenant-level control plane

- Tenant administration and configuration
- Tenant-scoped visibility and operational controls
- Maintenance initiation where allowed
- Tenant-specific feature flag overrides (governed)

---

## SaaS operating principles (Dynamics 365 benchmark)

1. **Single-cloud focus** — Azure-native only
2. **MVP horizontal slice** — deliver across ERP components, not vertical-deep on one
3. **Telemetry-first** — design telemetry early as core capability
4. **Safe deployment** — staged rollout for code and configuration
5. **Feature flags** — controlled rollout, preview, mitigation, deprecation
6. **Deployment stamps** — bounded scale and blast radius
7. **Standardization** — minimize one-off tenant divergence
8. **Customer trust first** — satisfaction and reliability before cost optimization

---

## SAP positioning

SAP is an optional governed integration surface — one of many external systems the platform
can connect to. SAP is not the benchmark architecture for the SaaS/multitenancy model.

---

*Last updated: 2026-04-10*
