# Implementation Plan — Odoo Copilot Marketplace

## Phase 1: Informational + Navigational (Read-Only)

### 1.1 Odoo Capability Gateway — Read Layer
- Define tool schema for informational queries (invoice status, overdue items, record lookups)
- Define tool schema for navigational actions (deep links to Odoo records, views, dashboards)
- Implement Odoo JSON-RPC wrapper with connection pooling and error handling
- Implement permission-aware query execution (respects Odoo access rights and record rules)

### 1.2 Identity and Access Bridge
- Map Microsoft 365 user identity (Azure AD / Entra ID) to Odoo user via email or external ID
- Implement token exchange flow (Microsoft → Odoo session)
- Enforce company scope and multi-company access rules

### 1.3 Knowledge Grounding Layer
- Index Odoo help documentation for semantic retrieval
- Support company SOP/policy document ingestion
- Implement retrieval-augmented generation for informational answers

### 1.4 Microsoft Teams / Copilot App
- Create Teams app manifest and Copilot plugin definition
- Implement adaptive card responses for query results
- Implement deep-link cards for navigational results
- Package for Microsoft marketplace submission

## Phase 2: Controlled Transactional Actions

### 2.1 Odoo Capability Gateway — Write Layer
- Define transactional tool schemas (create lead, create task, post note, etc.)
- Implement confirmation flow (preview → confirm → execute → audit)
- Implement write-scope controls (admin-configurable per action class)

### 2.2 Audit and Control Plane
- Log all write actions with user, timestamp, action, and result
- Log privileged reads (sensitive fields, financial data)
- Implement admin dashboard for audit review

### 2.3 Copilot Transactional UX
- Implement confirmation cards in Teams/Copilot
- Implement success/failure response cards
- Add undo/rollback guidance where applicable

## Phase 3: Domain Packs and Automation

### 3.1 Domain Pack Framework
- Define domain pack structure (tool set + knowledge sources + permissions)
- Implement CRM pack, Finance pack, Project pack
- Implement BIR/compliance pack (Philippines localization)

### 3.2 Agent/Workflow Orchestration
- Multi-step workflow support (e.g., expense report: create → attach → submit)
- Integration with Odoo automated actions and server actions
- Optional MCP-compatible gateway for non-Microsoft surfaces
