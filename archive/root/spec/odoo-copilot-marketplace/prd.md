# Odoo Copilot Marketplace — PRD

> AI copilot and agent layer for Odoo, delivered into Microsoft 365 Copilot, Teams, and Outlook.

---

## 1. Title

**Odoo Copilot for Microsoft 365** — an Odoo-native copilot marketplace app
that brings Odoo capabilities into Microsoft 365 Copilot, Teams, and Outlook.

## 2. Problem Statement

Odoo users still work across too many surfaces:

- Odoo UI for transactions
- Email and Teams for collaboration
- Documentation and knowledge bases for help
- External dashboards and spreadsheets for analysis
- Disconnected bots or custom scripts for automation

This forces users to switch context just to:

- Look up ERP/CRM/project data
- Navigate to the right Odoo page
- Create or update records
- Retrieve company-specific process guidance
- Summarize status across sales, accounting, inventory, HR, and projects

SAP Joule's marketplace model shows that enterprise buyers want a copilot
embedded in Microsoft 365 that can do three things well: retrieve information,
navigate to the right system/workflow, and complete business transactions.

## 3. Product Vision

Build an Odoo-native copilot marketplace app that brings Odoo into:

- Microsoft 365 Copilot
- Microsoft Teams
- Outlook / Office surfaces
- Later, optionally, ChatGPT and other agent channels

The product should let users:

- Ask business questions in natural language
- Navigate directly to the correct Odoo workflow or record
- Create/update approved Odoo records conversationally
- Retrieve grounded answers from Odoo help docs, company SOPs, and knowledge sources
- Operate under role-based access and auditability

## 4. Product Principles

1. **Odoo remains system of record** — the copilot does not replace Odoo business logic.
2. **Read / navigate / transact are separate capability classes** — following the clearest pattern from Joule's marketplace design.
3. **Authentication and authorization are first-class** — user identity/authorization alignment for Microsoft 365 Copilot access, with governed access and inherited permissions.
4. **Grounded answers over hallucinated answers** — informational mode must prefer Odoo docs, company docs, and approved knowledge bases.
5. **Transactional actions must be scoped and auditable** — high-risk writes require stronger confirmation and logging.

## 5. Users

### Primary users

- Finance users
- Sales and CRM users
- Operations managers
- Project managers
- HR / admin staff
- Executives needing summaries

### Secondary users

- Odoo implementation partners
- Support/admin teams
- Internal AI/platform operators

## 6. Capability Model

### 6.1 Informational

The assistant answers grounded questions such as:

- "What is the status of invoice INV-2026-0042?"
- "Show overdue customer invoices for TBWA"
- "What is our BIR filing deadline this month?"
- "How do we process travel liquidation?"

This mirrors the informational category from SAP Joule, including knowledge/doc
retrieval and summarized answers.

### 6.2 Navigational

The assistant directs users to the correct Odoo screen or workflow:

- Open customer record
- Navigate to draft vendor bills
- Open the month-end close workspace
- Open the project task board for a given team

This mirrors Joule's navigational pattern: helping users find and open the right
app or process without manual hunting.

### 6.3 Transactional

The assistant executes approved business actions:

- Create CRM lead
- Create/update task
- Draft expense report
- Post internal note
- Create purchase request
- Assign approver
- Add comment to project item
- Create follow-up activity

This mirrors Joule's transactional mode, where business data can be
created/viewed/updated conversationally.

## 7. Delivery Surfaces

### Phase 1

- Microsoft Teams app
- Microsoft 365 Copilot plugin/agent surface
- Outlook add-in style assist scenarios for message context

### Phase 2

- Odoo embedded side panel
- Web chat for portal/internal users
- ChatGPT / MCP-compatible app surface

Microsoft already positions Microsoft 365 Copilot and Copilot Studio as
channels for publishing business-connected agents across work surfaces.

## 8. Core Product Components

### 8.1 Odoo Capability Gateway

A backend service that maps Odoo capabilities into three classes:

- Informational tools
- Navigational tools
- Transactional tools

### 8.2 Identity and Access Bridge

Maps Microsoft identity / enterprise auth to Odoo users, roles, companies,
teams, and record rules.

### 8.3 Knowledge Grounding Layer

Supports:

- Odoo documentation
- Company SOPs / policies
- Uploaded procedural documents
- Odoo help text / metadata
- Optionally SharePoint / Teams documents later

### 8.4 Conversation Orchestration Layer

Handles:

- Intent detection
- Tool routing
- Confirmation for writes
- Context carryover
- Conversation/session audit

### 8.5 Marketplace Packaging Layer

Includes:

- Microsoft marketplace listing
- Teams/Copilot packaging
- Admin configuration
- Tenant onboarding
- License / entitlement checks

