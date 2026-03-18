import 'server-only'
import { createClient } from '@supabase/supabase-js'
import { getEnvOrThrow } from '@/platform/security'

// Server-only client (service role) for SSOT ops logging.
// Never expose this to the browser.
export function getSupabaseServiceClient() {
  const url = getEnvOrThrow('SUPABASE_URL')
  const serviceKey = getEnvOrThrow('SUPABASE_SERVICE_ROLE_KEY')
  return createClient(url, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  })
}
