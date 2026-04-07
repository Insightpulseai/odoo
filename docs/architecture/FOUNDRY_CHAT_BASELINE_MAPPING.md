# Foundry Chat Baseline → IPAI Odoo Copilot Mapping

> Source: [Baseline Microsoft Foundry chat reference architecture](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat)

---

## Architecture Mapping

| Baseline Component | IPAI Implementation | Status |
|--------------------|---------------------|--------|
| **Chat UI (App Service)** | Odoo systray widget + `/api/pulser/chat` controller | Deployed |
| **Foundry Agent Service** | `ipai.foundry.service` → Foundry C# SDK via HTTP | Deployed |
| **Prompt-based agent** | `ipai-odoo-copilot-azure` agent in Foundry | Deployed |
| **Skill router** | `ipai.copilot.skill.router` (deterministic, no ML) | Deployed |
| **Knowledge store (AI Search)** | Azure AI Search (Odoo docs index, 7224 chunks) | Deployed |
| **Memory database (Cosmos DB)** | Foundry-managed `enterprise_memory` | Not yet (Foundry manages) |
| **File storage (Blob)** | `ir.attachment` (Odoo) + `copilot.attachment.ref` | Deployed |
| **Document extraction** | `ipai.doc.intelligence.service` → Document Intelligence v4.0 | Deployed |
| **Attachment pipeline** | Upload → extract → ground → LLM answer | Deployed, E2E tested |
| **Application Gateway + WAF** | Azure Front Door (planned) | Not yet |
| **Virtual Network + Private Endpoints** | Not yet (dev uses public endpoints) | Not yet |
| **Azure Firewall (egress)** | Not yet | Not yet |
| **Azure DNS (private zones)** | Azure DNS (public, delegated from Squarespace) | Partial |
| **Managed Identity** | Planned (currently API key auth) | Not yet |
| **Content Safety** | Foundry built-in | Active |
| **Audit trail** | `ipai.copilot.audit` model (full telemetry) | Deployed |
| **Conversation state** | `ipai.copilot.conversation` + `ipai.copilot.message` | Deployed |

---

## Workflow Alignment

### Baseline Workflow (Microsoft)

1. User → Application Gateway → App Service (chat UI)
2. App Service → Foundry Agent Service (via SDK, private endpoint, managed identity)
3. Agent → knowledge store (AI Search, private endpoint)
4. Agent → external tools (via Azure Firewall egress)
5. Agent → language model (Azure OpenAI)
6. Agent → memory database (Cosmos DB, conversation persistence)
7. Response → chat UI

### IPAI Workflow (Current)

1. User → Odoo systray → `/api/pulser/chat` controller
2. Controller → skill router → `ipai.foundry.service.chat_completion()`
3. Foundry service → Foundry endpoint (HTTPS, API key)
4. Agent → Azure AI Search (Odoo docs knowledge base)
5. Agent → Azure OpenAI model
6. Response → controller → audit → systray UI

### Gap: What We Don't Have Yet

| Baseline Requirement | Gap | Priority |
|---------------------|-----|----------|
| Private endpoints for all PaaS | Public endpoints in dev | P1 for prod |
| Managed identity auth | API key auth | P1 for prod |
| Application Gateway + WAF | No ingress gateway | P1 for prod |
| Azure Firewall egress control | No egress filtering | P2 |
| Zone redundancy (3 zones) | Single instance | P2 for prod |
| Cosmos DB for conversation memory | Odoo PostgreSQL | P3 (Odoo-native is fine) |
| Multiregion DR | Single region | P3 |

---

## Key Decisions Aligned with Baseline

### 1. Agent Service as Runtime (not self-hosted)
The baseline uses Foundry Agent Service as managed runtime. We do the same — `ipai-odoo-copilot-azure` is a Foundry-hosted agent.

### 2. Single Agent (not multi-agent)
The baseline recommends starting with a single agent. We use a single agent with skill-based routing to scope tools per intent — functionally equivalent without multi-agent overhead.

### 3. Dedicated Dependencies
The baseline mandates isolating Foundry Agent Service dependencies (Cosmos DB, Storage, AI Search) from workload components. We partially comply — Odoo has its own PostgreSQL, attachment storage is Odoo-native, but the AI Search index is shared.

### 4. Agents Defined as Code
The baseline requires agent definitions in source control. Our agent config lives in `ssot/agent/` YAML files and Odoo `ir.config_parameter` — should be migrated to IaC.

### 5. Thin Bridge Pattern
The baseline says "App Service communicates with agent endpoints." Our Odoo copilot follows the same pattern — Odoo is the thin bridge, all AI logic lives in Foundry.

---

## Production Hardening Roadmap (from Baseline)

| Phase | Action | Baseline Section |
|-------|--------|------------------|
| **P0** | Move to managed identity auth (eliminate API keys) | Security > Identity |
| **P0** | Deploy private endpoints for Foundry, AI Search, Storage | Security > Network |
| **P1** | Add Application Gateway + WAF in front of Odoo | Reliability + Security |
| **P1** | Configure Azure Firewall for egress control | Security > Network |
| **P1** | Enable zone redundancy (3 replicas AI Search, ZRS storage) | Reliability |
| **P2** | Add Cosmos DB continuous backup for Foundry memory | Reliability > DR |
| **P2** | Define DR runbook for agent state recovery | Reliability > DR |
| **P3** | Evaluate multiregion for business continuity | Reliability > Multiregion |

---

*Source: Microsoft Learn, fetched 2026-04-07*
