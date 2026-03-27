# InsightPulseAI Odoo on Azure — Canonical Target State

## Canonical one-sentence target

> InsightPulseAI Odoo on Azure is a Joule-benchmarked, Odoo-native enterprise copilot platform where Odoo is the system of record, Foundry Agent Applications are the governed AI runtime, Document Intelligence is the OCR layer, and Azure landing zones plus Entra plus Azure DevOps/GitHub provide the operational backbone.

## Benchmark model (SAP Joule-adapted)

| Capability | What it means |
| --- | --- |
| **Informational** | Summarize records, answer grounded questions, explain OCR output and recommendations |
| **Navigational** | Route users to the correct record, queue, action, or menu; reduce context switching |
| **Transactional** | Create drafts, proposals, activities, and reviews; require approval for high-risk actions |

## System roles

| System | Role | Owns | Must NOT own |
| --- | --- | --- | --- |
| **Odoo 19** | Transactional SoR and workflow engine | Business records, approvals, posted state, trigger surface | LLM orchestration, knowledge retrieval |
| **Odoo Copilot** | User-facing ERP copilot | Contextual prompts, action launch, document review entry | Agent reasoning, tool execution |
| **Foundry Agent Applications** | Governed AI runtime | Agent reasoning, tool orchestration, stable endpoints, identity/RBAC | Unrestricted DB writes, canonical business state |
| **Document Intelligence** | OCR and structured extraction | OCR, layout, tables, fields, custom extraction | Business interpretation, approval decisions |

## Processing model

### Document flow

1. Odoo receives document/attachment
2. Odoo creates OCR/extraction job
3. Document Intelligence extracts structure and content
4. Output normalized into stable internal schema
5. Foundry interprets normalized payload
6. Odoo stores proposal, routes review, records approval
7. Approved outcomes committed into business workflows

### Interactive copilot flow

1. User invokes Copilot from Odoo
2. Odoo packages bounded record context
3. Foundry agent receives request through stable application endpoint
4. Agent uses approved tools only
5. Response returns as guidance, navigation, or bounded proposal
6. Odoo records interaction and audit metadata

## Governance model

### Authority

- **Azure** = cloud/runtime/control access
- **Azure DevOps** = planning/governance spine
- **GitHub** = current engineering truth until Azure Repos cutover
- **Repo SSOT** = intended-state truth
- **IaC / migrations / pipelines / tests** = executable truth

### Identity

- Microsoft Entra = canonical identity plane
- Human admins use named identities
- Automation uses workload identities
- Published agents use governed identity with explicit RBAC

### Landing zones

- Platform landing zone for shared identity, connectivity, management
- Application landing zones per workload (odoo, agent-platform, data-intelligence)
- No separate AI landing zone

## Resource group target (16-RG model)

### Shared

| RG | Contents |
| --- | --- |
| `rg-ipai-shared-observability` | Log Analytics, App Insights, Monitor action groups, alert rules, dashboards |

### Per environment (dev / staging / prod)

| RG pattern | Contents |
| --- | --- |
| `rg-ipai-<env>-edge` | Front Door, WAF policy, AFD security policies, custom domains |
| `rg-ipai-<env>-odoo-runtime` | ACA environment, web/worker/cron apps, runtime identities, ACA secrets |
| `rg-ipai-<env>-odoo-data` | PostgreSQL Flexible Server, storage account (filestore), Azure Files, private endpoints |
| `rg-ipai-<env>-platform` | Control-plane APIs, Key Vault, admin services, queues/event handlers |
| `rg-ipai-<env>-ai` | Foundry project/agents, AI Search, Document Intelligence, AI Vision |

### Total: 1 shared + (5 x 3 environments) = 16

### Current state mapping

| Current RG | Target |
| --- | --- |
| `rg-ipai-dev` | Split → `rg-ipai-dev-odoo-runtime` + `rg-ipai-dev-odoo-data` + `rg-ipai-dev-platform` |
| `rg-ipai-ai-dev` | Normalize → `rg-ipai-dev-ai` |
| `rg-ipai-shared-dev` | Normalize → `rg-ipai-shared-observability` |
| `rg-ipai-data-dev` | Fold into `rg-ipai-dev-odoo-data` or retire duplicates |
| `rg-data-intel-ph` | Part of `rg-ipai-dev-ai` |

## Repo ownership

| Repo | Responsibility |
| --- | --- |
| `odoo` | Runtime, addons, UI widget, actions, audit/job models |
| `infra` | Landing-zone implementation, network, edge, runtime infra |
| `platform` | Normalized contracts, control-plane, admin services |
| `agent-platform` | Foundry agents, tool contracts, published runtimes, evals |
| `data-intelligence` | Lakehouse, BI, semantic outputs |
| `agents` | Shared skills, prompts, registries |
| `automations` | Schedulers, runbooks |
| `docs` | Cross-platform architecture, governance |

## Canonical module set

- `ipai_odoo_copilot` — UI, user interaction, record-context packaging
- `ipai_document_intelligence` — OCR bridge, normalization, attachment handling
- `ipai_copilot_actions` — server actions, automation hooks, audit, bounded writeback

## Safety model

- Proposal-first for risky transactional actions
- Approval gates for financial/compliance outcomes
- Bounded tool contracts (no unrestricted ORM mutation)
- Full auditability: agent inputs, outputs, approvals, correlation IDs
- No silent business-state mutation by agents

## Operational readiness criteria

The target state is achieved when:

- [ ] Odoo Copilot supports informational, navigational, and transactional benchmark scenarios
- [ ] Foundry agents are published with stable application endpoints and distinct identity
- [ ] Document Intelligence is wired into production document flows
- [ ] Odoo remains the authoritative business system of record
- [ ] Landing-zone, identity, and runtime boundaries are enforced
- [ ] End-to-end observability, evidence capture, and rollback paths exist
- [ ] Platform is privately deployable to Microsoft 365/Teams
- [ ] Marketplace readiness path is documented
