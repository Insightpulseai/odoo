# Plan - IPAI AI Platform for Odoo CE/OCA 18

## Architecture Overview

### Container Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DigitalOcean Droplet                           │
│                          159.223.75.148                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │   odoo-erp-prod │    │    postgres     │    │    redis        │    │
│   │   Port: 8069    │───▶│   Port: 5432    │    │   Port: 6379    │    │
│   │                 │    │   DB: odoo      │    │   (optional)    │    │
│   └────────┬────────┘    └─────────────────┘    └─────────────────┘    │
│            │                                                            │
│            │ HTTPS                                                      │
│            ▼                                                            │
│   ┌─────────────────┐                                                   │
│   │     nginx       │                                                   │
│   │   (reverse      │                                                   │
│   │    proxy)       │                                                   │
│   └────────┬────────┘                                                   │
│            │                                                            │
└────────────┼────────────────────────────────────────────────────────────┘
             │
             ▼ HTTPS
┌─────────────────────────────────────────────────────────────────────────┐
│                         External Services                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │    Supabase     │    │       n8n       │    │  LLM Provider   │    │
│   │   (KB + Auth)   │    │  (Integrations) │    │ (OpenAI/Claude) │    │
│   │   spdtwktx...   │    │  n8n.insight... │    │                 │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Database Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Odoo PostgreSQL (odoo)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │  ipai_ai_       │    │   ipai_ai_      │    │   ipai_ai_      │    │
│   │  provider       │───▶│   thread        │───▶│   message       │    │
│   │                 │    │                 │    │        │        │    │
│   └─────────────────┘    └─────────────────┘    └────────┼────────┘    │
│                                                          │             │
│                                                          ▼             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│   │  ipai_ai_       │    │   ipai_ai_      │    │   ipai_ai_      │    │
│   │  event          │    │   prompt        │    │   citation      │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    │
│                                                                         │
│   ┌─────────────────┐    ┌─────────────────┐                           │
│   │  ipai_          │───▶│   ipai_         │                           │
│   │  workspace      │    │   workspace_    │                           │
│   │                 │    │   member        │                           │
│   └─────────────────┘    └─────────────────┘                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     Supabase PostgreSQL (kb schema)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         kb.chunks                               │   │
│   │  (id, tenant_ref, source_type, source_ref, title,              │   │
│   │   url, content, embedding, updated_at)                          │   │
│   │                                                                 │   │
│   │  Indexes: tenant_ref, source_type, embedding (ivfflat)         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 0: Foundation (2 days)

**Objective**: Establish documentation and test infrastructure

#### Tasks

1. **Spec Kit Bundle**
   - [x] constitution.md
   - [x] prd.md
   - [x] plan.md
   - [ ] tasks.md

2. **Architecture Documentation**
   - [ ] DBML schema definition
   - [ ] ERD diagram (Mermaid + dbdiagram.io)
   - [ ] ORD (Object Relationship Document)
   - [ ] Architecture diagrams

3. **API Documentation**
   - [ ] OpenAPI spec for Odoo endpoints
   - [ ] Supabase RPC contracts

4. **CI Infrastructure**
   - [ ] GitHub Actions workflow
   - [ ] Test framework setup

---

### Phase 1: Core AI Enhancement (4 days)

**Objective**: Production-ready AI panel with full features

#### Module: ipai_ai_core

- [ ] Add `ipai.ai.audit` model for operation logging
- [ ] Implement service layer with RAG orchestration
- [ ] Add prompt template system (`ipai.ai.prompt`)
- [ ] Implement confidence scoring algorithm
- [ ] Add provider fallback logic

#### Module: ipai_ai_agents_ui

- [ ] Enhance React App with streaming support
- [ ] Add keyboard navigation (Esc to close, Enter to send)
- [ ] Implement citation preview on hover
- [ ] Add conversation history sidebar
- [ ] Implement feedback submission

#### Module: ipai_ai_connectors

- [ ] Hardened event intake endpoint
- [ ] Token rotation support
- [ ] Event processing queue (queue_job)
- [ ] Event replay functionality

#### Module: ipai_ai_sources_odoo

- [ ] Chunking strategy for large content
- [ ] Incremental sync (delta updates)
- [ ] Support for mail.message indexing
- [ ] Support for document.page indexing

---

### Phase 2: Workspace Primitives (3 days)

**Objective**: Notion-style teamspaces using Odoo primitives

#### Module: ipai_workspace_core

- [ ] `ipai.workspace` model (space container)
- [ ] `ipai.workspace.member` model (membership)
- [ ] Space creation wizard
- [ ] Automatic project/channel/folder creation
- [ ] Access rule generation

#### Integration Points

