// apps/ops-console/app/api/queues/consume/route.ts
// Queue consumer endpoint — receives job messages and dispatches to agents.
//
// In Vercel Queues (push mode) the platform POSTs a message to this endpoint.
// The endpoint must return HTTP 2xx to acknowledge; non-2xx triggers retry.
//
// Idempotency: all handlers are keyed by run_id, so retries are safe.
//
// SSOT contract:
//   - ops.runs (written by cron/tick or enqueue call) is SSOT
//   - This endpoint reads run_id, dispatches handler, writes back events + status
import 'server-only'

import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { markRunning, markFinished, runEventKey } from '@ipai/taskbus'
import type { JobMessage } from '@ipai/taskbus'
import { dispatch } from '@ipai/agents'

function getSupabase() {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !key) throw new Error('SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set')
  return createClient(url, key)
}

export async function POST(req: NextRequest) {
  // Verify internal secret (Vercel Queues signs the request; minimal auth here)
  const queueSecret = process.env.QUEUE_CONSUMER_SECRET
  if (queueSecret) {
    const provided = req.headers.get('x-queue-secret')
    if (provided !== queueSecret) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
  }

  let msg: JobMessage
  try {
    msg = (await req.json()) as JobMessage
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  if (!msg.run_id || !msg.job_type || !msg.agent) {
    return NextResponse.json({ error: 'Missing run_id, job_type, or agent' }, { status: 400 })
  }

  const supabase = getSupabase()

  // Mark run as running
  await markRunning(supabase, msg.run_id)

  let result
  try {
    result = await dispatch(msg, supabase)
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : String(err)
    await markFinished(supabase, msg.run_id, 'failed', undefined, errMsg)
    // Return 200 so Vercel Queues doesn't retry on policy/dispatch errors
    return NextResponse.json({ run_id: msg.run_id, status: 'failed', error: errMsg })
  }

  // Write handler-emitted events
  if (result.events?.length) {
    const eventRows = result.events.map((e, i) => ({
      run_id: msg.run_id,
      event_type: e.event_type,
      source: 'supabase' as const,
      idempotency_key: runEventKey(msg.run_id, `${e.event_type}:${i}`),
      payload: e.payload,
    }))
    await supabase.from('run_events').upsert(eventRows, { onConflict: 'idempotency_key' }).schema('ops')
  }

  // Write handler-emitted artifacts
  if (result.artifacts?.length) {
    const artifactRows = result.artifacts.map(a => ({
      run_id: msg.run_id,
      artifact_type: a.artifact_type,
      name: a.name,
      content: a.content ?? null,
      storage_path: a.storage_path ?? null,
    }))
    await supabase.from('artifacts').insert(artifactRows).schema('ops')
  }

  await markFinished(
    supabase,
    msg.run_id,
    result.status,
    result.output,
    result.error,
  )

  return NextResponse.json({ run_id: msg.run_id, status: result.status })
}
