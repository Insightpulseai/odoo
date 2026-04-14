# Desired End-State Matrix

## Status
Proposed

## Purpose
Define the desired end state for the current IPAI wave across:
- product/app surfaces
- four-plane architecture
- MCP/tooling surfaces
- systems of record
- runtime placement
- repo ownership boundaries

This matrix is the practical translation of the current doctrine:
- benchmark scope is limited to **D365 Finance**, **Finance agents**, and **D365 Project Operations**
- architecture is split into **Transaction / Data Intelligence / Agent / Delivery**
- **GitHub is engineering truth**
- **Azure DevOps is planning/governance-aware, not the only execution surface**
- **Odoo CE + OCA first, `ipai_*` last-resort thin adapter only**

---

## Scope guardrails

### In scope
- Finance parity
- Finance-agent parity
- Project Operations parity
- public web surfaces:
  - `insightpulseai.com`
  - `prismalab.insightpulseai.com`
  - `w9studio.net`
- shared assistant/admin/control surfaces
- Odoo-on-Azure transactional runtime
- Databricks/Fabric data intelligence
- Foundry/Pulser agent plane
- GitHub-first delivery with Azure-aware governance

### Out of scope for current wave
- Supply Chain Management
- manufacturing-heavy scenarios
- Commerce / POS / call-center expansion
- hard-core HR / payroll
- broad Partner Center API automation
- custom forks of major Microsoft/Azure/Odoo platform repos unless explicitly justified

---

## Canonical desired end state summary

| Domain | Desired end state |
|---|---|
| Transaction plane | Odoo CE + selected OCA + thin `ipai_*` adapters only |
| Data intelligence plane | Databricks + Fabric / Power BI semantic consumption |
| Agent plane | Foundry + Agent Framework + Pulser tools/policies |
| Delivery plane | GitHub-first SDLC, Azure-hosted runtime, Azure DevOps-aware planning/governance |
| Public sites | Three distinct web properties with shared MCP substrate |
| MCP strategy | Shared MCP layer, not one MCP per website |
| Repo strategy | Consume frameworks directly, clone samples as references, own only composition/adapters/SSOT/tests |
| Testing strategy | Odoo native tests + Playwright + Azure Test Plans + DevTools MCP for diagnostics |
| Tagging/naming | Policy-enforced Azure naming/tagging with per-plane resource-group separation |
| Current-wave benchmark | Finance + Finance agents + Project Operations only |

---

## A. App and surface matrix

| Surface | Type | Audience | Primary business role | Canonical system of record | Required planes | Required MCPs / integrations | Desired state |
|---|---|---|---|---|---|---|---|
| `insightpulseai.com` | public website | prospects, partners, buyers | main brand and product site | CMS + Odoo CRM | agent, transaction, delivery | content, CRM, scheduling, knowledge, email | live product/brand site with shared assistant and lead capture |
| `prismalab.insightpulseai.com` | public website | research clients, consulting leads | PRISMA/research services site | CMS + Odoo CRM/projects | agent, transaction, delivery | content, CRM, scheduling, knowledge, documents, email | live consulting site with intake + document-aware assistant |
| `w9studio.net` | public website | studio renters, production clients | booking / inquiry / package site | CMS + Odoo CRM/sales | agent, transaction, delivery | content, CRM, scheduling, documents, email, optional payments | live booking-oriented site with assistant and inquiry workflow |
| Pulser/Odoo ERP | internal transactional app | ops, finance, delivery, admin | CRM, quoting, invoicing, projects, execution | Odoo + PostgreSQL | transaction, delivery | Odoo/ERP, CRM, scheduling, email | canonical transactional operating system |
| Assistant admin / control console | internal app | operators, admins | manage prompts, tools, guardrails, sources, telemetry | Foundry + internal config store | agent, delivery | knowledge, documents, Odoo/ERP, email, diagnostics | authenticated control plane for assistants and MCP configuration |
| Analytics / reporting app | internal app | leadership, finance, operations | KPI, reporting, insights, profitability | Databricks/Fabric semantic layer | data intelligence, delivery | reporting datasets, Power BI/Fabric, optional Odoo sync | governed reporting surface for business and operational insight |
| Booking / scheduling app | shared capability or app | prospects, clients, ops | consultation / booking / availability | scheduling system + Odoo CRM | transaction, agent | scheduling, CRM, email | shared booking capability embedded across sites |
| Client/project portal (later) | external/internal app | customers, project teams | deliverables, project status, files, messages | Odoo + document store | transaction, agent | documents, Odoo/ERP, email | later-phase controlled customer collaboration surface |

---

## B. MCP and shared integration matrix

