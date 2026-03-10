# Odoo Copilot — Implementation Plan

## Execution Order (Tightened)

Narrow verified slices. Each phase ends with a hard verification gate.
No phase begins until the prior gate passes.

---

## Batch 0: OCA Platform Baseline

### Phase B0.A: Platform Baseline Install
- Install 13 core OCA modules in disposable test DB (`test_oca_b0`):
  `queue_job`, `password_security`, `auditlog`, `base_name_search_improved`,
  `date_range`, `web_dialog_size`, `web_environment_ribbon`, `web_m2x_options`,
  `web_responsive`, `report_xlsx`, `disable_odoo_online`, `remove_odoo_enterprise`,
  `mail_debrand`
- Classify any failures per testing policy (env issue / migration gap / real defect)
- Known risk: `disable_odoo_online` + `remove_odoo_enterprise` may not exist on 19.0 if absorbed into CE core — mark conditional
- **GATE**: All available modules install; failures classified and documented

### Phase B0.B: Productivity Enhancements (Optional)
- Install additional UX modules where active use case exists:
  `server_action_mass_edit`, `web_listview_range_select`, `web_refresher`,
  `web_search_with_and`, `web_tree_many2one_clickable`, `mail_tracking`
- These are already in `baseline_optional_ux` profile in the manifest
- **GATE**: Modules install; no regressions on baseline

### Phase B0.C: OCA AI Compatibility Layer
- Verify `ai_oca_bridge` installs on Odoo 19 (source is 18.0 — requires port-and-verify)
- Optionally verify `ai_oca_bridge_extra_parameters` for payload enrichment
- This is a prerequisite for Batch 1 provider routing
- **GATE**: `ai_oca_bridge` installs cleanly or failure classified as migration gap

### Batch 0 → Batch 1 Promotion
- Promote verified Batch 0 modules to dev DB (`odoo_dev`)
- Document any modules skipped with classification
- Evidence → `docs/evidence/YYYYMMDD-HHMM/oca-batch0/`

---

## Batch 1: Official Odoo AI Foundation

### Phase B1.1: Agent Builder Verification
- Verify `ipai_ai_agent_builder` installs cleanly in devcontainer
- Verify agent form, topic inline editing, tool registry all render
- Verify Settings page (LLM providers) renders
- **GATE**: Install + form load + settings page verified

### Phase B1.2: Prompt Registry Module
- Create `ipai_ai_prompts` module with `ipai.ai.prompt` model
- Depends on `ipai_ai_agent_builder`
- Add views: tree, form
- Add menu item under AI Agents > Configuration > Default Prompts
- Add security (reuses existing IPAI AI groups)
- Seed 10 default prompts matching official Odoo AI structure
- **GATE**: Module installs, prompt CRUD works from UI

### Phase B1.3: Provider Verification
- Verify `ipai_ai_core` providers work
- Providers menu visible under AI Agents > Configuration > Providers
- Seed provider records (ChatGPT, Gemini) if not present
- **GATE**: Providers visible in Configuration menu

### Phase B1.4: Parity Seed Data + UI/Menu Verification
- Seed 3 agents: IPAI Agent (general), Ask AI (information), Livechat AI Agent (customer-facing)
- Seed 3 topics: View Builder, Information Retrieval, Create Leads
- Verify complete menu structure: Agents | Topics | Configuration > Default Prompts / Providers
- Verify 10 seed prompt records exist and render
- **GATE**: Menu structure matches official Odoo AI; data loads; UI renders cleanly

### Official Odoo AI Prompt Registry Pattern

The implementation mirrors the official Odoo AI prompt registry model:
- Each prompt rule has a name
- A contextual trigger (`when_users_need_to`)
- Instructions
- An assigned agent
- A button label (`button_prompt`)
- A target context (mail_composer, text_selector, chatter, etc.)

This prompt registry is part of Batch 1 and is not deferred to Batch 2.

---

## Batch 2: Copilot MVP

### Phase 0: Spec Normalization
- Lock constitution, prd, plan, tasks as SSOT
- Confirm naming taxonomy

### Phase 1: Core Repair + Bridge (Slice A — In-App Only)
- Repair `ipai_ai_rag` (fix broken dependency → `ipai_ai_core`)
- Add `ipai_ai_oca_bridge` (provider routing glue)
- Wire `ipai_ai_copilot` to provider stack via bridge
- Add one readonly tool: `search_knowledge` (RAG path)
- **GATE**: Verify full in-app Odoo Copilot flow end-to-end from Odoo UI

### Phase 2: Odoo Copilot In-App Verification
- Module install proof (`--stop-after-init`)
- Functional proof from Odoo UI
- Permission/context proof
- Evidence artifact committed

### Phase 3: n8n Router + Slack Ingress (Slice B)
- Supabase migration: `kb.channel_identity_map`
- n8n AI Agent Router workflow
- Slack inbound controller (thin relay)
- One readonly Slack question flow end-to-end
- **GATE**: Slack readonly flow works with correct identity resolution

### Phase 4: Teams Adapter (Slice C)
- Azure Bot Service registration (F0 free tier)
- n8n Teams adapter workflow
- Same readonly question flow, same identity resolution
- **GATE**: Teams readonly flow verified

### Phase 5: BIR RAG Ingestion + Readonly Tooling
- Supabase migration: BIR document types
- Edge Function: bir-ingest (chunk + embed + store)
- n8n scheduled ingestion pipeline
- Copilot tool: `bir_compliance_search` (citation-first, readonly)
- **GATE**: BIR RAG returns cited results from Odoo UI and Slack

### Phase 6: Transactional Actions / Approvals (Deferred)
- Only after Phases 1-5 verified
- Gap analysis: can `mail.activity` cover the workflow?
- If yes: thin `ipai_ai_channel_actions` mixin only
- If no: document gap, design minimal domain model
- **GATE**: Action execution from channel with correct user context

## Dependencies (Strict Sequential)

```
Phase 0 ← GATE
Phase 1 ← Phase 0
Phase 2 ← Phase 1 (verification only)
Phase 3 ← Phase 2 passes
Phase 4 ← Phase 3 passes
Phase 5 ← Phase 3 passes (can parallel with Phase 4)
Phase 6 ← Phase 3 + 4 + 5 all pass
```

## Naming Convention
- Product: Odoo Copilot
- Platform family: AI
- Internal namespace: `ipai_ai_*`
- Spec slug: `odoo-copilot`
