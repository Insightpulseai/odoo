# AI Engineering Reference Bundle

Canonical source: [`ssot/ai/external-reference-authorities.yaml`](../../ssot/ai/external-reference-authorities.yaml)

## Purpose

Single entrypoint for the four external AI engineering sources IPAI consumes. Each source has a fixed role, an absorbing repo, and a set of adoption rules. Cookbooks donate patterns. Prompt packs deliver operator assets. Foundry provides the governed runtime.

## The four sources

| Source | Role | Absorbs into | Contract doc |
|---|---|---|---|
| Anthropic Claude Cookbooks | Claude pattern donor | `agent-platform/` | [Cookbook pattern adoption rules](../../agents/docs/contracts/COOKBOOK_PATTERN_ADOPTION_RULES.md) |
| OpenAI Cookbook | OpenAI pattern donor | `agent-platform/` | [Cookbook pattern adoption rules](../../agents/docs/contracts/COOKBOOK_PATTERN_ADOPTION_RULES.md) |
| OpenAI Academy Prompt Packs | Role-based operator assets | `agents/` | [Role-based prompt packs](../../agents/docs/contracts/ROLE_BASED_PROMPT_PACKS.md) |
| Microsoft Foundry | Governed Azure runtime + control plane | `platform/` | [Foundry control plane](../../platform/docs/architecture/FOUNDRY_CONTROL_PLANE.md) |

## Clean role split

```
cookbooks        → implementation patterns       → agent-platform/
prompt packs     → role-based prompt assets      → agents/
Microsoft Foundry → governed runtime + control   → platform/
```

## Adoption rules (summary)

- **Cookbooks are adapted, not copied.** Source URL and revision recorded in module headers. Provider SDK imports permitted only under `agent-platform/src/agent_platform/providers/`.
- **Prompt packs are wrapped as skills.** Freeform prompt text outside a skill wrapper is forbidden. Each skill has input schema, output schema, evaluators, safe-outputs policy, approval band.
- **Foundry is referenced, not duplicated.** Endpoints, model names, and RBAC live in Foundry. `agent-platform/` reads via environment + Key Vault.

## What this bundle does not do

- Does not make any single external source the architecture source of truth.
- Does not blend cookbook recipes with governed runtime code.
- Does not let prompt packs bypass skill wrappers or Safe Outputs middleware.
- Does not leak provider SDKs outside `agent-platform/providers/`.

## Related

- [Multi-model runtime and prompt strategy](MULTI_MODEL_RUNTIME_AND_PROMPT_STRATEGY.md)
- [External reference authorities SSOT](../../ssot/ai/external-reference-authorities.yaml)
- [Agent framework adoption SSOT](../../ssot/agent-platform/agent_framework_adoption.yaml)
- [Foundry resource model](../../platform/ssot/ai/foundry-resource-model.yaml)
- [Three-protocol model](three-protocol-model.md)
