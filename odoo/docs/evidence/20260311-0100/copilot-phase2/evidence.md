# Odoo Copilot — Phase 2 In-App Functional Proof

**Date**: 2026-03-11
**Environment**: Devcontainer (Odoo CE 19, PostgreSQL 16)
**Database**: test_slice_a
**Modules installed**: ipai_ai_core, ipai_ai_rag, ipai_ai_copilot (32 total)
**User**: admin (uid 2)

---

## 1. Health Check

```
GET /web/health → 200
```

## 2. Authentication

```
POST /web/session/authenticate
→ uid: 2 (admin), session established
```

## 3. Tool Registry (/ipai/copilot/tools)

```json
Tools returned: 18
  - get_pipeline_summary (analysis)
  - run_aged_receivables (analysis)
  - trigger_workflow (automation)
  - navigate_to (navigation)
  - bir_compliance_search (read)
  - check_stock (read)
  - list_pending_activities (read)
  - read_record (read)
  - search_knowledge (read)
  - search_records (read)
  - confirm_invoice (write)
  - confirm_sale_order (write)
  - create_quotation (write)
  - create_record (write)
  - execute_activity (write)
  - schedule_activity (write)
  - send_chatter_message (write)
  - update_record (write)
```

## 4. Readonly Tool Execution (/ipai/copilot/execute_tools)

### search_records — PASS

```json
Request: {"tool_calls":[{"name":"search_records","arguments":{"model":"res.partner","query":"admin","limit":3}}]}

Response:
{
  "results": [
    {
      "tool": "search_records",
      "status": "ok",
      "result": [
        {"id": 6, "name": "AI Copilot"},
        {"id": 3, "name": "Administrator"},
        {"id": 1, "name": "My Company"}
      ]
    }
  ]
}
```

### get_pipeline_summary — Expected failure (CRM not installed)

```json
Response: {"status": "error", "error": "TOOL_EXECUTION_FAILED", "detail": "'crm.lead'"}
```

CRM module not installed in test DB — graceful error, no traceback.

## 5. Chat Endpoint (/ipai/copilot/chat)

```json
Request: {"message":"Search for partners named admin","session_id":false}
Response: {"error": "BRIDGE_URL_NOT_CONFIGURED", "status": 503}
```

Expected: Bridge URL (Supabase Edge Function) not configured in test environment.
The endpoint is reachable, authenticates correctly, returns structured error.

## 6. Server Logs

No tracebacks observed during tool execution. All errors are structured JSON responses
with appropriate error codes, not Python exceptions.

---

## Verification Summary

| Check | Result |
|-------|--------|
| Odoo starts with HTTP | PASS (200 on /web/health) |
| Authentication works | PASS (uid 2) |
| Copilot tools endpoint | PASS (18 tools returned) |
| Readonly tool executes | PASS (search_records returns 3 results) |
| No traceback in logs | PASS |
| User context preserved | PASS (runs as admin uid 2) |
| Chat endpoint reachable | PASS (structured 503, not crash) |
| Bridge URL needed for LLM | EXPECTED (requires Supabase Edge config) |

**Phase 2 Gate: PASS** — In-app copilot surface works over HTTP with readonly tools.
The LLM chat path requires bridge URL configuration (Phase 1 integration task, not a blocker for in-app proof).
