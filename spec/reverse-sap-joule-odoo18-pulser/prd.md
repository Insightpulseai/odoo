# PRD — Reverse SAP Joule for Odoo 18 Pulser

## Problem

ERP copilots often become navigation or summarization overlays that are
weakly grounded in operational workflow state. SAP Joule provides
conversational access to SAP data and actions, but is SAP-native and
tightly coupled to the SAP ecosystem. Odoo users need an equivalent
AI assistant that is grounded in Odoo's operational truth.

## Users

- Odoo end users (employees, managers)
- Approvers (expense, purchase, leave)
- Finance operators (accountants, controllers)
- Admins (system configuration, user management)
- Auditors (compliance review, action tracing)

## Outcomes

- Tri-modal assistant behavior (informational, navigational, transactional)
- Domain-agent routing (expense, project, HR, tax, accounting)
- Safe action-taking with explainable gates
- Odoo-grounded navigation and information retrieval
- Promotion from pilot runtime to governed runtime without business-logic rewrite

---

## 1. Product Name

**Reverse SAP Joule** — Pulser: Odoo-native AI Copilot + Agent Platform

## 2. Product Goal

Build an Odoo-native AI assistant that reverses SAP Joule's model by
grounding all intelligence in Odoo operational state, using domain agents
for specialized work, and maintaining safe action gates with full
explainability.

## 3. Reverse Benchmark

**Benchmark product**: SAP Joule

SAP Joule is SAP's generative AI copilot embedded across SAP applications.
It provides conversational access to SAP data, workflow automation,
document summarization, and cross-application actions. Recent 2026 updates
integrate Joule with Microsoft 365 Copilot for bidirectional enterprise AI.

The reverse move:

- **from SAP-native** to **Odoo-native**
- **from embedded monolithic copilot** to **shell + agent runtime split**
- **from opaque AI actions** to **explainable, gated actions**
- **from single-vendor AI** to **connector-portable AI (Azure-native)**
- **from navigation overlay** to **workflow-grounded assistant**

## 4. Source-of-Truth Architecture

Odoo CE 18 owns:

- All record state (invoices, expenses, projects, employees, etc.)
- Approval workflow transitions
- Permission and security group enforcement
- Accounting posting truth
- Audit trail for business actions

Pulser owns:

- Conversational interface (copilot shell)
- Intent routing and domain-agent orchestration
- Tool invocation and action gating
- Explanation generation and confidence scoring
- Tracing and evaluation

Azure owns:

- AI model hosting (Foundry)
- Knowledge search (AI Search, when needed)
- Identity (Entra ID)
- Secrets (Key Vault)
- Observability (Monitor / Application Insights)

## 5. Tri-Modal Behavior

### Informational mode

Answer questions using live Odoo data:

- "What is the status of invoice INV-2026-0042?"
- "How much budget is remaining on Project Alpha?"
- "Who approved this expense report?"

Source: direct Odoo model queries, not cached search index.

### Navigational mode

Guide users to the right Odoo views and actions:

- "Show me all pending purchase approvals"
- "Open the timesheet for this week"
- "Take me to the customer invoice list"

Source: Odoo menu structure, view definitions, and user permissions.

### Transactional mode

Execute bounded actions with safety gates:

- "Submit this expense report for approval" (approval-gated)
- "Create a draft purchase order for vendor X" (approval-gated)
- "Mark this task as done" (auto-routable if policy-compliant)

Every transactional action classified as advisory, approval-gated, or
auto-routable. No unclassified actions.

## 6. Domain Agents

| Agent | Domain | Odoo Models |
|-------|--------|-------------|
| Expense Agent | Expense submission, liquidation, policy | `hr.expense`, `hr.expense.sheet`, `cash.advance` |
| Project Agent | Project status, budget, timeline, tasks | `project.project`, `project.task`, `account.analytic.account` |
| HR Agent | Leave, attendance, employee info | `hr.leave`, `hr.attendance`, `hr.employee` |
| Tax Agent | Tax computation, withholding, compliance | `account.tax`, `account.fiscal.position` |
| Accounting Agent | Invoice, payment, reconciliation | `account.move`, `account.payment` |
| Admin Agent | Settings, users, module configuration | `res.users`, `ir.module.module` |

Each domain agent:

