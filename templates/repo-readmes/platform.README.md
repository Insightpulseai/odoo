# platform

Shared control-plane applications, contracts, APIs, and operator-facing surfaces for the InsightPulseAI platform.

## Purpose

This repository owns the control-plane layer: shared APIs, operator/admin interfaces, contracts, metadata services, and cross-plane coordination surfaces used by Odoo, agent runtime, web, and analytics systems.

## Owns

- Control-plane applications
- Admin and operator UI
- Shared APIs and service contracts
- Identity bridge and metadata surfaces
- Shared packages and SDKs
- Cross-repo policy/config surfaces consumed by other systems

## Does Not Own

- Odoo ERP runtime and addons
- Deployable agent execution runtime
- Lakehouse and semantic analytics workloads
- Azure infrastructure provisioning
- Canonical skill/persona/judge definitions

## Repository Structure

```text
platform/
├── .github/
├── apps/
│   ├── control-plane/
│   ├── admin-console/
│   └── ops-portal/
├── packages/
│   ├── contracts/
│   ├── sdk/
│   └── shared-ui/
├── services/
│   ├── api/
│   ├── workers/
│   └── identity-bridge/
├── docs/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Boundary Rule

If a capability is a shared control-plane or operator-facing product surface, it belongs here.

## Validation

Changes must:

- preserve public/internal contract compatibility
- document API or schema changes
- keep identity and policy behavior explicit
- pass contract and integration tests
