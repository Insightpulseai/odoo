---
name: Pulser IaC Scaffold
description: Generate Bicep-native infrastructure templates under `infra/azure/` — ACA, Front Door, Postgres, Key Vault, and AI Foundry.
disable-model-invocation: true
---

# Pulser IaC Scaffold Skill

## When to use
When converging manual Azure resources into the **canonical deployment contract** or bootstrapping new environment deployments.

## Design Rules

### 1. Ingress Rule
- **RULE**: Direct ACA custom-domain binding is the primary ingress path.
- **Legacy**: Front Door/Cloudflare marked as decommission targets.

### 2. Runtime Components
- **Core App**: `pulser-odoo-web` (Odoo CE 18 + OCA)
- **Agent API**: `pulser-agent-api` (Agent orchestration)
- **Worker**: `pulser-worker` (Async/Background)
- **Postgres**: Flexible Server with Fabric-mirroring support.

### 3. Convergence Rule
- **RULE**: No critical infrastructure left as manual Azure-only state.
- **Output**: Bicep modules in `infra/azure/*.bicep`.
- **Naming**: Use environment-agnostic, deterministic names (e.g., `aca-pulser-prod-01`).

## Validation Checks
1. Ensure all generated resources include cost-center and workload tags.
2. Verify inclusion of health probes on `/web/health` for Odoo.
3. Check for Managed Identity (UserAssigned) configuration for Key Vault access.
