# Supabase Memory Integration

**Purpose**: Central AI agent memory store with vector search, integrated with Superset, n8n, MCP, and Vercel.

**Stack**: Supabase Postgres + pgvector + pg_cron + Superset + n8n + MCP

---

## Architecture

```
┌────────────┐        Realtime         ┌───────────┐
│ Supabase   │ ──────────────────────▶ │ n8n       │
│ (Postgres) │                         │ (ETL)     │
└─────┬──────┘                         └────┬──────┘
      │                                     │
      │ SQL/Vector                          │ Webhook/Queue
      ▼                                     ▼
┌────────────┐     Retrieval API     ┌───────────────┐
│ Superset   │ ◀──────────────────── │ MCP Memory    │
│ (Dashboards│                       │ Server        │
└────────────┘                       └───────────────┘
     ▲                                       │
     │ HTTP                                  │ Tool Call
     │                                       ▼
┌──────────────┐                       ┌────────────┐
│ Vercel Apps  │◀─────────────────────▶│ Claude /   │
│ (Frontends)  │    Inference/Context  │ Codex       │
└──────────────┘                       └────────────┘
```

---

## Schema Overview

**Database**: Supabase Postgres (project: spdtwktxdalcfigzeqrz)
**Schema**: `ipai_memory`

### Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `sessions` | Agent execution sessions | `agent_id`, `topic`, `started_at` |
| `chunks` | Retrievable memory units | `topic`, `content`, `importance` |
| `chunk_embeddings` | Vector representations | `embedding` (1536-dim), `model` |
| `distilled` | Long-term stable knowledge | `topic`, `content`, `source_chunks` |

### RPC Functions

| Function | Purpose | Parameters |
|----------|---------|------------|
| `add_memory` | Add memory chunk with optional embedding | `agent_id`, `topic`, `content`, `importance`, `embedding`, `model` |
| `search_memory` | Hybrid vector+text search | `query_vector`, `query_text`, `topic_filter`, `limit` |
| `list_agent_memories` | List recent memories for agent | `agent_id`, `limit` |

### Views (Superset)

| View | Purpose |
|------|---------|
| `v_agent_activity` | Memory activity by agent (session count, chunk count, last active) |
| `v_recent_memories` | Recent memory timeline with preview |
| `v_topic_coverage` | Topic coverage stats (chunk count, avg importance, first/last updated) |

---

## Deployment

### 1. Apply Schema Migration

```bash
# Via Supabase CLI
supabase db push --file db/migrations/ipai_memory_schema.sql

# OR via psql
psql "$SUPABASE_URL" -f db/migrations/ipai_memory_schema.sql

# OR via Supabase Studio SQL Editor
# Copy/paste content of ipai_memory_schema.sql
```

### 2. Verify Installation

```sql
-- Check tables
select schemaname, tablename, rowsecurity
from pg_tables
where schemaname = 'ipai_memory'
order by tablename;

-- Check functions
select routine_name, routine_type
from information_schema.routines
where routine_schema = 'ipai_memory'
order by routine_name;

-- Check test data
select * from ipai_memory.chunks limit 5;
```

---

## Integration Patterns

### A. Local Sandbox → Supabase

**Use case**: Write sandbox discoveries to central memory

**Tool**: `tools/add_memory_to_supabase.py`

```python
#!/usr/bin/env python3
import os
import psycopg2

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Extract DB connection from URL
# postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
DSN = SUPABASE_URL.replace("https://", "postgresql://postgres:") + ":5432/postgres"

def add_memory(agent_id: str, topic: str, content: str, importance: int = 3):
    """Add memory chunk to Supabase"""
    conn = psycopg2.connect(DSN)
    cur = conn.cursor()

    cur.execute(
        "select ipai_memory.add_memory(%s, %s, %s, %s)",
        (agent_id, topic, content, importance)
    )
    chunk_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return chunk_id

if __name__ == "__main__":
    # Example: sandbox baseline
    chunk_id = add_memory(
        agent_id="odoo-dev-sandbox",
        topic="sandbox-baseline",
        content="""
        Odoo 18 CE sandbox baseline:
        - URL: http://localhost:8069/web/login
        - Database: odoo_dev_sandbox
        - Custom modules: ipai_hello only
        - Credentials: admin/admin
        """,
        importance=5
    )
    print(f"Memory added: {chunk_id}")
```

