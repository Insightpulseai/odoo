# Infrastructure Audit Dashboard

> **Date**: 2026-03-30
> **Scope**: Azure Subscription 1 (`536d8cf6-89e1-4815-aef3-d5f2c5f4d070`)
> **Total Resources**: 69 (across 14 resource groups)

---

## Critical Findings

### FINDING-1: Duplicate Private DNS Zone — FALSE ALARM

**Severity**: Cleared
**Observed**: User reported duplicate `privatelink.postgres.database.azure.com` in both `rg-ipai-ai-dev` and `rg-ipai-dev-odoo-runtime`.
**Verified**: Only ONE zone exists (`rg-ipai-dev-odoo-runtime`, 2 record sets, 1 VNet link). The zone in `rg-ipai-ai-dev` is a different Private DNS zone (not the PG one).
**Action**: None needed.

### FINDING-2: PG Flex Name — CORRECT

**Severity**: Cleared
**Observed**: Docs reference both `ipai-odoo-dev-pg` (old) and `pg-ipai-odoo` (new).
**Verified**: `HOST` env var on `ipai-odoo-dev-web` → `pg-ipai-odoo.postgres.database.azure.com` (**correct**)
**Action**: Old name `ipai-odoo-dev-pg` was deprecated 2026-03-21 per memory. No runtime mismatch.

---

## Architectural Decisions Required

### DECISION-1: Two Foundry Patterns — Consolidate

| Resource | Kind | RG | Location | SKU |
|----------|------|-----|----------|-----|
| `aifoundry-ipai-dev` | Hub | `rg-ipai-ai-dev` | eastus2 | Basic |
| `proj-ipai-claude` | Project | `rg-ipai-ai-dev` | eastus2 | Basic |
| `data-intel-ph-resource` | AIServices | `rg-data-intel-ph` | eastus2 | S0 |
| `data-intel-ph-resource/data-intel-ph` | Project | `rg-data-intel-ph` | eastus2 | — |

**Analysis**:
- `aifoundry-ipai-dev` + `proj-ipai-claude` = canonical platform hub (existing, used for agent eval)
- `data-intel-ph` = newer Cognitive Services AIServices account with attached project (appears to be a data-intelligence-specific workspace)

**Recommendation**: Keep `aifoundry-ipai-dev` as canonical Hub. Evaluate whether `data-intel-ph` serves a distinct purpose (data intelligence grounding?) or is redundant. If redundant, decommission `rg-data-intel-ph` entirely.

**Status**: Decision pending.

### DECISION-2: Fabric Capacity Billing

| Resource | SKU | Location | RG | State |
|----------|-----|----------|-----|-------|
| `fcipaidev` | F2 | southeastasia | `rg-ipai-ai-dev` | Active |

**Cost**: F2 = ~$262/month (pay-as-you-go).

**Analysis**: Fabric capacity is needed for the mirroring rehearsal (pre-flight GO confirmed). The `odoo_staging` mirroring is the immediate use case. If the rehearsal is not starting within 7 days, pause the capacity to stop billing.

**Recommendation**: Proceed with rehearsal immediately. Pause capacity after 48h soak if no follow-up production mirroring is planned.

**Status**: Rehearsal GO — capacity confirmed active.

### DECISION-3: OpenAI Region Exception

| Resource | Kind | Location | RG |
|----------|------|----------|-----|
| `oai-ipai-dev` | OpenAI | **eastus** | `rg-ipai-ai-dev` |
| `docai-ipai-dev` | FormRecognizer | southeastasia | `rg-ipai-ai-dev` |
| `lang-ipai-dev` | TextAnalytics | southeastasia | `rg-ipai-ai-dev` |
| `vision-ipai-dev` | ComputerVision | southeastasia | `rg-ipai-ai-dev` |
| `data-intel-ph-resource` | AIServices | eastus2 | `rg-data-intel-ph` |
| `aifoundry-ipai-dev` | Hub | eastus2 | `rg-ipai-ai-dev` |

**Analysis**: OpenAI in `eastus` is a model-availability exception — GPT-4o, o-series, and embedding models are not available in `southeastasia`. Foundry hub in `eastus2` follows the same pattern. All other compute is in `southeastasia`.

**Recommendation**: Document as explicit model-availability exception. No migration needed — cross-region latency for AI inference calls is acceptable (agent calls, not real-time UI).

**Status**: Document and close.

---

## Phase 1 Blockers (Not Yet Provisioned)

| Resource | Type | Purpose | Blocking |
|----------|------|---------|----------|
| Azure Front Door | CDN/WAF | TLS termination, WAF, global routing | Public ingress for all ACA apps |
| Event Hubs namespace | Streaming | Debezium CDC pipeline ingestion | Databricks medallion pipeline Bronze layer |
| Azure Service Bus | Messaging | Async command/event bus | Agent platform orchestration |

**Impact**: Without Front Door, all ACA apps are exposed via raw `*.azurecontainerapps.io` FQDNs with no WAF. Without Event Hubs, the Databricks CDC pipeline cannot receive change events. Without Service Bus, agent orchestration has no durable message bus.

**Note**: Fabric Mirroring (now GO) partially mitigates the Event Hubs blocker for Odoo data — mirroring provides near-real-time CDC to OneLake without Event Hubs. Event Hubs is still needed for non-PG sources.

---

## Resource Inventory by Resource Group

