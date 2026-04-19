# Foundry Control Plane

Canonical source: [`platform/ssot/ai/foundry-resource-model.yaml`](../../ssot/ai/foundry-resource-model.yaml)

Authority: [`ssot/ai/external-reference-authorities.yaml`](../../../ssot/ai/external-reference-authorities.yaml)

## Purpose

Describe Microsoft Foundry as the governed Azure runtime and control plane for IPAI AI workloads. Foundry unifies projects, model deployments, agents, tools, tracing, monitoring, evaluations, RBAC, and networking policy under one Azure resource-provider model.

## Resource hierarchy

| Level | IPAI binding | Present today? |
|---|---|---|
| Subscription | ISV Sponsored (`eba824fb`) | yes |
| Resource group | `rg-ipai-dev-ai-sea` (southeastasia) | yes |
| Foundry project | `ipai-copilot-resource` | **no — target state, not yet provisioned** |
| Key Vault | `kv-ipai-dev-sea` | yes |
| App Insights | `appi-ipai-dev-runtime-sea` | yes |
| Log Analytics | `log-ipai-dev-runtime-sea` | yes |
| Storage | `staipaiodoo` | yes |

> [!IMPORTANT]
> Live Azure verification on 2026-04-19 shows no Foundry project exists yet. Only `docai-ipai-dev` (Document Intelligence), `srch-ipai-dev-sea` (Azure AI Search), and `dbw-ipai-dev` (Databricks) are in the AI resource group. Provisioning is a go-live blocker.

## Control-plane capabilities

- **Projects** — one project per runtime scope; project owns agent and model visibility.
- **Model deployments** — default family `gpt-4.1` (team mode), `phi-4` / `qwen` (solo mode via Foundry Local).
- **Agents** — agent-platform registers agents into the Foundry project; Agent Card at `/.well-known/agent-card.json`.
- **Tools** — typed adapters (odoo, databricks, docintel, storage, communications) registered in the Foundry tool registry.
- **Tracing** — App Insights sink, retention per [`branch-environment-contract.yaml`](../../ssot/runtime/branch-environment-contract.yaml).
- **Monitoring** — dashboards / workbooks attached to the App Insights workspace.
- **Evaluations** — Foundry evals + agent-platform evals, gated by [`G6_eval_gate`](../../ssot/release/odoo-cloud-release-gates.yaml).
- **RBAC** — Managed Identity preferred; user impersonation for agent runtime is forbidden.
- **Networking** — private endpoints for production-dependent services.

## Authority boundaries

Foundry **is** authoritative for:

- Project and resource model
- Model deployment lifecycle
- Tracing / monitoring / evaluation controls
- Foundry-resource-level RBAC
- Networking policy for AI resources

Foundry **is not** authoritative for:

- Repo structure (→ `ssot/governance/`)
- Spec authority (→ `spec/` + `ssot/`)
- Release gating (→ Azure Pipelines + `ssot/release/`)
- Odoo business logic (→ `addons/` + `spec/`)
- Agent skill definitions (→ `agents/`)

## Guardrails

- Foundry endpoints are referenced, not hardcoded.
- Model names resolve via the provider adapter.
- Secrets flow only via Managed Identity → Key Vault bindings.
- No direct portal changes without an IaC commit reference.
- Every registered agent has an Agent Card.
- Every model deployment has eval coverage.

> [!IMPORTANT]
> Foundry is the runtime substrate, not the architecture source of truth. Repo structure, specs, and release gates remain governed by their own SSOTs.

## Related

- [Foundry resource model SSOT](../../ssot/ai/foundry-resource-model.yaml)
- [Foundry runtime alignment (agent-platform)](../../../agent-platform/docs/architecture/FOUNDRY_RUNTIME_ALIGNMENT.md)
- [Model provider adapters](../../../agent-platform/docs/architecture/MODEL_PROVIDER_ADAPTERS.md)
- [Agent framework adoption SSOT](../../../ssot/agent-platform/agent_framework_adoption.yaml)
- [External reference authorities](../../../ssot/ai/external-reference-authorities.yaml)
