# Memory Ingestion Edge Function

**Purpose**: Centralized API endpoint for ingesting infrastructure discovery data into Supabase knowledge graph.

**Status**: ✅ Implemented (Ready for deployment)

---

## Overview

The Memory Ingestion Edge Function provides a unified interface for all discovery scripts (Vercel, Supabase, Odoo, DigitalOcean, Docker) to submit their findings to the Supabase knowledge graph.

**Key Features**:
- Batch upsert with 500-row batches (Supabase limit: 1000 rows/request)
- Automatic source metadata updates (last_discovered_at, discovery_count)
- Caller provenance tracking (annotates nodes/edges with `_caller` property)
- Snapshot creation for audit trail
- Error handling with partial success support (HTTP 207)
- Service role authentication (protected endpoint)

---

## Architecture

```
Discovery Scripts (5 sources)
    ↓
Memory Ingest Edge Function (POST /functions/v1/memory-ingest)
    ↓
Supabase PostgreSQL
    ├── infra.sources (source metadata updates)
    ├── infra.nodes (infrastructure components)
    ├── infra.edges (relationships)
    └── infra.snapshots (audit trail)
```

---

## API Reference

### Endpoint
```
POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/memory-ingest
```

### Authentication
**Required**: Service role key (admin access)

```bash
Authorization: Bearer <SUPABASE_SERVICE_ROLE_KEY>
```

### Request Payload

```typescript
{
  source: string           // Required: Discovery source ID (vercel, supabase, odoo, digitalocean, docker)
  nodes: Node[]           // Required: Array of node objects
  edges: Edge[]           // Required: Array of edge objects
  caller?: string         // Optional: Caller annotation for provenance (e.g., "github-actions", "manual-run")
  metadata?: object       // Optional: Additional metadata for source update
}
```

**Node Schema**:
```typescript
{
  id: string              // Stable ID: <source>:<kind>:<key>
  source: string          // Discovery source
  kind: string            // Component type (project, database, service, etc.)
  key: string             // Source-specific unique key
  name: string            // Human-readable name
  props: object           // Component-specific properties
}
```

**Edge Schema**:
```typescript
{
  id: string              // Edge ID: <from_id>→<to_id>
  source: string          // Discovery source
  from_id: string         // Source node ID
  to_id: string           // Target node ID
  type: string            // Relationship type (OWNS, USES_INTEGRATION, DEPENDS_ON, etc.)
  props: object           // Relationship-specific properties
}
```

### Response

**Success (HTTP 200)**:
```json
{
  "success": true,
  "source": "vercel",
  "nodes_upserted": 42,
  "edges_upserted": 38,
  "caller": "github-actions",
  "timestamp": "2026-01-20T12:45:30.123Z"
}
```

**Partial Success (HTTP 207)**:
```json
{
  "success": false,
  "source": "supabase",
  "nodes_upserted": 15,
  "edges_upserted": 12,
  "caller": "manual-run",
  "timestamp": "2026-01-20T12:45:30.123Z",
  "errors": [
    "Nodes batch 500-1000 error: Foreign key violation",
    "Edges batch 0-500 error: Unique constraint violation"
  ]
}
```

**Error (HTTP 400/500)**:
```json
{
  "success": false,
  "error": "Missing required field: source",
  "message": "Detailed error message"
}
```

---

## Deployment

### Prerequisites

**Environment Variables** (set via Supabase Dashboard or CLI):
- `SUPABASE_URL` - Automatically provided by Supabase
- `SUPABASE_SERVICE_ROLE_KEY` - Automatically provided by Supabase

### Deploy Edge Function

```bash
# Deploy via Supabase CLI
supabase functions deploy memory-ingest --project-ref spdtwktxdalcfigzeqrz

# Verify deployment
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/memory-ingest" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"source":"test","nodes":[],"edges":[]}'

# Expected: {"success":true,"source":"test","nodes_upserted":0,"edges_upserted":0,...}
```

