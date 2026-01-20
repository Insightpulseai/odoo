# Supabase Stack Details

> **Purpose**: Detailed Supabase configuration for LLM agents.
> **Project Ref**: `spdtwktxdalcfigzeqrz`
> **Role**: Memory Hub + Knowledge Repository

---

## Project Configuration

| Setting | Value |
|---------|-------|
| Project Name | superset |
| Region | ap-southeast-1 (Singapore) |
| Postgres Version | 15.x |
| Extensions | pgvector, pg_cron, pgmq, vault |

---

## Schema Inventory

### `kb` - Knowledge Base
**Purpose**: Document storage, chunking, and catalog for RAG.

| Table | Purpose |
|-------|---------|
| `kb.spaces` | Tenant-scoped workspace containers |
| `kb.artifacts` | Canonical records (docs, specs, runbooks) |
| `kb.versions` | Immutable version snapshots |
| `kb.blocks` | Content atoms (code, notes, citations) |
| `kb.citations` | Provenance tracking |
| `kb.catalog_sources` | Content source registry |
| `kb.catalog_nodes` | Hierarchical taxonomy tree |
| `kb.harvest_state` | Ingestion status ledger |

### `kg` - Knowledge Graph
**Purpose**: Entity-relationship graph with vector embeddings.

| Table | Purpose |
|-------|---------|
| `kg.nodes` | Entities (person, org, module, task) |
| `kg.edges` | Relationships with predicates |
| `kg.evidence` | Provenance with source tracking |
| `kg.node_embeddings` | 1536-dim vectors (IVFFlat) |

**Key Functions**:
- `kg.neighborhood(node_id, k)` - K-hop traversal
- `kg.semantic_search(query, limit)` - Vector similarity
- `kg.upsert_node(...)` - Idempotent node insert/update
- `kg.upsert_edge(...)` - Idempotent edge insert/update

### `agent_mem` - Agent Memory
**Purpose**: Session and event tracking for MCP agents.

| Table | Purpose |
|-------|---------|
| `agent_mem.sessions` | Conversation containers |
| `agent_mem.events` | Fine-grained memory with embeddings |
| `agent_mem.skills` | Tool/skill registry |
| `agent_mem.agent_skill_bindings` | Permissions |
| `agent_mem.memory_sync_log` | Sync audit trail |

### `docs` - Document RAG
**Purpose**: Simple document storage for semantic search.

| Table | Purpose |
|-------|---------|
| `docs.chunks` | Content chunks with hash |
| `docs.embeddings` | 1536-dim vectors |

**Function**: `docs.search_chunks(query_embedding, limit)`

### `ops_advisor` - Recommendations
**Purpose**: Azure Advisor-style operational recommendations.

| Table | Purpose |
|-------|---------|
| `ops_advisor.recommendations` | Cost, security, reliability recs |
| `ops_advisor.scores` | Time-series scores |
| `ops_advisor.activity_log` | Change audit |

---

## API-Exposed Schemas

These schemas are exposed via PostgREST:

```
public, kb, kg, agent_mem, docs, ops_advisor
```

**Not Exposed** (internal only):
```
odoo_shadow, auth, storage, realtime, supabase_functions
```

---

## Edge Functions (23 deployed)

### Knowledge & RAG
| Function | Purpose |
|----------|---------|
| `docs-ai-ask` | RAG Q&A endpoint |
| `semantic-query` | Vector similarity search |
| `semantic-import-osi` | External source ETL |
| `semantic-export-osi` | Export to external systems |
| `sync-kb-to-schema` | KB → schema metadata sync |
| `catalog-sync` | Catalog source/node sync |

### Authentication
| Function | Purpose |
|----------|---------|
| `verify-secrets` | Environment validation |
| `verify-supabase` | DB connectivity check |
| `verify-github` | Token validation |
| `verify-external-apis` | API health checks |

### Integrations
| Function | Purpose |
|----------|---------|
| `mailgate-mailgun` | Inbound email handler |
| `n8n-proxy` | n8n workflow proxy |

---

## Vector Index Configuration

All vector columns use:
- **Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Index Type**: IVFFlat (balanced speed/accuracy)
- **Lists**: 100 (default)

```sql
-- Example index
CREATE INDEX ON kg.node_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## RLS Policies

**Pattern**: All user-facing tables enforce RLS with:
- `auth.uid()` for user identity
- `tenant_id` for multi-tenancy where applicable

```sql
-- Example policy
CREATE POLICY "Users can view own artifacts"
ON kb.artifacts FOR SELECT
USING (auth.uid() = created_by OR is_public = true);
```

---

## Cron Jobs (pg_cron)

| Job | Schedule | Purpose |
|-----|----------|---------|
| `kb_harvest_processor` | */15 * * * * | Process harvest queue |
| `agent_mem_cleanup` | 0 3 * * * | Purge old events |
| `ops_advisor_refresh` | 0 */6 * * * | Refresh recommendations |

---

## Common Query Patterns

### Semantic Search
```sql
-- Direct embedding query
SELECT id, content, 1 - (embedding <=> query_vec) as similarity
FROM docs.chunks
ORDER BY embedding <=> query_vec
LIMIT 10;

-- Using function
SELECT * FROM docs.search_chunks(query_embedding, 10);
```

### Knowledge Graph Traversal
```sql
-- Find related nodes
SELECT * FROM kg.neighborhood('node-uuid', 2);

-- Semantic node search
SELECT * FROM kg.semantic_search('inventory management', 5);
```

### Agent Memory Recall
```sql
-- Recent events for an agent
SELECT * FROM agent_mem.events
WHERE session_id IN (
  SELECT id FROM agent_mem.sessions
  WHERE agent_name = 'ipai_enterprise_bridge'
)
ORDER BY occurred_at DESC
LIMIT 20;
```

---

## Integration Points

### Vercel Projects
Connected via Supabase Vercel Integration:
- `shelf-nu` - Asset management UI
- `scout-dashboard` - Retail analytics
- `tbwa-agency-dash` - Agency dashboard

### GitHub
Connected via Supabase GitHub Integration:
- Repository: `jgtolentino/odoo-ce`
- Supabase Directory: `/supabase`
- Production Branch: `main`

### Odoo
- Shadow tables mirror Odoo via ETL
- Schema: `odoo_shadow` (internal only)
- Sync: Incremental by `write_date`
