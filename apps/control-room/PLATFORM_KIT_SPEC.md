# IPAI Platform Kit - Control Room Orchestration

Integration of Supabase Platform Kit patterns for unified ecosystem management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      IPAI Control Room                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    Bird's Eye View Dashboard                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │ Odoo CE  │  │ Superset │  │   n8n    │  │   MCP    │           │ │
│  │  │  Health  │  │  Health  │  │  Health  │  │  Health  │           │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │ │
│  └───────┼─────────────┼─────────────┼─────────────┼─────────────────┘ │
│          │             │             │             │                    │
│  ┌───────▼─────────────▼─────────────▼─────────────▼─────────────────┐ │
│  │                    MCP Jobs Observability                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │  Job Queue   │  │  Job Runs    │  │  Dead Letter │             │ │
│  │  │  Dashboard   │  │  Timeline    │  │    Queue     │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    Agent Orchestration                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │ │
│  │  │   Odoo     │  │  Superset  │  │  Digital   │  │   Pulser   │   │ │
│  │  │ MCP Server │  │ MCP Server │  │  Ocean MCP │  │ MCP Server │   │ │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Supabase Backend                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │  mcp_jobs    │  │  realtime    │  │   pgvector   │                   │
│  │   schema     │  │  subscriptions│  │  embeddings  │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components from Supabase Platform Kit

### 1. Manager Dialog Pattern

```tsx
// Similar to SupabaseManagerDialog but for IPAI ecosystem
<IPAIManagerDialog
  projectRef="ipai-production"
  open={open}
  onOpenChange={setOpen}
  isMobile={isMobile}
  tabs={['overview', 'jobs', 'agents', 'health', 'logs']}
/>
```

### 2. Tab-based Navigation

| Tab | Supabase Equivalent | IPAI Implementation |
|-----|---------------------|---------------------|
| Overview | Database | Bird's eye view of all services |
| Jobs | Performance | MCP Jobs queue + metrics |
| Agents | Users | MCP server management |
| Health | Logs | Service health endpoints |
| Logs | Logs | Aggregated logs from all services |

### 3. Real-time Updates

Using Supabase Realtime for:
- Job status changes
- Service health updates
- Agent activity feeds

## Installation

```bash
# Add Platform Kit components
npx shadcn@latest add @supabase/platform-kit-nextjs

# Required dependencies (already in control-room)
npm install @supabase/supabase-js @tanstack/react-query
```

## API Routes

### MCP Jobs Proxy

```typescript
// app/api/mcp-jobs/[...path]/route.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function GET(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/')

  // Route to appropriate handler
  switch (path) {
    case 'jobs':
      return getJobs(request)
    case 'jobs/stats':
      return getJobStats()
    case 'dead-letter':
      return getDeadLetterQueue()
    default:
      return new Response('Not found', { status: 404 })
  }
}

async function getJobs(request: Request) {
  const { searchParams } = new URL(request.url)
  const source = searchParams.get('source')
  const status = searchParams.get('status')
  const limit = parseInt(searchParams.get('limit') || '50')

  let query = supabase
    .from('jobs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit)

  if (source) query = query.eq('source', source)
  if (status) query = query.eq('status', status)

  const { data, error } = await query

  if (error) return Response.json({ error: error.message }, { status: 500 })
  return Response.json(data)
}
```

### Service Health Aggregator

```typescript
// app/api/health/route.ts
const SERVICES = [
  { name: 'odoo-core', url: 'http://odoo-core:8069/web/health' },
  { name: 'odoo-marketing', url: 'http://odoo-marketing:8070/web/health' },
  { name: 'odoo-accounting', url: 'http://odoo-accounting:8071/web/health' },
  { name: 'superset', url: process.env.SUPERSET_URL + '/health' },
  { name: 'n8n', url: process.env.N8N_URL + '/healthz' },
  { name: 'mcp-coordinator', url: 'http://mcp-coordinator:8766/health' },
]

export async function GET() {
  const results = await Promise.allSettled(
    SERVICES.map(async (service) => {
      const start = Date.now()
      try {
        const res = await fetch(service.url, {
          signal: AbortSignal.timeout(5000)
        })
        return {
          name: service.name,
          status: res.ok ? 'healthy' : 'unhealthy',
          responseTime: Date.now() - start,
          statusCode: res.status,
        }
      } catch (error) {
        return {
          name: service.name,
          status: 'unreachable',
          responseTime: Date.now() - start,
          error: error instanceof Error ? error.message : 'Unknown error',
        }
      }
    })
  )

  const health = results.map((r, i) =>
    r.status === 'fulfilled' ? r.value : {
      name: SERVICES[i].name,
      status: 'error',
      error: r.reason
    }
  )

  const overallStatus = health.every(h => h.status === 'healthy')
    ? 'healthy'
    : health.some(h => h.status === 'healthy')
      ? 'degraded'
      : 'down'

  return Response.json({ status: overallStatus, services: health })
}
```

## Component Structure

