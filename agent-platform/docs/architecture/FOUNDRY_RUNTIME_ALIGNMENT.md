# Foundry Runtime Alignment

Authority: [`platform/ssot/ai/foundry-resource-model.yaml`](../../../platform/ssot/ai/foundry-resource-model.yaml) + [`ssot/agent-platform/agent_framework_adoption.yaml`](../../../ssot/agent-platform/agent_framework_adoption.yaml)

## Purpose

Describe how `agent-platform/` aligns its runtime to the Microsoft Foundry control plane. Foundry is the governance and deployment substrate; `agent-platform/` is the runtime engine that registers into it.

## Alignment points

| Capability | Foundry role | `agent-platform/` role |
|---|---|---|
| Project scoping | Owns project resource (`ipai-copilot-resource`) | Registers agents + tools into the project |
| Model deployments | Owns deployed models (gpt-4.1, phi-4, qwen) | Consumes via provider adapters |
| Agent registry | Owns Foundry agent records | Publishes Agent Cards (`/.well-known/agent-card.json`) |
| Tool registry | Owns Foundry tool records | Registers typed adapters (odoo, databricks, docintel, storage, communications) |
| Tracing | Owns trace sink (App Insights) | Emits traces via middleware |
| Monitoring | Owns dashboards / workbooks | Emits metrics through middleware |
| Evaluations | Owns Foundry evals | Registers eval jobs + scorecards |
| RBAC | Owns Foundry RBAC boundaries | Uses Managed Identity; never holds secrets |
| Networking | Owns private endpoints + firewall | Uses endpoints through environment configuration |

## Runtime → Foundry handshake

1. `agent-platform/` container boots with Managed Identity.
2. Reads Foundry project endpoint + model deployment names from environment (sourced from Key Vault).
3. Loads provider adapter for the active mode (team → Foundry cloud, solo → Foundry Local).
4. Registers its agents into the Foundry project (idempotent).
5. Registers typed tool adapters into the Foundry tool registry.
6. Emits traces, metrics, and evals to Foundry-owned sinks.

## Agent Card contract

Every agent exposes `/.well-known/agent-card.json` with the same schema in team and solo modes. Only the backing model swaps.

## What `agent-platform/` must not do

- Hold model API keys directly.
- Bypass provider adapters to call vendor SDKs.
- Manage Foundry project lifecycle (create / delete projects).
- Redefine RBAC or networking policy.
- Hardcode Foundry endpoints.

## What `agent-platform/` owns

- Supervisor, router, dispatcher, planner.
- Retries, approvals, workflow state, judge loops.
- Envelopes and handoffs between specialist agents.
- Tool adapters (typed, not prompt blobs).
- Session, attachment, and observability middleware.

> [!IMPORTANT]
> The `agent-platform/` runtime is the only place where Microsoft Agent Framework (MAF) imports are permitted. `agents/`, `odoo/`, `addons/`, `platform/`, `infra/`, `data-intelligence/`, `web/`, and `apps/` must remain MAF-free.

## Two modes

- **Team mode**: Codespaces / local dev → `agent-platform/` on ACA → Foundry cloud (`ipai-copilot-resource`, gpt-4.1).
- **Solo mode**: Local Mac → `agent-platform/` in devcontainer → Foundry Local (phi-4 / qwen, NPU/GPU).
- **Forbidden**: Foundry Local inside Codespaces.

## Related

- [Model provider adapters](MODEL_PROVIDER_ADAPTERS.md)
- [Foundry resource model](../../../platform/ssot/ai/foundry-resource-model.yaml)
- [Foundry control plane](../../../platform/docs/architecture/FOUNDRY_CONTROL_PLANE.md)
- [Agent framework adoption SSOT](../../../ssot/agent-platform/agent_framework_adoption.yaml)
