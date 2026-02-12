# Knowledge Graph — Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-09

---

## Overview

This plan outlines the phased implementation of the Knowledge Graph (KG) system.
The approach prioritizes: **Schema → Ingestion → Search → UI**.

---

## Phase 1: Foundation (Schema + Indexes)

### 1.1 Create Core Schema

**Deliverable**: `db/migrations/20260109_KG.sql`

Tables to create:
- `kg_nodes` — Graph nodes with type/key/data
- `kg_edges` — Relationships between nodes
- `kg_docs` — Document storage with FTS + embeddings
- `kg_mentions` — Links between docs and nodes

Indexes:
- B-tree on `kg_nodes(type, key)`
- B-tree on `kg_edges(src_id)`, `kg_edges(dst_id)`, `kg_edges(type)`
- GIN on `kg_docs(tsv)` for full-text search
- IVFFlat on `kg_docs(embedding)` for vector similarity

Functions:
- `kg_docs_tsv_update()` — Auto-compute tsvector
- Trigger to maintain FTS index

### 1.2 Apply Migration

```bash
supabase db push
# or
psql $SUPABASE_DB_URL < db/migrations/20260109_KG.sql
```

### 1.3 Verify Schema

- Insert test node/edge/doc
- Verify unique constraints
- Test FTS query
- Test vector search (mock embedding)

---

## Phase 2: GitHub Ingestion

### 2.1 Webhook Receiver

**Deliverable**: Edge Function `ingest-github-event`

Handles events:
- `push` → Update `Repo`, `Branch` nodes
- `pull_request.*` → Create/update `PR` nodes
- `issues.*` → Create/update `Issue` nodes
- `workflow_run.*` → Create `Workflow`, `Run` nodes
- `check_suite.*` → Update `Run` nodes

Edge creation:
- PR closes issue → `IMPLEMENTS` edge
- Workflow on repo → `OWNS` edge

### 2.2 Entity Mapping

| GitHub Entity | Node Type | Key Pattern |
|---------------|-----------|-------------|
| Repository | `Repo` | `repo:<owner>/<name>` |
| Branch | `Branch` | `branch:<owner>/<repo>:<name>` |
| Pull Request | `PR` | `pr:<owner>/<repo>#<num>` |
| Issue | `Issue` | `issue:<owner>/<repo>#<num>` |
| Workflow | `Workflow` | `workflow:<owner>/<repo>:<name>` |
| Workflow Run | `Run` | `run:<owner>/<repo>:<run_id>` |

### 2.3 Nightly Backfill

**Deliverable**: Scheduled function `backfill-github`

- Uses GitHub GraphQL API
- Fetches repos, issues, PRs, workflows
- Upserts nodes/edges
- Fills gaps from missed webhooks

Frequency: Daily at 02:00 UTC

---

## Phase 3: DigitalOcean Ingestion

### 3.1 API Sync Function

**Deliverable**: Edge Function `sync-do-inventory`

Resources to sync:
- Droplets → `Host` nodes
- Domains → `Domain` nodes
- Domain Records → `DNSRecord` nodes
- Apps → `Service` nodes (optional)

### 3.2 Entity Mapping

| DO Resource | Node Type | Key Pattern |
|-------------|-----------|-------------|
| Droplet | `Host` | `droplet:<id>` |
| Domain | `Domain` | `domain:<name>` |
| Domain Record | `DNSRecord` | `dns:<domain>:<type>:<name>` |
| App | `Service` | `do-app:<id>` |

### 3.3 Edge Creation

- `DNSRecord` A/AAAA → `Host` = `CONFIGURES`
- `DNSRecord` CNAME → `Service` = `CONFIGURES`
- `Domain` → org = `OWNS`

Frequency: Every 6 hours

---

## Phase 4: Odoo Ingestion

### 4.1 Module Exporter

**Deliverable**: Python script or n8n workflow