```
apps/control-room/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── mcp-jobs/[...path]/route.ts
│   │   │   ├── health/route.ts
│   │   │   └── agents/route.ts
│   │   ├── (dashboard)/
│   │   │   ├── overview/page.tsx      # Bird's eye view
│   │   │   ├── jobs/page.tsx          # MCP Jobs dashboard
│   │   │   ├── agents/page.tsx        # Agent orchestration
│   │   │   └── health/page.tsx        # Service health
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── platform-kit/              # Adapted from Supabase
│   │   │   ├── IPAIManagerDialog.tsx
│   │   │   ├── TabNavigation.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── observability/
│   │   │   ├── JobQueueCard.tsx
│   │   │   ├── JobRunsTimeline.tsx
│   │   │   ├── DeadLetterQueue.tsx
│   │   │   ├── JobMetrics.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── health/
│   │   │   ├── ServiceHealthGrid.tsx
│   │   │   ├── ServiceCard.tsx
│   │   │   ├── HealthTimeline.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── agents/
│   │       ├── AgentGrid.tsx
│   │       ├── MCPServerCard.tsx
│   │       ├── ToolRegistry.tsx
│   │       └── index.ts
│   │
│   ├── hooks/
│   │   ├── useMCPJobs.ts
│   │   ├── useServiceHealth.ts
│   │   ├── useAgents.ts
│   │   └── useRealtimeSubscription.ts
│   │
│   └── lib/
│       ├── supabase.ts
│       └── mcp-jobs-client.ts
```

## Data Flow

### MCP Jobs Realtime

```typescript
// hooks/useMCPJobs.ts
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export function useMCPJobs(filters?: { source?: string; status?: string }) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['mcp-jobs', filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.source) params.set('source', filters.source)
      if (filters?.status) params.set('status', filters.status)

      const res = await fetch(`/api/mcp-jobs/jobs?${params}`)
      return res.json()
    },
    refetchInterval: 30000, // Fallback polling
  })

  // Realtime subscription
  useEffect(() => {
    const channel = supabase
      .channel('mcp_jobs_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'mcp_jobs', table: 'jobs' },
        () => {
          queryClient.invalidateQueries({ queryKey: ['mcp-jobs'] })
        }
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [queryClient])

  return query
}
```

### Service Health Polling

```typescript
// hooks/useServiceHealth.ts
import { useQuery } from '@tanstack/react-query'

export function useServiceHealth() {
  return useQuery({
    queryKey: ['service-health'],
    queryFn: async () => {
      const res = await fetch('/api/health')
      return res.json()
    },
    refetchInterval: 15000, // Poll every 15s
    staleTime: 10000,
  })
}
```

## UI Patterns

### Bird's Eye View

```tsx
// Inspired by Supabase Platform Kit overview
export function BirdsEyeView() {
  const { data: health } = useServiceHealth()
  const { data: jobStats } = useJobStats()
  const { data: agents } = useAgents()

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* Status Overview */}
      <div className="col-span-12">
        <StatusBanner status={health?.status} />
      </div>

      {/* KPI Row */}
      <div className="col-span-12 grid grid-cols-4 gap-4">
        <KPICard
          title="Services"
          value={health?.services.filter(s => s.status === 'healthy').length}
          total={health?.services.length}
          status={health?.status}
        />
        <KPICard
          title="Jobs (24h)"
          value={jobStats?.completed}
          delta={jobStats?.failed}
          deltaLabel="failed"
        />
        <KPICard
          title="Active Agents"
          value={agents?.filter(a => a.status === 'running').length}
          total={agents?.length}
        />
        <KPICard
          title="Dead Letter"
          value={jobStats?.deadLetter}
          status={jobStats?.deadLetter > 0 ? 'warning' : 'success'}
        />
      </div>

      {/* Service Grid */}
      <div className="col-span-8">
        <ServiceHealthGrid services={health?.services} />
      </div>

      {/* Activity Feed */}
      <div className="col-span-4">
        <ActivityFeed />
      </div>

      {/* Job Queue */}
      <div className="col-span-12">
        <JobQueueOverview />
      </div>
    </div>
  )
}
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Server-side only
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Service URLs (internal)
ODOO_CORE_URL=http://odoo-core:8069
SUPERSET_URL=https://superset.insightpulseai.net
N8N_URL=https://n8n.insightpulseai.net

# AI (optional)
OPENAI_API_KEY=sk-...
NEXT_PUBLIC_ENABLE_AI_QUERIES=true
```

## Security Considerations

1. **API Proxy**: Never expose Supabase service role key to client
2. **Health Endpoints**: Internal services only (via Docker network)
3. **Realtime**: Use RLS policies for job visibility
4. **AI Queries**: Implement permission checks before SQL generation

## Next Steps

1. Install Platform Kit components
2. Create API routes for MCP Jobs and Health
3. Build observability components
4. Add realtime subscriptions
5. Deploy to Vercel (control-room) + DigitalOcean (API proxy)
