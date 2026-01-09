# Knowledge Graph — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Draft
> **Last Updated**: 2026-01-09

---

## 1. Executive Summary

The Knowledge Graph (KG) is a **unified organizational memory** that indexes infrastructure, code, and documentation into a queryable graph with RAG capabilities. It enables AI agents and humans to answer questions like:

- "What services run on this droplet?"
- "Which modules depend on ipai_workspace_core?"
- "What was decided about the authentication architecture?"

**Key Value Propositions**:
1. **Infra Map**: Complete view of DO droplets, domains, DNS, services
2. **Code Map**: Repository, module, and dependency graph
3. **Why Map**: Decisions, specs, and chat context linked to entities
4. **RAG-Ready**: Hybrid search for AI agent context retrieval

---

## 2. Problem Statement

### Current State
- Infrastructure knowledge scattered across DO dashboard, DNS providers, docs
- Module dependencies only visible via manifest inspection
- Decisions buried in chat threads, PRDs, and meeting notes
- No unified way to query "what do we know about X?"
- AI agents lack organizational context for accurate responses

### Desired State
- Single graph connecting all organizational entities
- Query any entity and see its relationships + evidence
- AI agents retrieve relevant context via RAG
- New team members can explore and understand the org

---

## 3. User Personas

### 3.1 AI Agent (Claude/Codex)

- Retrieves context before answering questions
- Understands module dependencies
- Knows which services run where
- References decisions and specs

### 3.2 Developer

- Explores module dependency graph
- Finds which repos deploy to which services
- Searches for past decisions on a topic

### 3.3 Platform Engineer

- Maps infrastructure topology
- Traces DNS to service mappings
- Understands deployment relationships

### 3.4 Manager/Stakeholder

- Gets high-level view of system landscape
- Finds relevant documentation
- Understands what's connected to what

---

## 4. Functional Requirements

### 4.1 Node Management

| ID | Requirement | Priority |
|----|-------------|----------|
| ND-001 | Store nodes with type, key, title, and JSONB data | P1 |
| ND-002 | Enforce unique constraint on (type, key) | P1 |
| ND-003 | Support all defined node types (Org, Repo, Droplet, etc.) | P1 |
| ND-004 | Track created_at and updated_at timestamps | P1 |
| ND-005 | Upsert nodes idempotently by key | P1 |

### 4.2 Edge Management

| ID | Requirement | Priority |
|----|-------------|----------|
| ED-001 | Store edges with src_id, dst_id, type, and weight | P1 |
| ED-002 | Enforce unique constraint on (src_id, dst_id, type) | P1 |
| ED-003 | Support all defined edge types (OWNS, DEPENDS_ON, etc.) | P1 |
| ED-004 | Store optional metadata as JSONB | P2 |
| ED-005 | Cascade delete edges when nodes are removed | P1 |

### 4.3 Document Storage

| ID | Requirement | Priority |
|----|-------------|----------|
| DC-001 | Store documents with source, source_ref, title, body | P1 |
| DC-002 | Compute tsvector for full-text search | P1 |
| DC-003 | Store 1536-dimension embeddings for vector search | P1 |
| DC-004 | Support multiple source types (github, odoo, gdrive, etc.) | P1 |
| DC-005 | Store metadata as JSONB | P2 |

### 4.4 Mention Extraction

| ID | Requirement | Priority |
|----|-------------|----------|
| MN-001 | Link documents to nodes via mentions | P1 |
| MN-002 | Store mention kind (MENTIONS, DEFINES, DECIDES) | P2 |
| MN-003 | Store confidence score for extracted mentions | P2 |
| MN-004 | Cascade delete mentions when doc/node removed | P1 |

### 4.5 Query API

| ID | Requirement | Priority |
|----|-------------|----------|
| QR-001 | Full-text search across documents | P1 |
| QR-002 | Vector similarity search with embeddings | P1 |
| QR-003 | Hybrid search combining FTS + vector | P1 |
| QR-004 | Graph traversal (get neighbors of a node) | P1 |
| QR-005 | Mention expansion (doc → related nodes) | P2 |

### 4.6 GitHub Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| GH-001 | Receive webhooks for PR, issue, push, workflow events | P1 |
| GH-002 | Create/update Repo, PR, Issue, Workflow, Run nodes | P1 |
| GH-003 | Create IMPLEMENTS edges (PR → Issue) | P1 |
| GH-004 | Store event payloads as kg_docs | P2 |
| GH-005 | Nightly GraphQL backfill for missed events | P2 |

### 4.7 DigitalOcean Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| DO-001 | Sync droplets as Host nodes | P1 |
| DO-002 | Sync domains as Domain nodes | P1 |
| DO-003 | Sync DNS records as DNSRecord nodes | P1 |
| DO-004 | Create CONFIGURES edges (DNSRecord → Host/Service) | P1 |
| DO-005 | Scheduled sync (every 6 hours) | P2 |

