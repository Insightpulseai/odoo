# copilot-sdk-dev-assistant

Embed GitHub Copilot CLI engine in developer tools and workflows — coding assistance, file-edit planning, repo-aware context.

## When to use
- Developer tool integration requiring coding assistance
- Coding assistant setup for a team or project
- BYOK provider configuration (OpenAI, Azure AI Foundry, Anthropic)
- Quality evaluation of Copilot SDK code generation

## Key rule
This is a **technical preview** for developer assistance only. It is NOT an enterprise agent runtime. BYOK mode does NOT support Entra ID or managed identities — this is a hard auth constraint. Always evaluate code generation quality before production use.

## Cross-references
- `agents/personas/developer-copilot.md`
- `agents/knowledge/benchmarks/github-copilot-sdk.md`
- `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
