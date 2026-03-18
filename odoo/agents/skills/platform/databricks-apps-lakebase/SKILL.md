# Skill: Databricks Apps + Lakebase — Full-Stack AI Applications

## Metadata

| Field | Value |
|-------|-------|
| **id** | `databricks-apps-lakebase` |
| **domain** | `lakehouse` |
| **source** | Databricks "Hands-On Guide to Apps on Databricks" (2026) |
| **extracted** | 2026-03-15 |
| **applies_to** | lakehouse, agents, web |
| **tags** | databricks-apps, lakebase, neon, postgres, synced-tables, reverse-etl, dabs, ai-agents, conversational-memory |

---

## What They Are

**Databricks Apps**: Serverless application hosting for Python/Node.js web apps (Streamlit, Dash, Flask, FastAPI, React). Built-in OAuth, Unity Catalog governance, zero infrastructure management.

**Lakebase**: Fully managed PostgreSQL database integrated with the lakehouse. Based on Neon (acquired by Databricks). Provides OLTP alongside OLAP — synced tables bridge Delta Lake analytics to low-latency Postgres.

Together: Build full-stack data + AI applications without leaving the platform.

## Architecture

```
Unity Catalog (Delta Tables)
        │
        │ Synced Tables (snapshot/triggered/continuous)
        ▼
Lakebase (Managed Postgres)
    ├── Read: Synced analytical data (read-only)
    ├── Write: Application state, user inputs, agent memory
    └── Extensions: pgvector, PostGIS, pg_stat_statements
        │
        │ OAuth M2M / OBO authentication
        ▼
Databricks Apps (Serverless)
    ├── React + FastAPI (or Streamlit/Dash/Flask)
    ├── Built-in identity (service principal per app)
    └── Unity Catalog governance applied automatically
        │
        │ DABs (single-command deploy)
        ▼
Production (dev → staging → prod)
```

## Lakebase Sync Modes

| Mode | Update Method | Latency | Best For |
|------|--------------|---------|----------|
| **SNAPSHOT** | Full table replacement each run | High (scheduled) | Infrequent changes, >10% data modified |
| **TRIGGERED** | Initial full copy + incremental | Medium (on-demand) | Balanced cost/latency |
| **CONTINUOUS** | Initial load + real-time streaming | ~15 sec | Mission-critical, real-time requirements |

## Lakebase vs Traditional OLTP

| Traditional | Lakebase |
|-------------|---------|
| Separate hosting infrastructure | Serverless, zero infra management |
| Custom authentication | Built-in OAuth + Unity Catalog |
| Manual data sync pipelines | Automated synced tables |
| Fragmented governance | Unified governance via Unity Catalog |
| Complex multi-tool deployment | Single-command DABs deploy |
| Hours to provision | Milliseconds to branch |

## Key Capabilities

### Synced Tables (Reverse ETL Built-In)

```sql
-- Defined in DABs YAML:
resources:
  synced_database_tables:
    trips-synced:
      name: main.default.trips_synced
      database_instance_name: my-instance
      logical_database_name: my-database
      spec:
        source_table_full_name: main.default.trips
        scheduling_policy: CONTINUOUS  # or SNAPSHOT, TRIGGERED
        primary_key_columns:
          - id
```

No custom ETL pipelines needed. Delta table changes flow to Postgres automatically.

### OAuth Authentication (Python)

```python
from databricks.sdk import WorkspaceClient
import psycopg

workspace_client = WorkspaceClient()
token = workspace_client.config.oauth_token().access_token

conn = psycopg.connect(
    host=os.getenv("PGHOST"),
    port=5432,
    dbname="my_database",
    user=os.getenv("DATABRICKS_CLIENT_ID"),
    password=token,
    sslmode="require",
)
```

### DABs Deployment (Infrastructure as Code)

```yaml
# databricks.yml
bundle:
  name: my-app
include:
  - resources/*.yml
targets:
  dev:
    default: true
    mode: development
    workspace:
      host: https://company-dev.cloud.databricks.com/
  prod:
    mode: production
    workspace:
      host: https://company.cloud.databricks.com/
```

Deploy everything with one command: `databricks bundle deploy -t prod`

### Database Branching (Neon-Powered)

- Millisecond-scale database branching for test environments
- 80% of databases now created by AI agents (Databricks telemetry)
- 97% of database branches created by AI agents
- Copy-on-write: branches share storage until divergence

## AI Agent Memory with Lakebase

### Why Conversational Memory Matters

Agents need persistent state across conversations:
- Session history (what was discussed)
- User preferences (learned over time)
- Task state (multi-step workflows in progress)
- Tool results (cached for reuse)

### Memory Patterns

| Pattern | Description | Table Design |
|---------|-------------|-------------|
| **Buffer memory** | Last N messages | `conversations(id, agent_id, messages JSONB, updated_at)` |
| **Summary memory** | LLM-generated summaries | `memory_summaries(id, conversation_id, summary TEXT)` |
| **Entity memory** | Extracted entities | `entities(id, conversation_id, entity_type, entity_value)` |
| **Vector memory** | Embedded for semantic search | `memory_vectors(id, content, embedding vector(1536))` with pgvector |

### Agent Memory Schema

