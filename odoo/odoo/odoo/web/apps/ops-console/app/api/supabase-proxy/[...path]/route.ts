// Mark as server-only so Next.js never bundles this into a client chunk
import 'server-only'

import { NextResponse } from 'next/server'
import { getOrCreateRequestId, correlationHeaders } from '@/lib/http/correlation'

// ── Allowlist: only these Supabase project refs may be proxied ────────────────
const ALLOWED_PROJECT_REFS = new Set(
  (process.env.SUPABASE_ALLOWED_PROJECT_REFS ?? 'spdtwktxdalcfigzeqrz').split(',').map(s => s.trim()).filter(Boolean)
)

// ── Env validation (fail-fast at module load, not per-request) ────────────────
const MANAGEMENT_TOKEN = process.env.SUPABASE_MANAGEMENT_API_TOKEN

// ── Auth helper (replace with your actual session/JWT check) ─────────────────
async function isAuthenticated(request: Request): Promise<boolean> {
  // TODO: replace with real session validation once auth middleware is wired.
  // For now: require the internal service token header OR a non-empty Authorization.
  // In production this MUST be replaced with proper session validation.
  const authHeader = request.headers.get('authorization')
  const internalToken = request.headers.get('x-internal-token')
  const internalSecret = process.env.INTERNAL_API_SECRET
  if (internalSecret && internalToken === internalSecret) return true
  if (authHeader?.startsWith('Bearer ') && authHeader.length > 20) return true
  return false
}

async function forwardToSupabaseAPI(
  request: Request,
  method: string,
  params: { path: string[] }
) {
  const rid = getOrCreateRequestId(request.headers.get('x-request-id'))
  const hdrs = correlationHeaders(rid)

  // 1. Missing token → 503 KEY_MISSING
  if (!MANAGEMENT_TOKEN) {
    console.error({ rid, event: 'supabase_proxy_key_missing', msg: 'SUPABASE_MANAGEMENT_API_TOKEN not set' })
    return NextResponse.json(
      { error: 'KEY_MISSING', message: 'Supabase Management API token is not configured.' },
      { status: 503, headers: hdrs }
    )
  }

  // 2. Auth check → 401
  const authed = await isAuthenticated(request)
  if (!authed) {
    console.warn({ rid, event: 'supabase_proxy_unauthorized', path: params.path.join('/') })
    return NextResponse.json(
      { error: 'UNAUTHORIZED', message: 'Authentication required.' },
      { status: 401, headers: hdrs }
    )
  }

  const { path } = params
  const apiPath = '/' + path.join('/')

  // 3. ProjectRef allowlist → 403 FORBIDDEN_PROJECT
  // Supabase Management API paths: /v1/projects/{ref}/...
  // path[0]='v1', path[1]='projects', path[2]='{ref}'
  const projectRef = path[2]
  if (projectRef && !ALLOWED_PROJECT_REFS.has(projectRef)) {
    console.warn({ rid, event: 'supabase_proxy_forbidden_ref', projectRef })
    return NextResponse.json(
      { error: 'FORBIDDEN_PROJECT', message: 'Project ref is not allowlisted.' },
      { status: 403, headers: hdrs }
    )
  }

  const url = new URL('https://api.supabase.com' + apiPath)
  // Preserve query params from original request
  new URL(request.url).searchParams.forEach((v, k) => url.searchParams.set(k, v))

  try {
    const forwardHeaders: HeadersInit = {
      Authorization: `Bearer ${MANAGEMENT_TOKEN}`,
      'x-request-id': rid,
    }
    const contentType = request.headers.get('content-type')
    if (contentType) forwardHeaders['Content-Type'] = contentType

    const fetchOptions: RequestInit = { method, headers: forwardHeaders }
    if (method !== 'GET' && method !== 'HEAD') {
      const body = await request.text().catch(() => '')
      if (body) fetchOptions.body = body
    }

    const response = await fetch(url, fetchOptions)
    const responseText = await response.text()
    let responseData: unknown
    try {
      responseData = responseText ? JSON.parse(responseText) : null
    } catch {
      responseData = responseText
    }

    console.info({ rid, event: 'supabase_proxy_ok', method, path: apiPath, status: response.status })
    return NextResponse.json(responseData, { status: response.status, headers: hdrs })
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Unknown error'
    console.error({ rid, event: 'supabase_proxy_error', method, path: apiPath, error: msg })
    return NextResponse.json(
      { error: 'PROXY_ERROR', message: msg },
      { status: 502, headers: hdrs }
    )
  }
}

export async function GET(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'GET', await params)
}
export async function HEAD(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'HEAD', await params)
}
export async function POST(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'POST', await params)
}
export async function PUT(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'PUT', await params)
}
export async function DELETE(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'DELETE', await params)
}
export async function PATCH(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return forwardToSupabaseAPI(request, 'PATCH', await params)
}
