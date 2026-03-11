# PRD — IPAI AI Platform for Odoo CE/OCA 18

## Product Summary

IPAI AI Platform is a comprehensive AI layer for Odoo CE/OCA 18 that brings Notion-style "Ask AI" capabilities and Kapa.ai-inspired documentation intelligence to the Odoo ecosystem. Built with React + Fluent UI v9 for modern UX and Supabase pgvector for RAG retrieval.

## Problem Statement

Odoo CE/OCA deployments need:

1. **Modern AI Assistant** - Users expect ChatGPT-style help within their ERP
2. **Consistent UI Shell** - Need Fluent UI design system for platform modules
3. **Knowledge Integration** - Documentation, tasks, and discussions should inform AI responses
4. **Integration Plumbing** - Connect external systems (GitHub, Slack, n8n) without enterprise lock-in
5. **Deterministic Architecture** - Ship confidently with docs, tests, and contracts

## Goals (MVP)

1. Provide a **Fluent UI React "platform shell"** for AI and future IPAI apps
2. Provide **AI Agents with evidence-grounded answers** and citations
3. Provide **teamspace/workspace-style organization** using Odoo primitives
4. Provide **integrations hub** (n8n-first) with minimal Odoo surface area
5. Provide **comprehensive testing, architecture, DBML/ERD, and API docs**

## Non-Goals (MVP)

- Full ticketing system replacement (only escalation hooks)
- Full multi-lingual rewriting workflows (basic multi-language retrieval ok)
- Enterprise SSO breadth (support basic SSO later; MVP uses Odoo auth)
- Replacing all Odoo views with React (keep OWL for standard views)

## Target Users

| Persona | Role | Needs |
|---------|------|-------|
| **Admin** | System administrator | Config sources, policies, agent permissions |
| **Knowledge Manager** | Content curator | Curates sources, monitors gaps, updates docs |
| **Operator** | Daily user | Uses Ask AI in workflows, gets contextual help |
| **Integration Engineer** | Developer | Connects GitHub/Slack/n8n, monitors events |
| **Platform Engineer** | DevOps | Deploys, monitors, upgrades, manages infra |

## User Stories

### AI Agents

- **US-AI-001**: As a user, I open "Ask AI (Fluent UI)" from the command palette (Ctrl+K) and ask questions about workflows and records.
- **US-AI-002**: As an admin, I define agents with custom prompts, allowed tools, and sources.
- **US-AI-003**: As a user, I see citations with my answers and can click to view sources.
- **US-AI-004**: As a user, when AI is uncertain, I see a clear indication and option to escalate.

### Teamspaces/Workspaces

- **US-TS-001**: As an admin, I create a "Space" (project + doc folder + channel) with private membership.
- **US-TS-002**: As a user, I only see spaces I belong to.
- **US-TS-003**: As a space manager, I can add/remove members and set permissions.

### Integrations

- **US-INT-001**: As an integration engineer, I push events from n8n/GitHub to Odoo via one secured endpoint.
- **US-INT-002**: As a platform engineer, I can replay/inspect inbound events in the admin console.
- **US-INT-003**: As an admin, I see integration status and error logs.

### Knowledge Indexing

- **US-KB-001**: As an admin, I enable an exporter cron that pushes Odoo tasks/KB pages to Supabase KB.
- **US-KB-002**: As a knowledge manager, I see indexing status and last sync times.
- **US-KB-003**: As an admin, I can trigger manual reindex for specific sources.

## Functional Requirements

### F1: Fluent UI React Shell Inside Odoo

- React v18 + Fluent UI v9 bundle loaded via `web.assets_backend`
- Client action mounts the React app using Odoo session auth (same-origin)
- Command palette entry (Alt+Shift+F) opens the panel
- Theme switching (light/dark) with persistence
- Build outputs committed as IIFE bundle for deterministic deploys

### F2: AI Agent Runtime (Odoo)

**Endpoints:**

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `/ipai_ai_agents/bootstrap` | Odoo session | List agents available for company |
| `/ipai_ai_agents/ask` | Odoo session | Store thread + retrieve evidence + call LLM + store answer |
| `/ipai_ai_agents/feedback` | Odoo session | Submit user feedback on answers |

**Data Models (extending ipai_ai_core):**

- `ipai.ai.agent` - Agent configuration (prompt, model, policies)
- `ipai.ai.thread` - Conversation threads (inherits mail.thread)
- `ipai.ai.message` - Messages with citations + confidence
- `ipai.ai.source` - Source registry metadata

### F3: Connector Intake (Odoo)

**Endpoint:** `/ipai_ai_connectors/event` (token-protected, CSRF disabled)

**Payload:**
```json
{
  "token": "shared_secret",
  "source": "n8n|github|slack",
  "event_type": "issue.created|task.updated|...",
  "ref": "external_id",
  "payload": { ... }
}
```

**Persistence:** `ipai.ai.event` table with audit trail

### F4: Odoo → Supabase KB Export

**Cron Job:** Every 15 minutes (configurable)

**Sources:**
- `project.task` - Tasks with description, stage, project context
- `document.page` - Knowledge base articles (if OCA knowledge installed)
- `mail.message` - Scoped messages (optional)

