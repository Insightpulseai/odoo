// packages/agents/src/router.ts
// Maps job_type → agent handler. Pure dispatch, no side effects.

import type { SupabaseClient } from '@supabase/supabase-js'
import type { HandlerResult, JobMessage } from '@ipai/taskbus'
import { assertJobAllowed } from '@ipai/taskbus'

import { pingHandler }     from './handlers/ping'
import { syncOdooHandler } from './handlers/sync-odoo'

type Handler = (msg: JobMessage, supabase: SupabaseClient) => Promise<HandlerResult>

const ROUTES: Record<string, Handler> = {
  ping:      pingHandler,
  sync_odoo: syncOdooHandler,
}

/**
 * Dispatch a job message to the appropriate handler.
 * Validates policy before dispatching.
 */
export async function dispatch(
  msg: JobMessage,
  supabase: SupabaseClient,
): Promise<HandlerResult> {
  // Policy gate: agent must be allowed to handle this job type
  assertJobAllowed(msg.agent, msg.job_type)

  const handler = ROUTES[msg.job_type]
  if (!handler) {
    return {
      status: 'failed',
      error: `No handler registered for job_type '${msg.job_type}'`,
    }
  }

  return handler(msg, supabase)
}
