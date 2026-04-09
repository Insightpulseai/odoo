# Placement Matrix — Odoo / Foundry / Compliance Engines / Azure

## Purpose

This artifact defines the recommended target-state placement for major business domains and platform capabilities across:

- **Odoo CE 18 + OCA**
- **Microsoft Foundry**
- **External compliance engines**
- **Azure infrastructure**

It is intended to prevent architecture drift, clarify ownership, and standardize when a bridge is required.

---

## Decision rules

### Put capability in Odoo when
- it is transactional system-of-record data
- it is a business workflow state or user-facing remediation step
- it is an ERP-native approval, exception, or domain action
- it should remain coupled to the accounting, inventory, sales, HR, or services workflow

### Put capability in Foundry when
- it is agent runtime or tool orchestration
- it needs evaluation, tracing, monitoring, or agent governance
- it is reasoning/explanation assistance rather than transactional truth
- it coordinates tools but should not become the ERP source of record

### Put capability in external compliance engines when
- it depends on maintained statutory content
- it requires certified/regulated filing or e-invoicing rails
- it requires country-specific tax determination content at scale
- it is better treated as licensed compliance content or network access rather than custom app logic

### Put capability in Azure infra when
- it is identity, network, storage, monitoring, secrets, policy, or runtime substrate
- it is a platform concern rather than a domain workflow concern
- it must support secure integration, observability, and production hardening

---

# 1. Domain-by-domain target matrix

| Domain | Recommended target | Primary owner | System of record | Integration mode | Approval model | Bridge required | Notes |
|---|---|---|---|---|---|---|---|
| Finance | CE + OCA + bridge | Odoo + external compliance engine | Odoo | API/event bridge for tax, filing, OCR, e-invoicing | Human approval for high-risk tax/compliance actions; low-risk validation may be automated | Yes | Odoo owns transactions, journals, approvals, remediation; external engines own statutory content/services |
| Sales | CE + OCA | Odoo | Odoo | Native Odoo/OCA first; optional API connectors for edge cases | Native ERP approvals | No by default | Bridge only for advanced pricing, marketplace, or tax-at-quote edge cases |
| Inventory | CE + OCA | Odoo | Odoo | Native Odoo/OCA first; external connectors only for carriers/3PL/devices | Native ERP approvals and warehouse controls | No by default | Keep stock, valuation, and warehouse workflow in Odoo |
| HR | CE + OCA + bridge | Odoo + external payroll/compliance service where needed | Odoo for HR records/workflow | API/event bridge for payroll-adjacent compliance, identity, time systems | Human approval for sensitive HR/compliance actions | Yes in many jurisdictions | Keep HR workflow in Odoo; bridge jurisdiction-heavy statutory logic |
| Marketing | CE + OCA | Odoo | Odoo | Native first; selective martech connectors | Native ERP/user-role approvals | No by default | Bridge only for ad platforms, consent/comms compliance, or analytics activation |
| Services | CE + OCA | Odoo | Odoo | Native first; optional external service connectors | Native ERP/service approvals | No by default | Projects, timesheets, helpdesk, field service stay in Odoo |
| Compliance | CE + OCA + bridge | Odoo + external compliance engine + policy/control-plane service | Split: Odoo for case/remediation state, external engine for statutory content/results | API/event bridge with policy-mediated execution | Advisory or execute-with-approval by default; no unrestricted autonomy | Yes | This is the clearest bridge lane |
| Copilot / Agents | CE + OCA + bridge | Foundry + Odoo | Odoo for business truth; Foundry for agent runtime state and evaluations | Tool-calling + event integration | Bounded agent scopes; approval required for material mutations | Yes | Foundry orchestrates; Odoo executes business actions |

---

## 2. Placement by capability