## 9. Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-1 | Informational query support | Answer grounded questions using Odoo data and approved knowledge sources |
| FR-2 | Navigational support | Return direct navigation targets into Odoo workflows and records |
| FR-3 | Transactional execution | Support scoped create/update actions for approved Odoo objects |
| FR-4 | Role-based security | Respect Odoo permissions, company scope, and record rules |
| FR-5 | Audit logging | Log all write actions and privileged reads |
| FR-6 | Confirmation model | Require explicit confirmation for high-impact transactions |
| FR-7 | Knowledge grounding | Support document-grounded informational answers |
| FR-8 | Teams / Copilot presence | Installable and usable within Microsoft Teams and Microsoft 365 Copilot |
| FR-9 | Admin configuration | Configure Odoo endpoint, tenant/workspace binding, auth settings, enabled tool sets, knowledge sources, write permissions by action class |
| FR-10 | Extensible domain packs | Support domain packs for CRM, finance, inventory, project management, HR, compliance / BIR workflows |

## 10. Non-Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-1 | Security | Enterprise authentication; no unrestricted write access |
| NFR-2 | Governance | Audit logs, policy controls, tenant isolation |
| NFR-3 | Reliability | Read/navigation flows resilient even when transactional endpoint is unavailable |
| NFR-4 | Latency | Common informational and navigational requests feel near-interactive |
| NFR-5 | Portability | Odoo capability gateway reusable outside Microsoft surfaces |

## 11. Architecture

### 11.1 Front-end Channels

- Teams / Copilot app
- Optional Outlook context actions
- Future embedded Odoo panel

### 11.2 Copilot App Layer

- Tool definitions
- Response cards
- Action confirmations
- Auth/session handling

### 11.3 Odoo Capability Gateway

- Odoo API wrappers
- Object permission checks
- Route resolvers
- Transaction orchestrators

### 11.4 Knowledge and Grounding Layer

- Odoo docs
- Internal docs
- Document grounding / search index
- Semantic retrieval

### 11.5 Audit and Control Plane

- Logs
- Action history
- Environment config
- Tool enablement policy
- Tenant/workspace state

## 12. Differentiation vs SAP Joule

### Similarities to copy

- Three-mode capability model: informational, navigational, transactional
- Microsoft 365 Copilot / Teams delivery
- Business-system-aware assistant
- Role-aware access
- Document grounding

### Improvements to make

- Deeper Odoo object/action model than generic "business info"
- Explicit admin-controlled write scopes
- Richer Odoo-specific navigation shortcuts
- Domain packs for CRM, finance, BIR compliance, projects
- Reusable MCP/app-gateway architecture beyond Microsoft only

## 13. Marketplace Positioning

**Category:**

- Odoo Copilot for Microsoft 365
- Odoo AI Assistant for Teams
- Odoo Work Copilot

**Value proposition:**

> "Bring Odoo into the flow of work inside Teams and Microsoft 365 Copilot —
> ask questions, navigate faster, and complete business actions without leaving
> your collaboration workspace."

**Marketplace proof points:**

- Secure role-based access
- Grounded answers
- Transactional actions
- Odoo-native workflows
- Admin governance controls

## 14. Packaging

| Tier | Capabilities |
|------|-------------|
| **Free / Trial** | Read-only informational + navigation, limited objects, sandbox workspace |
| **Business** | Transactional actions, multiple domain packs, knowledge grounding, audit logs |
| **Enterprise** | SSO / enterprise auth, advanced policy controls, custom connectors, private deployment options, premium support |

## 15. Risks

- Odoo permission mismatches with Microsoft identity
- Over-broad write actions creating operational risk
- Grounding quality depending on document hygiene
- Marketplace approval and packaging complexity
- Need for per-tenant admin onboarding

## 16. Open Questions

1. Should the first write surface be Teams only, or Teams + Copilot simultaneously?
2. Which Odoo objects are in v1 transactional scope?
3. Is document grounding Odoo-only first, or Odoo + SharePoint?
4. What is the canonical auth bridge pattern for enterprise tenants?
5. Should this launch as a Microsoft marketplace app first, or as a direct app/plugin first?

## 17. Launch Recommendation

### Phase 1 — Informational + Navigational

- Teams and Copilot presence
- Read-only Odoo queries
- Navigation to records and workflows
- Grounded docs answers

### Phase 2 — Controlled Transactional Actions

- Create/update selected records
- Comments, tasks, leads, approvals
- Confirmation model
- Audit logging

### Phase 3 — Domain Packs and Automation

- Finance pack
- CRM pack
- Project pack
- BIR/compliance pack
- Agent/workflow orchestration

---

## Verification Checklist

- [x] PRD clearly separates informational, navigational, and transactional modes
- [x] Odoo remains the source of truth
- [x] Write actions are governed and auditable
- [x] Microsoft 365 Copilot / Teams are first-class delivery surfaces
- [x] The design improves on SAP Joule instead of just copying it
- [x] Ready for follow-on `plan.md`