**Usage**:
```bash
cd ~/Documents/GitHub/odoo-ce
python3 tools/add_memory_to_supabase.py
```

### B. Superset Dashboards

**Connection settings**:
- **Type**: PostgreSQL
- **Host**: `db.<project-ref>.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres` (or create `superset_readonly` role)
- **Schema**: `ipai_memory`

**Pre-built views for dashboards**:
1. `v_agent_activity` - Agent usage metrics
2. `v_recent_memories` - Memory timeline
3. `v_topic_coverage` - Knowledge coverage

**Sample dashboard queries**:

```sql
-- Memory growth over time
select
  date_trunc('day', created_at) as date,
  count(*) as memory_count
from ipai_memory.chunks
group by date
order by date desc;

-- Top topics by importance
select
  topic,
  count(*) as count,
  avg(importance) as avg_importance
from ipai_memory.chunks
group by topic
order by avg_importance desc, count desc
limit 10;

-- Agent activity heatmap
select
  agent_id,
  date_trunc('hour', started_at) as hour,
  count(*) as session_count
from ipai_memory.sessions
where started_at > now() - interval '7 days'
group by agent_id, hour
order by hour desc;
```

### C. n8n Workflows

**Webhook trigger** (Supabase Realtime → n8n):

```json
{
  "name": "Memory Ingestion Workflow",
  "nodes": [
    {
      "name": "Supabase Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "supabase-memory-insert"
      }
    },
    {
      "name": "Generate Embedding",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.openai.com/v1/embeddings",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "openAiApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "input", "value": "={{$json.record.content}}"},
            {"name": "model", "value": "text-embedding-3-small"}
          ]
        }
      }
    },
    {
      "name": "Update Embedding",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO ipai_memory.chunk_embeddings (chunk_id, embedding, model) VALUES ($1, $2::vector, $3)",
        "queryParameters": [
          "={{$json.chunk_id}}",
          "={{JSON.stringify($('Generate Embedding').item.json.data[0].embedding)}}",
          "text-embedding-3-small"
        ]
      }
    }
  ]
}
```

**Scheduled job** (pg_cron alternative via n8n):

```json
{
  "name": "Daily Memory Distillation",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 2 * * *"
      }
    },
    {
      "name": "Query Recent Chunks",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT topic, array_agg(content) as contents, array_agg(id) as chunk_ids FROM ipai_memory.chunks WHERE created_at > now() - interval '1 day' GROUP BY topic"
      }
    },
    {
      "name": "Claude Summarize",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {"name": "model", "value": "claude-3-5-sonnet-20241022"},
            {"name": "max_tokens", "value": 2000},
            {"name": "messages", "value": "[{\"role\":\"user\",\"content\":\"Summarize these memory chunks into a concise distilled summary:\\n{{$json.contents.join('\\n\\n')}}\"}]"}
          ]
        }
      }
    },
    {
      "name": "Upsert Distilled",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO ipai_memory.distilled (topic, content, source_chunks) VALUES ($1, $2, $3) ON CONFLICT (topic) DO UPDATE SET content = $2, source_chunks = $3, last_updated = now()",
        "queryParameters": [
          "={{$json.topic}}",
          "={{$('Claude Summarize').item.json.content[0].text}}",
          "={{JSON.stringify($json.chunk_ids)}}"
        ]
      }
    }
  ]
}
```

### D. MCP Memory Server

**Configuration** (`~/.mcp/config.json`):

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_BACKEND": "postgres",
        "POSTGRES_URL": "postgresql://postgres:[PASSWORD]@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres"
      }
    }
  }
}
```

**Usage from Claude/Codex**:

```
User: "Remember that the Odoo sandbox baseline is ipai_hello only"

Agent: [Calls MCP memory tool]
{
  "tool": "memory_add",
  "params": {
    "agent_id": "claude-web",
    "topic": "odoo-sandbox-baseline",
    "content": "Canonical Odoo 18 CE sandbox: only ipai_hello custom module, URL: localhost:8069, DB: odoo_dev_sandbox"
  }
}

User: "What's the sandbox baseline?"

Agent: [Calls MCP memory tool]
{
  "tool": "memory_search",
  "params": {
    "query_text": "sandbox baseline",
    "limit": 3
  }
}
→ Returns: "Canonical Odoo 18 CE sandbox: only ipai_hello custom module..."
```

### E. Vercel Apps

**Server-side memory access** (Next.js API route):

```typescript
// app/api/memory/search/route.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // server-side only
);

