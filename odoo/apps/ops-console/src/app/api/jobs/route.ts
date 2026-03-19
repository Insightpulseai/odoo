import { NextResponse } from 'next/server'

const SUPABASE_URL = process.env.SUPABASE_URL
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY
const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const GITHUB_REPO = process.env.GITHUB_REPO || 'Insightpulseai/odoo'

interface Job {
  id: string
  name: string
  type: 'supabase-job' | 'github-action' | 'odoo-cron' | 'n8n-workflow'
  status: 'active' | 'paused' | 'error' | 'running' | 'completed' | 'queued'
  schedule?: string
  lastRun?: string
  nextRun?: string
  workflow?: string
}

async function fetchGitHubWorkflows(): Promise<Job[]> {
  if (!GITHUB_TOKEN) return []
  try {
    const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/actions/runs?per_page=20`, {
      headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json' },
      cache: 'no-store',
    })
    if (!res.ok) return []
    const data = await res.json()
    return (data.workflow_runs || []).slice(0, 10).map((run: any) => ({
      id: `gh-${run.id}`,
      name: run.name,
      type: 'github-action' as const,
      status: run.conclusion === 'success' ? 'completed' : run.conclusion === 'failure' ? 'error' : run.status === 'in_progress' ? 'running' : 'queued',
      lastRun: run.updated_at,
      workflow: run.path?.split('/').pop(),
    }))
  } catch {
    return []
  }
}

async function fetchSupabaseJobs(): Promise<Job[]> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return []
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/list_recent_jobs`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        apikey: SUPABASE_KEY,
      },
      body: JSON.stringify({ p_limit: 10 }),
      cache: 'no-store',
    })
    if (!res.ok) return []
    const data = await res.json()
    return (data || []).map((j: any) => ({
      id: `sb-${j.id}`,
      name: j.job_type || j.name,
      type: 'supabase-job' as const,
      status: j.status,
      lastRun: j.updated_at,
    }))
  } catch {
    return []
  }
}

// Fallback static cron data
const FALLBACK_CRONS: Job[] = [
  { id: 'cron-1', name: 'Foundry Healthcheck', type: 'odoo-cron', status: 'active', schedule: 'Daily 02:00 UTC' },
  { id: 'cron-2', name: 'Odoo Docs KB Refresh', type: 'github-action', status: 'active', schedule: 'Weekly Mon 06:00 UTC', workflow: 'odoo-docs-kb-refresh.yml' },
  { id: 'cron-3', name: 'Org Docs Refresh', type: 'github-action', status: 'active', schedule: 'Weekly Mon 07:00 UTC', workflow: 'org-docs-refresh.yml' },
  { id: 'cron-4', name: 'Copilot Eval', type: 'github-action', status: 'active', schedule: 'On push/PR', workflow: 'odoo-copilot-eval.yml' },
  { id: 'cron-5', name: 'Service Matrix Sync', type: 'n8n-workflow', status: 'active', schedule: 'Daily 03:00 UTC' },
  { id: 'cron-6', name: 'DNS Consistency Check', type: 'github-action', status: 'active', schedule: 'On push (CI)', workflow: 'dns-sync-check.yml' },
]

export async function GET() {
  const [ghJobs, sbJobs] = await Promise.all([fetchGitHubWorkflows(), fetchSupabaseJobs()])

  const hasLiveData = ghJobs.length > 0 || sbJobs.length > 0
  const jobs = hasLiveData ? [...ghJobs, ...sbJobs] : FALLBACK_CRONS

  return NextResponse.json({
    jobs,
    crons: FALLBACK_CRONS,
    source: hasLiveData ? 'live' : 'fallback',
    fetchedAt: new Date().toISOString(),
  })
}
