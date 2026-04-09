# Odoo Copilot Deployed State Map

> Crawled from source code on 2026-03-15. All facts derived from code, config, and infra SSOT files.

---

## 1. Service Inventory

| Component | Type | Location | Status |
|-----------|------|----------|--------|
| `ipai_odoo_copilot` | Odoo addon (v19.0.2.0.0) | `addons/ipai/ipai_odoo_copilot/` | Installable |
| `ipai_enterprise_bridge` | Odoo addon (Foundry provider config) | `addons/ipai/ipai_enterprise_bridge/` | Installable |
| `odoo-docs-kb` | FastAPI RAG service | `apps/odoo-docs-kb/service.py` | Container image (ACA target: `ipai-odoo-docs-kb`) |
| `odoo-docs-kb` (package) | Python chunker/embed/index library | `packages/odoo-docs-kb/` | Library (not deployed standalone) |

### Azure Container App Targets

- **Odoo (copilot addon runs inside)**: `ipai-odoo-dev-web` in `rg-ipai-dev` (southeastasia)
- **Docs KB RAG service**: `ipai-odoo-docs-kb` in `rg-ipai-dev` (pipeline-defined, not yet in resources.yaml)
- **Foundry project**: `data-intel-ph` in `rg-data-intel-ph` (eastus2)

---

## 2. HTTP Endpoint Paths

### Odoo Controller Routes (ipai_odoo_copilot)

| Route | Method | Auth | CSRF | Description |
|-------|--------|------|------|-------------|
| `/ipai/copilot/chat` | POST (JSON-RPC) | `user` (Odoo session) | Yes | Authenticated chat for ERP users |
| `/ipai/copilot/chat/service` | POST (JSON-RPC) | `none` (service key) | No | Service-to-service for external widgets |

**Service auth**: `X-Copilot-Service-Key` header, validated via HMAC compare against `IPAI_COPILOT_SERVICE_KEY` env var.

### Docs KB RAG Service (FastAPI)

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/health` | GET | None | Health check (returns index name, client status) |
| `/search` | POST | None (internal) | Hybrid vector+text search over Odoo 18 docs |
| `/answer` | POST | None (internal) | Grounded answer with citations |
| `/search/module` | POST | None (internal) | Module-scoped doc search |

---

## 3. Config Parameters (ir.config_parameter)

All keys are prefixed with `ipai_odoo_copilot.`

| Key | Default | Description |
|-----|---------|-------------|
| `foundry_enabled` | `False` | Master switch |
| `foundry_endpoint` | (empty) | Portal URL for "Open Portal" button |
| `foundry_api_endpoint` | `https://data-intel-ph-resource.services.ai.azure.com` | API endpoint for probes and agent resolution |
| `foundry_project` | `data-intel-ph` | Azure Foundry project name |
| `foundry_agent_name` | `ipai-odoo-copilot-azure` | Physical agent name in Foundry |
| `foundry_model` | `gpt-4.1` | Model deployment name |
| `foundry_search_service` | `srch-ipai-dev` | Azure AI Search service name |
| `foundry_search_connection` | (empty) | Search connection name |
| `foundry_search_index` | (empty) | Default search index name |
| `foundry_memory_enabled` | `False` | Agent memory toggle |
| `foundry_read_only_mode` | `True` | Read-only mode (blocks write tools) |
| `foundry_agent_api_mode` | `agents` | API path mode: `agents` or `assistants-compat` |

### Additional config keys (ipai_enterprise_bridge via copilot-provider.yaml)

| Key | Description |
|-----|-------------|
| `ipai_ask_ai_azure.base_url` | Azure OpenAI base URL |
| `ipai_ask_ai_azure.api_key` | Azure OpenAI API key (seeded from env) |
| `ipai_ask_ai_azure.model` | Model deployment name |
| `ipai_ask_ai_azure.api_mode` | API mode (responses or chat_completions) |

---

## 4. Environment Variables Required

### ipai_odoo_copilot (Odoo addon)

