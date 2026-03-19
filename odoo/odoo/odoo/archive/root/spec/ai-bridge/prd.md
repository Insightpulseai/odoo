# AI Bridge — Product Requirements

**Version**: 1.0.0
**Status**: Active
**Owner**: Platform Engineering

---

## Context

Odoo 19 CE does not expose "Ask AI" natively — that is an Enterprise/IAP feature.
This spec defines the requirements for a CE-compatible AI widget addon (`ipai_ai_widget`)
that wires Odoo UI into the IPAI provider bridge (self-hosted, governed by SSOT).

OCA/ai (github.com/OCA/ai) provides the in-Odoo bridge abstraction layer (targeting 18.0;
porting to 19.0 is tracked as task T-1 below). Until ported, `ipai_ai_widget` depends on
`mail` only and implements its own bridge call.

---

## Objectives

### O1: "Ask AI" in Chatter

**Problem**: Engineers/users want to ask an LLM a question in context while on a record (invoice, task, CRM lead) without leaving Odoo.

**Requirement**: A button "Ask AI" appears in the chatter composer area. Clicking it opens a dialog where the user can type a prompt. The response is rendered in the dialog and can be inserted into the chatter message composer.

**Success criteria**:
- Button renders in chatter for installed `ipai_ai_widget` records
- Prompt POST reaches the Odoo controller within 2s of button click
- Response renders within 30s (60s timeout on controller)
- Insert button copies response text to composer

### O2: Deterministic failure modes

**Problem**: Silent failures (HTTP 500, empty response) are hard to triage.

**Requirement**: Controller returns structured errors:
- `503 BRIDGE_URL_NOT_CONFIGURED` — bridge URL missing from `ir.config_parameter`
- `503 AI_KEY_NOT_CONFIGURED` — IPAI bridge itself returned 503 KEY_MISSING
- `504 BRIDGE_TIMEOUT` — bridge call exceeded 30s
- `500 BRIDGE_ERROR` — any other bridge-side failure

**Success criteria**:
- Each error code is greppable in Odoo logs
- UI shows error message (not spinner)

### O3: Settings UX

**Problem**: Admins need to configure the bridge URL without touching shell/env.

**Requirement**: A settings field in Settings → Technical (or AI section) for `ipai_ai_widget.bridge_url`.

**Success criteria**:
- Field visible in Settings with label "AI Bridge URL"
- Saving sets `ir.config_parameter` `ipai_ai_widget.bridge_url`
- Default is empty (requires explicit configuration)

### O4: SSOT governance

**Problem**: AI bridge references must be auditable and drift-detectable.

**Requirement**:
- `ssot/bridges/catalog.yaml` has an `ipai_ai_widget` entry
- `docs/contracts/AI_WIDGET_CONTRACT.md` documents request/response schema
- `ssot/secrets/registry.yaml` `gemini_api_key` already covers consumers (no new secrets needed)

**Success criteria**:
- `check_parity_and_bridges_ssot.py` exits 0 with `ipai_ai_widget` in catalog
- Contract doc exists at `docs/contracts/AI_WIDGET_CONTRACT.md`

---

## Non-Requirements

- This spec does NOT require porting OCA/ai to 19.0 (tracked separately as T-1)
- This spec does NOT require multi-provider switching (Gemini only in v1)
- This spec does NOT require injecting AI response into form field editors (chatter only in v1)
