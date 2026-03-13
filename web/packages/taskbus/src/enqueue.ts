// packages/taskbus/src/enqueue.ts
// Enqueue runs into ops.runs + ops.run_events (Supabase SSOT).
// Optionally publishes to Vercel Queues topic for async fan-out.
//
// SSOT contract:
//   - ops.runs is the authoritative ledger — always written first.
//   - Vercel Queues is the delivery layer — written second, optional.
//   - If queue publish fails, the run remains in 'pending' and the
//     cron tick will re-attempt on the next cycle.

import type { SupabaseClient } from '@supabase/supabase-js'
import type { JobMessage, RunStatus } from './types'

export interface EnqueueOptions {
  supabase: SupabaseClient
  jobType: string
  agent: string
  input?: Record<string, unknown>
  idempotencyKey: string
  scheduleId?: string
  scheduleName?: string
}

export interface EnqueueResult {
  runId: string
  alreadyExists: boolean
}

/**
 * Idempotently enqueue a run into ops.runs.
 * Returns the run_id (new or existing).
 */
export async function enqueue(opts: EnqueueOptions): Promise<EnqueueResult> {
  const { supabase, jobType, agent, input = {}, idempotencyKey } = opts

  // Check for existing run with this idempotency key
  const { data: existing } = await supabase
    .from('runs')
    .select('id')
    .eq('idempotency_key', idempotencyKey)
    .schema('ops')
    .maybeSingle()

  if (existing) {
    return { runId: existing.id, alreadyExists: true }
  }

  const { data: run, error } = await supabase
    .from('runs')
    .insert({
      run_type: jobType,
      agent,
      status: 'pending' satisfies RunStatus,
      source: 'supabase',
      input_json: input,
      idempotency_key: idempotencyKey,
      metadata: {
        ...(opts.scheduleId ? { schedule_id: opts.scheduleId } : {}),
        ...(opts.scheduleName ? { schedule_name: opts.scheduleName } : {}),
      },
    })
    .schema('ops')
    .select('id')
    .single()

  if (error) throw new Error(`enqueue: failed to insert run: ${error.message}`)

  return { runId: run.id, alreadyExists: false }
}

/**
 * Mark a run as running, emit a 'run.started' event.
 */
export async function markRunning(
  supabase: SupabaseClient,
  runId: string,
): Promise<void> {
  await Promise.all([
    supabase.from('runs').update({ status: 'running', started_at: new Date().toISOString() })
      .schema('ops').eq('id', runId),
    supabase.from('run_events').insert({
      run_id: runId,
      event_type: 'run.started',
      source: 'supabase',
      idempotency_key: `${runId}:run.started`,
      payload: {},
    }).schema('ops'),
  ])
}

/**
 * Mark a run completed or failed with final result.
 */
export async function markFinished(
  supabase: SupabaseClient,
  runId: string,
  status: 'completed' | 'failed',
  output?: Record<string, unknown>,
  errorMsg?: string,
): Promise<void> {
  await Promise.all([
    supabase.from('runs').update({
      status,
      completed_at: new Date().toISOString(),
      ...(errorMsg ? { error_json: { message: errorMsg } } : {}),
    }).schema('ops').eq('id', runId),
    supabase.from('run_events').insert({
      run_id: runId,
      event_type: status === 'completed' ? 'run.completed' : 'run.failed',
      source: 'supabase',
      idempotency_key: `${runId}:${status}`,
      payload: { ...(output ?? {}), ...(errorMsg ? { error: errorMsg } : {}) },
    }).schema('ops'),
  ])
}

/**
 * Build the JobMessage payload to send to a queue consumer.
 */
export function buildJobMessage(runId: string, opts: EnqueueOptions): JobMessage {
  return {
    run_id: runId,
    job_type: opts.jobType,
    agent: opts.agent,
    input: opts.input ?? {},
    idempotency_key: opts.idempotencyKey,
    ...(opts.scheduleId ? { schedule_id: opts.scheduleId } : {}),
  }
}
