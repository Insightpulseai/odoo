# Checklist — copilot-sdk-dev-assistant

- [ ] Copilot subscription status verified OR BYOK provider configured
- [ ] If BYOK: provider selected (OpenAI, Azure AI Foundry, or Anthropic)
- [ ] If BYOK: API key stored in env var or secret store (never hardcoded)
- [ ] If BYOK: Entra/managed identity limitation documented for stakeholders
- [ ] SDK client configured for target language (Python, TypeScript, Go, .NET)
- [ ] JSON-RPC communication channel established and tested
- [ ] Repository context provided to SDK for repo-aware suggestions
- [ ] Target developer tool integration complete
- [ ] Code generation quality evaluated against test set
- [ ] Accuracy score meets minimum threshold (0.90)
- [ ] Safety evaluation performed (no secrets, no harmful code in suggestions)
- [ ] Technical preview maturity status documented for consumers
- [ ] Fallback plan documented in case SDK changes or is discontinued
- [ ] Evidence captured in `docs/evidence/{stamp}/copilot-sdk/integration/`
