// app/runs/page.tsx
// Runs dashboard — lists recent ops.runs and their event timeline.
// Server component: reads directly from Supabase with service role.
import 'server-only'

import { createClient } from '@supabase/supabase-js'
import RunsClient from './runs-client'

export const dynamic = 'force-dynamic'
export const revalidate = 0

async function getRuns() {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !key) return []

  const supabase = createClient(url, key)
  const { data } = await supabase
    .schema('ops')
    .from('runs')
    .select('id, run_type, agent, status, source, idempotency_key, metadata, started_at, completed_at, created_at, error_json')
    .order('created_at', { ascending: false })
    .limit(100)

  return data ?? []
}

export default async function RunsPage() {
  const runs = await getRuns()
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold">Agent Runs</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Task bus run ledger — SSOT: <code className="text-xs">ops.runs</code>
          </p>
        </div>
      </div>
      <RunsClient initialRuns={runs} />
    </div>
  )
}
