# Azure AI Foundry & MCP Configuration Audit

> **Audit date**: 2026-03-14
> **Scope**: Insightpulseai/odoo repo -- Azure AI Foundry integration, MCP configuration, endpoint taxonomy, auth model, secret handling
> **Azure subscription**: `536d8cf6-89e1-4815-aef3-d5f2c5f4d070`
> **Azure tenant**: `402de71a-87ec-4302-a609-fb76098d1da7`

---

## 1. Summary Findings

### Critical

| # | Finding | Severity |
|---|---------|----------|
| C1 | **Exposed API keys in tracked `.env` files**: `.env.platform.local` contains live `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` values. `web/docflow-agentic-finance/.env` contains a live `OPENAI_API_KEY`. These are committed to git. | **CRITICAL** |
| C2 | **`ipai_enterprise_bridge` `foundry_provider_config.py` connection test hits `/openai/models`** which is a resource-level Azure OpenAI endpoint, not a Foundry project API. The test should validate the project endpoint directly. | **HIGH** |
| C3 | **Auth audience mismatch**: `foundry_provider_config.py` uses `cognitiveservices.azure.com/.default` for managed identity, but Foundry project APIs require `ai.azure.com/.default` audience for project-scoped operations. | **HIGH** |

### High

| # | Finding | Severity |
|---|---------|----------|
| H1 | **Two parallel Foundry config models** exist: `ipai_enterprise_bridge.foundry_provider_config` and `ipai_odoo_copilot.foundry_service` with divergent endpoint patterns and env var names (`AZURE_AI_FOUNDRY_API_KEY` vs `AZURE_FOUNDRY_API_KEY`). | HIGH |
| H2 | **`foundry_provider_config.py` endpoint field** accepts any URL without validation. No enforcement of the expected shape `https://<resource>.services.ai.azure.com/api/projects/<project>`. | HIGH |
| H3 | **No `auth_audience` field** on `foundry_provider_config` -- operators cannot distinguish between Cognitive Services audience and Foundry project audience. | HIGH |
| H4 | **Stale copilot-provider SSOT** (`ssot/odoo/copilot-provider.yaml`) references `AZURE_OPENAI_*` env vars from the deprecated `ipai_ai_copilot` module, not the current `ipai_odoo_copilot` module. | HIGH |

### Medium

| # | Finding | Severity |
|---|---------|----------|
| M1 | **MCP legacy catalog** (`.claude/mcp-servers.legacy.json`) contains correct HTTP entry for `https://mcp.ai.azure.com` but is marked as "legacy" -- no corresponding entry in `.vscode/mcp.json`. | MEDIUM |
| M2 | **`.vscode/mcp.json`** only contains Docker MCP gateway; no Azure Foundry MCP entry. | MEDIUM |
| M3 | **No deprecated MCP patterns found**: No `git+https://github.com/azure-ai-foundry/mcp-foundry.git`, no `uvx`/`uv` based Foundry MCP, no stdio Foundry config. Clean on this front. | INFO |
| M4 | **View XML placeholder mismatch**: `foundry_provider_config_views.xml` uses `https://your-foundry.azure.com` which does not match any real Azure endpoint family. | MEDIUM |
| M5 | **Document Intelligence endpoint** in `ipai_enterprise_bridge` views uses correct `cognitiveservices.azure.com` family. No issues. | INFO |

### Low

| # | Finding | Severity |
|---|---------|----------|
| L1 | **Archive directory** contains extensive deprecated code (`archive/root/addons/ipai/ipai_ai_copilot/`) with old `AZURE_OPENAI_*` patterns. Expected for archive, no action needed. | LOW |
| L2 | **`QUICK_START_CONFIGURATION.md`** references `AZURE_DOCUMENT_INTELLIGENCE_KEY` and `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` which are consistent with Document Intelligence service. Correct. | INFO |

---

## 2. Step 1 -- Deprecated MCP Pattern Detection

| Pattern | Status | Location |
|---------|--------|----------|
| `git+https://github.com/azure-ai-foundry/mcp-foundry.git` | **Not found** | -- |
| `run-azure-ai-foundry-mcp` | **Not found** | -- |
| `uv` / `uvx` based Foundry MCP startup | **Not found** | -- |
| `stdio` MCP config for Foundry | **Not found** | -- |
| Old experimental env vars from deprecated repo | **Not found** | -- |
| HTTP MCP at `https://mcp.ai.azure.com` | **Current** | `.claude/mcp-servers.legacy.json:202` |

**Verdict**: No deprecated MCP Foundry patterns exist in the repo. The only Foundry MCP reference is the correct cloud-hosted HTTP server URL in the legacy catalog.

