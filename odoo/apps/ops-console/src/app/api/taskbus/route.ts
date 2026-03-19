import { NextResponse } from 'next/server'

const SUPABASE_URL = process.env.SUPABASE_URL
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

interface TaskBusStats {
  queued: number
  processing: number
  completed: number
  failed: number
  dlqCount: number
}

interface TaskBusJob {
  id: string
  source: string
  jobType: string
  status: string
  priority: number
  createdAt: string
  updatedAt: string
  payload?: Record<string, unknown>
}

async function supabaseQuery(path: string): Promise<any> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return null
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      Authorization: `Bearer ${SUPABASE_KEY}`,
      apikey: SUPABASE_KEY,
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  })
  if (!res.ok) return null
  return res.json()
}

// Fallback data for when Supabase is not configured
const FALLBACK_JOBS: TaskBusJob[] = [
  { id: 'tb-1', source: 'odoo-copilot', jobType: 'tool_execution', status: 'completed', priority: 5, createdAt: '2026-03-15T09:30:00Z', updatedAt: '2026-03-15T09:30:02Z' },
  { id: 'tb-2', source: 'n8n', jobType: 'webhook_sync', status: 'completed', priority: 3, createdAt: '2026-03-15T09:28:00Z', updatedAt: '2026-03-15T09:28:05Z' },
  { id: 'tb-3', source: 'github-actions', jobType: 'ci_pipeline', status: 'processing', priority: 7, createdAt: '2026-03-15T09:35:00Z', updatedAt: '2026-03-15T09:35:00Z' },
  { id: 'tb-4', source: 'mcp-coordinator', jobType: 'agent_routing', status: 'completed', priority: 5, createdAt: '2026-03-15T09:25:00Z', updatedAt: '2026-03-15T09:25:01Z' },
  { id: 'tb-5', source: 'kb-search', jobType: 'index_query', status: 'completed', priority: 3, createdAt: '2026-03-15T09:20:00Z', updatedAt: '2026-03-15T09:20:03Z' },
  { id: 'tb-6', source: 'foundry', jobType: 'llm_inference', status: 'failed', priority: 5, createdAt: '2026-03-15T09:15:00Z', updatedAt: '2026-03-15T09:15:10Z' },
  { id: 'tb-7', source: 'slack-agent', jobType: 'notification', status: 'completed', priority: 2, createdAt: '2026-03-15T09:10:00Z', updatedAt: '2026-03-15T09:10:01Z' },
  { id: 'tb-8', source: 'odoo-copilot', jobType: 'search_docs', status: 'queued', priority: 5, createdAt: '2026-03-15T09:40:00Z', updatedAt: '2026-03-15T09:40:00Z' },
]

const FALLBACK_STATS: TaskBusStats = { queued: 2, processing: 1, completed: 45, failed: 3, dlqCount: 1 }

export async function GET() {
  // Try Supabase live data
  if (SUPABASE_URL && SUPABASE_KEY) {
    try {
      const [jobs, stats] = await Promise.all([
        supabaseQuery('mcp_jobs.jobs?order=created_at.desc&limit=50&select=id,source,job_type,status,priority,created_at,updated_at'),
        supabaseQuery('rpc/get_job_stats'),
      ])

      if (jobs) {
        const mapped: TaskBusJob[] = jobs.map((j: any) => ({
          id: j.id,
          source: j.source,
          jobType: j.job_type,
          status: j.status,
          priority: j.priority,
          createdAt: j.created_at,
          updatedAt: j.updated_at,
        }))

        const dlqRes = await supabaseQuery('mcp_jobs.dead_letter_queue?select=id&resolved=eq.false')
        const dlqCount = Array.isArray(dlqRes) ? dlqRes.length : 0

        return NextResponse.json({
          jobs: mapped,
          stats: stats || {
            queued: mapped.filter(j => j.status === 'queued').length,
            processing: mapped.filter(j => j.status === 'processing').length,
            completed: mapped.filter(j => j.status === 'completed').length,
            failed: mapped.filter(j => j.status === 'failed').length,
            dlqCount,
          },
          source: 'supabase',
          fetchedAt: new Date().toISOString(),
        })
      }
    } catch {
      // Fall through to fallback
    }
  }

  return NextResponse.json({
    jobs: FALLBACK_JOBS,
    stats: FALLBACK_STATS,
    source: 'fallback',
    fetchedAt: new Date().toISOString(),
  })
}