Export sources:
- `ir.module.module` — Installed modules
- Manifest files — Dependencies
- `ir.model` — Model definitions (optional phase 2)

### 4.2 Entity Mapping

| Odoo Entity | Node Type | Key Pattern |
|-------------|-----------|-------------|
| Module | `OdooModule` | `odoo:module:<technical_name>` |
| Model | `OdooModel` | `odoo:model:<model_name>` |
| View | `OdooView` | `odoo:view:<xml_id>` |

### 4.3 Edge Creation

- Module depends on module → `DEPENDS_ON`
- Model belongs to module → `OWNS`
- View belongs to module → `OWNS`

---

## Phase 5: Document Indexing + Mentions

### 5.1 Embedding Pipeline

**Deliverable**: Edge Function `embed-doc`

Flow:
1. New/updated doc in `kg_docs`
2. Call OpenAI embeddings API
3. Store 1536-dim vector
4. Update `embedding` column

Trigger options:
- On insert/update trigger
- Batch job for backlog

### 5.2 Mention Extraction

**Deliverable**: Edge Function `extract-mentions`

Approach:
1. Parse doc body for known patterns:
   - `repo:org/name` → link to Repo node
   - `#123` in PR context → link to Issue
   - `ipai_*` → link to OdooModule
   - IP addresses → link to Host
2. Use LLM for fuzzy extraction (optional)
3. Insert `kg_mentions` with confidence

### 5.3 Chat Thread Ingestion

Store this conversation and future chat threads:
- Source: `chatgpt` or `claude`
- Extract entities mentioned
- Link via mentions

---

## Phase 6: Query API

### 6.1 Hybrid Search Endpoint

**Deliverable**: Edge Function `kg-query`

Input:
```json
{
  "query": "What modules depend on ipai_workspace_core?",
  "embedding": [0.1, ...],
  "limit": 10
}
```

Logic:
1. FTS search on `kg_docs.tsv`
2. Vector search on `kg_docs.embedding`
3. Combine + rerank by RRF
4. Expand via `kg_mentions` → related nodes
5. Traverse `kg_edges` for context

Output:
```json
{
  "docs": [...],
  "nodes": [...],
  "edges": [...]
}
```

### 6.2 Graph Traversal Helpers

RPC functions:
- `kg.get_neighbors(node_id, depth)` — N-hop traversal
- `kg.get_path(src_id, dst_id)` — Shortest path
- `kg.get_subgraph(node_ids)` — Induced subgraph

---

## Phase 7: UI Explorer

### 7.1 Minimal Graph Explorer

**Deliverable**: Next.js page in control-room

Features:
- Search bar (hybrid)
- Node detail panel (type, key, data)
- Edge list (in/out)
- Doc evidence panel
- Basic graph visualization (force-directed)

### 7.2 Integration Points

- Link from Odoo module list → KG node
- Link from PR → KG node
- RAG context display in AI responses

---

## Milestones

| Milestone | Deliverables | Target |
|-----------|--------------|--------|
| M1: Schema | Migration applied, smoke tested | Week 1 |
| M2: GitHub | Webhook + backfill working | Week 2 |
| M3: DO | Infra sync working | Week 3 |
| M4: Odoo | Module graph populated | Week 4 |
| M5: Search | Hybrid query API live | Week 5 |
| M6: UI | Graph explorer deployed | Week 6 |

---

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Supabase project | Platform | Available |
| GitHub webhook secret | DevOps | Needed |
| DO API token | Platform | Available |
| OpenAI API key | Platform | Available |
| Odoo DB access | DevOps | Available |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Embedding cost explosion | Batch, cache, limit doc size |
| Webhook reliability | Nightly backfill reconciliation |
| Key collisions | Strict key pattern enforcement |
| Performance at scale | Proper indexes, IVFFlat tuning |

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `prd.md` — Product Requirements
- `tasks.md` — Actionable Work Items
