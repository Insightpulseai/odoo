# Odoo Copilot — Product Requirements Document

## Product Taxonomy

- **Product name**: Odoo Copilot
- **Platform family**: AI
- **Technical namespace**: `ipai_ai_*`
- **Main assistant module**: `ipai_ai_copilot`

## Product Vision
Build Odoo Copilot for Odoo CE 19, implemented on top of the IPAI AI platform. Provides informational (RAG), navigational (deep links), and transactional (business action execution) capabilities across Odoo sidebar, Slack, and Teams.

## Batch Strategy

### Batch 0: OCA Platform Baseline
Harden CE with the OCA must-have layer before adding any AI modules:
- **Security**: `password_security`, `auditlog` — password policy + audit trail
- **Infrastructure**: `queue_job` — background job processing for async AI calls
- **UX**: `web_responsive`, `web_dialog_size`, `web_environment_ribbon`, `web_m2x_options` — operator productivity
- **Reporting**: `report_xlsx`, `date_range` — Excel export + reusable date ranges
- **CE Cleanup**: `disable_odoo_online`, `remove_odoo_enterprise`, `mail_debrand` — remove EE upsell noise
- **Search**: `base_name_search_improved` — better name_search across models

All 13 modules are OCA community modules already declared in `config/addons.manifest.yaml` (tiers 0-6) and cloned via git-aggregator. No custom ipai_* modules needed.

**Gate**: All 13 install cleanly via `--stop-after-init` on a disposable test DB.

### Batch 1: Official Odoo AI Foundation
Achieve parity with the official Odoo 19 AI app structure:
- **Agents**: Configurable AI assistants (IPAI Agent, Ask AI, Livechat AI Agent)
- **Topics**: Instruction bundles with tool groups (View Builder, Information Retrieval, Create Leads)
- **Providers**: Multi-provider config (ChatGPT, Gemini) via `ipai_ai_core`
- **Default Prompts**: Contextual prompt registry for embedded AI helpers via `ipai_ai_prompts`

Foundation modules: `ipai_ai_agent_builder` (agents + topics + tools), `ipai_ai_core` (providers), `ipai_ai_prompts` (prompt registry).

Default Prompts are a first-class Batch 1 layer. Official Odoo AI is not just chat/agents — it is contextual prompt-driven helpers embedded into mail, chatter, file viewer, text selection, and other workflow surfaces.

### Batch 2: Copilot MVP
Extend the foundation with the full Odoo Copilot product:
- Copilot sidebar + palette in Odoo
- RAG over approved knowledge sources
- Slack ingress (thin relay to n8n)
- Teams ingress (via Azure Bot Service)
- BIR compliance RAG
- Transactional actions / approvals

### MVP Tenant Scope
- Platform owner: InsightPulseAI
- Operating company / tenant: TBWA\SMP
- MVP project: `MVP – Odoo Copilot + Finance PPM`
- Initial visibility: invited internal users

## Scope

### In Scope
- Official Odoo 19 AI structure parity (Agents, Topics, Providers, Default Prompts)
- Copilot chat surface in Odoo (sidebar + palette)
- Provider routing via `ipai_ai_core` + `ipai_ai_oca_bridge`
- RAG over approved knowledge sources (BIR tax compliance, company docs)
- Slack ingress (thin relay to n8n)
- Teams ingress (via Azure Bot Service → n8n)
- Transactional actions only through explicit tool contracts with user confirmation

### Non-Goals
- No new approval engine unless gap analysis proves `mail.activity` cannot cover the workflow
- No orchestration logic embedded in Odoo controllers
- No raw channel-specific business logic in Odoo
- No Enterprise module dependencies

## User Stories

### US-1: Odoo Sidebar Copilot
As an Odoo user, I can interact with the AI copilot sidebar to search records, get summaries, and execute business actions with confirmation.

### US-2: Knowledge Search (RAG)
As a user, I can ask questions and receive citation-first answers with source metadata from approved knowledge bases.

### US-3: Slack Channel Integration
As a Slack user, I can message the copilot bot to query Odoo data and get BIR compliance answers — without leaving Slack.

### US-4: Teams Channel Integration
As a Teams user, I can interact with the copilot via Azure Bot Service to perform the same operations available in Slack.

### US-5: Channel-to-Business-Action (Deferred)
As a manager, I can approve purchase orders and complete activities from Slack/Teams interactive messages. *Deferred until readonly flows are proven stable.*

## Non-Functional Requirements
- Response latency: < 5s for informational, < 10s for transactional
- Identity mapping: Platform users must be resolved to Odoo users before any action
- Audit: All tool executions logged with trace_id, user_id, timestamp
- CE-only: Zero Enterprise module dependencies
- Citations: RAG responses include source document metadata

## Architecture
- **Odoo**: Thin adapter (tools, permissions, deep links, business actions)
- **n8n**: Orchestrator (conversation state, retries, routing, channel callbacks)
- **Supabase**: Data layer (pgvector RAG, identity mapping, Edge Functions for AI)
