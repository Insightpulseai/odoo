# GitHub Copilot SDK

> Source: github.com/copilot-sdk

## What it is

A technical preview SDK for embedding the GitHub Copilot CLI engine in applications. Provides SDKs for Python, TypeScript, Go, and .NET with JSON-RPC communication. This is the **developer assistant layer** — not an enterprise agent runtime, not a channel delivery SDK, not an external platform connector.

## Key Capabilities

| Capability | Description |
|-----------|-------------|
| Multi-language SDKs | Python, TypeScript, Go, .NET — all communicating via JSON-RPC |
| Copilot subscription mode | Uses active GitHub Copilot subscription for LLM access |
| BYOK mode | Bring Your Own Key — supports OpenAI, Azure AI Foundry, Anthropic as providers |
| Code generation | Context-aware code suggestions, completions, and generation |
| Repo-aware context | Understands repository structure, conventions, and codebase patterns |
| CLI integration | Embeddable in CLI tools, IDEs, and developer workflows |
| File-edit planning | Plans multi-file changes based on natural language descriptions |

## Role in Our Stack

**Developer-assistant embedding only, not enterprise runtime.**

Use this when you need to:
- Embed coding assistance in a developer tool
- Build a repo-aware development assistant
- Set up BYOK provider configuration for a dev team
- Integrate Copilot engine in CLI-based workflows

## What it is NOT

| Misuse | Correct layer |
|--------|--------------|
| Enterprise agent runtime | Microsoft Agent Framework (`microsoft/agent-framework`) |
| Channel delivery (Teams, M365 Copilot) | Microsoft 365 Agents SDK (`microsoft/Agents`) |
| External platform connector (Palantir) | Palantir Foundry SDK (`palantir/foundry-platform-python`) |

## Critical Auth Constraint

**BYOK does NOT support Entra ID or managed identities.** When using BYOK mode with OpenAI, Azure AI Foundry, or Anthropic, authentication is API-key-based only. Do not assume enterprise identity integration is available in BYOK mode. This is a hard architectural constraint documented by GitHub.

## Maturity Warning

The Copilot SDK is in **technical preview**. It is not GA (generally available). Production use requires:
- Explicit quality evaluation of generated code
- Acceptance of preview stability guarantees (or lack thereof)
- Fallback plan if the SDK changes or is discontinued

## Architecture Position

```
Microsoft Agent Framework    (orchestration)
Microsoft 365 Agents SDK    (channel delivery)
GitHub Copilot SDK         <-- THIS (developer assistance)
Palantir Foundry SDK        (external integration, optional)
```

The Copilot SDK is a peer to the other SDKs, not a layer above or below them. It serves a fundamentally different use case (developer productivity) and should not be used as a substitute for enterprise agent orchestration or channel delivery.

## Key Design Patterns

1. **JSON-RPC Client**: All SDK communication uses JSON-RPC. Configure the client with the target provider endpoint and credentials.
2. **BYOK Provider Setup**: Select provider (OpenAI, Azure AI Foundry, Anthropic), configure API key via environment variable, set model parameters.
3. **Quality Gate**: Before any production use, run generated code through quality evaluation — measure accuracy, safety, and relevance against a test set.
4. **Subscription Check**: At initialization, verify Copilot subscription status. If no subscription and no BYOK config, fail fast with a clear error.

## Cross-References

- Persona: `agents/personas/developer-copilot.md`
- Skill: `agents/skills/copilot-sdk-dev-assistant/`
- Skill map: `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
