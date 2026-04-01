# infra

Azure-native infrastructure as code, platform topology, identity, ingress, observability, and environment policy.

## Purpose

This repository owns the Azure-native infrastructure backbone for the platform, including networking, ingress, identity, workload environments, observability, and infrastructure validation.

## Owns

- Azure infrastructure definitions
- Azure DNS / Azure-native ingress and edge configuration
- Entra identity and access foundations
- Workload environment topology
- Monitoring, alerting, and operational policy
- Environment-level validation and deployment scripts

## Does Not Own

- Application business logic
- Odoo addons
- Canonical agent/persona/skill definitions
- Control-plane application code
- Public-facing web app code

## Repository Structure

```text
infra/
├── .github/
├── azure/
│   ├── foundations/
│   ├── networking/
│   ├── ingress/
│   ├── identity/
│   ├── observability/
│   └── workload/
├── env/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── docs/
├── scripts/
├── spec/
└── ssot/
```

## Native Infra Doctrine

- Azure-native only
- No nginx in the desired-state backbone
- No Cloudflare in the desired-state backbone
- Identity, ingress, monitoring, and workload policy must remain explicit and auditable

## Validation

Changes must:

- support plan/apply/validate discipline
- maintain deterministic environment topology
- preserve rollback and recovery paths
- emit evidence for material infrastructure changes
