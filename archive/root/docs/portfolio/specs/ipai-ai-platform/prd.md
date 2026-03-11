# PRD - IPAI AI Platform for Odoo CE/OCA 18

## Product Overview

IPAI AI Platform delivers a **Notion Business-equivalent** experience on Odoo CE/OCA 18:

| Notion Business Feature | IPAI Implementation |
|------------------------|---------------------|
| AI Agent | `ipai_ai_core` + `ipai_ai_agents_ui` |
| Teamspaces | `ipai_workspace_core` + Odoo Projects |
| Workspaces | Multi-company or DB-per-tenant |
| Integrations | `ipai_ai_connectors` + n8n |
| Connected Search | Supabase KB + RAG retrieval |
| Private Spaces | Record rules + security groups |

---

## Problem Statement

### Current Challenges

1. **Fragmented AI Experience**: No native AI assistant in Odoo CE
2. **No Unified Workspace**: Projects, docs, and chat scattered across modules
3. **Integration Complexity**: External tool connections require custom development
4. **Documentation Drift**: Architecture docs become stale
5. **Test Coverage Gaps**: Inconsistent testing practices

### Target Outcomes

1. **Unified AI Assistant**: Context-aware help across all Odoo modules
2. **Workspace Cohesion**: Project + Docs + Chat in unified "spaces"
3. **Integration Hub**: n8n-first approach with minimal Odoo surface
4. **Living Documentation**: CI-enforced documentation accuracy
5. **Comprehensive Testing**: Unit, integration, and E2E coverage

---

## Goals

### G1: AI Agent Experience (Notion AI Parity)

- Ask AI panel with context-aware responses
- Evidence-grounded answers with citations
- Read-only tool access (search, open views, explain records)
- Confidence scoring and uncertainty handling

### G2: Workspace Organization (Teamspaces)

- Spaces = Project + Docs Folder + Discuss Channel
- Private/public visibility controls
- Member management with RBAC

### G3: Integration Hub

- Inbound event intake endpoint
- n8n-first integration pattern
- External content indexing to KB

### G4: Documentation & Testing

- Complete DBML/ERD for data model
- OpenAPI specs for all endpoints
- Comprehensive test suites
- CI/CD pipelines

---

## Non-Goals

