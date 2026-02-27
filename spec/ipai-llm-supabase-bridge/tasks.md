# ipai_llm_supabase_bridge — Task Checklist

**Version**: 1.0.0 | **Status**: Active | **Last updated**: 2026-02-28

---

## Phase 1 — Vendor + Port Core Modules (D1)

- [ ] **T1.1** Initialize `vendor/apexive-llm` as git submodule on 18.0 branch
  - `git submodule add -b 18.0 https://github.com/apexive/odoo-llm vendor/apexive-llm`
  - Commit `.gitmodules` update
  - AC: `git submodule status` shows clean pointer

- [ ] **T1.2** Create `19.0-ipai` branch in vendor submodule (Apexive fork)
  - `cd vendor/apexive-llm && git checkout -b 19.0-ipai`
  - AC: Branch exists; no changes to module files yet

- [ ] **T1.3** Apply 19.0 checklist to `llm` (core)
  - `<tree>` → `<list>` in all XML views
  - `view_mode="tree,...` → `"list,...`
  - `__manifest__.py` version bump `18.0.x.y.z` → `19.0.x.y.z`
  - Python API fixes (see plan.md §1.2)
  - AC: `odoo -i llm --stop-after-init` exits 0

- [ ] **T1.4** Apply 19.0 checklist to `llm_tool`
  - AC: `odoo -i llm,llm_tool --stop-after-init` exits 0

- [ ] **T1.5** Apply 19.0 checklist to `llm_thread`
  - AC: `odoo -i llm,llm_tool,llm_thread --stop-after-init` exits 0

- [ ] **T1.6** Apply 19.0 checklist to `llm_assistant`
  - AC: Assistant UI renders in Odoo 19 Discuss sidebar

- [ ] **T1.7** Apply 19.0 checklist to `llm_openai`
  - AC: OpenAI provider creates a completion with test API key

- [ ] **T1.8** Apply 19.0 checklist to `llm_mcp_server`
  - AC: `curl localhost:8069/llm/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'`
       returns tool list JSON

- [ ] **T1.9** Add `vendor/apexive-llm` to `addons_path` in `config/dev/odoo.conf`
  - AC: Modules discoverable without manual path override

- [ ] **T1.10** Update `.gitignore` to exclude vendor build artifacts
  - AC: `git status` shows only submodule pointer, no untracked vendor files

---

## Phase 2 — `llm_anthropic` Port (D2)

- [ ] **T2.1** Cherry-pick `llm_anthropic` from Apexive 16.0 into `19.0-ipai`
  - AC: `llm_anthropic/` directory appears in vendor tree

- [ ] **T2.2** Bring provider interface up to 19.0 `llm.provider` spec
  - Implement `_generate(messages, tools=None)` → `anthropic.messages.create()`
  - Implement `_model_list()` → return Claude 4.5 family models
  - AC: No import errors on module load