---

## 3. Step 2 -- Current MCP Configuration Validation

### `.vscode/mcp.json`

```json
{"servers":{"MCP_DOCKER":{"command":"docker","args":["mcp","gateway","run"],"type":"stdio"}}}
```

**Finding**: Only Docker MCP gateway configured. No Azure Foundry MCP entry.

### `.claude/mcp-servers.legacy.json` (line 200-206)

```json
"microsoft-foundry": {
  "type": "http",
  "url": "https://mcp.ai.azure.com",
  "tools": ["*"],
  "description": "Microsoft Foundry MCP (official remote) ...",
  "status": "built"
}
```

**Finding**: Correct modern shape (`type: "http"`, `url: "https://mcp.ai.azure.com"`). However, this is in the **legacy** catalog, not the active `.vscode/mcp.json`. Needs promotion if Foundry MCP is desired in the dev workflow.

**Expected modern shape**: `{ "type": "http", "url": "https://mcp.ai.azure.com" }` with Entra sign-in.

---

## 4. Step 3 -- VS Code Workspace Readiness

| File | Status | Notes |
|------|--------|-------|
| `.vscode/settings.json` | Good | Python analysis paths include `addons/ipai`, `addons/oca`. Ruff formatter configured. |
| `.vscode/mcp.json` | Incomplete | Only Docker gateway. No Foundry MCP entry. |
| `.vscode/extensions.json` | Not audited (not in scope) | -- |
| Developer onboarding docs | Partial | `docs/development/VSCODE_ENTERPRISE.md` mentions `*.openai.azure.com` for Copilot inference but does not document Foundry MCP setup. |

---

## 5. Step 4 -- Azure Endpoint Taxonomy

### Active Code (non-archive)

| # | Endpoint | Family | Source File | Correct Family? | Auth Audience Correct? |
|---|----------|--------|-------------|-----------------|----------------------|
| E1 | `https://data-intel-ph-resource.services.ai.azure.com` | A. Foundry project API | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | Yes | Yes (`cognitiveservices.azure.com` for resource-level) |
| E2 | `https://<resource>.services.ai.azure.com` | A. Foundry project API | `ssot/ai/agents.yaml:17` | Yes | N/A (pattern only) |
| E3 | `https://cognitiveservices.azure.com/` | Auth scope | `addons/ipai/ipai_odoo_copilot/models/foundry_service.py:22` | N/A (IMDS scope) | Yes for resource-level API |
| E4 | `https://cognitiveservices.azure.com/.default` | Auth scope | `addons/ipai/ipai_enterprise_bridge/models/foundry_provider_config.py:94` | N/A (token scope) | **Partial** -- correct for resource-level, wrong for project-scoped |
| E5 | `https://<resource>.services.ai.azure.com/api/projects/<project>` | A. Foundry project API | `foundry_provider_config.py:115` (docstring only) | Yes | Needs `ai.azure.com/.default` for project scope |
| E6 | `https://<resource>.services.ai.azure.com/openai/models` | B. Azure OpenAI (via Foundry resource) | `foundry_provider_config.py:117`, `:139` | **Wrong for Foundry project test** | Mixed |
| E7 | `https://myresource.openai.azure.com` | B. Azure OpenAI | `addons/ipai/ipai_ask_ai_azure/views/res_config_settings_views.xml` | Yes (for Azure OpenAI) | N/A |
| E8 | `https://your-doc-ai.cognitiveservices.azure.com` | D. Document Intelligence | `ipai_enterprise_bridge` views | Yes | `cognitiveservices.azure.com/.default` |
| E9 | `https://ai.azure.com` | Foundry portal | `addons/ipai/ipai_odoo_copilot/views/res_config_settings_views.xml:25` | Yes (portal only) | N/A |
| E10 | `https://mcp.ai.azure.com` | Foundry MCP | `.claude/mcp-servers.legacy.json:202` | Yes | Entra sign-in |

### Endpoint Family Classification

| Family | Pattern | Auth Audience |
|--------|---------|---------------|
| **A. Foundry Project APIs** | `https://<resource>.services.ai.azure.com/api/projects/<project>` | `https://ai.azure.com/.default` (project-scoped) |
| **A'. Foundry Resource APIs** | `https://<resource>.services.ai.azure.com/openai/*` | `https://cognitiveservices.azure.com/.default` (resource-scoped) |
| **B. Azure OpenAI** | `https://<resource>.openai.azure.com` | `https://cognitiveservices.azure.com/.default` |
| **C. Azure AI Search** | `https://<service>.search.windows.net` | `https://search.azure.com/.default` |
| **D. Document Intelligence** | `https://<resource>.cognitiveservices.azure.com` | `https://cognitiveservices.azure.com/.default` |