- Full Notion editor replacement (use existing Odoo views)
- Real-time collaboration (use Odoo's native patterns)
- Custom ML model training
- Mobile-native apps (web-responsive only)

---

## Personas

### P1: Knowledge Worker (End User)

- Uses Ask AI daily for workflow questions
- Accesses documents and tasks within spaces
- Expects fast, accurate responses with sources

### P2: Knowledge Manager (Admin)

- Curates AI sources and prompts
- Manages space membership and permissions
- Reviews AI usage analytics

### P3: Platform Engineer (Ops)

- Deploys and monitors the platform
- Configures integrations via n8n
- Manages secrets and infrastructure

### P4: Integration Developer

- Builds n8n workflows for external systems
- Uses connector endpoint for event intake
- Indexes external content to KB

---

## User Stories

### US1: Ask AI Panel

```gherkin
Feature: Ask AI Panel
  As a knowledge worker
  I want to ask questions in a chat panel
  So that I get context-aware answers about my Odoo workflows

  Scenario: Basic question answering
    Given I am logged into Odoo
    When I press Alt+Shift+F
    Then the Ask AI panel opens
    And I can type a question
    And I receive an answer with citations

  Scenario: Confidence display
    Given I ask a question with limited evidence
    When the AI responds
    Then I see a confidence indicator
    And uncertain answers are clearly marked

  Scenario: Citation navigation
    Given I receive an answer with citations
    When I click a citation link
    Then I am taken to the source (URL or Odoo record)
```

### US2: Workspace Spaces

```gherkin
Feature: Workspace Spaces
  As an admin
  I want to create private spaces for teams
  So that work is organized and access-controlled

  Scenario: Create private space
    Given I am a space admin
    When I create a new space with private visibility
    Then only invited members can see the space contents

  Scenario: Space components
    Given I create a space
    Then it includes a project, doc folder, and discuss channel
    And all components share the same access rules
```

### US3: Integration Events

```gherkin
Feature: Integration Events
  As an integration developer
  I want to push events from external systems
  So that Odoo can react to external triggers

  Scenario: GitHub event intake
    Given I configure a GitHub webhook to call /ipai_ai_connectors/event
    When a push event occurs
    Then the event is logged in ipai.ai.event
    And optionally triggers downstream actions
```

### US4: Knowledge Indexing

```gherkin
Feature: Knowledge Indexing
  As a knowledge manager
  I want Odoo content indexed to the KB
  So that AI can answer questions about our data

  Scenario: Task indexing
    Given I have project tasks in Odoo
    When the exporter cron runs
    Then task content is upserted to kb.chunks
    And Ask AI can retrieve relevant tasks
```

---

## Functional Requirements

### F1: AI Agent Runtime (Odoo Backend)

#### Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/ipai_ai/bootstrap` | POST | Session | List agents, user context |
| `/ipai_ai/ask` | POST | Session | RAG + LLM answer |
| `/ipai_ai/feedback` | POST | Session | Submit rating |
| `/ipai_ai_connectors/event` | POST | Token | Inbound event intake |

#### Data Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ipai.ai.provider` | Provider config | name, provider_type, is_default |
| `ipai.ai.thread` | Conversation | provider_id, user_id, state |
| `ipai.ai.message` | Message log | thread_id, role, content, confidence |
| `ipai.ai.citation` | Source reference | message_id, title, url, snippet |
| `ipai.ai.event` | Integration event | source, event_type, payload_json |
| `ipai.ai.prompt` | Prompt template | name, template, variables |
| `ipai.ai.audit` | Operation audit | operation, request, response |

### F2: React + Fluent UI Panel

#### Components

| Component | Purpose |
|-----------|---------|
| `App` | Root with FluentProvider theming |
| `Header` | Agent selector, theme toggle |
| `MessageList` | Conversation display |
| `MessageCard` | Individual message with citations |
| `Composer` | Input with send button |
| `CitationList` | Source references |
| `FeedbackButtons` | Thumbs up/down |

#### Interactions

- **Keyboard**: Alt+Shift+F opens panel
- **Theme**: Light/dark toggle preserved in localStorage
- **Agent Selection**: Dropdown changes active provider
- **New Chat**: Resets thread context

### F3: Supabase KB

#### Schema

```sql
-- kb.chunks table
CREATE TABLE kb.chunks (
  id BIGSERIAL PRIMARY KEY,
  tenant_ref TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  title TEXT,
  url TEXT,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (tenant_ref, source_type, source_ref)
);
```

#### RPCs

| RPC | Purpose | Parameters |
|-----|---------|------------|
| `kb.search_chunks` | Vector search | tenant_ref, query_embedding, limit |
| `kb.search_chunks_text` | Text fallback | tenant_ref, query, limit |

### F4: Workspace Spaces

#### Space Model

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ipai.workspace` | Space container | name, visibility, company_id |
| `ipai.workspace.member` | Membership | workspace_id, user_id, role |

#### Components per Space

- **Project**: `project.project` linked to workspace
- **Document Folder**: `documents.folder` or `document.page` category
- **Discuss Channel**: `mail.channel` linked to workspace

---

## Non-Functional Requirements

### NFR1: Security

- Record rules enforce tenant isolation
- Token validation on public endpoints
- Audit logging for all AI operations
- PII redaction at boundaries

### NFR2: Performance

| Metric | Target |
|--------|--------|
| Ask latency P95 | < 5s |
| Bootstrap latency | < 500ms |
| KB retrieval | < 500ms |
| UI interactions | < 100ms |

### NFR3: Reliability

- Graceful degradation on service failures
- Retry logic with exponential backoff
- Circuit breakers for external services
- Health check endpoints

### NFR4: Observability

- Structured JSON logging
- Correlation IDs across services
- Metrics for latency, errors, throughput
- Dashboard for AI usage analytics

---

## Technical Architecture

### High-Level Flow

```
User → Odoo Webclient → React Panel → /ipai_ai/ask
                                          ↓
                            Odoo Controller
                                          ↓
                    ┌─────────────────────┴─────────────────────┐
                    ↓                                           ↓
            KB Retrieval (Supabase)                    LLM Provider
                    ↓                                           ↓
            Evidence Chunks                            Generated Answer
                    └─────────────────────┬─────────────────────┘
                                          ↓
                              Formatted Response
                                          ↓
                              React Panel (Citations)
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Odoo CE 18 + OCA                         │
├─────────────────────────────────────────────────────────────────┤
│  ipai_ai_agents_ui (React + Fluent UI)                         │
│    └── Mount in client action via web.assets_backend            │
├─────────────────────────────────────────────────────────────────┤
│  ipai_ai_core (Python)                                          │
│    ├── Provider Registry                                        │
│    ├── Thread/Message Persistence                               │
│    ├── Service Layer (RAG orchestration)                        │
│    └── HTTP Controllers                                         │
├─────────────────────────────────────────────────────────────────┤
│  ipai_ai_connectors (Python)                                    │
│    └── Event intake endpoint                                    │
├─────────────────────────────────────────────────────────────────┤
│  ipai_ai_sources_odoo (Python)                                  │
│    └── Cron exporter to Supabase KB                            │
├─────────────────────────────────────────────────────────────────┤
│  ipai_workspace_core (Python)                                   │
│    └── Workspace/Space model + membership                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                    Supabase (External)                          │
│  ├── kb.chunks (pgvector)                                       │
│  └── RPCs (search_chunks, search_chunks_text)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ Webhooks
┌─────────────────────────────────────────────────────────────────┐
│                         n8n                                     │
│  └── Integration workflows (GitHub, Slack, etc.)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Metrics

| Metric | Target | Baseline |
|--------|--------|----------|
| Weekly Active AI Users | 30% of total users | 0% |
| Answers with Citations | > 95% | N/A |
| User Satisfaction | > 70% helpful ratings | N/A |
| Response Latency P95 | < 5s | N/A |
| Error Rate | < 1% | N/A |
| Test Coverage | > 80% | ~40% |

---

## Rollout Plan

### Phase 1: Foundation (Week 1-2)

- Complete spec kit documentation
- DBML/ERD for all models
- OpenAPI specs for endpoints
- Comprehensive test framework

### Phase 2: Core AI (Week 3-4)

- Enhanced AI panel with full features
- Provider abstraction layer
- Citation rendering improvements
- Confidence scoring

### Phase 3: Workspaces (Week 5-6)

- Workspace model + membership
- Space creation wizard
- Linked project/docs/channel
- Access control rules

### Phase 4: Integrations (Week 7-8)

- Connector endpoint hardening
- n8n workflow templates
- External content indexing
- Analytics dashboard

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM Provider Downtime | High | Multi-provider fallback |
| Supabase Rate Limits | Medium | Caching, batching |
| Large Data Volumes | Medium | Chunking, pagination |
| Security Vulnerabilities | High | Security audits, pen testing |
| Documentation Drift | Medium | CI validation gates |

---

*Last updated: 2025-01-06*
