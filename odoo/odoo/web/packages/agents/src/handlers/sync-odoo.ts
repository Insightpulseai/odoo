// packages/agents/src/handlers/sync-odoo.ts
// Odoo sync placeholder handler.
// Emits NOT_CONFIGURED when ODOO_URL / ODOO_DB are absent.
// Never commits writes to Odoo SoR without explicit credentials.

import type { SupabaseClient } from '@supabase/supabase-js'
import type { HandlerResult, JobMessage } from '@ipai/taskbus'

export async function syncOdooHandler(
  msg: JobMessage,
  _supabase: SupabaseClient,
): Promise<HandlerResult> {
  const odooUrl = process.env.ODOO_URL
  const odooDb  = process.env.ODOO_DB

  if (!odooUrl || !odooDb) {
    return {
      status: 'completed',
      output: { configured: false },
      events: [
        {
          event_type: 'sync_odoo.NOT_CONFIGURED',
          payload: {
            reason: 'ODOO_URL or ODOO_DB env var is not set. No sync performed.',
            dry_run: msg.input.dry_run ?? true,
          },
        },
      ],
    }
  }

  // When credentials are present: implement Odoo → Supabase sync here.
  // Must route through ipai_llm_supabase_bridge (no direct DB writes to Odoo).
  return {
    status: 'completed',
    output: { configured: true, dry_run: msg.input.dry_run },
    events: [
      {
        event_type: 'sync_odoo.skipped',
        payload: { reason: 'sync not yet implemented', model: msg.input.model },
      },
    ],
  }
}