```sql
CREATE TABLE agent_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES agent_conversations(id),
    memory_type TEXT NOT NULL, -- 'summary', 'entity', 'preference'
    content TEXT NOT NULL,
    embedding vector(1536),   -- pgvector for semantic search
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_memory_embedding ON agent_memory
    USING ivfflat (embedding vector_cosine_ops);
```

### Agent State Management

```python
# Save agent state to Lakebase
def save_agent_state(agent_id, conversation_id, state):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO agent_state (agent_id, conversation_id, state, updated_at)
            VALUES (:agent_id, :conv_id, :state, now())
            ON CONFLICT (agent_id, conversation_id)
            DO UPDATE SET state = :state, updated_at = now()
        """), {"agent_id": agent_id, "conv_id": conversation_id,
               "state": json.dumps(state)})

# Restore agent state
def load_agent_state(agent_id, conversation_id):
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT state FROM agent_state
            WHERE agent_id = :agent_id AND conversation_id = :conv_id
        """), {"agent_id": agent_id, "conv_id": conversation_id})
        row = result.fetchone()
        return json.loads(row[0]) if row else {}
```

## Reverse ETL: Analytics → Applications

### Traditional Reverse ETL Challenges
- Brittle custom ETL pipelines
- Multiple disconnected systems
- Inconsistent governance models

### Lakebase Solution
- **Deep lakehouse integration**: Synced tables replace custom pipelines
- **Fully managed Postgres**: ACID, indexes, joins, extensions
- **Scalable architecture**: Sub-10ms latency, thousands of QPS, multi-AZ HA
- **Integrated governance**: Unity Catalog for audit + permissions
- **Cloud-agnostic**: Deploy in any cloud alongside lakehouse

### Reverse ETL Pattern

```
Lakehouse Gold Tables (curated insights)
        │
        │ Synced Tables (managed pipeline)
        ▼
Lakebase (operational Postgres)
        │
        │ App queries via OAuth
        ▼
Applications (support portal, AI assistant, dashboard)
```

## Real-World Patterns from Guide

### 1. Taxi Trip Dashboard (React + FastAPI)
- Synced table mirrors Delta table in real-time
- React polls FastAPI every 3 seconds for updates
- Insert new rows in Delta → appears in app within seconds

### 2. Holiday Request Approval (Streamlit)
- Lakebase stores application state (requests, approvals)
- Managers approve/reject via web UI
- SQLAlchemy + Databricks SDK for secure connection

### 3. Intelligent Support Portal (Flask)
- ML predictions synced from lakehouse (continuous mode)
- User updates stored in separate Lakebase table
- Combines analytics + operations in one app

### 4. Campaign Metrics Dashboard (Streamlit)
- CI/CD via GitHub Actions + DABs
- OAuth OBO for user-level permissions
- Unity Catalog governance applied automatically

### 5. AI Agent with Conversational Memory
- Lakebase as state layer for agent conversations
- pgvector for semantic memory search
- Buffer + summary + entity memory patterns

## IPAI Relevance Map

| Databricks Pattern | IPAI Equivalent | Gap/Action |
|-------------------|-----------------|------------|
| Databricks Apps (serverless) | ACA-hosted apps | Evaluate for copilot UI |
| Lakebase (managed Postgres) | Azure PG Flexible Server | Lakebase adds synced tables + branching |
| Synced Tables | Custom ETL (planned) | **Adopt**: eliminates our ETL gap |
| DABs (IaC deploy) | Bicep + GitHub Actions | DABs is simpler for Databricks resources |
| OAuth M2M | Managed identity (ACA) | Aligned pattern |
| Agent memory in Lakebase | ops.runs in Supabase | **Consider**: Lakebase for agent state |
| Database branching | Manual `test_<module>` creation | **Adopt**: agent-driven test DB creation |
| Reverse ETL built-in | Planned (n8n + custom) | **Adopt**: Lakebase replaces custom reverse ETL |
| pgvector | Supabase pgvector | Both support it — Lakebase unifies with lakehouse |

### Decision: Lakebase vs Supabase for Agent State

| Criteria | Lakebase | Supabase |
|----------|---------|----------|
| Lakehouse integration | Native (synced tables) | Manual ETL |
| Agent memory patterns | Built-in examples | DIY |
| Database branching | Millisecond (Neon) | Not supported |
| Edge Functions | No | Yes (Deno) |
| Realtime subscriptions | No | Yes (WebSocket) |
| Self-hosted option | No (Databricks-managed) | Yes (Azure VM) |
| Auth system | Databricks OAuth | Supabase Auth |

**Recommendation**: Keep Supabase as SSOT (control plane, Edge Functions, Realtime). Use Lakebase for lakehouse-proximate workloads (synced tables, agent memory near analytics, reverse ETL). Don't replace one with the other — they serve different layers.

### Priority Actions

1. **Provision Lakebase instance** in `dbw-ipai-dev` workspace
2. **Create synced table** for `account.move` (journal entries) — eliminates need for custom ETL
3. **Deploy first Databricks App** — Superset alternative for specific dashboards
4. **Add agent memory tables** — buffer + summary patterns for copilot
5. **Enable database branching** — agents create `test_<module>` branches in milliseconds
