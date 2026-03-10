# ipai_llm_supabase_bridge — Product Requirements

**Version**: 1.0.0
**Status**: Active
**Owner**: Platform Engineering

---

## Context

Odoo 19 CE has no built-in LLM framework. Apexive's `odoo-llm` (github.com/apexive/odoo-llm)
fills this gap with 30+ modules covering tool calling, assistant UIs, MCP server, RAG,
pgvector, and multi-provider support (OpenAI, Ollama, Mistral — plus an unmaintained 16.0
Anthropic provider). It is LGPL-3, architecturally sound, and the de-facto community standard.

This spec covers three sequential deliverables:

| Deliverable | What | Output |
|-------------|------|--------|
| D1 | Port Apexive odoo-llm 18.0 → 19.0 | `vendor/apexive-llm` submodule on `19.0-ipai` branch |
| D2 | Port `llm_anthropic` 16.0 → 19.0 | Working Claude provider in vendor tree |
| D3 | Build `ipai_llm_supabase_bridge` | Observability bridge module + Supabase schema |

---

## Objectives

### O1: Apexive odoo-llm Vendored and Running on 19.0

**Problem**: No LLM framework exists in the repo. Building from scratch would duplicate
1,800+ commits of Apexive work.

**Requirement**: Fork Apexive 18.0 into `vendor/apexive-llm` as a git submodule on an
internal `19.0-ipai` branch. Apply the 19.0 migration checklist to at minimum these modules:
`llm`, `llm_thread`, `llm_tool`, `llm_assistant`, `llm_openai`, `llm_mcp_server`.

**Success criteria**:
- `docker compose exec odoo odoo -d odoo_dev -i llm,llm_tool,llm_assistant --stop-after-init`
  exits 0
- `llm_mcp_server` MCP endpoint reachable at `http://localhost:8069/llm/mcp`
- An OpenAI-backed assistant can complete a chat exchange end-to-end

**Not in scope**: `llm_knowledge`, `llm_pgvector`, `llm_store` (Phase 2)

### O2: `llm_anthropic` Provider on 19.0 with Claude 4.x + Tool Use

**Problem**: The only Anthropic provider in Apexive is a stale 16.0 module with no tool use,
no streaming, and no Claude 3/4 model support. Claude is the canonical AI provider for IPAI.

**Requirement**: Port `llm_anthropic` from Apexive 16.0 (cherry-pick source) to 19.0, extending
it with:
- Claude 4.5 family model enumeration (claude-sonnet-4-6, claude-haiku-4-5-20251001, claude-opus-4-6)
- Tool use / function calling via the `anthropic` SDK tool_use content blocks
- Streaming via `anthropic` SDK streaming API (optional, for responsive chat UI)
- `anthropic>=0.40.0` as external dependency
- Passes the standard `llm` provider test suite (`test_provider_basic.py`)

**Success criteria**:
- `llm_anthropic` installs cleanly alongside ported `llm` core
- Creating an `llm.provider` record of type `anthropic` with a valid API key
  returns a completion when called via `assistant._generate()`
- `llm_tool` decorator works end-to-end: tool registered → assistant calls it → result returned

**API key handling**: The key is configured via `ir.config_parameter:anthropic.api_key`
(set through Settings → LLM → Providers). It MUST be registered in `ssot/secrets/registry.yaml`
as `anthropic_api_key`.

### O3: `ipai_llm_supabase_bridge` — Observability Outbox

**Problem**: Every LLM tool call, thread, and generation goes completely unobserved.
There is no audit trail, no governance telemetry, and no way to correlate Odoo activity
with the Supabase control plane.

**Requirement**: A thin Odoo module (`ipai_llm_supabase_bridge`) that:
1. Hooks into Apexive's `llm_tool._execute()` to emit `tool.call` / `tool.result` events
2. Hooks into Apexive's `llm_thread` lifecycle to emit `thread.create` / `generation.start` /
   `generation.complete` events
3. Delivers events to a Supabase Edge Function via signed webhooks (HMAC-SHA256)
4. Stores all events in `ipai.bridge.event` outbox before delivery attempt
5. On delivery failure: DLQ (`status=failed`) with exponential backoff retry via cron
6. Provides Settings UI (TransientModel) for webhook URL, secret, enabled toggle, retry config

**Success criteria**:
- Installing the module with Apexive modules present imports cleanly
- Enabling the bridge → running an assistant chat → `ops.run_events` contains
  `thread.create`, `generation.start`, `generation.complete` events in Supabase
- Killing the Supabase endpoint → events queue in DLQ → restarting → cron delivers them
- Disabling the bridge (`enabled=False`) → zero events emitted, zero performance impact

**Constraints**:
- No blocking of LLM execution on webhook failure (non-blocking delivery)
- No write-back from Supabase to Odoo (one-way: Odoo → Supabase only)
- `ipai.bridge.event` records are immutable (no user-facing delete)

### O4: Supabase Schema — `ops` Observability Tables

**Problem**: No Supabase schema exists for LLM observability data.

**Requirement**: A single migration file creating:
- `ops.runs` — top-level execution tracking per LLM thread or generation
- `ops.run_events` — append-only timeline of events with idempotency key
- `ops.artifacts` — output references (reports, exports, Storage pointers)
- `ops.ingest_bridge_event()` — idempotent RPC function called by Edge Function
- RLS: `service_role` full access; `authenticated` read-only own runs
- Edge Function `llm-webhook-ingest`: HMAC verification → calls `ops.ingest_bridge_event()`

**Success criteria**:
- Migration applies cleanly via `supabase db push` or dashboard SQL editor
- Edge Function deployed: `supabase functions deploy llm-webhook-ingest`
- Ping event (`bridge.ping`) from Odoo Settings test button → `ops.run_events` row created
- `SELECT COUNT(*) FROM ops.run_events` after E2E test shows expected event count

### O5: SSOT Registration

**Requirement**: All new artifacts registered in SSOT:
- `ssot/bridges/catalog.yaml` — `ipai_llm_supabase_bridge` entry
- `ssot/secrets/registry.yaml` — `anthropic_api_key` and `llm_bridge_webhook_secret`
- `ssot/ai/odoo_ai.yaml` — note `anthropic` as available provider alongside `gemini`
- `docs/contracts/LLM_SUPABASE_BRIDGE_CONTRACT.md` — webhook request/response schema

**Success criteria**:
- `python scripts/ci/check_parity_and_bridges_ssot.py` exits 0 (bridge in catalog)
- `ssot/secrets/registry.yaml` has entries for both new secrets

---

## Non-Requirements (v1.0)

- `llm_knowledge` / `llm_pgvector` / RAG (Phase 2)
- `llm_voice` (no roadmap item)
- Bidirectional Supabase → Odoo write-back
- Multi-tenant isolation in `ops` schema (v1 uses `odoo_db` column to differentiate)
- Production deployment (dev + staging only in v1)
