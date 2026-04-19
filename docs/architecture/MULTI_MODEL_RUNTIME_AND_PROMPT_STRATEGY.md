# Multi-Model Runtime and Prompt Strategy

Canonical sources:

- [`ssot/ai/external-reference-authorities.yaml`](../../ssot/ai/external-reference-authorities.yaml)
- [`ssot/agent-platform/agent_framework_adoption.yaml`](../../ssot/agent-platform/agent_framework_adoption.yaml)
- [`platform/ssot/ai/foundry-resource-model.yaml`](../../platform/ssot/ai/foundry-resource-model.yaml)
- [`agents/registries/skills/canonical/prompt-packs.yaml`](../../agents/registries/skills/canonical/prompt-packs.yaml)

## Purpose

Describe how IPAI combines multiple model providers and role-based prompt assets under a single governed runtime without mixing up examples, prompt assets, and runtime authority.

## The operating model

```
model_providers:
  anthropic          → Claude-specific patterns, managed agents, tool use
  openai             → API examples, role prompt libraries, general recipes
  foundry_hosted     → default IPAI model provider (gpt-4.1 team, phi-4/qwen solo)

runtime_and_governance:
  microsoft_foundry  → deployment, project scoping, tracing, monitoring,
                       evaluations, RBAC, networking policy
```

## Provider selection policy

- **Default**: Foundry (team mode) / Foundry Local (solo mode).
- **Anthropic (Claude)**: use for patterns that benefit from Claude-specific behavior — long-context code review, Claude Cookbook managed agents, tool-use recipes with strong observability defaults.
- **OpenAI direct**: last resort where Foundry-hosted equivalents are insufficient.
- Selection is **configuration**, not code. Agents depend on the provider adapter interface, never on a vendor SDK.

## Prompt strategy

- Role-based prompt assets (OpenAI Academy Prompt Packs and equivalents) enter IPAI **only as structured skills** under `agents/skills/<pack>/<skill_id>/`.
- Each skill has a manifest with schemas, evaluators, safe-outputs policy, approval band.
- Raw prompt text outside a skill wrapper is forbidden.
- Prompts that touch mutating tools or finance/identity state require evaluator coverage.

## Runtime strategy

- `agent-platform/` registers agents and tools into Foundry via the provider adapter at startup.
- Agent Cards (`/.well-known/agent-card.json`) remain identical across team and solo modes; only the backing model swaps.
- Tracing, metrics, and evals flow to Foundry-owned sinks (App Insights, Log Analytics, Foundry evals).
- Managed Identity is the only auth principal for agent-platform → Foundry.

## Two modes

| Mode | Frontend | Runtime | Model |
|---|---|---|---|
| Team | Codespaces / local dev | ACA (agent-platform) | Foundry cloud (gpt-4.1) |
| Solo | Local Mac | devcontainer (agent-platform) | Foundry Local (phi-4 / qwen) |

Forbidden: Foundry Local inside Codespaces.

## What this strategy does not do

- Does not make the latest cookbook recipe architecture truth.
- Does not let prompt packs bypass skill wrappers.
- Does not allow provider SDK leakage outside `agent-platform/providers/`.
- Does not duplicate Foundry governance inside `agents/` or `agent-platform/`.

## Bottom line

Cookbooks donate patterns. Prompt packs deliver operator assets. Foundry runs the show. The provider adapter keeps the seams clean.

## Related

- [AI engineering reference bundle](AI_ENGINEERING_REFERENCE_BUNDLE.md)
- [Role-based prompt packs contract](../../agents/docs/contracts/ROLE_BASED_PROMPT_PACKS.md)
- [Cookbook pattern adoption rules](../../agents/docs/contracts/COOKBOOK_PATTERN_ADOPTION_RULES.md)
- [Model provider adapters](../../agent-platform/docs/architecture/MODEL_PROVIDER_ADAPTERS.md)
- [Foundry runtime alignment](../../agent-platform/docs/architecture/FOUNDRY_RUNTIME_ALIGNMENT.md)
- [Foundry control plane](../../platform/docs/architecture/FOUNDRY_CONTROL_PLANE.md)
