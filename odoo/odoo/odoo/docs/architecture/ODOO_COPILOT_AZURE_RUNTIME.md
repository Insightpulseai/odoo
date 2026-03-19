# Odoo Copilot Azure Runtime

## Purpose

This document defines the canonical runtime path for operating Odoo Copilot on Azure.

## Canonical runtime path

Browser
-> `https://erp.insightpulseai.com`
-> Odoo web/client
-> Copilot controller (`/ipai/copilot/chat`)
-> provider bridge (`services/provider_bridge.py`)
-> Azure OpenAI deployment

## Ownership

### `odoo`
- Copilot UI entry
- controller/route
- persona/auth context
- request/response handling
- provider SSOT
- config seeding (env -> ir.config_parameter)

### `infra`
- ACA / Front Door / DNS / Key Vault / managed identity
- Azure runtime service inventory
- public hostname routing

### `ops-platform` (optional)
- control-plane metadata if provider settings are stored there

## Canonical public surface

- `https://erp.insightpulseai.com`

ACA-generated hostnames are implementation details and not canonical user-facing URLs.

## Provider contract

Machine-readable provider configuration is defined in:

- `ssot/odoo/copilot-provider.yaml`

## Config seeding mechanism

At module install/upgrade, the `post_init_hook` in `hooks.py` reads Azure OpenAI
configuration from container environment variables and writes them into
`ir.config_parameter`. This enables zero-touch configuration on Azure Container Apps
where Key Vault secrets are injected as env vars via managed identity.

**Seeding rules:**
- Only writes if the env var is set AND the DB value is empty/missing.
- DB values always take precedence (manual overrides via Settings UI are never clobbered).
- API key values are never logged; only key names are logged.

**Environment variables seeded:**

| Env Var | ir.config_parameter key | Required |
|---------|------------------------|----------|
| `AZURE_OPENAI_BASE_URL` | `ipai_ask_ai_azure.base_url` | Yes |
| `AZURE_OPENAI_API_KEY` | `ipai_ask_ai_azure.api_key` | Yes |
| `AZURE_OPENAI_DEPLOYMENT` | `ipai_ask_ai_azure.model` | Yes |
| `AZURE_OPENAI_API_MODE` | `ipai_ask_ai_azure.api_mode` | No (defaults to `responses`) |

## API mode support

Two Azure OpenAI API modes are supported:

### `responses` (default)
- Endpoint: `{base_url}/openai/v1/responses`
- Input format: array of message objects with `input_text` content blocks
- Output: parsed from `output[].content[].text`

### `chat_completions`
- Endpoint: `{base_url}/openai/v1/chat/completions`
- Input format: standard OpenAI `messages` array
- Output: parsed from `choices[0].message.content`

Set the mode via `AZURE_OPENAI_API_MODE` env var or `ipai_ask_ai_azure.api_mode`
config parameter. If unset, defaults to `responses`.

## ir.config_parameter keys used at runtime

| Key | Purpose | Source |
|-----|---------|--------|
| `ipai_ask_ai_azure.base_url` | Azure OpenAI endpoint URL | `AZURE_OPENAI_BASE_URL` env var or Settings UI |
| `ipai_ask_ai_azure.api_key` | API key for authentication | `AZURE_OPENAI_API_KEY` env var or Settings UI |
| `ipai_ask_ai_azure.model` | Azure deployment name | `AZURE_OPENAI_DEPLOYMENT` env var or Settings UI |
| `ipai_ask_ai_azure.api_mode` | API mode (responses/chat_completions) | `AZURE_OPENAI_API_MODE` env var or Settings UI |
| `ipai_ai_copilot.bridge_url` | Optional external bridge URL | Settings UI only |
| `ipai_ai_copilot.bridge_token` | Optional bridge auth token | Settings UI only |

## Runtime rule

The Azure OpenAI deployment name must be used as the configured target identifier for provider calls.
Do not assume the base model family name (e.g., `gpt-4o`) is the deployment name.

## Provider resolution order

1. Azure OpenAI direct (if `ipai_ask_ai_azure.*` config params are set)
2. `ipai.ai.provider` model default (any provider type)
3. Error: `NO_PROVIDER_CONFIGURED`

## Operational minimum

Copilot is operational only when:

- login works
- authenticated route call succeeds
- Azure-backed response succeeds
- logs are usable
- health surfaces remain green

## Evidence expectation

A live validation artifact should be recorded once the first successful Azure-backed Copilot request completes.
See `docs/reports/ODOO_COPILOT_AZURE_LIVE_VALIDATION.md` for the checklist.