| Resource Group | Resources | Purpose |
|----------------|-----------|---------|
| `rg-ipai-dev-odoo-runtime` | 22 | ACA environment, 12 container apps, ACR, VNet, DNS, certs, App Insights |
| `rg-ipai-ai-dev` | 24 | Databricks, Foundry, OpenAI, Cognitive Services, Fabric, Search, Storage, VNet |
| `rg-ipai-dev-odoo-data` | 2 | PG Flex Server (`pg-ipai-odoo`), Storage |
| `rg-ipai-dev-platform` | 1 | Key Vault (`kv-ipai-dev`) |
| `rg-ipai-shared-dev` | 5 | Managed identities (4), action group |
| `rg-ipai-shared-staging` | 4 | Managed identities (3), Key Vault |
| `rg-ipai-shared-prod` | 4 | Managed identities (3), Key Vault |
| `rg-ipai-shared-observability` | 2 | Log Analytics workspace, App Insights |
| `rg-ipai-devops` | 1 | Managed DevOps Pool |
| `rg-ipai-agents-dev` | 1 | Managed identity (Supabase VM deleted) |
| `rg-data-intel-ph` | 2 | AIServices account + project (decision pending) |
| `rg-dbw-managed-ipai-dev` | 3 | Databricks-managed (storage, access connector, identity) |
| `ai_*_managed*` (2 RGs) | 2 | Auto-managed Log Analytics workspaces |
| `networkwatcherrg` | 1 | Network Watcher (auto-created) |
| `visualstudioonline-*` | 1 | Azure DevOps (auto-created) |

**Total**: 69 resources across 14 resource groups (+ 2 auto-managed RGs).

---

## Container Apps Inventory (12 apps)

All in `rg-ipai-dev-odoo-runtime`, environment `ipai-odoo-dev-env`.

| App | Purpose | Public | Status |
|-----|---------|--------|--------|
| `ipai-odoo-dev-web` | Odoo ERP (HOST=`pg-ipai-odoo`) | Yes | Active |
| `ipai-odoo-dev-worker` | Odoo background worker | No | Active |
| `ipai-odoo-dev-cron` | Odoo scheduled jobs | No | Active |
| `ipai-auth-dev` | Keycloak SSO | Yes | Decommission candidate |
| `ipai-mcp-dev` | MCP coordination | Yes | Active |
| `ipai-ocr-dev` | Document OCR | Yes | Active |
| `ipai-superset-dev` | Apache Superset BI | Yes | Active |
| `ipai-plane-dev` | Plane project mgmt | Yes | Active |
| `ipai-crm-dev` | CRM service | Yes | Active |
| `ipai-shelf-dev` | Shelf service | Yes | Active |
| `ipai-website-dev` | Website / landing | Yes | Active |
| `ipai-copilot-gateway` | Copilot gateway | No | Active |

---

## Cognitive Services Map

| Resource | Kind | Location | SKU | Purpose |
|----------|------|----------|-----|---------|
| `oai-ipai-dev` | OpenAI | eastus | S0 | GPT-4o, embeddings (model availability) |
| `docai-ipai-dev` | FormRecognizer | southeastasia | S0 | Document Intelligence / OCR |
| `lang-ipai-dev` | TextAnalytics | southeastasia | F0 | Language services |
| `vision-ipai-dev` | ComputerVision | southeastasia | F0 | Image analysis |
| `data-intel-ph-resource` | AIServices | eastus2 | S0 | Unified AI endpoint (decision pending) |

---

## Key Vault Inventory

| Vault | RG | Purpose |
|-------|----|---------|
| `kv-ipai-dev` | `rg-ipai-dev-platform` | Dev secrets (Odoo, SMTP, API keys) |
| `kv-ipai-staging` | `rg-ipai-shared-staging` | Staging secrets |
| `kv-ipai-prod` | `rg-ipai-shared-prod` | Production secrets |
| (AI vault) | `rg-ipai-ai-dev` | Foundry/Databricks secrets |

---

## Managed Identities (10 total)

| RG | Count | Purpose |
|----|-------|---------|
| `rg-ipai-shared-dev` | 4 | Dev workload identities |
| `rg-ipai-shared-staging` | 3 | Staging workload identities |
| `rg-ipai-shared-prod` | 3 | Prod workload identities |
| `rg-ipai-ai-dev` | 1 | Foundry managed identity |
| `rg-ipai-agents-dev` | 1 | Legacy (Supabase VM deleted) |
| `rg-dbw-managed-ipai-dev` | 1 | Databricks managed identity |

---

## Action Items

| Priority | Item | Owner | Status |
|----------|------|-------|--------|
| P0 | Provision Azure Front Door | Infra | **Not provisioned** |
| P1 | Execute Fabric mirroring rehearsal | Data | **GO** (capacity active) |
| P1 | Inject Entra credentials for SSO | Identity | Runbook ready |
| P2 | Decide Foundry hub consolidation | Architecture | Decision pending |
| P2 | Document OpenAI region exception | Docs | Close with note |
| P2 | Provision Event Hubs (if non-PG CDC needed) | Infra | Deferred (Fabric covers Odoo) |
| P3 | Provision Service Bus (agent orchestration) | Infra | Deferred |
| P3 | Decommission `ipai-auth-dev` (Keycloak) | Runtime | After Entra SSO live |
| P3 | Clean up `rg-ipai-agents-dev` (1 orphan identity) | Infra | Low priority |
| P3 | Evaluate `rg-data-intel-ph` necessity | Architecture | Decision pending |
