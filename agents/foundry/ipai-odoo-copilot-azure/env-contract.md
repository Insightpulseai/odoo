# Environment Variable Contract -- Odoo Copilot on Azure

> Version: 1.0.0
> Last updated: 2026-03-27
> Parent: runtime-contract.md (C-30)

## Required Variables

| Variable | Purpose | Source | Required At |
| --- | --- | --- | --- |
| `AZURE_FOUNDRY_API_KEY` | Azure OpenAI API key for Track 1 (direct) backend | Azure Key Vault `kv-ipai-dev` | Stage 1 (bootstrap) |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Foundry project config | Stage 1 |

## Optional Variables

| Variable | Purpose | Default | Required At |
| --- | --- | --- | --- |
| `AZURE_AI_FOUNDRY_ENDPOINT` | Foundry project endpoint for hosted agent surface | None | Stage 2 |
| `AZURE_AI_FOUNDRY_PROJECT` | Foundry project name | None | Stage 2 |
| `APPINSIGHTS_CONNECTION_STRING` | Application Insights telemetry sink | None (telemetry disabled) | Stage 2 |
| `COPILOT_TELEMETRY_ENABLED` | Enable/disable telemetry emission | `true` | Stage 2 |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint for retrieval grounding | None (retrieval disabled) | Stage 2 |
| `AZURE_SEARCH_API_KEY` | Azure AI Search query key | Azure Key Vault | Stage 2 |
| `AZURE_SEARCH_INDEX_NAME` | Search index name for knowledge grounding | `ipai-knowledge-index` | Stage 2 |

## Odoo ir.config_parameter Keys

These are set via the module's Settings UI or `data/ir_config_parameter.xml`:

| Parameter Key | Purpose | Default |
| --- | --- | --- |
| `ipai.copilot.enabled` | Master enable/disable switch | `True` |
| `ipai.copilot.gateway_url` | Custom gateway URL (Track 2 backend) | `http://localhost:8088` |
| `ipai.copilot.mode` | Operating mode | `PROD-ADVISORY` |
| `ipai.copilot.model` | Azure OpenAI deployment/model name | `gpt-4.1` |

## Backend Selection Logic

The gateway controller selects a backend automatically:

1. If `AZURE_FOUNDRY_API_KEY` env var is set and non-empty: **Track 1** (direct Azure OpenAI Chat Completions)
2. Otherwise: **Track 2** (custom gateway URL from `ipai.copilot.gateway_url`)

Track 1 is the current production path. Track 2 is reserved for the agent-platform gateway when it becomes operational.

## Secret Handling

- All secrets are sourced from Azure Key Vault (`kv-ipai-dev`) via managed identity at runtime.
- Secrets are injected as container environment variables by Azure Container Apps.
- No secrets in `odoo.conf`, `.env` files tracked in git, or any committed config.
- The `AZURE_FOUNDRY_API_KEY` is a Stage 1 bootstrap mechanism; the target is managed identity (Stage 2+).

## Vault Secret Names

| Vault Secret | Maps To |
| --- | --- |
| `azure-foundry-api-key` | `AZURE_FOUNDRY_API_KEY` |
| `srch-ipai-dev-api-key` | `AZURE_SEARCH_API_KEY` |
| `appinsights-connection-string` | `APPINSIGHTS_CONNECTION_STRING` |