- [ ] **T2.3** Add Claude 4.5 model enumeration
  - `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
  - AC: Models appear in `llm.provider` model selection dropdown

- [ ] **T2.4** Add tool use support
  - Map `llm_tool` declarations → Anthropic SDK `tools=` parameter format
  - Parse `tool_use` content blocks from response → `llm_tool._execute()`
  - AC: A tool-calling assistant invokes a registered tool via Claude

- [ ] **T2.5** Pin `anthropic>=0.40.0` in manifest external_dependencies
  - AC: `pip install anthropic` via entrypoint or requirements.txt

- [ ] **T2.6** Register `anthropic_api_key` in `ssot/secrets/registry.yaml`
  - Approved store: `odoo_config_parameter`
  - AC: Key appears in registry with consumers list

- [ ] **T2.7** Run `llm_anthropic` tests (or write basic test if none exist)
  - AC: Test module installs + `--test-tags /llm_anthropic` exits 0

---

## Phase 3 — `ipai_llm_supabase_bridge` Module (D3)

- [ ] **T3.1** Copy scaffold files from zip deliverable to `addons/ipai/ipai_llm_supabase_bridge/`
  - `__manifest__.py`, `models/ipai_bridge_config.py`, `models/ipai_bridge_event.py`
  - `models/llm_tool.py`, `models/llm_thread.py`
  - AC: All 5 Python files present

- [ ] **T3.2** Create `__init__.py` files (module + models package)
  - AC: Module importable without `ImportError`

- [ ] **T3.3** Create `security/ir.model.access.csv`
  - `ipai.bridge.event`: read/write/create for `base.group_user`; delete for `base.group_system`
  - `ipai.bridge.config`: full access for `base.group_system`
  - AC: No `AccessError` on UI access with non-admin user

- [ ] **T3.4** Create `views/ipai_bridge_event_views.xml`
  - List view: event_type, status, attempts, create_date, next_retry_at
  - Form view: all fields + error_message + payload (JSON widget)
  - Action + menu item under Settings → Technical → IPAI Bridge
  - AC: DLQ visible and filterable in UI

- [ ] **T3.5** Create `views/ipai_bridge_config_views.xml`
  - TransientModel wizard: webhook_url, webhook_secret (password widget), enabled, retry config
  - "Save" and "Test Connection" buttons
  - AC: Settings form saves to `ir.config_parameter`; test button shows success/error toast

- [ ] **T3.6** Create `data/ipai_llm_supabase_bridge_data.xml`
  - Cron: `_cron_retry_failed` every 5 minutes (active=False by default)
  - Cron: `_cron_flush_pending` every 1 minute (active=False by default)
  - AC: Crons appear in Settings → Technical → Automation; manually triggerable

- [ ] **T3.7** Install module: `odoo -i ipai_llm_supabase_bridge --stop-after-init`
  - AC: Exits 0; no import warnings

- [ ] **T3.8** Write `tests/test_bridge_event.py`
  - Test `_emit()` with bridge disabled → no event created
  - Test `_emit()` with bridge enabled, mock webhook → event status=sent
  - Test `_emit()` with bridge enabled, webhook error → event status=failed, attempts=1
  - Test `_cron_retry_failed` with a failed event past retry time → _try_send called
  - AC: `--test-tags /ipai_llm_supabase_bridge` exits 0 with 4+ tests passing

---

## Phase 4 — Supabase Schema + Edge Function

- [ ] **T4.1** Apply `supabase/migrations/20260228_001_ops_llm_observability.sql`
  - Via `supabase db push` or Dashboard SQL Editor
  - AC: `SELECT COUNT(*) FROM ops.runs` returns 0 (tables exist, empty)

- [ ] **T4.2** Verify RLS policies
  - `SET ROLE authenticated; SELECT * FROM ops.runs;` → empty (not error)
  - `SET ROLE service_role; INSERT INTO ops.runs ...` → succeeds
  - AC: No RLS policy errors

- [ ] **T4.3** Deploy `supabase/functions/llm-webhook-ingest/index.ts`
  - `supabase functions deploy llm-webhook-ingest --project-ref spdtwktxdalcfigzeqrz`
  - AC: Function appears in Supabase Dashboard → Edge Functions

- [ ] **T4.4** Set `LLM_BRIDGE_WEBHOOK_SECRET` in Supabase Vault
  - `supabase secrets set LLM_BRIDGE_WEBHOOK_SECRET=<32-char-random>`
  - AC: Secret appears in `supabase secrets list` (name only, value hidden)

- [ ] **T4.5** Register `llm_bridge_webhook_secret` in `ssot/secrets/registry.yaml`
  - Approved store: `supabase_vault`
  - Consumers: `supabase:functions/llm-webhook-ingest`, `odoo_config_parameter:ipai_llm_supabase_bridge.webhook_secret`
  - AC: Key appears in registry

- [ ] **T4.6** Configure Odoo bridge settings
  - Odoo Settings → Technical → IPAI Bridge → Configuration
  - Webhook URL: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/llm-webhook-ingest`
  - HMAC Secret: matching value; Enabled: ✓
  - "Test Connection" → success toast
  - AC: `ops.run_events` shows `bridge.ping` event after test

- [ ] **T4.7** E2E integration test
  - Run a full chat exchange through `llm_assistant` with `llm_anthropic` provider
  - AC: `ops.run_events` contains `thread.create`, `generation.start`, `generation.complete`

- [ ] **T4.8** DLQ test
  - Temporarily set webhook URL to invalid endpoint
  - Run a chat → events go to DLQ
  - Restore URL → manually trigger `_cron_retry_failed` → events delivered
  - AC: All DLQ events transition to `status=sent`; `ops.run_events` populated

---

## Phase 5 — SSOT Registration

- [ ] **T5.1** Add `ipai_llm_supabase_bridge` to `ssot/bridges/catalog.yaml`
  - `status: planned` (promote to `active` after prod deploy)
  - `contract_doc: docs/contracts/LLM_SUPABASE_BRIDGE_CONTRACT.md`
  - AC: Entry present with all required fields

- [ ] **T5.2** Create `docs/contracts/LLM_SUPABASE_BRIDGE_CONTRACT.md`
  - Document webhook request schema (event envelope JSON)
  - Document response schema (200 OK / 401 invalid signature / 409 duplicate)
  - Document Edge Function error codes
  - AC: File exists; referenced from catalog entry

- [ ] **T5.3** Update `ssot/ai/odoo_ai.yaml`
  - Add `anthropic` as an available provider alongside `gemini`
  - Note: `anthropic` requires `llm_anthropic` installed and API key configured
  - AC: File updated; no schema validation errors

- [ ] **T5.4** Run CI gate
  - `python scripts/ci/check_parity_and_bridges_ssot.py`
  - AC: Exits 0; bridge catalog validates

- [ ] **T5.5** Commit all spec + implementation files
  - Commit 1: `feat(spec): scaffold ipai-llm-supabase-bridge spec bundle`
  - Commit 2: `feat(ai): add ipai_llm_supabase_bridge module scaffold + Supabase schema`
  - Commit 3: `chore(ssot): register llm bridge in bridges catalog and secrets registry`
  - AC: All 3 commits pushed; CI green
