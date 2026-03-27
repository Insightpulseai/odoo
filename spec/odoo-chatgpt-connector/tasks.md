# Tasks — InsightPulseAI Odoo Connector for ChatGPT

## Task Rules

- Status: `todo`, `in_progress`, `blocked`, `done`
- Priority: `P0`, `P1`, `P2`

---

## Phase 0 — Foundation

### T-001 — Create spec bundle

- Status: done
- Priority: P0
- Output: constitution.md, prd.md, plan.md, tasks.md

### T-002 — Create app scaffold

- Status: todo
- Priority: P0
- Output: `apps/odoo-chatgpt-connector/` with server, tools, auth, odoo directories

### T-003 — Verify Odoo JSON-2 API availability

- Status: todo
- Priority: P0
- Output: smoke test against `erp.insightpulseai.com/json/2/res.partner/search_read`
- Acceptance: JSON-2 endpoint responds, bearer auth works

---

## Phase 1 — Read-only tools

### T-010 — Implement Odoo JSON-2 client

- Status: todo
- Priority: P0
- Output: `server/odoo/client.ts`
- Acceptance: wrapper for `/json/2/<model>/<method>` with bearer auth, error handling, rate limiting

### T-011 — Implement model/method mapping

- Status: todo
- Priority: P0
- Output: `server/odoo/mapping.ts`
- Acceptance: allowlist of model+method pairs, rejects unmapped calls

### T-012 — Implement customer tools

- Status: todo
- Priority: P0
- Output: `odoo_search_partners`, `odoo_get_partner`

### T-013 — Implement sales tools

- Status: todo
- Priority: P0
- Output: `odoo_search_sale_orders`, `odoo_get_sale_order`, `odoo_list_pipeline_opportunities`

### T-014 — Implement finance tools

- Status: todo
- Priority: P0
- Output: `odoo_list_overdue_invoices`, `odoo_get_invoice`

### T-015 — Implement project tools

- Status: todo
- Priority: P0
- Output: `odoo_search_projects`, `odoo_get_project_status`, `odoo_list_project_tasks`

### T-016 — Implement inventory tools

- Status: todo
- Priority: P1
- Output: `odoo_get_product_availability`, `odoo_get_inventory_snapshot`

### T-017 — Implement OAuth flow

- Status: todo
- Priority: P0
- Output: `server/auth/oauth.ts`, `server/auth/session.ts`
- Acceptance: ChatGPT user can authenticate, session maps to Odoo identity

### T-018 — Register MCP server with Apps SDK

- Status: todo
- Priority: P0
- Output: working MCP server exposing all Phase 1 tools
- Acceptance: tools appear in ChatGPT, invocations return structured results

---

## Phase 2 — Scoped writes

### T-020 — Implement `odoo_create_activity`

- Status: todo
- Priority: P1
- Acceptance: activity created on target record, audit logged

### T-021 — Implement `odoo_post_record_note`

- Status: todo
- Priority: P1
- Acceptance: chatter note posted, audit logged

### T-022 — Add human confirmation UX for writes

- Status: todo
- Priority: P1
- Acceptance: structured content preview shown before mutation

---

## Phase 3 — Widgets

### T-030 — Order summary widget

- Status: todo
- Priority: P2

### T-031 — Invoice aging widget

- Status: todo
- Priority: P2

### T-032 — Project health widget

- Status: todo
- Priority: P2

---

## Backlog

### T-100 — ChatGPT app submission

- Status: todo
- Priority: P2

### T-101 — Multi-tenant support

- Status: todo
- Priority: P2

### T-102 — Odoo customer statement tool

- Status: todo
- Priority: P2
