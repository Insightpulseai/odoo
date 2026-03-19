# Azure AI Foundry Integration Test Evidence

**Timestamp**: 2026-03-19T02:17:38Z (UTC)
**Tester**: Claude Agent (automated integration test)

## Endpoint Tested

- **Resource**: `data-intel-ph-resource`
- **Endpoint**: `https://data-intel-ph-resource.cognitiveservices.azure.com/`
- **Resource Group**: `rg-data-intel-ph`

## Model Deployments Tested

- **Chat**: `gpt-4.1` (OpenAI-compat surface, api-version `2025-01-01-preview`)
- **Embedding**: `text-embedding-3-small` (not tested in this run)

## Raw Curl Result: PASS

Direct API call via `AzureFoundryClient.chatCompletion()`:

- **Status**: HTTP 200 OK
- **Model response**: Coherent month-end close process explanation (200 tokens)
- **Finish reason**: `length` (200 max_tokens limit hit, expected)
- **Token usage**: 29 prompt / 200 completion
- **Latency**: ~3000ms (first call, includes TLS + cold path)

Sample response (first 300 chars):

> The **standard month-end close process** is a series of accounting procedures performed at the end of each month to ensure that financial records are accurate, complete, and ready for reporting. The process helps organizations track performance, comply with regulations, and prepare for audits. Here's...

## Agent-Platform Integration Result: PASS

Full orchestrator flow (`Orchestrator.execute()` with `AzureFoundryClient`):

- **Status**: Success (4/4 tests pass)
- **System prompt**: Loaded from `agents/foundry/ipai-odoo-copilot-azure/system-prompt.md`
- **Tool definitions**: Loaded from `agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json`
- **Guardrails**: Loaded from `agents/foundry/ipai-odoo-copilot-azure/guardrails.md`
- **Token usage**: 1444 prompt / 473 completion (includes system prompt + tool defs)
- **Latency**: 6069ms (full orchestration including prompt assembly, API call, audit)
- **Blocked**: false (advisory query correctly allowed)
- **Correlation ID propagation**: Verified (request_id matches response)
- **Audit events**: 2 emitted (copilot_chat_request + copilot_chat_response)

Sample orchestrated response (first 300 chars):

> The standard month-end close process in Odoo typically follows these key steps, designed to ensure accurate and timely financial reporting. Here's an overview applicable to Odoo Community Edition (CE 19.0):
> ### 1. Preliminary Checks
> - **Verify Data Entry:** Ensure all sales, purchase, expense...

## Errors Found and Fixed

### 1. Tool schema validation error (FIXED)

**Error**: `Invalid schema for function 'search_records': In context=('properties', 'domain', 'items'), array schema missing items.`

**Root cause**: The `domain` field in `tool-definitions.json` defined `items: { type: "array" }` without a nested `items` property. The OpenAI function-calling API requires all array types to have `items` defined recursively.

**Fix**: Added `items: { type: "string" }` to the inner array definition in `agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json`.

### 2. Test assertion too strict (FIXED)

**Error**: Test asserted `finish_reason === 'stop'` but got `'length'` due to 200 max_tokens limit.

**Fix**: Relaxed assertion to accept both `stop` and `length` as valid finish reasons for the raw client test.

## Test Summary

| Test | Result | Latency |
|------|--------|---------|
| AzureFoundryClient.isConfigured() | PASS | <1ms |
| AzureFoundryClient.healthCheck() | PASS | 1170ms |
| AzureFoundryClient.chatCompletion() (raw) | PASS | 3001ms |
| Orchestrator.execute() (full flow) | PASS | 6074ms |

## Key Vault

**Action required (manual)**: Store the API key in Azure Key Vault:

```bash
az keyvault secret set --vault-name ipai-odoo-dev-kv --name foundry-api-key \
  --value "$(az cognitiveservices account keys list -n data-intel-ph-resource -g rg-data-intel-ph --query 'key1' -o tsv)" \
  --query "name" -o tsv
```

## Files Changed

- `agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json` -- Fixed `search_records.domain.items` schema
- `agent-platform/packages/builder-runner/src/tests/foundry-integration.test.ts` -- Integration test (new)
- `agent-platform/packages/builder-runner/src/tests/run-integration.ts` -- Test runner helper (new)
- `agent-platform/packages/builder-runner/package.json` -- Added `test:integration` script, fixed `test` glob
- `agent-platform/docs/evidence/foundry-integration-test/README.md` -- This file