- Has bounded tool access (specific Odoo models and actions)
- Respects Odoo security groups and record rules
- Emits explainable rationale for every action
- Cannot bypass approval workflows

## 7. Functional Requirements

### FR-1: Copilot Shell
Conversational interface with tri-modal behavior detection. Routes user
intent to appropriate domain agent or direct Odoo query.

### FR-2: Intent Router
Classifies user intent as informational, navigational, or transactional.
Routes to domain agent with bounded tool access.

### FR-3: Domain Agent Framework
Pluggable agent architecture where each domain agent has:
- Defined tool bindings (Odoo RPC calls)
- Security context (inherits user's Odoo permissions)
- Action classification (advisory / approval-gated / auto-routable)
- Explanation template

### FR-4: Safe Action Gates
All transactional actions pass through gate classification before execution.
Gates are configurable per company/role/domain.

### FR-5: Knowledge Grounding
RAG-based access to:
- Company policies and SOPs
- Odoo documentation
- Procedural guides

Knowledge grounding supplements, never replaces, live Odoo state queries.

### FR-6: Tracing and Evaluation
Every Pulser interaction produces:
- Trace record (intent, routing, tools invoked, result)
- Evaluation metrics (accuracy, latency, user satisfaction)
- Audit log (actions taken, rationale, confidence)

## 8. MVP Scope

### MVP includes

- Pulser assistant shell with tri-modal behavior (transactional, navigational, informational)
- Safe action classes (advisory, approval-gated, auto-routable where explicitly allowed)
- Domain-agent routing contract (Expense Agent, Project Agent as first two)
- Navigational help (Odoo menu/view routing)
- Informational grounding (live Odoo state queries)
- Audited action logs (rationale, inputs, confidence, policy reference)
- RAG for policies, SOPs, uploaded docs, and curated knowledge only
- Lightweight pilot runtime (ACA shell, bounded tools, App Insights tracing)

### Deferred / post-MVP

- Broad multi-agent autonomy beyond initial two domain agents
- Full enterprise cross-suite orchestration
- Mandatory governed Foundry-first deployment
- Proactive background operations unless explicitly scoped later
- Azure AI Search (governed mode knowledge grounding)
- Full domain agent expansion (HR, Tax, Accounting, Admin agents)

## 9. Non-Goals

- Replacing SAP Joule on the SAP side
- Building a general-purpose chatbot
- Storing operational state outside Odoo
- Bypassing Odoo security groups or approval workflows
- Real-time streaming conversational UX (request-response is sufficient)
- Embedding AI logic directly in Odoo Python models

## 9. Success Metrics

- >80% of informational queries answered from live Odoo state (not cached)
- >90% of transactional actions correctly classified by safety gate
- >95% of domain agent actions respect Odoo security boundaries
- <3s p95 response time for informational queries
- >70% user satisfaction on copilot interactions
- Zero unclassified transactional actions in production

## 10. MVP Framing

MVP is a viable horizontal slice across the minimum required workflow
components, not a disconnected feature fragment.

## 11. External Validation Inputs

This feature may be validated against:

- Azure architecture review checklists for promotion-lane cloud and SaaS controls
- Odoo 18 go-live accounting/operations checklists for cutover and finance readiness

These references support review and go-live readiness only. They do not
redefine MVP scope or architecture ownership.

## 12. Testability Requirements

MVP requires executable Odoo-native tests for all core business flows
introduced by this feature.

Required coverage classes:

- business/model logic
- form/onchange/default behavior
- approval/routing logic
- critical browser flows only where backend/form coverage is insufficient

## 13. Optional Tooling Surfaces

This feature may use MCP servers for testing, debugging, documentation
lookup, and controlled platform operations. These are implementation aids
only and do not redefine product scope or ownership boundaries.

## 14. API Edge Decision

This feature may expose a FastAPI-based Azure API edge for the assistant
shell or agent-facing APIs, but only as a facade or sidecar. Odoo remains
the source of truth for workflow, approvals, accounting, and related ERP
state. FastAPI may own orchestration endpoints and external assistant
surfaces only.

## 15. SaaS / Tenant Framing

This feature may participate in a SaaS or multitenant operating model, but
tenant boundaries and isolation strategy must be specified explicitly and
must not be assumed.