### Deploy Database Schema

**Note**: If not already deployed, run the infra schema migration:

```bash
# Via psql
psql "$POSTGRES_URL" -f supabase/migrations/20260120_infra_schema.sql

# OR via Supabase CLI
supabase db push
```

---

## Integration with Discovery Scripts

All 5 discovery scripts need to be updated to POST their findings to the memory function.

### Update Pattern (Python Example)

**Before**:
```python
# Write to local JSON files
with open('infra/infra_graph/sources/vercel_nodes.json', 'w') as f:
    json.dump(nodes, f, indent=2)
```

**After**:
```python
import os
import requests

# Read from environment or hardcode
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://spdtwktxdalcfigzeqrz.supabase.co')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def ingest_to_memory(source: str, nodes: List[Dict], edges: List[Dict], caller: str = None):
    """Send discovery results to memory ingestion endpoint"""
    url = f"{SUPABASE_URL}/functions/v1/memory-ingest"
    headers = {
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'source': source,
        'nodes': nodes,
        'edges': edges,
        'caller': caller or os.getenv('GITHUB_ACTOR', 'manual-run')
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# After building nodes and edges
result = ingest_to_memory('vercel', nodes, edges, caller='github-actions')
print(f"Ingested: {result['nodes_upserted']} nodes, {result['edges_upserted']} edges")

# Still write to local files for debugging
with open('infra/infra_graph/sources/vercel_nodes.json', 'w') as f:
    json.dump(nodes, f, indent=2)
```

### Update Pattern (Bash Example)

**Before**:
```bash
# Write to local JSON files
echo "$nodes_json" > "$NODES_FILE"
```

**After**:
```bash
# Function to ingest to memory
ingest_to_memory() {
    local source="$1"
    local nodes_json="$2"
    local edges_json="$3"
    local caller="${4:-manual-run}"

    local payload=$(cat <<EOF
{
  "source": "$source",
  "nodes": $nodes_json,
  "edges": $edges_json,
  "caller": "$caller"
}
EOF
)

    curl -s -X POST "$SUPABASE_URL/functions/v1/memory-ingest" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: application/json" \
        -d "$payload"
}

# After building nodes and edges
RESULT=$(ingest_to_memory "digitalocean" "$nodes_json" "$edges_json" "github-actions")
echo "Ingestion result: $RESULT"

# Still write to local files for debugging
echo "$nodes_json" > "$NODES_FILE"
```

---

## Verification

### Query Ingested Data

```sql
-- Check source metadata
SELECT
    id,
    name,
    last_discovered_at,
    discovery_count,
    metadata
FROM infra.sources
ORDER BY last_discovered_at DESC NULLS LAST;

-- Check ingested nodes
SELECT
    source,
    kind,
    COUNT(*) as count,
    MAX(discovered_at) as last_discovery
FROM infra.nodes
GROUP BY source, kind
ORDER BY source, kind;

-- Check ingested edges
SELECT
    source,
    type,
    COUNT(*) as count,
    MAX(discovered_at) as last_discovery
FROM infra.edges
GROUP BY source, type
ORDER BY source, type;

-- Check recent snapshots
SELECT
    snapshot_at,
    sources,
    node_count,
    edge_count,
    metadata->>'caller' as caller,
    metadata->'has_errors' as has_errors
FROM infra.snapshots
ORDER BY snapshot_at DESC
LIMIT 10;
```

### Test Memory Function

```bash
# Test with empty data
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/memory-ingest" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "nodes": [],
    "edges": [],
    "caller": "manual-test"
  }'

# Test with sample data
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/memory-ingest" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "nodes": [
      {
        "id": "test:project:sample-1",
        "source": "test",
        "kind": "project",
        "key": "sample-1",
        "name": "Sample Project",
        "props": {"status": "active"}
      }
    ],
    "edges": [
      {
        "id": "test:project:sample-1→test:database:db-1",
        "source": "test",
        "from_id": "test:project:sample-1",
        "to_id": "test:database:db-1",
        "type": "USES_DATABASE",
        "props": {"connection_type": "pooled"}
      }
    ],
    "caller": "manual-test"
  }'
```

