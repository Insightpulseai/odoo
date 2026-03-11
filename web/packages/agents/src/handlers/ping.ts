// packages/agents/src/handlers/ping.ts
// Ping handler — writes a run_event and marks the run complete.
// Pure function. All Supabase writes go through enqueue helpers (SSOT boundary).

import type { SupabaseClient } from '@supabase/supabase-js'
import type { HandlerResult, JobMessage } from '@ipai/taskbus'

export async function pingHandler(
  msg: JobMessage,
  supabase: SupabaseClient,
): Promise<HandlerResult> {
  const message = (msg.input.message as string | undefined) ?? 'pong'

  return {
    status: 'completed',
    output: { message, run_id: msg.run_id, ts: new Date().toISOString() },
    events: [
      {
        event_type: 'ping.pong',
        payload: { message, run_id: msg.run_id },
      },
    ],
  }
}
