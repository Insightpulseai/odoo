# IPAI AI Platform Architecture

## Overview

The IPAI AI Platform provides Notion-style "Ask AI" capabilities for Odoo CE/OCA 18. It combines a React + Fluent UI frontend with Supabase pgvector for RAG retrieval.

## Runtime Snapshot (Production)

### Containers

| Component | Container Name | Service | Port | Purpose |
|-----------|---------------|---------|------|---------|
| Odoo CE | `odoo-erp-prod` | `odoo` | 8069 | Web + workers |
| PostgreSQL | `postgres` | `db` | 5432 | Primary database |
| n8n | `n8n` | `n8n` | 5678 | Workflow automation |

### Databases

| Database | Purpose | Location |
|----------|---------|----------|
| `odoo` | Primary Odoo database | PostgreSQL container |
| Supabase KB | Vector search store | Managed (spdtwktxdalcfigzeqrz) |

### Volumes

| Volume | Mount Path | Purpose |
|--------|-----------|---------|
| `odoo-web-data` | `/var/lib/odoo` | Filestore |
| `postgres-data` | `/var/lib/postgresql/data` | Database |

### Domains

| Domain | Purpose |
|--------|---------|
| `erp.insightpulseai.net` | Odoo web application |
| `n8n.insightpulseai.net` | n8n workflows |

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Odoo CE 18 Container                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Web Assets (Frontend)                            ││
│  │  ┌──────────────────────────────────────────────────────────────────┐  ││
│  │  │                    ipai_ai_agents_ui                              │  ││
│  │  │  ┌────────────────┐ ┌────────────────┐ ┌─────────────────────┐   │  ││
│  │  │  │ Command Palette│ │  Client Action │ │   React+Fluent UI   │   │  ││
│  │  │  │    Hook        │ │    Wrapper     │ │   IIFE Bundle       │   │  ││
│  │  │  │ (Alt+Shift+F)  │ │  (OWL Mount)   │ │   (~300KB)          │   │  ││
│  │  │  └────────────────┘ └────────────────┘ └─────────────────────┘   │  ││
│  │  └──────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Backend Modules                                  ││
│  │                                                                          ││
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────────────────┐  ││
│  │  │  ipai_ai_core   │ │ipai_agent_core  │ │  ipai_ai_connectors       │  ││
│  │  │  (Existing)     │ │  (Existing)     │ │  (New)                    │  ││
│  │  │                 │ │                 │ │                           │  ││
│  │  │  Models:        │ │  Models:        │ │  Models:                  │  ││
│  │  │  - provider     │ │  - skill        │ │  - event                  │  ││
│  │  │  - thread       │ │  - tool         │ │                           │  ││
│  │  │  - message      │ │  - knowledge    │ │  Controller:              │  ││
│  │  │  - citation     │ │  - run          │ │  - /event (webhook)       │  ││
│  │  └─────────────────┘ └─────────────────┘ └───────────────────────────┘  ││
│  │                                                                          ││
│  │  ┌───────────────────────────────────────────────────────────────────┐  ││
│  │  │                   ipai_ai_sources_odoo (New)                       │  ││
│  │  │                                                                    │  ││
│  │  │  Models:                          Cron:                           │  ││
│  │  │  - exporter (abstract)            - Every 15 min export           │  ││
│  │  │  - export_run (audit)                                             │  ││
│  │  │                                                                    │  ││
│  │  │  Sources:                                                         │  ││
│  │  │  - project.task                                                   │  ││
│  │  │  - document.page (if OCA installed)                               │  ││
│  │  └───────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Controllers                                      ││
│  │                                                                          ││
│  │  ipai_ai_agents_ui/controllers/main.py                                  ││
│  │  ├── /ipai_ai_agents/bootstrap    (JSON-RPC, auth=user)                ││
│  │  ├── /ipai_ai_agents/ask          (JSON-RPC, auth=user)                ││
│  │  └── /ipai_ai_agents/feedback     (JSON-RPC, auth=user)                ││
│  │                                                                          ││
│  │  ipai_ai_connectors/controllers/main.py                                 ││
│  │  ├── /ipai_ai_connectors/event    (JSON-RPC, auth=public, token)       ││
│  │  └── /ipai_ai_connectors/health   (JSON-RPC, auth=public)              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            External Services                                 │
│                                                                              │
│  ┌─────────────────────┐ ┌─────────────────┐ ┌───────────────────────────┐  │
│  │    Supabase KB      │ │   LLM Provider  │ │        n8n                │  │
│  │   (pgvector RAG)    │ │  (OpenAI/etc)   │ │     (Workflows)           │  │
│  │                     │ │                 │ │                           │  │
│  │  Table:             │ │  Endpoints:     │ │  Patterns:                │  │
│  │  - kb.chunks        │ │  - /chat        │ │  - Trigger on event       │  │
│  │                     │ │  - /embeddings  │ │  - Call connector         │  │
│  │  RPCs:              │ │                 │ │  - Index content          │  │
│  │  - search_chunks    │ │  Models:        │ │                           │  │
│  │  - search_chunks_   │ │  - gpt-4o-mini  │ │                           │  │
│  │    text             │ │  - claude-3     │ │                           │  │
│  └─────────────────────┘ └─────────────────┘ └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Ask AI Flow

