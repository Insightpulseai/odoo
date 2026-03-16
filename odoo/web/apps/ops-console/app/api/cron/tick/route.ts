// apps/ops-console/app/api/cron/tick/route.ts
// Cron trigger endpoint — called by Vercel Cron every 5 minutes.
//
// Security:
//   1. User-Agent must contain 'vercel-cron/1.0'
//   2. x-cron-secret header must match CRON_SECRET env var
//
// Behavior:
//   - Reads ops.schedules (enabled=true)
//   - For each schedule, computes the bucket key and calls ops.enqueue_scheduled_run
//   - Returns a JSON summary of enqueued runs
//
// SSOT contract:
//   - Supabase ops.runs is written first (SSOT)
//   - This endpoint does NOT write to Odoo SoR
import 'server-only'

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { scheduleBucketKey } from '@ipai/taskbus'

function getSupabase() {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !key) throw new Error('SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set')
  return createClient(url, key)
}

function isAuthorized(req: NextRequest): boolean {
  // 1. Vercel Cron User-Agent check
  const ua = req.headers.get('user-agent') ?? ''
  const isCronAgent = ua.includes('vercel-cron/1.0')

  // 2. Shared-secret header check
  const cronSecret = process.env.CRON_SECRET
  const providedSecret = req.headers.get('x-cron-secret')
  const hasValidSecret = cronSecret ? providedSecret === cronSecret : false

  return isCronAgent || hasValidSecret
}

export async function GET(req: NextRequest) {
  if (!isAuthorized(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const now = new Date()
  const supabase = getSupabase()

  // Fetch enabled schedules
  const { data: schedules, error: fetchErr } = await supabase
    .schema('ops')
    .from('schedules')
    .select('id, name, job_type, agent, input_json')
    .eq('enabled', true)

  if (fetchErr) {
    console.error('[cron/tick] failed to fetch schedules', fetchErr)
    return NextResponse.json({ error: 'Failed to fetch schedules' }, { status: 500 })
  }

  if (!schedules || schedules.length === 0) {
    return NextResponse.json({ enqueued: 0, skipped: 0, schedules: [] })
  }

  const results: Array<{
    schedule: string
    run_id: string | null
    already_exists: boolean
    error?: string
  }> = []

  for (const sched of schedules) {
    const bucketKey = scheduleBucketKey(sched.id, now)

    const { data: runId, error: rpcErr } = await supabase
      .rpc('enqueue_scheduled_run', {
        p_schedule_id: sched.id,
        p_bucket_key:  bucketKey,
        p_now:         now.toISOString(),
      })
      .schema('ops')

    if (rpcErr) {
      console.error(`[cron/tick] enqueue failed for schedule '${sched.name}'`, rpcErr)
      results.push({ schedule: sched.name, run_id: null, already_exists: false, error: rpcErr.message })
      continue
    }

    const isNew = runId !== null
    results.push({ schedule: sched.name, run_id: runId ?? null, already_exists: !isNew })
  }

  const enqueued = results.filter(r => r.run_id && !r.already_exists).length
  const skipped  = results.filter(r => r.already_exists).length
  const failed   = results.filter(r => r.error).length

  return NextResponse.json({ enqueued, skipped, failed, results, at: now.toISOString() })
}