| Capability | Primary owner | System of record | Primary runtime/location | Integration mode | Approval model | Bridge required | Notes |
|---|---|---|---|---|---|---|---|
| Customer/vendor master data | Odoo | Odoo | Odoo | Native | Native ERP approval/admin controls | No | External systems may enrich but do not own |
| Product/service catalog | Odoo | Odoo | Odoo | Native | Native ERP controls | No | External tax classification may enrich |
| Orders, invoices, bills, refunds | Odoo | Odoo | Odoo | Native | Native ERP approvals | No | Core transactional truth stays in Odoo |
| Tax metadata validation | Odoo + policy service | Odoo for business record; policy service for validation state if separated | Odoo + control-plane service | Event/API | Execute-with-approval for high-risk overrides | Usually yes | Recommended as a thin bridge or tightly-coupled service |
| Tax determination | External compliance engine + Odoo | Odoo stores applied result on transaction | External engine + Odoo | API lookup / sync-back | Auto for low-risk; approval for overrides | Yes | Do not bury statutory logic in custom modules if licensed content is available |
| Exemption certificate validation | External compliance engine + Odoo | Odoo references state; external engine may hold certificate workflows | External engine + Odoo | API/event | Review required for exceptions | Yes | Odoo should surface status and remediation |
| E-invoicing / filing submission | External compliance engine or network adapter | Odoo stores submission/evidence references; external service owns transport/external acknowledgement | External service | API/event | Execute-with-approval by default | Yes | Certified rails belong outside core ERP |
| Filing calendar and readiness | Odoo + policy/control-plane service | Odoo or control-plane service | Odoo + control-plane | API/event | Human-reviewed for final submission readiness | Usually yes | Odoo should own operational task visibility |
| Evidence pack generation | Odoo + control-plane service | Evidence ledger / storage + Odoo references | Odoo + supporting service | Event-driven aggregation | Human review for material cases | Usually yes | Must aggregate ERP, policy, approval, and external result artifacts |
| Compliance case management | Odoo | Odoo | Odoo | Native + bridged enrichments | Approval and assignment rules in ERP | No for core case state | Avoid orphaned exceptions outside ERP |
| Agent runtime / tool orchestration | Foundry | Foundry for traces/evals; Odoo for business truth | Foundry | Tool calls / APIs / events | Bounded scopes; material actions gated | Yes | Foundry should not become transactional SoR |
| Agent traces / evaluations | Foundry | Foundry | Foundry | Native within agent platform | Review-gated for production policy changes | No for agent-plane internals | Keep evaluation and monitoring in Foundry |
| OCR / document intelligence | Azure service or specialized provider | Odoo stores accepted document/result references | Azure / external provider | API/event | Human review for low-confidence extraction | Yes | Odoo receives validated outputs and exceptions |
| Identity and access control | Azure infra + Odoo app RBAC | Split: Azure for platform identity, Odoo for app roles | Azure + Odoo | SSO / tokens / service identities | Least privilege / SoD enforced | No for baseline identity, yes for connector wiring | Keep enterprise identity out of custom business logic |
| Secrets, networking, observability | Azure infra | Azure | Azure | Native platform services | Platform-admin controlled | No | Infrastructure concern, not domain logic |
| Search / knowledge retrieval for agents | Azure/Foundry supporting services | Supporting platform store | Azure/Foundry | API/tool | Read-only by default | Usually yes | Separate knowledge retrieval from transactional mutation |
| Jurisdiction policy graph | Control-plane service | Control-plane service with references back to Odoo | Control-plane service | API/event | Policy-owner approval for rule changes | Yes | Do not distribute policy truth across random modules |

---

## 3. Bridge taxonomy

| Bridge type | When to use | Example concern | Anti-pattern to avoid |
|---|---|---|---|
| Thin data bridge | External service enriches Odoo record | Tax lookup, address normalization | Rebuilding external service logic inside Odoo |
| Workflow bridge | External decision or submission feeds ERP task state | E-invoicing acknowledgement, filing status | Leaving exception handling stranded outside ERP |
| Agent tool bridge | Foundry agent invokes bounded ERP or compliance actions | Case summarization, evidence assembly, validation checks | Letting the agent mutate business state without explicit policy/approval |
| Policy bridge | Control-plane evaluates rules and returns actionable results | Jurisdiction-specific validation, risk scoring | Hard-coding policies separately in Odoo, agent prompts, and external services |

---

## 4. Approval model reference

| Action class | Default approval model |
|---|---|
| Read-only analysis | Advisory only |
| Draft note, workpaper, explanation, evidence summary | Draft generation |
| Metadata correction recommendation | Draft generation or execute-with-approval |
| Low-risk validation pass/fail flag | Execute with post-review if policy-approved |
| Tax override | Execute with approval |
| Filing submission | Execute with approval |
| Registration/license action | Execute with approval |
| Legal/tax interpretation with material consequence | Human-required |

---

## 5. Non-negotiable architecture constraints

1. Odoo remains the primary business system of record.
2. Foundry remains the agent runtime and evaluation/governance plane, not the ERP database.
3. External compliance engines provide statutory content or certified execution surfaces where justified.
4. Azure infra provides secure substrate and platform controls, not business workflow ownership.
5. Exceptions and remediation must terminate back in Odoo-visible workflow state.
6. No bridge may become an opaque policy owner without versioned rule provenance and auditability.

---

## 6. Default build posture

### Build in Odoo/OCA first
Use for:
- transactional workflows
- user-facing ERP state
- approvals/remediation
- standard domain extensions

### Add a bridge second
Use for:
- compliance content
- agent orchestration
- OCR/document AI
- filing/e-invoicing rails
- jurisdiction policy services

### Avoid custom parity modules when
- OCA already covers the surface
- the gap is really external content/network/control-plane behavior
- the problem is policy orchestration, not ERP CRUD

---

## 7. Final target-state summary

- **Odoo** = transactional truth, workflow state, remediation, approvals
- **Foundry** = agent runtime, tracing, evaluation, tool orchestration
- **External compliance engines** = statutory content, filing rails, e-invoicing rails, certificate/compliance specializations
- **Azure infra** = identity, secrets, network, storage, search, telemetry, policy, secure runtime substrate
