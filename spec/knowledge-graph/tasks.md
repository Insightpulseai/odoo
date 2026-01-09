# Knowledge Graph — Tasks

> **Last Updated**: 2026-01-09

---

## Legend

- `[ ]` — Pending
- `[~]` — In Progress
- `[x]` — Completed
- `[-]` — Blocked/Cancelled

---

## Phase 1: Foundation

### 1.1 Schema

- [ ] Create `db/migrations/20260109_KG.sql` with:
  - [ ] `kg_nodes` table (id, type, key, title, data, timestamps)
  - [ ] `kg_edges` table (id, src_id, dst_id, type, weight, data, timestamps)
  - [ ] `kg_docs` table (id, source, source_ref, title, body, meta, tsv, embedding, timestamps)
  - [ ] `kg_mentions` table (id, doc_id, node_id, kind, confidence, meta)
  - [ ] Unique constraints on (type, key) and (src_id, dst_id, type)
  - [ ] B-tree indexes on edges (src_id, dst_id, type)
  - [ ] GIN index on tsv
  - [ ] IVFFlat index on embedding
  - [ ] Trigger for auto-updating tsv

### 1.2 Deployment

- [ ] Apply migration to Supabase project `spdtwktxdalcfigzeqrz`
- [ ] Verify tables created
- [ ] Insert smoke test data (1 node, 1 edge, 1 doc)
- [ ] Verify FTS query works
- [ ] Verify vector search works (mock embedding)

---

## Phase 2: GitHub Ingestion

### 2.1 Webhook Receiver

- [ ] Create Edge Function `ingest-github-event`
- [ ] Handle `push` events → Repo/Branch nodes
- [ ] Handle `pull_request.*` events → PR nodes
- [ ] Handle `issues.*` events → Issue nodes
- [ ] Handle `workflow_run.*` events → Workflow/Run nodes
- [ ] Create IMPLEMENTS edges (PR → Issue)
- [ ] Store event summaries as kg_docs

### 2.2 Backfill

- [ ] Create scheduled function `backfill-github`
- [ ] Fetch repos via GraphQL
- [ ] Fetch issues via GraphQL
- [ ] Fetch PRs via GraphQL
- [ ] Fetch workflows via GraphQL
- [ ] Upsert nodes/edges
- [ ] Schedule daily at 02:00 UTC

### 2.3 Testing

- [ ] Deploy webhook to test environment
- [ ] Trigger test PR
- [ ] Verify nodes created
- [ ] Verify edges created
- [ ] Run backfill manually
- [ ] Verify reconciliation works

---

## Phase 3: DigitalOcean Ingestion

### 3.1 Sync Function

- [ ] Create Edge Function `sync-do-inventory`
- [ ] Sync droplets → Host nodes
- [ ] Sync domains → Domain nodes
- [ ] Sync domain records → DNSRecord nodes
- [ ] Create CONFIGURES edges (DNS → Host/Service)

### 3.2 Deployment

- [ ] Store DO API token as secret
- [ ] Schedule sync every 6 hours
- [ ] Test initial sync
- [ ] Verify all droplets present
- [ ] Verify all domains present
- [ ] Verify DNS records mapped correctly

---

## Phase 4: Odoo Ingestion

### 4.1 Exporter

- [ ] Create exporter script (Python or n8n)
- [ ] Export installed modules from `ir.module.module`
- [ ] Parse manifest files for dependencies
- [ ] Create OdooModule nodes
- [ ] Create DEPENDS_ON edges

### 4.2 Extended Export (v2)

- [ ] Export model definitions from `ir.model`
- [ ] Create OdooModel nodes
- [ ] Export view definitions from `ir.ui.view`
- [ ] Create OdooView nodes
- [ ] Create OWNS edges (Module → Model/View)

### 4.3 Deployment

- [ ] Test against odoo-core instance
- [ ] Verify module count matches
- [ ] Verify dependency graph accurate
- [ ] Schedule periodic export

---

## Phase 5: Document Indexing

### 5.1 Embedding Pipeline

- [ ] Create Edge Function `embed-doc`
- [ ] Integrate OpenAI embeddings API
- [ ] Handle rate limiting
- [ ] Batch processing for backlog
- [ ] Update kg_docs.embedding column

### 5.2 Mention Extraction

- [ ] Create Edge Function `extract-mentions`
- [ ] Pattern matching for repo references
- [ ] Pattern matching for issue/PR numbers
- [ ] Pattern matching for module names
- [ ] Pattern matching for IP addresses/hostnames
- [ ] Insert kg_mentions with confidence scores

### 5.3 Chat Ingestion

- [ ] Define source format for chat threads
- [ ] Create ingestion endpoint
- [ ] Extract entities from this conversation
- [ ] Store as kg_docs
- [ ] Link via kg_mentions

---

## Phase 6: Query API

### 6.1 Hybrid Search

- [ ] Create Edge Function `kg-query`
- [ ] Implement FTS search
- [ ] Implement vector search
- [ ] Implement RRF ranking
- [ ] Implement mention expansion
- [ ] Return docs + nodes + edges

### 6.2 Graph Traversal

- [ ] Create RPC `kg.get_neighbors(node_id, depth)`
- [ ] Create RPC `kg.get_path(src_id, dst_id)`
- [ ] Create RPC `kg.get_subgraph(node_ids)`
- [ ] Test with real data

### 6.3 Documentation

- [ ] Document API endpoints
- [ ] Create example queries
- [ ] Add to README

---

## Phase 7: UI Explorer

### 7.1 Implementation

- [ ] Create KG explorer page in control-room
- [ ] Implement search bar
- [ ] Implement node detail panel
- [ ] Implement edge list
- [ ] Implement doc evidence panel
- [ ] Basic graph visualization

### 7.2 Integration

- [ ] Link from Odoo module list
- [ ] Link from GitHub PR view
- [ ] Display RAG context in AI responses

---

## GitHub Issues (Tracking)

| Issue | Title | Status |
|-------|-------|--------|
| #TBD | KG MVP: Create kg_nodes/kg_edges/kg_docs schema + indexes | Pending |
| #TBD | KG Ingest: GitHub webhook → Edge Function upsert nodes/edges/docs | Pending |
| #TBD | KG Ingest: nightly GitHub GraphQL backfill | Pending |
| #TBD | KG Ingest: DigitalOcean sync (droplets/domains/apps/certs) | Pending |
| #TBD | KG Ingest: Odoo exporter (installed modules, models, views) | Pending |
| #TBD | KG Model: DNSRecord node type + CONFIGURES edges | Pending |
| #TBD | KG Docs: ingest ChatGPT thread + extract mentions | Pending |
| #TBD | KG Index: embed kg_docs + upsert vectors; enable hybrid search | Pending |
| #TBD | KG API: /kg_query hybrid search + neighborhood expansion | Pending |
| #TBD | KG UI: Graph explorer (node view, neighbors, doc evidence) | Pending |

---

## Notes

- All node keys must follow patterns defined in constitution.md
- RLS policies must be applied before production use
- Embeddings use OpenAI text-embedding-3-small (1536 dims)
- IVFFlat index requires `lists = 100` for < 1M vectors