| Variable | Purpose | Required |
|----------|---------|----------|
| `AZURE_FOUNDRY_API_KEY` | Fallback API key auth (dev/local) | No (fallback) |
| `AZURE_CLIENT_ID` | EnvironmentCredential for DefaultAzureCredential | No (chain) |
| `AZURE_CLIENT_SECRET` | EnvironmentCredential for DefaultAzureCredential | No (chain) |
| `AZURE_TENANT_ID` | EnvironmentCredential for DefaultAzureCredential | No (chain) |
| `AZURE_SEARCH_API_KEY` | Azure AI Search client credential | Yes (for KB tools) |
| `IPAI_COPILOT_SERVICE_KEY` | Service-to-service auth for `/chat/service` | Yes (for widget) |
| `APPINSIGHTS_CONNECTION_STRING` | App Insights telemetry | No (graceful degrade) |

### ipai_enterprise_bridge (Foundry provider config)

| Variable | Purpose | Required |
|----------|---------|----------|
| `AZURE_AI_FOUNDRY_API_KEY` | API key auth mode | Conditional |
| `AZURE_AI_FOUNDRY_BEARER_TOKEN` | Bearer token fallback | Conditional |

### odoo-docs-kb (FastAPI service)

| Variable | Purpose | Required |
|----------|---------|----------|
| `AZURE_SEARCH_ENDPOINT` | AI Search endpoint URL | Yes |
| `AZURE_SEARCH_API_KEY` | AI Search credential | Yes |
| `AZURE_SEARCH_INDEX_NAME` | Index name (default: `odoo18-docs`) | No |
| `AZURE_OPENAI_ENDPOINT` | OpenAI endpoint for embeddings/chat | Yes |
| `AZURE_OPENAI_API_KEY` | OpenAI credential | Yes |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model (default: `text-embedding-ada-002`) | No |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Chat model (default: `gpt-4o`) | No |

---

## 5. Auth Modes

| Mode | Mechanism | Priority | Where Used |
|------|-----------|----------|------------|
| `api-key` | `AZURE_FOUNDRY_API_KEY` env var | 1 (fast path) | Dev/local |
| `default-credential` | `DefaultAzureCredential` chain | 2 | ACA runtime (managed identity, az login, env cred) |
| `none` | No credentials available | 3 (fail) | Reported as auth-unavailable |

**Token scope**: `https://cognitiveservices.azure.com/.default`

### Service endpoint auth

| Endpoint | Auth |
|----------|------|
| `/ipai/copilot/chat` | Odoo session (cookie-based) |
| `/ipai/copilot/chat/service` | `X-Copilot-Service-Key` header (HMAC compare) |

---

## 6. Agent API Mode

| Mode | Path | API Version | Status |
|------|------|-------------|--------|
| `agents` | `GET /agents?api-version=2025-03-01-preview` | `2025-03-01-preview` | Default (Foundry Responses API v2) |
| `assistants-compat` | `GET /openai/assistants?api-version=2025-03-01-preview` | `2025-03-01-preview` | Rollback switch |

Config key: `ipai_odoo_copilot.foundry_agent_api_mode`

---

## 7. Knowledge Base Indexes

| Index Name | Status | Source | Chunker | Embedding |
|------------|--------|--------|---------|-----------|
| `odoo18-docs` | Active (service exists, 7224 chunks) | `odoo/documentation` 19.0 branch (RST) | `packages/odoo-docs-kb/chunker.py` | text-embedding-ada-002 (1536d) |
| `azure-platform-docs` | Scaffold (source.yaml defined, no service) | Web crawl of learn.microsoft.com | `packages/odoo-docs-kb/md_chunker.py` | text-embedding-ada-002 (1536d) |
| `databricks-docs` | Scaffold (source.yaml defined, no service) | Web crawl of docs.databricks.com | `packages/odoo-docs-kb/md_chunker.py` | text-embedding-ada-002 (1536d) |

---

## 8. Tool Registry (11 tools, all read-only)

| Tool Name | Handler Method | Category |
|-----------|---------------|----------|
| `read_record` | `_execute_read_record` | ORM read |
| `search_records` | `_execute_search_records` | ORM search |
| `search_docs` | `_execute_search_docs` | Knowledge search (generic) |
| `get_report` | `_execute_get_report` | Report metadata |
| `read_finance_close` | `_execute_read_finance_close` | Domain-specific |
| `view_campaign_perf` | `_execute_view_campaign_perf` | Domain-specific |
| `view_dashboard` | `_execute_view_dashboard` | Domain-specific |
| `search_strategy_docs` | `_execute_search_strategy_docs` | Knowledge search (scoped) |
| `search_odoo_docs` | `_execute_search_odoo_docs` | KB: Odoo 18 docs (grounded RAG) |
| `search_azure_docs` | `_execute_search_azure_docs` | KB: Azure platform docs (grounded RAG) |
| `search_databricks_docs` | `_execute_search_databricks_docs` | KB: Databricks docs (grounded RAG) |

