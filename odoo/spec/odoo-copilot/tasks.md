# Odoo Copilot — Task Checklist

Tasks split into: build | integration | verification | evidence.
Each phase ends with a hard verification gate.

---

## Batch 0 — Phase B0.A: Platform Baseline Install
### Build
- [ ] Verify all 13 OCA modules exist in `addons/oca/` (cloned via git-aggregator)
- [ ] Confirm modules declared in `config/addons.manifest.yaml` tiers 0-6

### Verification
- [ ] `--stop-after-init` install of 13 modules in `test_oca_b0`
- [ ] Classify any failures: env issue / migration gap / real defect
- [ ] Verify `disable_odoo_online` + `remove_odoo_enterprise` availability on 19.0

### Evidence
- [ ] Install log committed to `docs/evidence/YYYYMMDD-HHMM/oca-batch0/`
- [ ] Module status table (installed / not found / failed) committed

**GATE: B0.A — platform baseline verified**

---

## Batch 0 — Phase B0.B: Productivity Enhancements (Optional)
### Build
- [ ] Identify active use cases for optional UX modules

### Verification
- [ ] `--stop-after-init` install of selected optional modules
- [ ] No regressions on B0.A baseline

### Evidence
- [ ] Install log appended to batch0 evidence

**GATE: B0.B — optional UX modules verified**

---

## Batch 0 — Phase B0.C: OCA AI Compatibility Layer
### Build
- [ ] Add `ai_oca_bridge` to OCA `ai` repo must-have list in manifest
- [ ] Port-and-verify `ai_oca_bridge` on Odoo 19 (source targets 18.0)

### Verification
- [ ] `--stop-after-init` install of `ai_oca_bridge` in `test_oca_b0`
- [ ] Provider routing interface accessible from Python

### Evidence
- [ ] Install log committed
- [ ] Migration gap documented if 19.0 port fails

**GATE: B0.C — AI bridge verified or classified**

---

## Batch 0 → Batch 1 Promotion
- [ ] Promote verified B0 modules to `odoo_dev`
- [ ] Document skipped modules with classification
- [ ] Evidence bundle complete in `docs/evidence/`

---

## Batch 1 — Phase B1.1: Agent Builder Verification
### Build
- [x] Confirm `ipai_ai_agent_builder` installable: True (verified in code)

### Verification
- [ ] `--stop-after-init` install in devcontainer
- [ ] Agent form loads (tree + form views render)
- [ ] Topics inline editing works
- [ ] Settings page renders (LLM Providers block)

### Evidence
- [ ] Install log committed

**GATE: B1.1 — install + UI verified**

---

## Batch 1 — Phase B1.2: Prompt Registry Module
### Build
- [x] Create `addons/ipai/ipai_ai_prompts/` module scaffold
- [x] Model: `ipai.ai.prompt` with fields (name, sequence, active, when_users_need_to, instructions, button_prompt, target_context, agent_id, topic_id, company_id)
- [x] Views: tree + form + search
- [x] Menu: AI Agents > Configuration > Default Prompts
- [x] Security: ir.model.access.csv using existing groups
- [x] Seed data: 10 default prompts

### Verification
- [ ] `--stop-after-init` install
- [ ] CRUD via UI (create, read, update, delete prompt)
- [ ] Seed data: 10 prompt records exist

### Evidence
- [ ] Install log committed

**GATE: B1.2 — prompt module installed + functional**

---

## Batch 1 — Phase B1.3: Provider Verification
### Build
- [x] Add Providers menuitem under AI Agents > Configuration (owned by `ipai_ai_core`)
- [ ] Seed 2 provider records (ChatGPT gpt-4o, Gemini gemini-pro) if not present

### Verification
- [ ] Providers visible in Configuration menu
- [ ] Provider form renders cleanly

### Evidence
- [ ] Screenshot/curl committed

**GATE: B1.3 — providers visible in Configuration**

---

## Batch 1 — Phase B1.4: Parity Seed Data + UI/Menu Verification
### Build
- [ ] Seed 3 agents (IPAI Agent, Ask AI, Livechat AI Agent)
- [ ] Seed 3 topics (View Builder, Information Retrieval, Create Leads)
- [ ] Link topics to appropriate tools

### Verification
- [ ] Combined install: `ipai_ai_agent_builder,ipai_ai_core,ipai_ai_prompts` — 0 errors
- [ ] Menus exist: Agents, Topics, Configuration, Default Prompts (assert >= 4)
- [ ] Seed prompts: 10 records exist (ORM query)
- [ ] Prompt list + form render cleanly

### Evidence
- [ ] ORM verification output committed
- [ ] Evidence artifact in `docs/evidence/`

**GATE: B1.4 — Odoo AI parity verified**

---

# Batch 2: Copilot MVP

## Phase 0: Spec Normalization
### Build
- [x] constitution.md — 10 rules locked
- [x] prd.md — taxonomy, scope, non-goals
- [x] plan.md — tightened 6-phase execution order
- [x] tasks.md — split by category with gates

### Verification
- [x] Spec bundle internally consistent
- [x] Naming confirmed: Odoo Copilot / AI / ipai_ai_*

---