### 4.8 Odoo Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| OD-001 | Export installed modules as OdooModule nodes | P1 |
| OD-002 | Export model definitions as OdooModel nodes | P2 |
| OD-003 | Create DEPENDS_ON edges from manifest | P1 |
| OD-004 | Export key system parameters | P2 |
| OD-005 | Support multiple Odoo instances | P3 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| PF-001 | Node upsert latency | < 50ms |
| PF-002 | Full-text search latency | < 100ms |
| PF-003 | Vector search latency | < 200ms |
| PF-004 | Graph traversal (1-hop) | < 100ms |
| PF-005 | Total nodes capacity | > 100,000 |

### 5.2 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| RL-001 | Ingestion availability | 99.9% |
| RL-002 | Data durability | 99.999% |
| RL-003 | Webhook retry on failure | 3 attempts |

### 5.3 Security

| ID | Requirement | Target |
|----|-------------|--------|
| SC-001 | RLS tenant isolation | Enforced |
| SC-002 | Webhook signature verification | Required |
| SC-003 | API key authentication | Required |

---

## 6. Data Model

### 6.1 Core Tables

```
┌─────────────────┐       ┌─────────────────┐
│    kg_nodes     │───────│    kg_edges     │
├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │       │ id (PK, UUID)   │
│ type            │       │ src_id (FK)     │
│ key             │       │ dst_id (FK)     │
│ title           │       │ type            │
│ data (JSONB)    │       │ weight          │
│ created_at      │       │ data (JSONB)    │
│ updated_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘
        │
        │ via kg_mentions
        ▼
┌─────────────────┐       ┌─────────────────┐
│    kg_docs      │───────│  kg_mentions    │
├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │       │ id (PK, UUID)   │
│ source          │       │ doc_id (FK)     │
│ source_ref      │       │ node_id (FK)    │
│ title           │       │ kind            │
│ body            │       │ confidence      │
│ meta (JSONB)    │       │ meta (JSONB)    │
│ tsv (tsvector)  │       └─────────────────┘
│ embedding       │
│ created_at      │
└─────────────────┘
```

### 6.2 Key Patterns

| Node Type | Key Pattern | Example |
|-----------|-------------|---------|
| Org | `org:<name>` | `org:insightpulseai-net` |
| Repo | `repo:<org>/<name>` | `repo:insightpulseai-net/odoo-ce` |
| PR | `pr:<org>/<repo>#<num>` | `pr:insightpulseai-net/odoo-ce#183` |
| Droplet | `droplet:<id>` | `droplet:123456789` |
| Domain | `domain:<fqdn>` | `domain:odoo.insightpulse.ai` |
| OdooModule | `odoo:module:<name>` | `odoo:module:ipai_workspace_core` |

---

## 7. Integration Contracts

### 7.1 GitHub Webhook → Node/Edge

```json
{
  "event": "pull_request.opened",
  "nodes": [
    {
      "type": "PR",
      "key": "pr:org/repo#123",
      "title": "feat: add knowledge graph",
      "data": {"state": "open", "author": "user"}
    }
  ],
  "edges": [
    {
      "src_key": "pr:org/repo#123",
      "dst_key": "issue:org/repo#100",
      "type": "IMPLEMENTS"
    }
  ]
}
```

### 7.2 DO Sync → Nodes

```json
{
  "nodes": [
    {
      "type": "Host",
      "key": "droplet:123456",
      "title": "odoo-prod-01",
      "data": {
        "ip": "157.245.1.2",
        "region": "sgp1",
        "size": "s-2vcpu-4gb"
      }
    }
  ]
}
```

### 7.3 RAG Query → Response

```json
{
  "query": "What modules depend on ipai_workspace_core?",
  "embedding": [0.1, 0.2, ...],
  "results": {
    "docs": [...],
    "nodes": [...],
    "edges": [...]
  }
}
```

---

## 8. UI/UX Requirements

### 8.1 Graph Explorer (v1)

- Node view with type icon and title
- Edge list showing relationships
- Doc evidence panel
- Search bar (hybrid)

### 8.2 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/kg/nodes` | GET | List/search nodes |
| `/kg/nodes/:id` | GET | Get node with edges |
| `/kg/query` | POST | Hybrid search (RAG) |
| `/kg/ingest/github` | POST | GitHub webhook receiver |
| `/kg/sync/do` | POST | Trigger DO sync |

---

## 9. Acceptance Criteria

### 9.1 MVP Acceptance

- [ ] Schema deployed to Supabase
- [ ] GitHub webhook creates nodes/edges
- [ ] Full-text search works
- [ ] Vector search works
- [ ] Graph traversal returns neighbors

### 9.2 V1.0 Acceptance

- [ ] DO sync populates infra nodes
- [ ] Odoo exporter populates module nodes
- [ ] Mention extraction links docs to nodes
- [ ] Hybrid search returns ranked results
- [ ] Graph explorer UI navigable

---

## 10. Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Supabase | Database + Auth | Available |
| pgvector | Embeddings | Available |
| OpenAI | Embedding generation | Available |
| GitHub API | Webhook + GraphQL | Available |
| DO API | Resource sync | Available |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Embedding cost | High API spend | Batch + cache embeddings |
| Key collision | Data corruption | Strict key patterns |
| Webhook delays | Stale data | Nightly backfill |
| Entity extraction errors | Bad mentions | Confidence thresholds |

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `plan.md` — Implementation Roadmap
- `tasks.md` — Actionable Work Items