```
┌──────────┐   Alt+Shift+F   ┌────────────────┐
│   User   │───────────────► │  Command       │
│          │                 │  Palette       │
└──────────┘                 └───────┬────────┘
                                     │
                                     ▼
                             ┌────────────────┐
                             │  React Panel   │
                             │  (Fluent UI)   │
                             └───────┬────────┘
                                     │ JSON-RPC
                                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    Odoo Controller                              │
│                                                                 │
│  1. Validate session                                            │
│  2. Get provider config                                         │
│  3. Create/resume thread                                        │
│  4. Store user message                                          │
│                                                                 │
└───────────────────────────────┬────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
           ┌────────────────┐     ┌────────────────┐
           │   Supabase     │     │  LLM Provider  │
           │  kb.search_*   │     │  /chat         │
           └───────┬────────┘     └───────┬────────┘
                   │ Evidence             │ Answer
                   └───────────┬──────────┘
                               │
                               ▼
                    ┌────────────────┐
                    │ Store Response │
                    │ - message      │
                    │ - citations    │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │  React Panel   │
                    │  (Render)      │
                    └────────────────┘
```

### Knowledge Export Flow

```
┌────────────────┐
│  ir.cron       │  Every 15 minutes
│  Scheduler     │
└───────┬────────┘
        │
        ▼
┌────────────────┐     ┌─────────────────────┐
│ ipai.kb.       │     │  Odoo Models        │
│ exporter       │◄────│  - project.task     │
│                │     │  - document.page    │
└───────┬────────┘     └─────────────────────┘
        │
        │ Build chunks[]
        │
        ▼
┌────────────────┐
│ Create         │
│ export_run     │
└───────┬────────┘
        │
        │ POST /rest/v1/kb.chunks
        │ (Prefer: resolution=merge-duplicates)
        │
        ▼
┌────────────────┐
│   Supabase     │
│   Upsert       │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Update         │
│ export_run     │
│ (success/fail) │
└────────────────┘
```

### Connector Event Flow

```
┌─────────────────┐
│  External       │
│  (n8n/GitHub)   │
└───────┬─────────┘
        │
        │ POST /ipai_ai_connectors/event
        │ {token, source, event_type, payload}
        │
        ▼
┌────────────────────────────────────────────┐
│              Odoo Controller               │
│                                            │
│  1. Validate token                         │
│     ├─ Invalid → 401 reject                │
│     └─ Valid   → Continue                  │
│                                            │
│  2. Normalize source                       │
│     (n8n, github, slack, custom)           │
│                                            │
│  3. Create ipai.ai.event record            │
│                                            │
└───────────────────┬────────────────────────┘
                    │
                    ▼
           ┌────────────────┐
           │ ipai.ai.event  │
           │ (state=received)│
           └───────┬────────┘
                   │
                   │ Optional: queue_job
                   │
                   ▼
           ┌────────────────┐
           │ Event          │
           │ Processing     │
           │ (future)       │
           └────────────────┘
```

## Security Boundaries

### Authentication Layers

| Endpoint | Auth Method | Description |
|----------|-------------|-------------|
| `/ipai_ai_agents/*` | Odoo session (cookie) | Requires logged-in user |
| `/ipai_ai_connectors/event` | Token (header/param) | Shared secret from env |
| `/ipai_ai_connectors/health` | None | Public health check |
| Supabase REST | API Key (header) | Service role key from env |
| LLM API | API Key (header) | Provider key from env |

### Data Isolation

- **Company-level**: All data is scoped by `company_id`
- **User-level**: Threads owned by creating user
- **Record rules**: Enforce access via Odoo record rules
- **RLS (Supabase)**: Tenant isolation via `tenant_ref`

## Failure Modes

| Failure | Detection | Fallback |
|---------|-----------|----------|
| Supabase down | HTTP timeout/error | Text search fallback, show warning |
| LLM down | HTTP timeout/error | Return graceful error message |
| Embeddings fail | API error | Fall back to text search |
| Export fails | Exception | Log error, mark run failed |
| Token invalid | Auth check | Return 401 error |

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Ask response (P50) | < 2s | Cached retrieval |
| Ask response (P95) | < 5s | Cold retrieval + generation |
| Ask response (timeout) | 15s | Hard timeout |
| Export batch | < 60s | 100 chunks per batch |
| Panel load | < 1s | Initial bootstrap |

## Module Dependencies

```
ipai_dev_studio_base (base)
    │
    └── ipai_workspace_core
        │
        └── ipai_ai_core ─────────────────┐
            │                             │
            ├── ipai_ai_agents_ui         │
            │   (React panel)             │
            │                             │
            ├── ipai_ai_connectors        │
            │   (Webhook intake)          │
            │                             │
            └── ipai_ai_sources_odoo ─────┘
                (KB exporter)

project (Odoo core)
    │
    └── ipai_ai_sources_odoo
        (exports tasks)

document_page (OCA, optional)
    │
    └── ipai_ai_sources_odoo
        (exports KB articles)
```

## Environment Variables

### Required

```bash
# Supabase KB connection
IPAI_SUPABASE_URL=https://<project>.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=<key>

# LLM provider
IPAI_LLM_API_KEY=<key>

# Connector security
IPAI_CONNECTORS_TOKEN=<shared_secret>
```

### Optional

```bash
# LLM configuration
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_MODEL=gpt-4o-mini
IPAI_LLM_TEMPERATURE=0.2

# Embeddings
IPAI_EMBEDDINGS_PROVIDER=openai
IPAI_EMBEDDINGS_MODEL=text-embedding-3-small
IPAI_EMBEDDINGS_API_KEY=<key>

# Exporter
IPAI_KB_EXPORT_LOOKBACK_HOURS=24
IPAI_PUBLIC_BASE_URL=https://erp.insightpulseai.net
```

## References

- Odoo CE 18 docs: https://www.odoo.com/documentation/18.0
- Supabase pgvector: https://supabase.com/docs/guides/ai
- Fluent UI React: https://react.fluentui.dev
- OpenAI API: https://platform.openai.com/docs
