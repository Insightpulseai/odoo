# Plan — IPAI AI Platform for Odoo CE/OCA 18

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Odoo CE 18                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        web.assets_backend                               ││
│  │  ┌──────────────────────────────────────────────────────────────────┐  ││
│  │  │                    ipai_ai_agents_ui                              │  ││
│  │  │  ┌────────────────┐ ┌────────────────┐ ┌─────────────────────┐   │  ││
│  │  │  │ Command Palette│ │  Client Action │ │   React+Fluent UI   │   │  ││
│  │  │  │    Hook        │ │    Wrapper     │ │   IIFE Bundle       │   │  ││
│  │  │  └────────────────┘ └────────────────┘ └─────────────────────┘   │  ││
│  │  └──────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Backend Modules                                  ││
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────────────────┐  ││
│  │  │  ipai_ai_core   │ │ipai_agent_core  │ │  ipai_ai_connectors       │  ││
│  │  │  (Existing)     │ │  (Existing)     │ │  (New)                    │  ││
│  │  │  - Providers    │ │  - Skills       │ │  - Event intake           │  ││
│  │  │  - Threads      │ │  - Tools        │ │  - Token auth             │  ││
│  │  │  - Messages     │ │  - Knowledge    │ │  - Audit log              │  ││
│  │  │  - Citations    │ │  - Runs         │ │                           │  ││
│  │  └─────────────────┘ └─────────────────┘ └───────────────────────────┘  ││
│  │                                                                          ││
│  │  ┌───────────────────────────────────────────────────────────────────┐  ││
│  │  │                   ipai_ai_sources_odoo (New)                       │  ││
│  │  │  - Exporter cron (project.task, document.page)                    │  ││
│  │  │  - Supabase REST upsert                                           │  ││
│  │  │  - Tenant mapping (odoo_company:<id>)                             │  ││
│  │  └───────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            External Services                                 │
│  ┌─────────────────────┐ ┌─────────────────┐ ┌───────────────────────────┐  │
│  │    Supabase KB      │ │   LLM Provider  │ │        n8n                │  │
│  │   (pgvector RAG)    │ │  (OpenAI/etc)   │ │     (Workflows)           │  │
│  │  - kb.chunks        │ │  - /chat        │ │  - Inbound events         │  │
│  │  - search_chunks()  │ │  - /embeddings  │ │  - Outbound triggers      │  │
│  └─────────────────────┘ └─────────────────┘ └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Container & Database Identifiers

### Production Environment

| Component | Container Name | Service Name | Port |
|-----------|---------------|--------------|------|
| Odoo CE | `odoo-erp-prod` | `odoo` | 8069 |
| PostgreSQL | `postgres` | `db` | 5432 |
| n8n | `n8n` | `n8n` | 5678 |

### Database Names

| Database | Purpose | Container |
|----------|---------|-----------|
| `odoo` | Primary Odoo database | `postgres` |
| Supabase (external) | KB vector store | Managed (spdtwktxdalcfigzeqrz) |

### Volume Mounts

| Volume | Path | Purpose |
|--------|------|---------|
| `odoo-web-data` | `/var/lib/odoo` | Filestore |
| `postgres-data` | `/var/lib/postgresql/data` | Database |

## Data Flow Diagrams

### Ask AI Flow

```
User Input
    │
    ▼
┌─────────────────┐
│ React UI Panel  │
│ (Fluent UI)     │
└────────┬────────┘
         │ JSON-RPC
         ▼
┌─────────────────┐     ┌─────────────────┐
│ /ipai_ai_agents │     │    Supabase     │
│    /ask         │────►│  kb.search_*    │
└────────┬────────┘     └────────┬────────┘
         │                       │ Evidence
         │◄──────────────────────┘
         ▼
┌─────────────────┐
│  LLM Provider   │
│  (OpenAI/etc)   │
└────────┬────────┘
         │ Answer + Citations
         ▼
┌─────────────────┐
│ ipai.ai.message │
│ (Persist)       │
└────────┬────────┘
         │
         ▼
    Response to UI
```

### Knowledge Export Flow

```
┌─────────────────┐
│  ir.cron        │
│  (Every 15 min) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ ipai.kb.exporter│     │  project.task   │
│ cron_export_*   │◄────│  document.page  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Build payload  │
│  (chunks list)  │
└────────┬────────┘
         │ POST /rest/v1/kb.chunks
         ▼
┌─────────────────┐
│   Supabase      │
│   (Upsert)      │
└─────────────────┘
```

### Connector Event Flow

```
┌─────────────────┐
│  External       │
│  (n8n/GitHub)   │
└────────┬────────┘
         │ POST /ipai_ai_connectors/event
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Token Auth     │─No──►│  401 Reject     │
└────────┬────────┘     └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐
│ ipai.ai.event   │
│ (Create)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Optional       │
│  Processing     │
│  (queue_job)    │
└─────────────────┘
```

## Milestones

### M1: Bootstrap (Days 1-2)

**Goal:** Scaffold modules, wire dependencies, basic UI mount

**Deliverables:**
- [ ] Create `ipai_ai_agents_ui` module skeleton
- [ ] Create `ipai_ai_connectors` module skeleton
- [ ] Create `ipai_ai_sources_odoo` module skeleton
- [ ] Add Supabase KB migration
- [ ] Verify React IIFE builds and loads in Odoo
- [ ] Verify command palette opens panel

