# Plan: Supabase Platform Kit Observability

## Implementation Phases

### Phase 1: Schema Foundation

**Deliverables:**
- `db/migrations/20260121_observability_schema.sql` - Complete schema
- RLS policies for all tables
- RPC functions for job/agent operations

**Key Tables:**
```sql
observability.jobs          -- Unified job queue
observability.job_runs      -- Execution history
observability.job_events    -- Granular event log
observability.dead_letter   -- Failed jobs
observability.services      -- Service registry
observability.service_health -- Health samples
observability.edges         -- Topology graph
```

### Phase 2: API Layer

**Deliverables:**
- `apps/control-room/app/api/observability/` - API routes
- `apps/control-room/app/api/ai/sql/route.ts` - AI SQL generation

**Endpoints:**
```
GET  /api/observability/jobs
GET  /api/observability/jobs/[id]
POST /api/observability/jobs/[id]/retry
GET  /api/observability/agents
POST /api/observability/agents/[id]/heartbeat
GET  /api/observability/health
GET  /api/observability/topology
POST /api/ai/sql
```

### Phase 3: Platform Kit Integration

**Deliverables:**
- `apps/control-room/src/components/observability/ObservabilityManager.tsx`
- Custom tabs: Jobs, Agents, Health, Topology

**Component Structure:**
```
ObservabilityManager (Dialog/Drawer)
├── TabsContainer
│   ├── JobsTab
│   │   ├── JobFilters
│   │   ├── JobsTable
│   │   └── JobDetailSheet
│   ├── AgentsTab
│   │   ├── AgentFilters
│   │   ├── AgentsTable
│   │   └── AgentDetailSheet
│   ├── HealthTab
│   │   ├── HealthSummary
│   │   ├── ServiceGrid
│   │   └── ConnectivityMatrix
│   └── TopologyTab
│       ├── GraphControls
│       └── EcosystemGraph
└── AIQueryPanel (optional)
```

### Phase 4: Topology Visualization

**Deliverables:**
- `apps/control-room/src/components/observability/TopologyGraph.tsx`
- D3.js/React Flow based graph rendering

**Node Types:**
- Services (Odoo, n8n, MCP, Supabase)
- Agents (AI agents from registry)
- Databases (PostgreSQL instances)
- External (APIs, webhooks)

**Edge Types:**
- Data flow (sync/async)
- Health dependency
- Agent delegation

### Phase 5: AI SQL Integration

**Deliverables:**
- OpenAI integration for SQL generation
- Schema introspection for prompt context
- Query execution and result display

## File Structure

```
apps/control-room/
├── app/
│   └── api/
│       ├── observability/
│       │   ├── jobs/
│       │   │   ├── route.ts
│       │   │   └── [id]/
│       │   │       ├── route.ts
│       │   │       └── retry/route.ts
│       │   ├── agents/
│       │   │   ├── route.ts
│       │   │   └── [id]/
│       │   │       └── heartbeat/route.ts
│       │   ├── health/route.ts
│       │   └── topology/route.ts
│       └── ai/
│           └── sql/route.ts
├── src/
│   ├── components/
│   │   └── observability/
│   │       ├── ObservabilityManager.tsx
│   │       ├── JobsTab.tsx
│   │       ├── AgentsTab.tsx
│   │       ├── HealthTab.tsx
│   │       ├── TopologyTab.tsx
│   │       └── TopologyGraph.tsx
│   ├── hooks/
│   │   └── useObservability.ts
│   └── types/
│       └── observability.ts
└── lib/
    └── supabase/
        └── observability.ts

db/migrations/
└── 20260121_observability_schema.sql
```

## Dependencies

**Required packages (add to package.json):**
```json
{
  "@supabase/supabase-js": "^2.x",
  "reactflow": "^11.x",
  "openai": "^4.x"
}
```

**Environment variables:**
```env
NEXT_PUBLIC_SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
OPENAI_API_KEY=
NEXT_PUBLIC_ENABLE_AI_QUERIES=true
```

## Verification Checklist

- [ ] Schema migration applies cleanly
- [ ] RLS blocks anon access (test with anon key)
- [ ] Jobs API returns paginated results
- [ ] Agents API returns registry with heartbeats
- [ ] Health API aggregates all services
- [ ] Topology API returns valid graph structure
- [ ] AI SQL generates valid queries
- [ ] Manager dialog opens on desktop and mobile
- [ ] All tabs render without errors
- [ ] Topology graph renders without cycles
