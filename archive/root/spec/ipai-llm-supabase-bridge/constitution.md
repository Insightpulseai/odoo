# ipai_llm_supabase_bridge — Constitution

Version: 1.0.0 | Status: Active | Last updated: 2026-02-28

---

## Scope and Relationship to Other AI Specs

This spec governs **two interlocking concerns**:

1. **Vendoring Apexive `odoo-llm`** — the in-Odoo LLM framework (direct provider calls from Odoo).
2. **`ipai_llm_supabase_bridge`** — the IPAI observability layer that hooks into Apexive and
   streams events to Supabase SSOT.

**Architectural note**: Apexive's framework makes direct LLM provider calls from Odoo
(different from `ipai_ai_copilot` which routes all inference through the IPAI bridge URL).
Both patterns are valid and coexist. Use Apexive when you need the full tool/assistant/thread
framework (Claude Desktop MCP, RAG, pgvector). Use `ipai_ai_copilot` for the chatter sidebar.

---

## Non-Negotiable Rules

**Rule 1: Apexive odoo-llm is vendored in `vendor/apexive-llm/` — never modified inline.**
All customizations must go into `ipai_*` override modules using `_inherit`. The vendor submodule
tracks our internal `19.0-ipai` branch (forked from Apexive 18.0). CI must fail if any file
under `vendor/apexive-llm/` is committed outside of a submodule pointer update.

**Rule 2: `ipai_llm_supabase_bridge` is read-only with respect to Odoo-owned domains.**
The bridge MUST NOT modify any `llm.*` record, tool execution result, thread message, or
generation output. It only reads (via `_execute` / `create` hooks) and appends to its own
outbox model (`ipai.bridge.event`). This rule enforces the SOR/SSOT doctrine:
Odoo = SOR for ERP; Supabase = SSOT for observability and control plane.

**Rule 3: All events MUST be HMAC-SHA256 signed before delivery to Supabase.**
Webhook POST requests to the Supabase Edge Function MUST include the `X-Signature-256` header
computed over the JSON body. The Edge Function MUST reject any event where the signature
does not match. The HMAC secret (`LLM_BRIDGE_WEBHOOK_SECRET`) lives in Supabase Vault only —
never in Odoo source code or `ir.config_parameter` in plaintext (only in the transient config
form which stores it as a system parameter — acceptable since system parameters are encrypted
by Odoo's at-rest protections and never committed to git).

**Rule 4: The event outbox is append-only. No event record may be deleted.**
`ipai.bridge.event` records are immutable once created. The `status` field may be updated
(pending → sent → dead) but no record may be unlinkable by non-admin users. This preserves
a local audit trail even when Supabase is unreachable.

**Rule 5: The bridge MUST degrade gracefully when Supabase is unreachable.**
Failed deliveries go to DLQ (`status=failed`) and are retried via cron with exponential backoff.
LLM tool execution and thread creation MUST NOT be blocked or slowed by webhook failures.
All webhook calls are non-blocking (best-effort, exceptions caught and logged, never re-raised
to the caller).

**Rule 6: API keys for LLM providers live in `ir.config_parameter` only — never in source.**
`llm_anthropic` provider requires `ANTHROPIC_API_KEY`. This key MUST be configured via Odoo
Settings (persisted to `ir.config_parameter`) or via environment variable injection at container
startup. It MUST be registered in `ssot/secrets/registry.yaml`. It MUST NOT appear in any
committed file, Dockerfile ENV, or docker-compose environment block in git.

**Rule 7: Supabase schema additions require a migration file with the standard naming convention.**
New tables or columns for the `ops` schema must go in
`supabase/migrations/YYYYMMDD_NNN_<description>.sql`. Migrations are append-only (no DROP TABLE,
no TRUNCATE on existing tables per SSOT Platform Rule 5). The migration SQL must be idempotent
(`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, `DO $$ ... EXCEPTION WHEN ...`).

**Rule 8: The bridge module MUST be registered in `ssot/bridges/catalog.yaml`.**
Every bridge in this repo must have a catalog entry with `contract_doc` pointing to
`docs/contracts/LLM_SUPABASE_BRIDGE_CONTRACT.md`. CI checks (via `check_parity_and_bridges_ssot.py`)
must pass before merging changes that add or remove bridge references.

**Rule 9: `llm_mcp_server` is the ONLY approved external entry point for tool calls.**
External clients (Claude Desktop, Claude Code, Cursor) MUST connect via the MCP server endpoint
(`/llm/mcp`). No direct Odoo XML-RPC or JSON-RPC from LLM client processes. This ensures
all external tool calls flow through the `llm_tool` decorator hook and are captured by the bridge.

**Rule 10: Vendor path is `vendor/` (not `addons/oca/`).**
`addons/oca/` is reserved for OCA-maintained modules. Apexive `odoo-llm` is LGPL but not OCA.
The vendor submodule lives at `vendor/apexive-llm/` with a dedicated `addons_path` entry.
This separation makes the non-OCA provenance explicit and prevents confusion in SSOT audits.
