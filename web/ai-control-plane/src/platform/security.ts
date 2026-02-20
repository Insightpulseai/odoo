import 'server-only'
import { createClient } from '@supabase/supabase-js'

export type PlatformRole = 'platform_admin' | 'platform_operator' | 'readonly'

export function getEnvOrThrow(name: string): string {
  const v = process.env[name]
  if (!v) throw new Error(`Missing required env var: ${name}`)
  return v
}

// Comma-separated refs OR "*" not allowed (force explicit allowlist)
export function getAllowedProjectRefs(): Set<string> {
  const raw = getEnvOrThrow('ALLOWED_PROJECT_REFS')
  const refs = raw.split(',').map(s => s.trim()).filter(Boolean)
  if (refs.length === 0) throw new Error('ALLOWED_PROJECT_REFS must contain at least 1 project ref')
  if (refs.includes('*')) throw new Error('ALLOWED_PROJECT_REFS cannot include "*"')
  return new Set(refs)
}

// Supabase Auth integration using anon key (not service_role)
export async function getRequestContext(req: Request): Promise<{ userId: string | null; role: PlatformRole }> {
  const authHeader = req.headers.get('authorization')
  if (!authHeader?.startsWith('Bearer ')) return { userId: null, role: 'readonly' }
  const token = authHeader.slice('Bearer '.length).trim()
  if (!token) return { userId: null, role: 'readonly' }

  // Use anon key for auth validation; DO NOT use service_role for user identity checks.
  const supabase = createClient(
    getEnvOrThrow('SUPABASE_URL'),
    getEnvOrThrow('SUPABASE_ANON_KEY')
  )

  const { data, error } = await supabase.auth.getUser(token)
  if (error || !data?.user) return { userId: null, role: 'readonly' }

  // Map user metadata to platform role with safe fallback
  const role = (data.user.user_metadata as any)?.platform_role ?? 'readonly'
  return { userId: data.user.id, role }
}

export function assertAllowedProjectRef(projectRef: string) {
  const allowed = getAllowedProjectRefs()
  if (!allowed.has(projectRef)) {
    throw new Response('Forbidden: projectRef not allowed', { status: 403 })
  }
}

export function assertRole(role: PlatformRole, required: PlatformRole) {
  const order: PlatformRole[] = ['readonly', 'platform_operator', 'platform_admin']
  if (order.indexOf(role) < order.indexOf(required)) {
    throw new Response('Forbidden: insufficient role', { status: 403 })
  }
}
