# Tasks — Odoo Copilot Marketplace

## Phase 1: Informational + Navigational

- [ ] Define JSON schema for informational tool definitions (query, lookup, search)
- [ ] Define JSON schema for navigational tool definitions (deep links, view routing)
- [ ] Implement Odoo JSON-RPC client with auth, retry, and connection pooling
- [ ] Implement permission-aware query layer (access rights, record rules, company scope)
- [ ] Build identity bridge: Microsoft 365 email → Odoo user resolution
- [ ] Implement token exchange flow (Azure AD → Odoo session token)
- [ ] Index Odoo documentation for semantic retrieval
- [ ] Implement document ingestion for company SOPs/policies
- [ ] Build RAG pipeline for grounded informational answers
- [ ] Create Teams app manifest (bot + messaging extension)
- [ ] Create Copilot plugin definition with tool declarations
- [ ] Implement adaptive card templates for query results
- [ ] Implement deep-link cards for navigational results
- [ ] Write integration tests for read-only flows
- [ ] Submit Teams app for marketplace review

## Phase 2: Controlled Transactional

- [ ] Define transactional tool schemas (create lead, task, note, expense, activity)
- [ ] Implement confirmation flow (preview card → user confirm → execute → audit log)
- [ ] Implement admin-configurable write-scope controls
- [ ] Build audit log table and API (user, action, timestamp, result, rollback info)
- [ ] Implement privileged-read logging for sensitive fields
- [ ] Build admin dashboard for audit review
- [ ] Implement confirmation/success/failure adaptive cards
- [ ] Write integration tests for transactional flows
- [ ] Security review: permission escalation, injection, scope bypass

## Phase 3: Domain Packs

- [ ] Define domain pack structure (tool set + knowledge sources + permissions)
- [ ] Implement CRM domain pack
- [ ] Implement Finance domain pack
- [ ] Implement Project domain pack
- [ ] Implement BIR/compliance domain pack (Philippines localization)
- [ ] Implement multi-step workflow orchestration
- [ ] Build MCP-compatible gateway for non-Microsoft surfaces
- [ ] Write end-to-end tests for each domain pack