**Upsert Logic:**
- Unique key: `(tenant_ref, source_type, source_ref)`
- Update `updated_at` on change
- Skip unchanged records (hash comparison)

### F5: Supabase KB Schema

**Table:** `kb.chunks`

| Column | Type | Purpose |
|--------|------|---------|
| id | bigserial | Primary key |
| tenant_ref | text | Company identifier (`odoo_company:<id>`) |
| source_type | text | `odoo_task`, `odoo_kb`, `github`, etc. |
| source_ref | text | Stable ID (`project.task:123`) |
| title | text | Document title |
| url | text | Deep link to source |
| content | text | Chunk content |
| embedding | vector(1536) | OpenAI embedding |
| updated_at | timestamptz | Last modification |

**RPCs:**
- `kb.search_chunks(tenant_ref, query_embedding, limit)` - Vector search
- `kb.search_chunks_text(tenant_ref, query, limit)` - Text fallback

## Non-Functional Requirements

### Security

- Read-only by default; strict record rules for threads/messages
- User can only access their own threads
- Company-scoped agent visibility
- Token-protected connector endpoint

### Reliability

- No silent failures; surface error states in UI
- Graceful degradation when Supabase/LLM unavailable
- Retry logic with exponential backoff for external calls

### Observability

- Structured logs with correlation IDs
- Event table for audit trail
- Latency metrics per provider

### Compatibility

- Odoo 18 CE + OCA modules
- Minimal dependencies (base, web, mail, project)
- Python 3.10+ / Node 18+

### Performance

- P95 response time < 5s (cached < 2s)
- Cache embeddings (optional)
- Fast text fallback when embeddings unavailable

### Deterministic Builds

- React bundle committed to repo
- CI verifies bundle matches source
- No dynamic CDN dependencies

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Adoption | 50% of active users try Ask AI in week 1 | Analytics |
| Utility | 70% "helpful" rating on answered questions | Feedback |
| Reliability | < 1% error rate for ask calls | Monitoring |
| Index freshness | > 99% exporter run success rate | Cron logs |
| Citation coverage | > 95% answers with valid citation | Answer analysis |

## Module Inventory (Minimal IPAI Custom)

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `ipai_ai_core` | Existing - Provider registry, threads, messages | base, mail, web |
| `ipai_agent_core` | Existing - Skills, tools, knowledge | base, web |
| `ipai_ai_agents_ui` | **NEW** - React + Fluent UI panel | web, ipai_ai_core |
| `ipai_ai_connectors` | **NEW** - Inbound event intake | base, mail |
| `ipai_ai_sources_odoo` | **NEW** - KB exporter | base, project |

## Dependencies (OCA-First)

- `server-tools/queue_job` - Optional but recommended for async
- `knowledge/document_page` - Optional for KB articles
- `project` - Core project module for tasks

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IPAI AI Platform                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │ React+Fluent │    │ Odoo Backend │    │    Supabase KB       │   │
│  │   UI Panel   │◄──►│  (AI Core)   │◄──►│   (pgvector RAG)     │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
│         │                   │                      ▲                 │
│         │                   │                      │                 │
│         ▼                   ▼                      │                 │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────┴────────────┐   │
│  │   Command    │    │  Connector   │    │   Exporter Cron      │   │
│  │   Palette    │    │   Endpoint   │    │ (Tasks/KB → Chunks)  │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
│                             ▲                                        │
│                             │                                        │
│  ─────────────────────────────────────────────────────────────────  │
│                             │                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │     n8n      │    │   GitHub     │    │       Slack          │   │
│  │  Workflows   │───►│   Webhooks   │    │       Bot            │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Deployment Targets

- **Current:** DigitalOcean Droplet + Docker
- **Container:** `odoo-erp-prod` (Odoo web + workers)
- **Database:** `db` container (PostgreSQL)
- **KB Store:** Supabase (external, managed)
- **Future:** DOKS/K8s optional, same container images

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Embeddings provider downtime | AI fallback to text search | Implement text RPC fallback |
| Large chatter/task data | Slow exports, storage costs | Chunking, size caps, incremental sync |
| Odoo UI constraints | Limited React integration | Keep React in bounded client action |
| Multi-tenant RLS mistakes | Data leakage | Policy tests + CI checks |

## Rollout Plan

### Phase 1: Core (Week 1-2)
- React panel with Fluent UI
- Bootstrap + Ask endpoints
- Basic citations rendering

### Phase 2: Integration (Week 2-3)
- Connector endpoint
- Event viewer
- KB exporter cron

### Phase 3: Polish (Week 3-4)
- Feedback loop
- Theme switching
- Comprehensive tests

### Phase 4: Documentation (Week 4)
- Architecture docs
- DBML/ERD
- OpenAPI specs
- CI gates

## References

- Kapa.ai docs: https://docs.kapa.ai
- Fluent UI React: https://react.fluentui.dev
- Supabase pgvector: https://supabase.com/docs/guides/ai
- Odoo OWL framework: https://www.odoo.com/documentation/18.0/developer/reference/frontend/owl.html