## Phase 1: Core Repair + Bridge (Slice A — Install Verification)
### Build
- [x] Fix `ipai_ai_rag` dependency (ipai_ai_agent_builder → ipai_ai_core, v19.0.1.0.0)
- [x] Fix `ipai_ai_rag` model refs (agent_id → provider_id, Odoo 19 view compat)
- [x] Create `ipai_ai_oca_bridge` module (provider routing glue)
- [x] Add `search_knowledge` readonly tool to copilot
- [x] Fix `ipai_ai_copilot` cron (remove `numbercall`, fix eval — Odoo 19 compat)

### Integration
- [x] Wire `ipai_ai_copilot` tool registry (18 tools declared in XML with handlers)
- [ ] Wire `ipai_ai_copilot` → `ipai_ai_oca_bridge` → provider stack
- [ ] Verify bridge payload reaches Supabase Edge Function

### Verification
- [x] `ipai_ai_core` installs cleanly (`--stop-after-init`)
- [x] `ipai_ai_rag` installs cleanly (`--stop-after-init`)
- [x] `ipai_ai_copilot` installs cleanly (`--stop-after-init`)
- [x] Combined install (core + rag + copilot) — 32 modules, 0 errors

### Evidence
- [x] Install verification passed 2026-03-11 in devcontainer

**GATE: Phase 1 install verification — PASSED.**

---

## Phase 2: In-App Functional Proof (Slice A Gate)

### Acceptance Criteria
- Odoo starts with HTTP enabled in devcontainer
- Copilot UI surface is reachable in Odoo backend
- One readonly tool executes successfully from the UI
- Request runs under standard Odoo user context (no sudo escalation)
- No traceback in server logs
- Evidence captured

### Verification
- [ ] Module install proof (carried from Phase 1)
- [ ] Odoo HTTP server starts and serves /web
- [ ] Copilot endpoint responds at /ipai/copilot/chat
- [ ] One readonly tool (search_records or get_pipeline_summary) executes
- [ ] Response returns valid JSON with no traceback
- [ ] Permission/context proof (tool runs as logged-in user)

### Evidence
- [ ] curl output or HTTP response committed
- [ ] Server log excerpt committed
- [ ] Evidence artifact in `docs/evidence/`

**GATE: Phase 2 must pass before Phase 3 begins.**

---

## Phase 3: n8n Router + Slack Ingress (Slice B)
### Build
- [x] Supabase migration: `kb.channel_identity_map`
- [x] Edge Function: `copilot-classify-intent`
- [x] n8n AI Agent Router workflow
- [x] Slack inbound controller on `ipai_slack_connector`

### Integration
- [ ] Identity resolution: Slack user → Odoo user via Supabase
- [ ] Intent classification → RAG/navigation/transaction routing
- [ ] Callback response to Slack

### Verification
- [ ] Slack message reaches n8n webhook
- [ ] Identity resolves correctly
- [ ] Readonly question returns answer in Slack
- [ ] No business action executed without identity

### Evidence
- [ ] n8n execution log
- [ ] Slack message screenshot/curl
- [ ] Evidence note committed

**GATE: Phase 3 must pass before Phase 4 begins.**

---

## Phase 4: Teams Adapter (Slice C)
### Build
- [x] Azure Bot Service registration script
- [x] n8n Teams adapter workflow
- [x] Azure Bot Service contract doc

### Integration
- [ ] Bot Framework JWT validation
- [ ] AAD Object ID → Odoo user resolution
- [ ] Same readonly flow as Slack

### Verification
- [ ] Teams message reaches n8n webhook
- [ ] Identity resolves correctly
- [ ] Readonly question returns answer in Teams

### Evidence
- [ ] Bot registration proof
- [ ] Teams message flow evidence
- [ ] Evidence note committed

**GATE: Phase 4 must pass before Phase 6 begins.**

---

## Phase 5: BIR RAG Ingestion + Readonly Tooling
### Build
- [x] Supabase migration: BIR document types
- [x] Edge Function: `bir-ingest`
- [x] n8n scheduled workflow: BIR ingestion pipeline
- [x] Copilot tool: `bir_compliance_search` (readonly, citation-first)

### Integration
- [ ] BIR docs ingested into Supabase pgvector
- [ ] `bir_compliance_search` tool returns cited results
- [ ] Results include issuance number, title, effective date

### Verification
- [ ] RAG search returns relevant BIR content
- [ ] Citations are accurate and include source metadata
- [ ] Tool works from Odoo UI and from Slack (after Phase 3)

### Evidence
- [ ] Sample RAG query results committed
- [ ] Evidence note committed

---

## Phase 6: Transactional Actions / Approvals (Deferred)
### Prerequisites
- [ ] Phase 1-5 all verified
- [ ] Gap analysis: does `mail.activity` cover the workflow?

### Build
- [x] Module: `ipai_ai_channel_actions` (thin mixin)
- [x] n8n channel action workflow
- [x] Edge Function: `action-card-builder`
- [x] Copilot tools: `list_pending_activities`, `execute_activity`

### Integration
- [ ] Interactive message sent to Slack/Teams
- [ ] Button callback executes Odoo action under resolved user
- [ ] Confirmation flow works end-to-end

### Verification
- [ ] Action runs under correct Odoo user context
- [ ] Permission denied for wrong user
- [ ] Audit envelope emitted for every execution

### Evidence
- [ ] Action execution logs committed
- [ ] Evidence note committed

**GATE: Phase 6 passes only with user context + audit proofs.**