**Verification:**
```bash
docker exec -it odoo-erp-prod odoo -d odoo -u ipai_ai_agents_ui --stop-after-init
# Panel should open via Alt+Shift+F
```

### M2: Core AI (Days 3-5)

**Goal:** Working Ask AI with evidence retrieval and citations

**Deliverables:**
- [ ] Implement `/ipai_ai_agents/bootstrap` endpoint
- [ ] Implement `/ipai_ai_agents/ask` endpoint
- [ ] Wire retriever to Supabase KB
- [ ] Wire LLM provider (OpenAI-compatible)
- [ ] Render citations in UI
- [ ] Add confidence scoring and "uncertain" indicator

**Verification:**
```bash
# Supabase should have test chunks
# Ask a question and verify citation appears
curl -sS -X POST https://erp.insightpulseai.com/ipai_ai_agents/bootstrap \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
```

### M3: Integration (Days 6-8)

**Goal:** Connector endpoint and KB exporter working

**Deliverables:**
- [ ] Implement `/ipai_ai_connectors/event` endpoint
- [ ] Add token authentication
- [ ] Create event viewer in admin
- [ ] Implement KB exporter cron
- [ ] Add task + KB page collection
- [ ] Test Supabase upsert

**Verification:**
```bash
# Test connector
curl -sS -X POST https://erp.insightpulseai.com/ipai_ai_connectors/event \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"call","params":{"token":"test","source":"n8n","event_type":"ping"},"id":1}'

# Verify exporter
docker exec -it odoo-erp-prod odoo shell -d odoo <<< "env['ipai.kb.exporter'].cron_export_recent()"
```

### M4: Testing & Docs (Days 9-12)

**Goal:** Comprehensive test coverage and documentation

**Deliverables:**
- [ ] Unit tests for Python services
- [ ] Integration tests with mocks
- [ ] E2E tests (Playwright) for UI
- [ ] Architecture documentation
- [ ] DBML/ERD documentation
- [ ] ORD documentation
- [ ] OpenAPI specification
- [ ] CI workflow with all gates

**Verification:**
```bash
./scripts/ci_local.sh
./scripts/spec_validate.sh spec/ipai-ai-platform-odoo18
```

## Technical Decisions

### D1: React Bundle Strategy

**Decision:** Commit compiled IIFE bundle to repo

**Rationale:**
- Deterministic deploys without build step in container
- CI verifies bundle matches source
- Faster container startup

**Trade-offs:**
- Larger repo size (+100KB)
- Must rebuild on source change

### D2: Supabase for KB Only

**Decision:** Use Supabase only for KB vector search, not primary data

**Rationale:**
- Odoo remains source of truth
- Supabase optimized for vector operations
- Clear separation of concerns

**Trade-offs:**
- Sync latency (15 min default)
- Must manage two data stores

### D3: Read-Only AI Default

**Decision:** AI can read and propose, but not write without confirmation

**Rationale:**
- Safety first for ERP operations
- User remains in control
- Audit trail for all proposals

**Trade-offs:**
- Less "magical" automation
- More user interaction required

### D4: Token Auth for Connectors

**Decision:** Simple shared token for connector endpoint

**Rationale:**
- Works with all webhook sources
- Simple to configure in n8n
- Sufficient for internal network

**Trade-offs:**
- Not as secure as OAuth
- Token rotation is manual

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Supabase API rate limits | Medium | High | Batch upserts, caching |
| LLM provider downtime | Low | High | Fallback message, retry logic |
| Large data volume | Medium | Medium | Chunking, pagination, limits |
| React/Odoo conflicts | Low | Medium | Isolated client action, no core patches |
| Multi-tenant leakage | Low | Critical | RLS policies, record rules, tests |

## Dependencies

### Python Packages (Odoo Image)

```
requests>=2.28.0  # Already in standard Odoo image
```

### NPM Packages (Build Only)

```json
{
  "@fluentui/react-components": "^9.0.0",
  "@fluentui/react-icons": "^2.0.0",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "vite": "^5.4.0"
}
```

### OCA Modules (Optional)

- `queue_job` - Async processing (recommended)
- `document_page` - Knowledge articles

## Environment Variables

### Required

```bash
IPAI_SUPABASE_URL=https://<project>.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=<key>
IPAI_LLM_API_KEY=<key>
IPAI_CONNECTORS_TOKEN=<shared_token>
```

### Optional

```bash
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_MODEL=gpt-4o-mini
IPAI_LLM_TEMPERATURE=0.2
IPAI_EMBEDDINGS_PROVIDER=openai
IPAI_EMBEDDINGS_MODEL=text-embedding-3-small
IPAI_KB_EXPORT_LOOKBACK_HOURS=24
IPAI_PUBLIC_BASE_URL=https://erp.insightpulseai.com
```

## References

- Existing modules: `addons/ipai/ipai_ai_core/`, `addons/ipai/ipai_agent_core/`
- Design tokens: `packages/ipai-design-tokens/`
- Supabase project: `spdtwktxdalcfigzeqrz`
- Container names: See `/deploy/docker-compose.yml`