---

## 6. Step 5 -- Auth Model Validation by Service

### `ipai_odoo_copilot` (foundry_service.py)

| Aspect | Intended | Actual | Status |
|--------|----------|--------|--------|
| Auth method | Managed identity (IMDS) -> env key fallback | Managed identity (IMDS) -> `AZURE_FOUNDRY_API_KEY` fallback | Correct |
| IMDS scope | `cognitiveservices.azure.com` | `cognitiveservices.azure.com/` | Correct for resource-level APIs |
| Test endpoint | Resource-level base URL | `GET <api_endpoint>` (base URL probe) | Correct |
| Agent resolution | Assistants API | `GET /openai/assistants?api-version=2024-12-01-preview` | Correct |

### `ipai_enterprise_bridge` (foundry_provider_config.py)

| Aspect | Intended | Actual | Status |
|--------|----------|--------|--------|
| Auth method | Managed identity -> api_key -> oauth2 | `DefaultAzureCredential` with `cognitiveservices.azure.com/.default` | **Partial** |
| Env var (api_key mode) | `AZURE_AI_FOUNDRY_API_KEY` | `AZURE_AI_FOUNDRY_API_KEY` | OK (but different from copilot module's `AZURE_FOUNDRY_API_KEY`) |
| Env var (bearer fallback) | `AZURE_AI_FOUNDRY_BEARER_TOKEN` | `AZURE_AI_FOUNDRY_BEARER_TOKEN` | OK |
| Connection test URL | Should test project endpoint | **Tests `/openai/models`** (resource-level) | **Wrong** |
| Auth audience | Should vary by API family | **Hardcoded to `cognitiveservices.azure.com/.default`** | **Incorrect for project APIs** |

### Audience Mismatch Summary

| Service | Expected Audience | `foundry_provider_config.py` Uses | Match? |
|---------|-------------------|-----------------------------------|--------|
| Foundry Project API | `https://ai.azure.com/.default` | `https://cognitiveservices.azure.com/.default` | No |
| Foundry Resource API (OpenAI) | `https://cognitiveservices.azure.com/.default` | `https://cognitiveservices.azure.com/.default` | Yes |
| Document Intelligence | `https://cognitiveservices.azure.com/.default` | N/A (separate config) | N/A |

---

## 7. Step 6 -- Secret Handling Validation

### Expected Secret Inventory

| Secret Name | Source | Used By |
|-------------|--------|---------|
| `AZURE_FOUNDRY_API_KEY` | Azure Key Vault / env var | `ipai_odoo_copilot` |
| `AZURE_AI_FOUNDRY_API_KEY` | Azure Key Vault / env var | `ipai_enterprise_bridge` |
| `AZURE_AI_FOUNDRY_BEARER_TOKEN` | Azure Key Vault / env var | `ipai_enterprise_bridge` |
| `AZURE_OPENAI_BASE_URL` | Azure Key Vault / env var | `ssot/odoo/copilot-provider.yaml` (stale) |
| `AZURE_OPENAI_API_KEY` | Azure Key Vault / env var | `ssot/odoo/copilot-provider.yaml` (stale) |
| `AZURE_OPENAI_DEPLOYMENT` | Azure Key Vault / env var | `ssot/odoo/copilot-provider.yaml` (stale) |

### Actual Secret Findings

| File | Finding | Severity |
|------|---------|----------|
| `.env.platform.local:48` | **Live `ANTHROPIC_API_KEY`** committed: `sk-ant-api03-w98D...` | **CRITICAL** |
| `.env.platform.local:51` | **Live `OPENAI_API_KEY`** committed: `sk-proj-Uw32...` | **CRITICAL** |
| `web/docflow-agentic-finance/.env:4` | **Live `OPENAI_API_KEY`** committed: `sk-proj-cztG...` | **CRITICAL** |
| `web/apps/ops-console/.env.local:17` | Placeholder key `sk-test-placeholder-key` | LOW (not real) |
| Multiple `.env.example` files | Template keys (no real values) | OK |

### Secret Handling in Odoo Modules

| Module | Pattern | Status |
|--------|---------|--------|
| `ipai_odoo_copilot` | `os.environ.get("AZURE_FOUNDRY_API_KEY")` | Correct -- env var only |
| `ipai_enterprise_bridge` | `os.getenv("AZURE_AI_FOUNDRY_API_KEY")` | Correct -- env var only |
| `ipai_enterprise_bridge` | `DefaultAzureCredential()` | Correct -- SDK-based |
| `ir.config_parameter` | Non-secret config only (endpoints, project names) | Correct |

---

## 8. Step 7 -- Architecture Assessment

### Separation of Concerns

| Principle | Status | Notes |
|-----------|--------|-------|
| **Config vs runtime secrets** | Good | Non-secret config in `ir.config_parameter`, secrets in env vars / Key Vault |
| **Module boundaries** | **Needs work** | Two modules (`ipai_enterprise_bridge`, `ipai_odoo_copilot`) both configure Foundry with different field names, env vars, and test patterns |
| **Endpoint family clarity** | **Needs work** | `foundry_provider_config.py` mixes Foundry project URLs with OpenAI resource-level URLs in test |
| **Auth audience separation** | **Needs work** | Single hardcoded audience; no field to distinguish per-service audience |

### Identity-First Auth

| Principle | Status |
|-----------|--------|
| Managed identity preferred | Yes -- both modules try IMDS first |
| API key as fallback | Yes -- env var only, never in DB |
| No secrets in DB | Yes -- verified |
| Token scope documented | Partially -- in docstrings but not in field help text |

### Least Privilege

| Principle | Status |
|-----------|--------|
| Read-only default | Yes -- `ipai_odoo_copilot` defaults to `read_only_mode=True` |
| Test connection is non-mutating | Yes -- GET only |
| Agent resolution is read-only | Yes -- list only, never creates |

### Service Boundary Clarity

| Area | Status |
|------|--------|
| Foundry project API vs OpenAI resource API | **Not clear** -- `foundry_provider_config.py` conflates them |
| Document Intelligence vs Foundry | Good -- separate config model |
| Portal URL vs API URL | Good -- `ipai_odoo_copilot` separates them clearly |

---

## 9. Step 8 -- Remediation Table

| # | Issue | Severity | File | Change Needed |
|---|-------|----------|------|---------------|
| R1 | Exposed API keys in `.env.platform.local` | CRITICAL | `.env.platform.local` | **Revoke keys immediately**. Add to `.gitignore`. Remove from git history with `git filter-repo`. |
| R2 | Exposed API key in `web/docflow-agentic-finance/.env` | CRITICAL | `web/docflow-agentic-finance/.env` | **Revoke key immediately**. Add to `.gitignore`. |
| R3 | Connection test hits `/openai/models` | HIGH | `addons/ipai/ipai_enterprise_bridge/models/foundry_provider_config.py` | **Fixed in this audit** -- test now validates project endpoint shape and hits correct URL |
| R4 | No endpoint URL shape validation | HIGH | `foundry_provider_config.py` | **Fixed in this audit** -- added `_validate_endpoint_shape()` constraint |
| R5 | Missing `auth_audience` field | HIGH | `foundry_provider_config.py` | **Fixed in this audit** -- added `auth_audience` selection field |
| R6 | View placeholder incorrect | MEDIUM | `foundry_provider_config_views.xml` | **Fixed in this audit** -- updated to correct shape |
| R7 | Enterprise bridge settings help text vague | MEDIUM | `ipai_enterprise_bridge/models/res_config_settings.py` | **Fixed in this audit** -- updated help text |
| R8 | Enterprise bridge settings view placeholder | MEDIUM | `ipai_enterprise_bridge/views/res_config_settings_views.xml` | **Fixed in this audit** -- updated placeholder |
| R9 | Stale `copilot-provider.yaml` | HIGH | `ssot/odoo/copilot-provider.yaml` | Needs separate update to reference `ipai_odoo_copilot` env vars |
| R10 | Dual env var names for same purpose | HIGH | Both Foundry modules | Needs consolidation: pick one of `AZURE_FOUNDRY_API_KEY` / `AZURE_AI_FOUNDRY_API_KEY` |
| R11 | No Foundry MCP in `.vscode/mcp.json` | MEDIUM | `.vscode/mcp.json` | Add HTTP entry for `https://mcp.ai.azure.com` when Foundry MCP is needed in dev workflow |

---

## 10. Current vs Target Configuration Matrix

### MCP Configuration

| Aspect | Current | Target |
|--------|---------|--------|
| `.vscode/mcp.json` | Docker gateway only | Docker gateway + Foundry HTTP MCP |
| Foundry MCP type | `http` (in legacy catalog) | `http` |
| Foundry MCP URL | `https://mcp.ai.azure.com` | `https://mcp.ai.azure.com` |
| Foundry MCP auth | Entra sign-in | Entra sign-in |
| Deprecated stdio/uvx patterns | None found | None (clean) |

### Endpoints

| Service | Current Endpoint | Target Endpoint |
|---------|-----------------|----------------|
| Foundry Project API | `https://data-intel-ph-resource.services.ai.azure.com` (resource-level) | `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph` (project-level) |
| Foundry Portal | `https://ai.azure.com` | `https://ai.azure.com` |
| Azure OpenAI | `https://<resource>.openai.azure.com` (in `ipai_ask_ai_azure`) | Same |
| Document Intelligence | `https://<resource>.cognitiveservices.azure.com` | Same |
| Azure AI Search | `srch-ipai-dev` (service name only) | `https://srch-ipai-dev.search.windows.net` |
| Foundry MCP | `https://mcp.ai.azure.com` | Same |

### Auth Audiences

| Service | Current Audience | Target Audience |
|---------|-----------------|----------------|
| Foundry Project API | `cognitiveservices.azure.com/.default` | `ai.azure.com/.default` (project-scoped) |
| Foundry Resource API (OpenAI compat) | `cognitiveservices.azure.com/.default` | `cognitiveservices.azure.com/.default` (correct) |
| Document Intelligence | `cognitiveservices.azure.com/.default` | Same (correct) |
| Azure AI Search | Not configured | `search.azure.com/.default` |

### Secret Sources

| Secret | Current Source | Target Source |
|--------|---------------|--------------|
| Foundry API key (`ipai_odoo_copilot`) | `AZURE_FOUNDRY_API_KEY` env var | Azure Key Vault -> env var |
| Foundry API key (`ipai_enterprise_bridge`) | `AZURE_AI_FOUNDRY_API_KEY` env var | Azure Key Vault -> env var (consolidate name) |
| Foundry bearer token | `AZURE_AI_FOUNDRY_BEARER_TOKEN` env var | Managed identity (eliminate env var) |
| Azure OpenAI key (stale) | `AZURE_OPENAI_API_KEY` env var | Deprecate -- use Foundry project API instead |

### VS Code Setup

| Aspect | Current | Target |
|--------|---------|--------|
| Python analysis paths | Includes `addons/ipai`, `addons/oca` | Same (correct) |
| MCP servers | Docker gateway only | Docker gateway + Foundry HTTP MCP |
| Copilot instructions | Enabled via `github.copilot.chat.codeGeneration.useInstructionFiles` | Same (correct) |

---

## 11. Azure Resources Inventory (Actual)

| Resource Group | Resource | Type | Status |
|----------------|----------|------|--------|
| `rg-ipai-ai-dev` | `aifoundry-ipai-dev` | AI Foundry Workspace | Exists |
| `rg-ipai-ai-dev` | `proj-ipai-claude` | AI Foundry Project | Exists |
| `rg-ipai-ai-dev` | `aifoundrkeyvault67125c7c` | Key Vault | Exists |
| `rg-ipai-ai-dev` | `aifoundrstorage6ff030454` | Storage Account | Exists |
| `rg-data-intel-ph` | `data-intel-ph-resource` | Cognitive Services | Exists |
| `rg-data-intel-ph` | `data-intel-ph` | AI Project | Exists |
| -- | ACR | Container Registry | **Does not exist** |
| -- | Container Apps | ACA | **Does not exist** |
| -- | Front Door | CDN/WAF | **Does not exist** |

**Note**: 14 resource groups exist, mostly empty. Production infrastructure (ACR, ACA, Front Door) referenced in `docs/architecture/` does not yet exist in Azure.

---

## 12. Code Changes Applied in This Audit

### `foundry_provider_config.py`

1. Added `auth_audience` selection field with correct audiences per API family
2. Updated `endpoint` help text to specify expected URL shape
3. Added `_validate_endpoint_shape()` constraint method
4. Fixed `action_test_connection()` to use the project endpoint directly (not `/openai/models`)
5. Updated `_resolve_auth_headers()` to use configured `auth_audience`

### `foundry_provider_config_views.xml`

1. Updated endpoint placeholder to correct shape
2. Added `auth_audience` field to form

### `test_foundry_config.py`

1. Updated tests to cover new `auth_audience` field
2. Updated connection test assertions for new endpoint pattern
3. Added endpoint validation test

### `ipai_enterprise_bridge/models/res_config_settings.py`

1. Updated `ipai_foundry_endpoint` help text to specify expected URL shape

### `ipai_enterprise_bridge/views/res_config_settings_views.xml`

1. Updated Foundry endpoint placeholder to correct URL shape

---

*Audit performed by Claude Opus 4.6. All code changes are in the working tree, not yet committed.*
