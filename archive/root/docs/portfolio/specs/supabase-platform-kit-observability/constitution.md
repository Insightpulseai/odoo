# Constitution: Supabase Platform Kit Observability

## Purpose

Unified agent orchestration, job bus, MCP observability, and ecosystem health monitoring built on Supabase Platform Kit foundation.

## Non-Negotiables

### Architecture Constraints

1. **Platform Kit First** - All database/logs/secrets management uses Supabase Platform Kit dialog pattern
2. **Schema Isolation** - Custom tables live in `observability` schema, separate from `agent_coordination`
3. **No UI Duplication** - Extend Platform Kit dialog, do not rebuild parallel UIs
4. **Supabase Only** - All state stored in Supabase PostgreSQL, no local state files

### Data Constraints

1. **Event Sourcing** - All state changes emit events to `observability.events` table
2. **Immutable Logs** - Never update/delete event records, only append
3. **Soft Deletes** - All entities use `deleted_at` timestamp, never hard delete
4. **JSON Schema** - All `payload`/`context` JSONB fields validated against registered schemas

### Security Constraints

1. **RLS Always** - Row-Level Security enabled on all tables
2. **Service Role Only** - Management API uses service_role key, never anon
3. **Audit Trail** - All mutations logged with `actor_id`, `action`, `timestamp`

### Performance Constraints

1. **Pagination Required** - All list endpoints paginated (max 100 per page)
2. **Index Coverage** - All query patterns have covering indexes
3. **Heartbeat TTL** - Stale agents/services marked offline after 5 minutes

## Integration Points

| Component | Protocol | Port | Health Endpoint |
|-----------|----------|------|-----------------|
| Control Room API | HTTP | 8789 | `/health` |
| MCP Coordinator | HTTP | 8766 | `/health` |
| Odoo Core | HTTP | 8069 | `/web/health` |
| n8n | HTTP | 5678 | `/healthz` |
| Supabase | HTTP | 443 | `/rest/v1/` |

## Canonical Schemas

### Job States (FSM)

```
queued → processing → completed
           ↓
         failed → retrying → queued
           ↓
         dead_letter
```

### Agent States (FSM)

```
registering → active → busy → idle
                ↓        ↓
             offline ← maintenance
```

### Service Health States

```
healthy → degraded → unhealthy → offline
    ↑_________|_________|
```

## Verification Gates

1. Schema migration applies without errors
2. RLS policies block anon access
3. RPC functions return expected types
4. Health check aggregates all services
5. Topology graph renders without cycles
