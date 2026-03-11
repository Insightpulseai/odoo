# LLM Query Playbook

> **Purpose**: Query recipes for LLM agents working with this stack.
> **Audience**: AI agents using Supabase as memory/knowledge backend.

---

## Query Patterns

### Pattern 1: Semantic Document Search

**When to use**: Finding documents about a topic.

```sql
-- Step 1: Generate embedding for query (external API)
-- Step 2: Search using vector similarity

SELECT
  c.id,
  c.content,
  1 - (e.embedding <=> $query_embedding) as similarity
FROM docs.chunks c
JOIN docs.embeddings e ON c.id = e.chunk_id
ORDER BY e.embedding <=> $query_embedding
LIMIT 10;
```

**Alternative using function**:
```sql
SELECT * FROM docs.search_chunks($query_embedding::vector, 10);
```

---

### Pattern 2: Knowledge Graph Traversal

**When to use**: Finding related entities.

```sql
-- Find nodes of a specific kind
SELECT * FROM kg.nodes WHERE kind = 'odoo_module';

-- Find relationships from a node
SELECT e.*, n2.label as target_label
FROM kg.edges e
JOIN kg.nodes n2 ON e.to_node = n2.id
WHERE e.from_node = $node_id;

-- K-hop neighborhood
SELECT * FROM kg.neighborhood($node_id, 2);

-- Semantic node search
SELECT * FROM kg.semantic_search('finance ppm workflow', 10);
```

---

### Pattern 3: Agent Memory Recall

**When to use**: Accessing past agent context.

```sql
-- Recent sessions for an agent
SELECT * FROM agent_mem.sessions
WHERE agent_name = $agent_name
ORDER BY created_at DESC
LIMIT 10;

-- Events from a specific session
SELECT * FROM agent_mem.events
WHERE session_id = $session_id
ORDER BY occurred_at ASC;

-- Semantic memory search
SELECT
  e.id,
  e.event_type,
  e.content,
  1 - (e.embedding <=> $query_embedding) as relevance
FROM agent_mem.events e
WHERE e.embedding IS NOT NULL
ORDER BY e.embedding <=> $query_embedding
LIMIT 20;
```

---

### Pattern 4: KB Artifact Lookup

**When to use**: Finding specific documents or specs.

```sql
-- Find artifacts by title
SELECT * FROM kb.artifacts
WHERE title ILIKE '%' || $search_term || '%'
ORDER BY updated_at DESC;

-- Find by kind
SELECT * FROM kb.artifacts
WHERE kind = 'spec_bundle'  -- or: doc_page, runbook, etc.
ORDER BY created_at DESC;

-- Get artifact with version history
SELECT a.*, v.content, v.created_at as version_date
FROM kb.artifacts a
JOIN kb.versions v ON a.id = v.artifact_id
WHERE a.slug = $slug
ORDER BY v.created_at DESC;
```

---

### Pattern 5: Catalog Navigation

**When to use**: Browsing the knowledge taxonomy.

```sql
-- Get top-level sources
SELECT * FROM kb.catalog_sources
WHERE is_active = true
ORDER BY priority;

-- Get nodes under a parent
SELECT * FROM kb.catalog_nodes
WHERE parent_id = $parent_id
ORDER BY sort_order;

-- Get harvest status
SELECT
  n.id,
  n.title,
  h.status,
  h.last_harvested_at
FROM kb.catalog_nodes n
LEFT JOIN kb.harvest_state h ON n.id = h.node_id
WHERE n.source_id = $source_id;
```

---

### Pattern 6: Ops Recommendations

**When to use**: Getting operational advice.

```sql
-- Open recommendations by category
SELECT * FROM ops_advisor.v_open_by_category;

-- Latest scores
SELECT * FROM ops_advisor.v_latest_scores;

-- Dashboard summary
SELECT * FROM ops_advisor.v_dashboard_summary;

-- Recommendations for a specific resource
SELECT * FROM ops_advisor.recommendations
WHERE resource_id = $resource_id
  AND status = 'open'
ORDER BY impact DESC;
```

---

## Common Filters

### Tenant Isolation
Always include tenant filter when multi-tenancy applies:

```sql
WHERE tenant_id = $tenant_id
```

### Time-Based Queries
```sql
-- Last 24 hours
WHERE created_at > now() - interval '24 hours'

-- Date range
WHERE created_at BETWEEN $start_date AND $end_date
```

### Active/Enabled Only
```sql
WHERE is_active = true
WHERE status = 'active'
```

---

## Query Construction Rules

### Do
- ✅ Use parameterized queries (`$param`)
- ✅ Include `LIMIT` on all searches
- ✅ Order by relevance or recency
- ✅ Filter by tenant when applicable
- ✅ Use existing functions when available

### Don't
- ❌ Use `SELECT *` without `LIMIT`
- ❌ Query without tenant isolation
- ❌ Perform writes without explicit approval
- ❌ Query `odoo_shadow.*` for writes
- ❌ Bypass RLS policies

---

## Response Formatting

### Document Results
```json
{
  "query": "original query",
  "results": [
    {
      "id": "uuid",
      "title": "Document Title",
      "snippet": "Relevant excerpt...",
      "similarity": 0.92,
      "source": "kb.artifacts"
    }
  ],
  "count": 10
}
```

### Graph Results
```json
{
  "node": {
    "id": "uuid",
    "kind": "odoo_module",
    "label": "ipai_finance_ppm"
  },
  "edges": [
    {
      "relation": "DEPENDS_ON",
      "target": "ipai_enterprise_bridge"
    }
  ]
}
```

---

## Error Handling

### No Results
If a query returns empty:
1. Broaden search terms
2. Check if data exists in the catalog
3. Report "no matching documents found"

### Permission Denied
If RLS blocks access:
1. Verify auth context is set
2. Check tenant_id matches
3. Escalate to human if persistent

### Vector Search Failures
If embedding query fails:
1. Verify embedding dimension (1536)
2. Check index exists
3. Fall back to text search

---

## Quick Reference

| Task | Table/Function |
|------|----------------|
| Semantic doc search | `docs.search_chunks()` |
| Graph traversal | `kg.neighborhood()` |
| Semantic node search | `kg.semantic_search()` |
| Agent memory | `agent_mem.events` |
| KB artifacts | `kb.artifacts` |
| Catalog browse | `kb.catalog_nodes` |
| Ops recommendations | `ops_advisor.recommendations` |
