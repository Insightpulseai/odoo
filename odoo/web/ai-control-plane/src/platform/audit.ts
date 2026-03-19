import 'server-only'
import { getSupabaseServiceClient } from '@/platform/supabase-server'

export async function audit(event: {
  userId: string
  action: string
  projectRef?: string | null
  path: string
  method: string
  status?: number
  requestId?: string
  payload?: Record<string, unknown>
}) {
  const row = {
    request_id: event.requestId ?? null,
    user_id: event.userId,
    action: event.action,
    project_ref: event.projectRef ?? null,
    path: event.path,
    method: event.method,
    status: event.status ?? null,
    payload: event.payload ?? {},
  }

  try {
    const supabase = getSupabaseServiceClient()
    // Upsert makes retries idempotent (requires unique index on request_id+action)
    const { error } = await supabase
      .from('ops.platform_events')
      .upsert(row, { onConflict: 'request_id,action' })
    if (error) throw error
  } catch (e) {
    // Fail-open for logging: do not break the proxy path.
    console.info('[AUDIT_FALLBACK]', JSON.stringify({ ts: new Date().toISOString(), ...row, err: String(e) }))
  }
}
