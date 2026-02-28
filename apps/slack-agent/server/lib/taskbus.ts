// server/lib/taskbus.ts
// Thin adapter: converts Slack payloads into SSOT ops.runs via @ipai/taskbus.
//
// Boundary rule (SOW_BOUNDARY.md):
//   Slack events → ops.runs (SSOT) → workers execute → ops.run_events/artifacts
//   Slack NEVER writes directly to Odoo (SoR) or work.* (SoW) without an approved run.
//
// This file is the single chokepoint where Slack payloads enter the SSOT ledger.

import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { enqueue, type EnqueueResult } from '@ipai/taskbus'

export interface SlackRunInput {
  /** Slack event_type, callback_id, or command name — maps to a run_type */
  jobType: string
  /** Agent that handles this run type (see packages/agents/src/router.ts) */
  agent: string
  /** Pre-built idempotency key (use builders in ./idempotency.ts) */
  idempotencyKey: string
  /** Normalized Slack payload to pass as run input */
  input: Record<string, unknown>
}

let _supabase: SupabaseClient | null = null

function getSupabase(url: string, key: string): SupabaseClient {
  if (!_supabase) {
    _supabase = createClient(url, key)
  }
  return _supabase
}

/**
 * Enqueue a Slack-triggered run into ops.runs (SSOT).
 * Idempotent: duplicate Slack retries with the same key return the existing run.
 *
 * @returns EnqueueResult with runId and whether it already existed
 */
export async function enqueueSlackRun(
  opts: SlackRunInput & { supabaseUrl: string; supabaseServiceRoleKey: string },
): Promise<EnqueueResult> {
  const supabase = getSupabase(opts.supabaseUrl, opts.supabaseServiceRoleKey)

  return enqueue({
    supabase,
    jobType: opts.jobType,
    agent: opts.agent,
    input: {
      ...opts.input,
      _source: 'slack',
    },
    idempotencyKey: opts.idempotencyKey,
  })
}

/**
 * Map a Slack event_type to a run_type + agent.
 * Add new event types here as the Slack app grows.
 */
export function resolveSlackAction(eventType: string): { jobType: string; agent: string } | null {
  const routes: Record<string, { jobType: string; agent: string }> = {
    // Example: app_mention → AI copilot agent answers in thread
    app_mention: { jobType: 'slack.app_mention', agent: 'slack-copilot-agent' },
    // Example: message (DM) → AI agent processes direct message
    message: { jobType: 'slack.direct_message', agent: 'slack-copilot-agent' },
  }
  return routes[eventType] ?? null
}

/**
 * Map a slash command to a run_type + agent.
 */
export function resolveSlackCommand(command: string): { jobType: string; agent: string } | null {
  const routes: Record<string, { jobType: string; agent: string }> = {
    '/run': { jobType: 'slack.run_command', agent: 'ops-agent' },
    '/ask': { jobType: 'slack.ask_command', agent: 'slack-copilot-agent' },
  }
  return routes[command] ?? null
}
