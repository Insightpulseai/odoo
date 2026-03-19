# Foundation Blockers and Mocks

> Version: 0.1.0
> Date: 2026-03-19
> Status: **Implemented and locally verified, not yet cloud-integrated or production-ready**

## Current State

The precursor runtime is implemented and verified locally against mock/cloud-blocked adapters.

### Completed

- Runtime contracts (request/response/context/tool/audit/eval/specialist)
- Orchestrator with asset loading from `agents/`
- Runner CLI (chat/health/eval/status)
- Mock Foundry client (deterministic responses)
- Advisory-mode policy enforcement
- Audit event emission (structured JSON, correlation IDs)
- Fail-closed tax specialist blocking (ATC divergence)
- Smoke tests: **6/6 pass**
- TypeScript compilation: **pass**

### Still blocked for production

- Real Foundry endpoint/project integration
- AI Search grounding/indexing
- App Insights tracing
- Odoo Discuss/systray integration (`ipai_odoo_copilot` module not built)
- Azure DevOps release gating
- Managed identity auth
- Entra RBAC enforcement

## Blockers

### B-1: Azure AI Foundry Endpoint (Blocking for Cloud)

**Required**: `AZURE_AI_FOUNDRY_ENDPOINT` and `AZURE_AI_FOUNDRY_PROJECT` environment variables.

**Current state**: AzureFoundryClient stub exists but throws "not configured" when env vars are missing.

**Mock**: MockFoundryClient provides deterministic responses matching the system prompt behavior patterns. Supports tool call simulation.

**Resolution**: Set env vars pointing to the `data-intel-ph` project at `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph`.

### B-2: Managed Identity (Blocking for Production)

**Required**: Azure Container App with managed identity bound to AI Foundry project.

**Current state**: Auth falls back to API key when managed identity is unavailable.

**Mock**: MockFoundryClient bypasses all auth.

**Resolution**: Configure identity per `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` auth chain.

### B-3: Azure AI Search Index (Blocking for Grounded Advisory)

**Required**: `srch-ipai-dev` search service with populated `ipai-knowledge-index`.

**Current state**: Knowledge base assets exist in `agents/knowledge-base/` but are not indexed.

**Mock**: MockFoundryClient returns synthetic knowledge results for `search_docs` tool.

**Resolution**: Index `agents/knowledge-base/` content using the schema at `agents/knowledge-base/index-schema.json`.

### B-4: App Insights / OpenTelemetry (Blocking for Observability)

**Required**: `APPINSIGHTS_CONNECTION_STRING` environment variable.

**Current state**: ConsoleAuditEmitter logs structured JSON to stdout. All audit event types implemented.

**Mock**: Console logging provides local observability. Audit events buffered in memory for test assertions.

**Resolution**: Replace ConsoleAuditEmitter with an OpenTelemetry-compatible emitter targeting App Insights.

### B-5: ATC Namespace Divergence (Blocking for Tax Specialist)

**Required**: Resolved ATC (Alphanumeric Tax Code) namespace mapping for Philippine withholding tax.

**Current state**: TaxPulse specialist registered with `production_ready: false`. SpecialistRouter fail-closed: all tax computation routing blocked.

**Mock**: Tax-related prompts handled by general advisory (copilot provides guidance with advisory disclaimer, no autonomous computation).

**Resolution**: Resolve ATC divergence between BIR published codes and Odoo tax configuration. This is a domain problem, not a platform problem.

### B-6: Entra App Roles (Blocking for RBAC)

**Required**: App roles registered in Entra tenant `ceoinsightpulseai.onmicrosoft.com`.

**Current state**: Context envelope defaults to empty `app_roles` and `groups`. All requests get most-restrictive permissions.

**Mock**: Tests use `defaultContextEnvelope()` with manually specified `permitted_tools`.

**Resolution**: Register app roles per `agents/foundry/ipai-odoo-copilot-azure/context-envelope-contract.md`.

### B-7: Real Odoo Tool Execution (Blocking for Assisted Actions)

**Required**: Odoo JSON-RPC adapter for `read_record`, `search_records`, etc.

**Current state**: Orchestrator has `mockToolExecution()` returning synthetic data.

**Mock**: Mock returns plausible record shapes for all tool types.

**Resolution**: Implement real tool executor using Odoo XML-RPC/JSON-RPC via `ipai_*` adapter modules. Credentials from Azure Key Vault.

## Mocks Summary

| Component | Mock | Production Target |
|-----------|------|-------------------|
| Model backend | MockFoundryClient | AzureFoundryClient → Azure AI Foundry |
| Tool execution | mockToolExecution() | Odoo JSON-RPC via ipai_* adapters |
| Knowledge retrieval | Synthetic results | Azure AI Search (ipai-knowledge-index) |
| Audit/telemetry | ConsoleAuditEmitter | OpenTelemetry → App Insights |
| Authentication | No auth | Managed identity → Entra |
| RBAC | Default restrictive | Entra app roles → context envelope |
| Tax specialist | Fail-closed blocked | TaxPulse agent (post-ATC resolution) |
