import { NextResponse } from 'next/server'
import { assertAllowedProjectRef, assertRole, getEnvOrThrow, getRequestContext } from '@/platform/security'
import { audit } from '@/platform/audit'

const MGMT_TOKEN = getEnvOrThrow('SUPABASE_MANAGEMENT_API_TOKEN')

function getProjectRefFromUrl(url: URL): string | null {
  // Most Platform Kit calls include /projects/{ref}/... in the path.
  const m = url.pathname.match(/\/projects\/([^/]+)\//)
  return m?.[1] ?? null
}

function getRequestId(req: Request): string {
  const h = req.headers.get('x-request-id')
  if (h && h.trim()) return h.trim()
  // Stable enough for correlation; crypto is available in Next runtime.
  return crypto.randomUUID()
}

async function forwardToSupabaseAPI(request: Request, method: string, params: { path: string[] }) {
  const { path } = params
  const apiPath = path.join('/')

  const url = new URL(request.url)
  url.protocol = 'https'
  url.hostname = 'api.supabase.com'
  url.port = '443'
  url.pathname = apiPath

  try {
    const forwardHeaders: HeadersInit = {
      Authorization: `Bearer ${MGMT_TOKEN}`,
    }

    // Copy relevant headers from the original request
    const contentType = request.headers.get('content-type')
    if (contentType) {
      forwardHeaders['Content-Type'] = contentType
    }

    const fetchOptions: RequestInit = {
      method,
      headers: forwardHeaders,
    }

    // Include body for methods that support it
    if (method !== 'GET' && method !== 'HEAD') {
      try {
        const body = await request.text()
        if (body) {
          fetchOptions.body = body
        }
      } catch (error) {
        // Handle cases where body is not readable
        console.warn('Could not read request body:', error)
      }
    }

    const response = await fetch(url, fetchOptions)

    // Get response body
    const responseText = await response.text()
    let responseData

    try {
      responseData = responseText ? JSON.parse(responseText) : null
    } catch {
      responseData = responseText
    }

    // Return the response with the same status
    return NextResponse.json(responseData, { status: response.status })
  } catch (error: any) {
    console.error('Supabase API proxy error:', error)
    const errorMessage = error.message || 'An unexpected error occurred.'
    return NextResponse.json({ message: errorMessage }, { status: 500 })
  }
}

export async function GET(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { userId, role } = await getRequestContext(request)
  if (!userId) return new Response('Unauthorized', { status: 401 })
  assertRole(role, 'platform_operator')

  const requestId = getRequestId(request)
  const projectRef = getProjectRefFromUrl(new URL(request.url))
  if (projectRef) assertAllowedProjectRef(projectRef)

  const resolvedParams = await params
  const res = await forwardToSupabaseAPI(request, 'GET', resolvedParams)

  await audit({
    userId,
    action: 'supabase_mgmt_proxy',
    projectRef,
    path: new URL(request.url).pathname,
    method: 'GET',
    status: res.status,
    requestId,
    payload: {
      upstream: 'api.supabase.com',
    },
  })

  // Optional: echo for downstream correlation
  res.headers.set('x-request-id', requestId)
  return res
}

export async function HEAD(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { userId, role } = await getRequestContext(request)
  if (!userId) return new Response('Unauthorized', { status: 401 })
  assertRole(role, 'platform_operator')

  const requestId = getRequestId(request)
  const projectRef = getProjectRefFromUrl(new URL(request.url))
  if (projectRef) assertAllowedProjectRef(projectRef)

  const resolvedParams = await params
  const res = await forwardToSupabaseAPI(request, 'HEAD', resolvedParams)

  await audit({
    userId,
    action: 'supabase_mgmt_proxy',
    projectRef,
    path: new URL(request.url).pathname,
    method: 'HEAD',
    status: res.status,
    requestId,
    payload: {
      upstream: 'api.supabase.com',
    },
  })

  res.headers.set('x-request-id', requestId)
  return res
}

export async function POST(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { userId, role } = await getRequestContext(request)
  if (!userId) return new Response('Unauthorized', { status: 401 })
  assertRole(role, 'platform_admin') // POST is powerful; start strict

  const requestId = getRequestId(request)
  const projectRef = getProjectRefFromUrl(new URL(request.url))
  if (projectRef) assertAllowedProjectRef(projectRef)

  const resolvedParams = await params
  const res = await forwardToSupabaseAPI(request, 'POST', resolvedParams)

  await audit({
    userId,
    action: 'supabase_mgmt_proxy',
    projectRef,
    path: new URL(request.url).pathname,
    method: 'POST',
    status: res.status,
    requestId,
    payload: {
      upstream: 'api.supabase.com',
    },
  })

  res.headers.set('x-request-id', requestId)
  return res
}

// Temporarily disabled for safety - enable when explicitly needed
export async function PUT(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return new Response('Method temporarily disabled for safety', { status: 405 })
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return new Response('Method temporarily disabled for safety', { status: 405 })
}

export async function PATCH(request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  return new Response('Method temporarily disabled for safety', { status: 405 })
}