| MCP / integration surface | Purpose | Shared across sites? | System of record / backing service | Priority | Desired state |
|---|---|---:|---|---|---|
| Content MCP | site copy, FAQs, structured content grounding | Yes | CMS/content repository | P0 | one shared content MCP for all public surfaces |
| CRM MCP | lead intake, contact creation, pipeline routing | Yes | Odoo CRM | P0 | shared lead-routing and CRM orchestration layer |
| Scheduling MCP | booking, consultations, availability | Yes | calendar/scheduling service | P0 | one shared booking/scheduling surface |
| Odoo / ERP MCP | transactional access for sales, projects, finance | Yes | Odoo + PostgreSQL | P0 | one shared ERP MCP with strict governance |
| Knowledge MCP | retrieval over docs, packages, FAQs, policies | Yes | AI Search / knowledge store | P0 | shared knowledge substrate for all sites/agents |
| Documents MCP | proposals, templates, contracts, research files | Yes | document/file store | P1 | shared document-aware assistant surface |
| Email / communications MCP | acknowledgment, follow-up, reminders, collections | Yes | mail system | P1 | shared outbound/inbound communications layer |
| Analytics / BI MCP | traffic, funnel, assistant usage, conversion | Yes | Databricks/Fabric/analytics stack | P2 | optional later shared analytics tool surface |
| Payments MCP | checkout/deposits/payment-state awareness | Partly | payment platform | P2 | only if W9 / public commerce flows require it |

### Current-wave MCP target
- **Minimum viable:** 5 MCPs
- **Preferred production:** 7 MCPs
- **Upper bound before over-fragmenting:** 8–9 MCPs

---

## C. Four-plane architecture matrix

| Plane | Canonical responsibility | Primary runtime / substrate | Current-wave owned code | Do not put here |
|---|---|---|---|---|
| Transaction | CRM, sales, invoices, projects, finance execution | Odoo CE + OCA + PostgreSQL | thin `ipai_*` adapters, local overlays, config, tests | custom agent runtime, lakehouse logic, duplicated OCA parity |
| Data Intelligence | OLTP/OLAP separation, curated datasets, BI, analytics | Databricks + ADLS + Fabric / Power BI | data contracts, semantic ownership, export policies | transactional business logic, website CMS logic |
| Agent | orchestration, tools, grounding, evaluation, safety, assistant flows | Foundry + Agent Framework | Pulser tools, policies, prompts, guardrails, approval logic | direct business-domain forks inside Odoo core |
| Delivery | source control, CI/CD, release evidence, planning links, testing ops | GitHub-first + Azure-hosted infra + Azure DevOps-aware governance | workflow templates, release doctrine, test orchestration, docs | core ERP functionality, data-product business logic |

---

## D. Repo and ownership matrix

| Repo / surface class | Adoption mode | Own internally? | Target destination | Desired end state |
|---|---|---:|---|---|
| Odoo core (`odoo/odoo`) | upstream reference / clone-reference | No hard fork by default | canonical Odoo repo with upstream remote | track upstream, avoid divergence-heavy core fork |
| OCA selected repos/modules | selective clone/reference | Partly | `addons/oca/` | pull only justified repos/modules for current scope |
| Azure AVM / Bicep modules | consume-directly | No | `infra/azure/` composition only | own composition, not AVM itself |
| Microsoft agent/runtime frameworks | consume-directly | No | agent dependencies | use upstream packages directly |
| Azure/Microsoft samples/accelerators | clone-reference | No | `docs/architecture/reference-adaptations/` + experiments | harvest patterns, do not productize upstream repos |
| Playwright | consume-directly | No | `tests/playwright/` | canonical browser automation framework |
| Azure DevOps MCP / tooling | consume-directly | No | agent/editor config | use upstream connector/tools directly |
| IPAI infra composition | own-directly | Yes | `infra/azure/` or `platform/infra/` | environment composition, naming, tags, policy |
| IPAI Azure SSOT | own-directly | Yes | `ssot/azure/` | BOM, desired end state, naming, tags |
| IPAI Odoo thin adapters | own-directly | Yes | `addons/ipai/` and `addons/local/` | only thin adapters and overlays |
| IPAI Pulser tools/policies | own-directly | Yes | `agent-platform/` or `agents/` | agent logic, policy, approval, telemetry |
| IPAI tests/fixtures | own-directly | Yes | `tests/` | Odoo tests, Playwright suites, CI wrappers |
| IPAI delivery doctrine/templates | own-directly | Yes | `.github/`, `.azuredevops/`, `docs/delivery/` | GitHub-first / Azure-aware release model |

---

## E. Azure runtime desired end-state matrix

| Environment | Plane | Desired resource group pattern | Core resources | Desired state |
|---|---|---|---|---|
| shared | shared | `rg-ipai-shared-sea` | ACR and shared platform assets | one shared platform group |
| dev | transaction | `rg-ipai-dev-transaction-sea` | Container Apps env, Odoo app, init job, PostgreSQL, Service Bus, workload MI | normalized transactional dev runtime |
| dev | data | `rg-ipai-dev-data-sea` | Databricks, lake storage, access connector, VNet, NSG | governed dev data plane |
| dev | observability | `rg-ipai-dev-observability-sea` | App Insights, Log Analytics, action groups | per-plane monitoring and alerting |
| dev | security | `rg-ipai-dev-security-sea` | Key Vault, security identities as needed | isolated security plane |
| stg | transaction | `rg-ipai-stg-transaction-sea` | staging Odoo runtime | release-candidate environment |
| stg | data | `rg-ipai-stg-data-sea` | staging data plane as needed | optional until staging analytics is required |
| stg | observability | `rg-ipai-stg-observability-sea` | staging monitoring | isolated staging observability |
| stg | security | `rg-ipai-stg-security-sea` | staging/security assets as needed | isolated staging security |
| prod | transaction | `rg-ipai-prod-transaction-sea` | production Odoo runtime | production transactional plane |
| prod | data | `rg-ipai-prod-data-sea` | production data plane | governed analytics and reporting plane |
| prod | observability | `rg-ipai-prod-observability-sea` | production monitoring | production telemetry and alerting |
| prod | security | `rg-ipai-prod-security-sea` | production Key Vault / identities | production security isolation |