---

## Monitoring & Alerts

### Key Metrics

Monitor these metrics for memory ingestion health:

1. **Ingestion Success Rate**: `snapshots.metadata->>'has_errors' = false`
2. **Ingestion Latency**: Time between discovery script start and snapshot creation
3. **Node/Edge Count Growth**: Track `infra.nodes` and `infra.edges` row counts over time
4. **Batch Errors**: Check `snapshots.metadata->'errors'` for failed batches

### Alert Queries

```sql
-- Alert: Ingestion failures in last 24 hours
SELECT
    snapshot_at,
    sources,
    metadata->'errors' as errors
FROM infra.snapshots
WHERE
    snapshot_at > NOW() - INTERVAL '24 hours'
    AND (metadata->>'has_errors')::boolean = true
ORDER BY snapshot_at DESC;

-- Alert: Stale sources (no discovery in 7 days)
SELECT
    id,
    name,
    last_discovered_at,
    NOW() - last_discovered_at as staleness
FROM infra.sources
WHERE
    last_discovered_at < NOW() - INTERVAL '7 days'
    OR last_discovered_at IS NULL
ORDER BY last_discovered_at NULLS FIRST;

-- Alert: Unexpected node/edge count drops
WITH recent_snapshots AS (
    SELECT
        snapshot_at,
        sources[1] as source,
        node_count,
        edge_count,
        LAG(node_count) OVER (PARTITION BY sources[1] ORDER BY snapshot_at) as prev_node_count,
        LAG(edge_count) OVER (PARTITION BY sources[1] ORDER BY snapshot_at) as prev_edge_count
    FROM infra.snapshots
    WHERE snapshot_at > NOW() - INTERVAL '7 days'
)
SELECT
    snapshot_at,
    source,
    node_count,
    prev_node_count,
    node_count - prev_node_count as node_delta,
    edge_count,
    prev_edge_count,
    edge_count - prev_edge_count as edge_delta
FROM recent_snapshots
WHERE
    prev_node_count IS NOT NULL
    AND (
        node_count < prev_node_count * 0.5  -- 50% drop
        OR edge_count < prev_edge_count * 0.5
    )
ORDER BY snapshot_at DESC;
```

---

## Troubleshooting

### Error: "Missing required field: source"
**Cause**: Request payload missing `source` field
**Fix**: Ensure discovery script includes `source` in POST body

### Error: "Foreign key violation"
**Cause**: Node ID referenced in edge doesn't exist
**Fix**: Ensure nodes are upserted before edges, verify node ID format

### Error: "Unique constraint violation"
**Cause**: Duplicate node/edge IDs in single batch
**Fix**: Deduplicate IDs in discovery script before ingestion

### HTTP 207 Partial Success
**Cause**: Some batches failed (check `errors` array in response)
**Fix**: Review errors, fix discovery script data quality, retry failed batches

### Slow Ingestion (>30 seconds)
**Cause**: Large dataset, batch size too small, network latency
**Fix**: Increase batch size (max 1000), run discovery closer to Supabase region

---

## Production Checklist

- [x] Edge Function deployed to Supabase
- [ ] Database schema migration applied
- [ ] Environment variables configured
- [ ] All 5 discovery scripts updated to POST to memory function
- [ ] Test ingestion with sample data (empty + real data)
- [ ] Verify RLS policies (service role = full access, authenticated = read-only)
- [ ] Setup monitoring alerts (stale sources, ingestion failures)
- [ ] Document rollback procedure
- [ ] Test error handling (malformed data, duplicate IDs)
- [ ] Verify snapshot creation and audit trail

---

**Last Updated**: 2026-01-20
**Status**: Ready for deployment
**Next Step**: Deploy Edge Function and update discovery scripts
