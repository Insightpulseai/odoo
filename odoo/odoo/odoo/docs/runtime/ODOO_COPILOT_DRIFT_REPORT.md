# Odoo Copilot Drift Report

> Reconciliation of expected state (from docs, SSOT, memory) vs observed state (from code).
> Generated: 2026-03-15. No live HTTP calls made.

---

## Drift Matrix

| # | Area | Expected (docs/SSOT) | Observed (code) | Drift | Severity |
|---|------|---------------------|-----------------|-------|----------|
| 1 | **Auth mode** | Managed identity (docs say "zero-secret") | `DefaultAzureCredential` chain with 3-tier fallback: (1) env-var API key fast path, (2) DefaultAzureCredential, (3) none. API key env var `AZURE_FOUNDRY_API_KEY` is checked first. | Low — DefaultAzureCredential includes managed identity but the code also has a non-MI fast path. Docs oversimplify. | **Low** |
| 2 | **Agent API path** | Was `/openai/assistants` (memory file says "assistants"), now `/agents` | Code defaults to `/agents` with `assistants-compat` rollback via `foundry_agent_api_mode` config. Both paths use same API version `2025-03-01-preview`. | Aligned — the migration memory file correctly tracks this as partially done. | **Info** |
| 3 | **SDK usage** | Memory file says "should use `AIProjectClient`"; registry.yaml says "azure-ai-projects 2.x SDK" | `foundry_service.py` uses raw `urllib.request` for HTTP. Search tools use `azure.search.documents.SearchClient` (SDK). Auth uses `azure.identity.DefaultAzureCredential` (SDK). Agent resolution is raw HTTP. | **Active drift** — agent resolution is the last raw-HTTP holdout. Memory file correctly identifies this as the migration gate. | **Medium** |
| 4 | **KB indexes** | 3 defined in registry.yaml: `odoo19-docs` (active), `azure-platform-docs` (scaffold), `databricks-docs` (scaffold) | All 3 have tool handlers wired (`search_odoo_docs`, `search_azure_docs`, `search_databricks_docs`). But only `odoo19-docs` has a deployed service (`apps/odoo-docs-kb/`). The other 2 indexes have source contracts but no service, no deployed index, and no data. | Expected — registry correctly marks 2 as "scaffold". Tool handlers will fail gracefully (return error "Search client not available"). | **Low** |
| 5 | **Tool count** | Memory file says "8 original, now 11 with KB tools" | Code shows exactly 11 tools in `_TOOL_HANDLERS`. 8 original + 3 KB search tools added. | Aligned | **None** |
| 6 | **API version** | Memory file says "bumped from 2024-12-01-preview to 2025-03-01-preview" | Code: `_AGENTS_API_VERSION = "2025-03-01-preview"`. Enterprise bridge: `api_version` default = `"2025-03-01-preview"`. | Aligned | **None** |
| 7 | **Deployment target** | Infrastructure rules say Azure Container Apps. CLAUDE.md says ACA is canonical. | Pipeline deploys to ACA (`az containerapp update --name ipai-odoo-docs-kb --resource-group rg-ipai-dev`). No DO/Vercel deployment code. | Aligned | **None** |
| 8 | **`chat_completion` method** | Controller and copilot_bot.py call `service.chat_completion()` | Method does not exist in `foundry_service.py`. This is the core Foundry completion call path -- it is **missing from code**. | **Critical drift** — the Discuss bot and HTTP controller both call a method that doesn't exist. The module will raise `AttributeError` at runtime when a user sends a message. | **Critical** |
| 9 | **`_build_context_envelope` method** | Controller calls `service._build_context_envelope()` | Method does not exist in `foundry_service.py`. | **Critical drift** — controller will fail at runtime. | **Critical** |
| 10 | **Model registration** | 5 model files exist: `foundry_service.py`, `copilot_bot.py`, `copilot_audit.py`, `tool_executor.py`, `telemetry.py` | `models/__init__.py` only imports `res_config_settings` and `foundry_service`. The other 3 models (`copilot_bot`, `copilot_audit`, `tool_executor`, `telemetry`) are NOT imported -- they will not be registered in the Odoo ORM. | **High drift** — copilot_audit model won't exist, cron references to it will fail, tool executor is unreachable. | **High** |
| 11 | **ir.model.access.csv** | Should define ACL for all models (per Odoo 19 coding rules) | File contains only the header row. Zero ACL rules. `ipai.copilot.audit` has no read/write/create/unlink permissions for any group. | **High drift** — even admin users may not be able to access audit records depending on Odoo's default behavior for models without ACL. | **High** |
| 12 | **Manifest data files** | `copilot_audit_views.xml` and `copilot_partner_data.xml` exist in the module | `copilot_partner_data.xml` IS in manifest `data`. `copilot_audit_views.xml` is NOT in manifest `data` -- audit views will not be loaded. | **Medium drift** — audit log menu and views won't appear in the UI. | **Medium** |
| 13 | **External dependencies** | Manifest declares `azure-identity` and `azure-search-documents` | `copilot_bot.py` does not need external deps. `tool_executor.py` uses `azure-search-documents` (graceful). `foundry_service.py` uses `azure-identity` (graceful). `telemetry.py` uses only stdlib. Enterprise bridge's `foundry_provider_config.py` uses `requests` (not declared). | Low — graceful imports handle missing deps. `requests` in enterprise_bridge is an undeclared dependency. | **Low** |
| 14 | **Docs KB container app** | Pipeline targets `ipai-odoo-docs-kb` | `resources.yaml` (65 confirmed resources) does not list `ipai-odoo-docs-kb` as a container app. It may not exist yet in Azure. | **Medium drift** — pipeline will fail on first deploy if the container app hasn't been created. | **Medium** |
| 15 | **Foundry resource region** | `resources.yaml` says `data-intel-ph-resource` is in `eastus2` | Config parameter defaults API endpoint to `https://data-intel-ph-resource.services.ai.azure.com` (no region in URL -- Azure AI services URLs are region-independent). | Aligned — URL is correct form. | **None** |
| 16 | **Search service name** | `resources.yaml` says `srch-ipai-dev` (confirmed active) | Config parameter default: `srch-ipai-dev`. Code builds endpoint as `https://srch-ipai-dev.search.windows.net`. | Aligned | **None** |
| 17 | **Mail server** | CLAUDE.md (repo) says Mailgun; global rules say Zoho; global rules say Mailgun is deprecated | Copilot module has no mail dependency -- bot partner email `copilot@insightpulseai.com` is informational only. No drift in copilot. | **None** |
| 18 | **Hosting** | Global CLAUDE.md says DO; repo CLAUDE.md says Azure ACA. Infrastructure rules say ACA. | Code deploys to ACA. No DO references in copilot code. Global CLAUDE.md is stale (still mentions DO). | **Low** (global CLAUDE.md stale, not copilot-specific) |