---

## F. Naming and tagging desired end state

### Resource naming grammar
```text
<type>-<org>-<env>-<workload>-<region>
```

Examples:

* `cae-ipai-dev-odoo-sea`
* `ca-ipai-prod-odoo-web-sea`
* `pgfs-ipai-stg-odoo-sea`
* `law-ipai-dev-odoo-sea`

### Required tags

```yaml
org: ipai
platform: pulser-odoo
env: dev|stg|prod|shared
plane: transaction|data|agent|delivery|observability|security|shared
workload: odoo|finance|finance-agents|project-ops|prismalab|monitoring|dbw
service: <resource purpose>
owner: jake
managed_by: bicep|azure-system|manual
criticality: low|medium|high|mission-critical
cost_center: ipai-platform
data_classification: public|internal|confidential|restricted
dr_tier: none|bronze|silver|gold
backup_policy: none|daily|pitr|custom
ops_state: active|pilot|deprecated|candidate-delete
billing_scope: core-platform|benchmark|experimentation|shared
```

### Tagging rules

* enforce tags with Azure Policy
* do not store secrets in tags
* do not assume RG tags inherit to resources automatically
* use `cm-resource-parent` when cost grouping by logical parent is needed

---

## G. Testing desired end state

| Layer              | Canonical tool      | Purpose                                           | Desired state                                   |
| ------------------ | ------------------- | ------------------------------------------------- | ----------------------------------------------- |
| backend logic      | Odoo native testing | model/business/security/integration logic         | default validation for server-side behavior     |
| browser automation | Playwright          | UI smoke, regression, agent browser flows         | canonical browser automation stack              |
| manual / UAT       | Azure Test Plans    | structured UAT, exploratory testing, traceability | used for manual validation and business signoff |
| diagnostics        | Chrome DevTools MCP | network/performance/console/resource debugging    | debugging aid only, not main regression runner  |

---

## H. Boards desired end state

### Current-wave benchmark epics only

Use exactly these benchmark-facing top-level epics for the current wave:

1. `D365 Finance Parity`
2. `Finance Agents Parity`
3. `D365 Project Operations Parity`

Under those:

* use **Issues** as feature buckets
* use **Tasks** as execution work

Keep platform and governance epics separate:

* Odoo on Azure Operating Model
* AI Platform Operating Model
* AI-Led Engineering Model
* Data Intelligence Operating Model
* Governance / hardening / security epics

Do not create top-level benchmark epics yet for:

* Supply Chain
* Commerce
* hard-core HR
* manufacturing

---

## I. Current-wave repo adoption target

### Consume directly

* AVM / Bicep modules
* Agent Framework
* Azure DevOps MCP
* Playwright

### Clone as reference

* Azure PostgreSQL / ACA / RAG / Foundry starter samples
* Foundry templates / Release Manager Assistant patterns
* selected OCA repos/modules only
* Odoo core as upstream reference, not a divergence-heavy product fork

### Own directly

* infra composition
* SSOT
* Pulser tools/policies
* Odoo thin adapters
* tests and delivery doctrine

---

## J. Desired end-state checklist

| Area              | Desired outcome                                               | State target |
| ----------------- | ------------------------------------------------------------- | ------------ |
| Public web        | 3 distinct public sites sharing common MCP substrate          | target       |
| Transaction plane | Odoo CE + selected OCA + thin adapters only                   | target       |
| Data plane        | Databricks/Fabric governed analytics                          | target       |
| Agent plane       | Foundry/Pulser with explicit grounding, safety, and telemetry | target       |
| Delivery plane    | GitHub-first SDLC with Azure-aware governance                 | target       |
| Testing           | Odoo + Playwright + Test Plans + diagnostics                  | target       |
| Azure estate      | per-plane RG normalization across dev/stg/prod                | target       |
| Tags/naming       | policy-enforced and consistent                                | target       |
| Boards            | only 3 benchmark epics for current-wave product scope         | target       |
| Repo strategy     | no unnecessary forks of platform repos                        | target       |

---

## Final desired-state statement

The desired end state is a four-plane, GitHub-first, Azure-hosted operating model in which Odoo CE + selected OCA modules provide the transactional core for Finance and Project Operations parity, Pulser/Foundry provides the assistive agent layer for Finance agents parity, Databricks/Fabric provides governed data intelligence, and the three public web properties share a common MCP substrate for content, CRM, scheduling, knowledge, documents, and communications.
