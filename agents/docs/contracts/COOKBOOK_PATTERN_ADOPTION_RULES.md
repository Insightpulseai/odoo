# Cookbook Pattern Adoption Rules — Contract

Authority: [`ssot/ai/external-reference-authorities.yaml`](../../../ssot/ai/external-reference-authorities.yaml)

## Purpose

Define how patterns from Anthropic Claude Cookbooks and OpenAI Cookbook are absorbed into IPAI. Cookbooks are **pattern donors**, not architecture sources of truth. Patterns enter `agent-platform/`, not `agents/`.

## Rules

- Cookbook patterns are **adapted, not copied**. Direct verbatim paste is forbidden.
- Source URL and cookbook revision are recorded in the module header of the adapted code.
- Cookbook dependencies are **not** imported wholesale — only the specific libraries required for the adopted pattern.
- Cookbook examples do not gain runtime authority, RBAC authority, or deployment authority.
- Claude-specific patterns live alongside OpenAI-specific patterns under `agent-platform/src/agent_platform/providers/`.

## What to extract

- Tool-calling patterns
- Managed-agent patterns
- Evaluation and observability patterns
- Multimodal patterns
- Skills packaging ideas

## What to ignore

- Hardcoded API keys, example credentials, test endpoints
- Provider-specific defaults that conflict with Foundry-as-default
- Prompt text (that belongs in `agents/` as a skill — see [Role-based prompt packs](ROLE_BASED_PROMPT_PACKS.md))
- Deployment instructions (Azure Pipelines owns deploy)

## Adoption header template

Every file that adopts a cookbook pattern includes a header comment:

```python
# Pattern adopted from: <cookbook source URL>
# Original revision: <commit sha or dated snapshot>
# Adaptation notes: <what was changed for IPAI>
# Owner: <team or person>
```

> [!NOTE]
> Cookbook examples may assume direct provider SDK usage. In IPAI, provider access always flows through the provider adapter in `agent-platform/src/agent_platform/providers/`. Adapt accordingly.

## Placement

| Pattern class | Target |
|---|---|
| Tool use / function calling | `agent-platform/src/agent_platform/tools/<domain>/` |
| Managed agent orchestration | `agent-platform/src/agent_platform/orchestration/` |
| Observability / tracing | `agent-platform/src/agent_platform/observability/` |
| Evaluation harnesses | `agent-platform/src/agent_platform/evals/` |
| Retrieval / RAG | `agent-platform/src/agent_platform/retrieval/` |
| Multimodal handling | `agent-platform/src/agent_platform/attachments/` |

## Non-goals

- Not treating cookbook recipes as canonical architecture.
- Not importing cookbook repositories as submodules.
- Not pulling prompt text from cookbooks without wrapping it as a skill.

## Related

- [Role-based prompt packs](ROLE_BASED_PROMPT_PACKS.md)
- [Model provider adapters](../../../agent-platform/docs/architecture/MODEL_PROVIDER_ADAPTERS.md)
- [Foundry runtime alignment](../../../agent-platform/docs/architecture/FOUNDRY_RUNTIME_ALIGNMENT.md)
- [External reference authorities](../../../ssot/ai/external-reference-authorities.yaml)