---

## Severity Summary

| Severity | Count | Items |
|----------|-------|-------|
| **Critical** | 2 | #8 (chat_completion missing), #9 (_build_context_envelope missing) |
| **High** | 2 | #10 (model registration), #11 (empty ACL) |
| **Medium** | 3 | #3 (SDK migration), #12 (audit views not loaded), #14 (ACA not provisioned) |
| **Low** | 4 | #1 (auth docs oversimplify), #4 (scaffold KBs), #13 (undeclared dep), #18 (stale global docs) |
| **None/Info** | 7 | #2, #5, #6, #7, #15, #16, #17 |

---

## Recommended Fix Order

1. **#10 Model registration**: Add imports to `models/__init__.py` for `copilot_bot`, `copilot_audit`, `tool_executor`, `telemetry`.
2. **#8 + #9 Missing methods**: Implement `chat_completion()` and `_build_context_envelope()` in `foundry_service.py` or a new model file.
3. **#11 ACL**: Add ACL rows to `ir.model.access.csv` for all 4 models that create tables or are referenced by views/crons.
4. **#12 Manifest data**: Add `copilot_audit_views.xml` to `__manifest__.py` `data` list.
5. **#14 ACA provisioning**: Create `ipai-odoo-docs-kb` container app in `rg-ipai-dev` before running pipeline.
6. **#3 SDK migration**: Replace urllib agent resolution with `AIProjectClient` (tracked in memory file).

---

*Generated: 2026-03-15 from source code reconciliation.*
