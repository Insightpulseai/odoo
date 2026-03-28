# Runtime Overview

> Odoo Copilot runtime modes, Foundry project dependencies, and model configuration.

## Runtime Modes

### Prompt-only (current)

The copilot module (`ipai_odoo_copilot`) calls Azure AI Foundry via the
Responses API. No durable agent state exists on the Foundry side. Each request
is a stateless prompt with Odoo context injected by the bridge module.

```
User -> Odoo Web Client -> ipai_odoo_copilot -> Azure AI Foundry (Responses API) -> gpt-4.1
```

Characteristics:
- No Foundry Agent deployment required
- No persistent thread or conversation state on Foundry
- Context window is the sole memory mechanism
- Tool definitions are sent per-request from Odoo
- Suitable for single-turn and short multi-turn interactions

### Hosted Agent (target)

Foundry Agent Service hosts a durable agent with registered tools, knowledge
connections, and thread management. Odoo acts as a channel that routes user
messages to the hosted agent and renders responses.

```
User -> Odoo Web Client -> ipai_odoo_copilot -> Foundry Agent Service -> gpt-4.1
                                                      |
                                              Tool calls -> Odoo JSON-RPC / FastAPI
                                              Knowledge  -> Azure AI Search
```

Characteristics:
- Durable agent definition in Foundry project
- Thread-based conversation state
- Server-side tool orchestration with retry/timeout
- Knowledge grounding via connected Azure AI Search index
- Evaluation and tracing via Foundry built-in capabilities
- Requires Foundry Agent deployment

## Foundry Project Dependencies

| Resource | Value | Purpose |
|----------|-------|---------|
| Foundry project | `data-intel-ph` | Agent definitions, evaluations, tracing |
| Foundry resource | `data-intel-ph-resource` | Azure OpenAI endpoint backing |
| Model deployment | `gpt-4.1` | Primary inference model |
| Entra tenant | `402de71a-87ec-4302-a609-fb76098d1da7` | Identity provider |
| Token scope | `https://cognitiveservices.azure.com/.default` | Foundry auth scope |

## Model Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | `gpt-4.1` | Azure OpenAI deployment name |
| API mode | `responses` | Responses API (default), `chat_completions` supported |
| Timeout | 60s | Per-request timeout |
| Temperature | 0.1 | Low temperature for deterministic ERP actions |
| Max tokens | 4096 | Response token limit |

Provider SSOT: `ssot/odoo/copilot-provider.yaml`

## Configuration Hierarchy

```
Azure Key Vault (kv-ipai-dev)
  -> Container App env vars (AZURE_OPENAI_BASE_URL, AZURE_OPENAI_API_KEY, ...)
    -> Odoo ir.config_parameter (ipai_ask_ai_azure.base_url, ...)
      -> Module runtime reads from ir.config_parameter
```

DB values take precedence over env vars after initial seeding. Env vars seed
`ir.config_parameter` at module install time only.

## Transition Path: Prompt-only to Hosted

| Step | Action | Dependency |
|------|--------|------------|
| 1 | Register tools in Foundry Agent definition | Tool contract finalized (`ssot/odoo/odoo_copilot_finance_tools.yaml`) |
| 2 | Connect Azure AI Search index as knowledge source | Search index provisioned and populated |
| 3 | Deploy Foundry Agent in `data-intel-ph` project | Agent definition + tool registration |
| 4 | Update `ipai_odoo_copilot` to use Agent API | Module code change |
| 5 | Enable Foundry tracing and evaluation | Foundry project configuration |
| 6 | Migrate from per-request tool injection to server-side tools | Module + agent config |
