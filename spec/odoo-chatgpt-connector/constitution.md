# Constitution — InsightPulseAI Odoo Connector for ChatGPT

## 1. Document Control

- Spec Slug: `odoo-chatgpt-connector`
- Product Name: `InsightPulseAI Odoo Connector`
- Status: Draft / Proposed
- Owner: Platform + Odoo Integrations
- Product Type: ChatGPT Apps SDK app backed by MCP server
- Primary Host Surface: ChatGPT
- Primary System of Action: Odoo (JSON-2 API)
- Canonical Repo Path: `spec/odoo-chatgpt-connector/`

## 2. Purpose

Expose curated Odoo business operations as ChatGPT-native tools so users can search, read, and act on ERP data through natural language without leaving ChatGPT.

## 3. Constitutional Principles

### 3.1 Business-safe tools only

Expose curated, named business tools (e.g., `odoo_search_customers`, `odoo_get_sale_order`). Never expose generic `execute_kw` or arbitrary model/method passthrough.

### 3.2 Read-first

Phase 1 is read-only. Write tools require narrow contracts, human confirmation UX, server-side policy checks, and audit logging.

### 3.3 Gateway-mediated access

ChatGPT never calls Odoo directly. A thin gateway validates input, maps tool calls to allowed models/methods, enforces RBAC and tenant scoping, rate-limits, and audits.

### 3.4 JSON-2 API only

Use Odoo 18's JSON-RPC API (`/web/dataset/call_kw`). XML-RPC is legacy; JSON-RPC is the current standard for Odoo 18.

### 3.5 Structured output contract

Tool results return `structuredContent` (for widget + model), `content` (for transcript), and `_meta` (for UI-only/private data). Follow OpenAI Apps SDK conventions.

### 3.6 Auth boundary at the gateway

- ChatGPT authenticates user to the connector via OAuth
- Connector maps user/session to allowed Odoo identity
- Connector calls Odoo with service credentials
- No raw Odoo API keys exposed to browser or model

## 4. Invariants

- Do not expose raw Odoo model names or method names to the ChatGPT model
- Do not let the model choose arbitrary domains or methods
- Do not expose API keys to the widget layer
- Do not skip audit logging for write operations
- Do not build against legacy XML-RPC/JSON-RPC

## 5. Phase 1 Scope (Read-Only)

- Search customers/contacts
- Get customer profile
- List open quotations
- Get sales order details
- List overdue invoices
- Project/task status
- Inventory by product

## 6. Phase 2 Scope (Scoped Writes)

- Create CRM activity
- Draft quotation note
- Create helpdesk/task follow-up
- Create internal note/chatter entry
