# IPAI Odoo Copilot — Azure Foundry

This addon is the Odoo-side policy and configuration boundary for the physical Azure Foundry agent `ipai-odoo-copilot-azure` in project `data-intel-ph`.

## Integration Policy

- All new external Odoo integrations must use JSON-2 (`/json/2`).
- Legacy `/xmlrpc`, `/xmlrpc/2`, and `/jsonrpc` are migration-only.
- Custom Odoo controllers declared with `@route(type='jsonrpc')` are app-internal controller endpoints and are not the same as the deprecated external RPC endpoints.
- Odoo Extract API (`https://extract.api.odoo.com`) is a separate Odoo IAP OCR product path and is not the default path for Azure Document Intelligence integration.

## Canonical Defaults

- `foundry_project = data-intel-ph`
- `foundry_agent_name = ipai-odoo-copilot-azure`
- `foundry_model = gpt-4.1`
- `memory_enabled = False`
- `read_only_mode = True`
- `search_service = srch-ipai-dev`
- `foundry_api_endpoint = https://data-intel-ph-resource.services.ai.azure.com`
