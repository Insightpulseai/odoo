# Model Provider Adapters

Authority: [`ssot/agent-platform/agent_framework_adoption.yaml`](../../../ssot/agent-platform/agent_framework_adoption.yaml) + [`ssot/ai/external-reference-authorities.yaml`](../../../ssot/ai/external-reference-authorities.yaml)

## Purpose

Define how model providers (Foundry, Anthropic, OpenAI, Foundry Local) are isolated behind typed adapters in `agent-platform/src/agent_platform/providers/`. All agent code consumes providers through this adapter layer — never directly.

## Rules

- Provider SDK imports are permitted **only** under `agent-platform/src/agent_platform/providers/<provider>/`.
- Agent code imports from `agent_platform.providers` interface, not the vendor SDK.
- Model names are resolved through the adapter's registry, not hardcoded strings.
- API keys and endpoints are resolved through Managed Identity + Key Vault bindings, never embedded.
- Adapters normalize tracing, retries, rate limits, and error shapes across providers.

## Provider lanes

| Provider | Adapter path | Primary use |
|---|---|---|
| Foundry (default) | `providers/foundry/` | Production runtime for team mode; GPT-4.1 family deployments |
| Foundry Local | `providers/foundry_local/` | Solo mode on-device (phi-4 / qwen via NPU/GPU) |
| Anthropic | `providers/anthropic/` | Claude-specific pattern use cases |
| OpenAI (direct) | `providers/openai/` | Reserved for patterns where Foundry-hosted equivalents are insufficient |

## Provider selection policy

- **Default**: Foundry (team mode) / Foundry Local (solo mode).
- **Claude** only when a pattern demonstrably benefits from Claude-specific behavior (long-context code review, managed agent recipes from Claude Cookbooks).
- **OpenAI direct** only as a last resort where Foundry-hosted equivalents do not cover the capability.
- Selection is **configuration**, not code. Agents do not branch on provider.

## Adapter interface (shape)

```python
class ModelProvider(Protocol):
    async def complete(self, request: CompletionRequest) -> CompletionResponse: ...
    async def stream(self, request: CompletionRequest) -> AsyncIterator[Chunk]: ...
    async def tool_call(self, request: ToolCallRequest) -> ToolCallResponse: ...
    def capabilities(self) -> ProviderCapabilities: ...
```

Every adapter implements the same interface. Callers depend on the protocol, not the concrete class.

## Cross-provider normalization

Adapters normalize:

- Token counts and cost attribution
- Retry/backoff behavior
- Safety response handling
- Tracing span names and attributes
- Error taxonomy (rate_limit / context_window / provider_unavailable / content_blocked)

## What adapters do not own

- Agent skill definitions (→ `agents/`)
- Deployment / RBAC (→ `platform/` + Foundry resource model)
- Business logic (→ Odoo addons + domain packs)
- Prompt content (→ skills with prompt contracts)

> [!WARNING]
> Do not import provider SDKs outside `providers/`. Any code that does so is a boundary violation and must be refactored through the adapter interface.

## Related

- [Foundry runtime alignment](FOUNDRY_RUNTIME_ALIGNMENT.md)
- [Cookbook pattern adoption rules](../../../agents/docs/contracts/COOKBOOK_PATTERN_ADOPTION_RULES.md)
- [Agent framework adoption SSOT](../../../ssot/agent-platform/agent_framework_adoption.yaml)
- [Foundry resource model](../../../platform/ssot/ai/foundry-resource-model.yaml)