**Stage 2 planned (not implemented)**: `create_record`, `update_record`, `action_confirm`

### Blocked Models (security boundary)

`ir.config_parameter`, `ir.cron`, `ir.module.module`, `ir.rule`, `ir.model.access`, `res.users`, `base.module.upgrade`, `base.module.uninstall`, `ir.actions.server`, `ir.actions.act_window`

---

## 9. Cron Jobs

| Name | Model | Method | Interval | Active |
|------|-------|--------|----------|--------|
| IPAI Foundry: Nightly Healthcheck | `ipai.foundry.service` | `nightly_healthcheck()` | 1 day | Yes |

---

## 10. Odoo Models

| Model | Type | Table | Purpose |
|-------|------|-------|---------|
| `ipai.foundry.service` | `_auto = False` | No table | Service bridge for Foundry API calls |
| `ipai.copilot.audit` | Standard | `ipai_copilot_audit` | Audit log for interactions |
| `ipai.copilot.tool.executor` | `_auto = False` | No table | Tool dispatch and execution |
| `ipai.copilot.telemetry` | `_auto = False` | No table | App Insights telemetry sender |
| `discuss.channel` (inherit) | Inheritance | N/A | Message routing for Discuss bot |
| `res.config.settings` (inherit) | Transient | N/A | Settings UI |
| `ipai.foundry.provider.config` | Standard | `ipai_foundry_provider_config` | Provider config (enterprise_bridge) |

### Data Records

| XML ID | Model | Purpose |
|--------|-------|---------|
| `partner_copilot` | `res.partner` | Bot identity (copilot@insightpulseai.com) |
| `action_server_ensure_foundry_agent` | `ir.actions.server` | Server action to verify agent |
| `ir_cron_foundry_healthcheck` | `ir.cron` | Nightly health check |

---

## 11. Deployment Pipeline

**Workflow**: `.github/workflows/publish-agent-services.yml`

| Step | Action |
|------|--------|
| Trigger | Push to `main` touching `apps/odoo-docs-kb/**`, `packages/odoo-docs-kb/**`, `addons/ipai/ipai_odoo_copilot/**`, `addons/ipai/ipai_agent/**` |
| Auth | Azure OIDC (federated identity) |
| Registry | ACR (`$ACR_LOGIN_SERVER`, e.g. `cripaidev.azurecr.io`) |
| Build | `docker build -f apps/odoo-docs-kb/Dockerfile` |
| Deploy | `az containerapp update --name ipai-odoo-docs-kb --resource-group rg-ipai-dev` |
| Verify | `curl /health` after 30s wait |

---

## 12. Code Gaps Observed

1. **`chat_completion()` method**: Called in `copilot_bot.py` and `controllers/main.py` but not defined in `foundry_service.py`. This method is the actual Foundry call path -- currently missing from the codebase.
2. **`_build_context_envelope()` method**: Called in `controllers/main.py` but not defined in any model file. Required for building user context for tool execution.
3. **`ir.model.access.csv` is empty**: Only the header row exists. No ACL rules are defined for `ipai.copilot.audit`, `ipai.foundry.service`, `ipai.copilot.tool.executor`, or `ipai.copilot.telemetry`.
4. **`models/__init__.py` only imports 2 of 5 models**: `copilot_bot.py`, `copilot_audit.py`, `tool_executor.py`, and `telemetry.py` exist but are not imported in `models/__init__.py` (only `res_config_settings` and `foundry_service` are imported).
5. **`controllers/__init__.py` imports `main`** but the controller is not listed in `__manifest__.py` data files (controllers are auto-discovered, so this is fine, but `copilot_audit_views.xml` and `copilot_partner_data.xml` are loaded via manifest `data` -- only `copilot_partner_data.xml` is loaded; `copilot_audit_views.xml` is present but NOT in the manifest `data` list).

---

*Generated: 2026-03-15 from source code crawl. No live HTTP calls made.*