export async function POST(req: Request) {
  const { query } = await req.json();

  const { data, error } = await supabase
    .rpc('ipai_memory.search_memory', {
      p_query_text: query,
      p_limit: 5
    });

  if (error) return Response.json({ error }, { status: 500 });
  return Response.json({ memories: data });
}
```

**Client-side display** (with RLS):

```typescript
// components/MemorySearch.tsx
'use client';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // public, RLS-protected
);

export function MemorySearch() {
  const [memories, setMemories] = useState([]);

  const search = async (query: string) => {
    const { data } = await supabase
      .from('ipai_memory.v_recent_memories')
      .select('*')
      .textSearch('content_preview', query)
      .limit(10);

    setMemories(data || []);
  };

  return (/* UI */);
}
```

---

## Security

### Roles

| Role | Purpose | Permissions |
|------|---------|-------------|
| `superset_readonly` | Superset dashboards | SELECT on all tables/views |
| `n8n_service` | n8n ETL workflows | SELECT, INSERT, UPDATE + EXECUTE on functions |
| `mcp_agent` | MCP memory server | EXECUTE on RPC functions only |

### Row-Level Security (RLS)

**Policy**: `agent_isolation` on `chunks` table
- Agents only see memories from sessions where `agent_id` matches `current_setting('app.agent_id')`
- Set via connection parameter: `SET app.agent_id = 'odoo-sandbox';`

**Bypass RLS** (for n8n/Superset):
```sql
-- n8n uses service role with RLS bypass
grant bypassrls on ipai_memory.chunks to n8n_service;
```

---

## Maintenance

### Auto-Vacuum (pg_cron)

Configured via `ipai_memory_schema.sql`:

```sql
-- Daily at 2 AM: Delete sessions older than 30 days
select cron.schedule(
  'vacuum-old-sessions',
  '0 2 * * *',
  'delete from ipai_memory.sessions where finished_at < now() - interval ''30 days''...'
);
```

**Check cron jobs**:
```sql
select * from cron.job;
select * from cron.job_run_details order by start_time desc limit 10;
```

### Manual Cleanup

```sql
-- Remove low-importance chunks older than 7 days
delete from ipai_memory.chunks
where importance <= 2
  and created_at < now() - interval '7 days';

-- Vacuum embeddings table
vacuum full ipai_memory.chunk_embeddings;
```

---

## Troubleshooting

### Extensions not available

**Symptom**: `ERROR: extension "vector" does not exist`

**Fix**: Enable in Supabase Studio
1. Go to Database → Extensions
2. Enable: `vector`, `pg_cron`, `pg_stat_statements`

### RPC function not found

**Symptom**: `ERROR: function ipai_memory.add_memory does not exist`

**Fix**: Re-apply migration
```bash
psql "$SUPABASE_URL" -f db/migrations/ipai_memory_schema.sql
```

### Vector search slow

**Symptom**: `search_memory` takes >1s for 1K rows

**Fix**: Rebuild IVFFlat index
```sql
-- Drop and recreate with more lists
drop index ipai_memory.idx_chunk_embeddings_vector;
create index idx_chunk_embeddings_vector
  on ipai_memory.chunk_embeddings
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 1000);  -- increase for larger datasets
```

### Memory not persisting across sessions

**Symptom**: Chunks disappear after session ends

**Fix**: Check cascade deletes
```sql
-- Verify session still exists
select * from ipai_memory.sessions where id = '<session-id>';

-- If session was deleted, chunks cascade
-- Fix: Set finished_at instead of deleting
update ipai_memory.sessions set finished_at = now() where id = '<session-id>';
```

---

## Next Steps

1. **Deploy schema**: `psql "$SUPABASE_URL" -f db/migrations/ipai_memory_schema.sql`
2. **Configure Superset**: Add ipai_memory schema connection
3. **Setup n8n workflows**: Import memory ingestion + distillation flows
4. **Configure MCP**: Point memory server to Supabase
5. **Test integration**: Add test memory from local sandbox

---

**Related Documentation**:
- Supabase Postgres: https://supabase.com/docs/guides/database
- pgvector: https://github.com/pgvector/pgvector
- MCP Memory Server: https://github.com/modelcontextprotocol/servers/tree/main/src/memory
- Anthropic Contextual Retrieval: https://www.anthropic.com/engineering/contextual-retrieval