- [ ] Link to project.project
- [ ] Link to mail.channel
- [ ] Link to document.page (if OCA knowledge installed)
- [ ] Menu reorganization for "My Spaces"

---

### Phase 3: Testing & Quality (3 days)

**Objective**: Comprehensive test coverage

#### Python Tests (Odoo)

- [ ] Unit tests for ipai_ai_core models
- [ ] Unit tests for service layer
- [ ] Integration tests for HTTP endpoints
- [ ] Security tests for record rules

#### JavaScript Tests (Jest)

- [ ] Unit tests for odooRpc helper
- [ ] Component tests for App
- [ ] Component tests for MessageCard
- [ ] Component tests for Composer

#### E2E Tests (Playwright)

- [ ] Open AI panel via keyboard shortcut
- [ ] Send message and receive response
- [ ] Citation link navigation
- [ ] Theme toggle persistence
- [ ] New conversation reset

---

### Phase 4: CI/CD & Documentation (2 days)

**Objective**: Automated validation and living docs

#### CI Workflows

- [ ] `ipai-ai-platform-ci.yml` - Main validation
- [ ] `ipai-ai-ui-build.yml` - React bundle build
- [ ] `openapi-validate.yml` - API spec validation
- [ ] `dbml-validate.yml` - Schema validation

#### Documentation

- [ ] Complete README for each module
- [ ] API reference with examples
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## Technical Decisions

### TD1: React Bundle Strategy

**Decision**: Pre-built IIFE bundle committed to repo

**Rationale**:
- Odoo's asset system works best with pre-built assets
- Avoids npm install during Odoo deployment
- CI builds and validates bundle freshness

### TD2: Supabase KB vs Odoo DB

**Decision**: Supabase for KB, Odoo DB for operational data

**Rationale**:
- pgvector is more mature in Supabase
- RPC interface simplifies retrieval
- Operational data stays close to Odoo for performance
- Clear separation of concerns

### TD3: Provider Abstraction

**Decision**: Provider registry with pluggable adapters

**Rationale**:
- Support multiple LLM providers (OpenAI, Claude, Ollama)
- Runtime provider switching per company
- Statistics tracking per provider

### TD4: Workspace Model

**Decision**: Dedicated workspace model vs reusing projects

**Rationale**:
- Projects have specific semantics (tasks, timesheets)
- Workspaces are conceptually containers
- Membership model allows cross-cutting access

---

## Risk Mitigation

### R1: LLM Provider Failures

**Mitigation**:
- Provider fallback chain (primary → secondary)
- Cached responses for common queries
- Graceful degradation UI states

### R2: Large KB Volumes

**Mitigation**:
- Chunking with size limits (1000 chars)
- Incremental sync with change detection
- Pagination in retrieval

### R3: Security Exposure

**Mitigation**:
- Token rotation for connector endpoint
- Record rules enforce isolation
- Audit logging for all AI operations

### R4: Performance Degradation

**Mitigation**:
- Redis caching for embeddings (optional)
- Connection pooling for Supabase
- Async processing for exports

---

## Milestones

| Milestone | Target | Deliverables |
|-----------|--------|--------------|
| M0: Spec Complete | Day 2 | All spec docs, DBML, OpenAPI |
| M1: Core AI | Day 6 | Enhanced panel, citations, feedback |
| M2: Workspaces | Day 9 | Space model, wizard, access rules |
| M3: Testing | Day 12 | > 80% coverage, all test types |
| M4: CI/CD | Day 14 | All workflows, docs complete |

---

## Dependencies

### External

| Dependency | Purpose | Fallback |
|------------|---------|----------|
| Supabase | KB storage, vector search | Text search in Odoo |
| OpenAI API | LLM responses | Claude, Ollama |
| n8n | Integration workflows | Direct webhook |

### Internal (OCA)

| Module | Purpose |
|--------|---------|
| `queue_job` | Async processing |
| `document_page` | KB page model |
| `web_responsive` | Mobile layout |

---

## Environment Configuration

### Required Environment Variables

```bash
# Supabase
IPAI_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=<service_role_key>

# LLM Provider
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_API_KEY=<openai_api_key>
IPAI_LLM_MODEL=gpt-4o-mini

# Embeddings (optional, enables vector search)
IPAI_EMBEDDINGS_PROVIDER=openai
IPAI_EMBEDDINGS_MODEL=text-embedding-3-small

# Connectors
IPAI_CONNECTORS_TOKEN=<secure_random_token>

# Exporter
IPAI_KB_EXPORT_LOOKBACK_HOURS=24
IPAI_PUBLIC_BASE_URL=https://erp.insightpulseai.net
```

---

*Last updated: 2025-01-06*
