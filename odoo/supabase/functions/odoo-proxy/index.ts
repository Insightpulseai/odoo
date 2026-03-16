/**
 * Odoo Proxy Edge Function
 *
 * Secure gateway for Vercel apps to call Odoo (System of Record).
 * Signs requests with HMAC so Odoo can verify the caller.
 *
 * Pattern:
 *   Vercel App → Supabase Auth → This Function → Odoo API
 *
 * NEVER let apps call Odoo directly. This function:
 * 1. Verifies the Supabase JWT and role claims
 * 2. Signs the request with HMAC
 * 3. Forwards to Odoo with retry logic
 * 4. Logs to ops.events for audit trail
 * 5. Returns the response
 *
 * Features:
 * - Retry with exponential backoff (3 attempts)
 * - Role-based access control via JWT claims
 * - Future agent hook support
 * - Comprehensive audit logging
 *
 * Environment Variables:
 * - ODOO_BASE_URL: Odoo server URL (e.g., https://erp.example.com)
 * - IPAI_APP_HMAC_SECRET: Shared secret with Odoo (must match Odoo's env)
 * - SUPABASE_URL: For JWT verification
 * - SUPABASE_ANON_KEY: For JWT verification
 * - SUPABASE_SERVICE_ROLE_KEY: For audit logging
 */

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Retry configuration
const MAX_RETRIES = 3
const INITIAL_BACKOFF_MS = 500

// Role-based access control for paths
const PATH_ROLE_REQUIREMENTS: Record<string, string[]> = {
  '/ipai/write/': ['admin', 'manager', 'agent'],
  '/ipai/read/': ['admin', 'manager', 'agent', 'user'],
  '/web/': ['admin', 'manager'],
  '/api/': ['admin'],
}

/**
 * Get required environment variable
 */
function required(name: string): string {
  const value = Deno.env.get(name)
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`)
  }
  return value
}

/**
 * Calculate HMAC-SHA256 signature
 */
async function hmacSha256Hex(secret: string, data: Uint8Array): Promise<string> {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  const signature = await crypto.subtle.sign('HMAC', key, data)
  return Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

/**
 * Sleep for exponential backoff
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Check if user has required role for the path
 */
function checkRoleAccess(
  path: string,
  user?: Record<string, unknown>
): { allowed: boolean; requiredRoles?: string[]; userRole?: string } {
  // Find matching path prefix
  const matchingPrefix = Object.keys(PATH_ROLE_REQUIREMENTS).find((prefix) =>
    path.startsWith(prefix)
  )

  // If no role requirements defined, allow access
  if (!matchingPrefix) {
    return { allowed: true }
  }

  const requiredRoles = PATH_ROLE_REQUIREMENTS[matchingPrefix]

  // If no user, deny access for protected paths
  if (!user) {
    return { allowed: false, requiredRoles }
  }

  // Extract role from user metadata
  const metadata = (user.user_metadata || user.app_metadata || {}) as Record<string, unknown>
  const userRole = (metadata.role as string) || 'user'

  // Check if user has required role
  const allowed = requiredRoles.includes(userRole)

  return { allowed, requiredRoles, userRole }
}

/**
 * Check if this is an agent request (for future agent hook support)
 */
function isAgentRequest(user?: Record<string, unknown>): boolean {
  if (!user) return false
  const metadata = (user.user_metadata || user.app_metadata || {}) as Record<string, unknown>
  return (metadata.role as string) === 'agent' || (metadata.is_agent as boolean) === true
}

/**
 * Verify Supabase JWT and extract user info
 */
async function verifyJwt(
  authHeader: string | null
): Promise<{ valid: boolean; user?: Record<string, unknown>; error?: string }> {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return { valid: false, error: 'Missing or invalid Authorization header' }
  }

  const token = authHeader.replace('Bearer ', '')

  try {
    const supabaseUrl = required('SUPABASE_URL')
    const supabaseAnonKey = required('SUPABASE_ANON_KEY')

    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: { Authorization: `Bearer ${token}` },
      },
    })

    const { data: { user }, error } = await supabase.auth.getUser()

    if (error || !user) {
      return { valid: false, error: error?.message || 'Invalid token' }
    }

    return { valid: true, user: user as unknown as Record<string, unknown> }
  } catch (err) {
    return { valid: false, error: err instanceof Error ? err.message : 'JWT verification failed' }
  }
}

/**
 * Forward request to Odoo with HMAC signature and retry logic
 */
async function forwardToOdoo(
  path: string,
  method: string,
  body: Uint8Array,
  contentType: string,
  user?: Record<string, unknown>,
  requestId?: string
): Promise<{ response: Response; attempts: number; retryErrors: string[] }> {
  const odooBaseUrl = required('ODOO_BASE_URL')
  const hmacSecret = required('IPAI_APP_HMAC_SECRET')

  // Calculate signature
  const signature = await hmacSha256Hex(hmacSecret, body)

  // Build request URL
  const url = `${odooBaseUrl}${path}`

  // Forward headers
  const headers: Record<string, string> = {
    'Content-Type': contentType || 'application/json',
    'X-IPAI-SIGNATURE': signature,
    'X-IPAI-TIMESTAMP': Date.now().toString(),
    'X-IPAI-REQUEST-ID': requestId || crypto.randomUUID(),
  }

  // Add user context if available
  if (user) {
    headers['X-IPAI-USER-ID'] = (user.id as string) || ''
    headers['X-IPAI-USER-EMAIL'] = (user.email as string) || ''

    // Extract role and company_id from metadata if present
    const metadata = (user.user_metadata || user.app_metadata || {}) as Record<string, unknown>
    if (metadata.company_id) {
      headers['X-IPAI-COMPANY-ID'] = String(metadata.company_id)
    }
    if (metadata.role) {
      headers['X-IPAI-USER-ROLE'] = String(metadata.role)
    }

    // Mark agent requests for Odoo-side handling
    if (isAgentRequest(user)) {
      headers['X-IPAI-AGENT-REQUEST'] = 'true'
    }
  }

  // Retry with exponential backoff
  let lastError: Error | null = null
  const retryErrors: string[] = []

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body.length > 0 ? body : undefined,
      })

      // Return successful response (including 4xx client errors - don't retry those)
      if (response.ok || response.status < 500) {
        return {
          response: new Response(response.body, {
            status: response.status,
            headers: {
              'Content-Type': response.headers.get('Content-Type') || 'application/json',
              'Access-Control-Allow-Origin': '*',
              'X-IPAI-ATTEMPTS': String(attempt),
              'X-IPAI-REQUEST-ID': headers['X-IPAI-REQUEST-ID'],
            },
          }),
          attempts: attempt,
          retryErrors,
        }
      }

      // Server error - may retry
      const errorText = await response.text()
      lastError = new Error(`HTTP ${response.status}: ${errorText.slice(0, 200)}`)
      retryErrors.push(`Attempt ${attempt}: ${lastError.message}`)
    } catch (err) {
      // Network error - may retry
      lastError = err instanceof Error ? err : new Error('Unknown network error')
      retryErrors.push(`Attempt ${attempt}: ${lastError.message}`)
    }

    // Don't sleep after last attempt
    if (attempt < MAX_RETRIES) {
      const backoffMs = INITIAL_BACKOFF_MS * Math.pow(2, attempt - 1)
      await sleep(backoffMs)
    }
  }

  // All retries exhausted
  throw new Error(
    `Odoo request failed after ${MAX_RETRIES} attempts: ${lastError?.message || 'Unknown error'}`
  )
}

/**
 * Log the request to ops.events with full audit context
 */
async function logRequest(
  path: string,
  method: string,
  status: number,
  durationMs: number,
  user?: Record<string, unknown>,
  error?: string,
  options?: {
    attempts?: number
    retryErrors?: string[]
    requestId?: string
    roleCheck?: { allowed: boolean; requiredRoles?: string[]; userRole?: string }
  }
): Promise<void> {
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (!supabaseUrl || !serviceRoleKey) return

    const supabase = createClient(supabaseUrl, serviceRoleKey)

    const isAgent = isAgentRequest(user)
    const metadata = (user?.user_metadata || user?.app_metadata || {}) as Record<string, unknown>

    await supabase.rpc('ops.log_event', {
      p_level: error ? 'error' : 'info',
      p_message: error || `Odoo proxy: ${method} ${path}`,
      p_system: 'supabase',
      p_category: isAgent ? 'agent-odoo-proxy' : 'odoo-proxy',
      p_event_type: 'http_request',
      p_component: 'odoo-proxy',
      p_duration_ms: durationMs,
      p_metadata: {
        path,
        method,
        status,
        user_id: user?.id,
        user_email: user?.email,
        user_role: metadata.role || 'user',
        company_id: metadata.company_id,
        is_agent: isAgent,
        request_id: options?.requestId,
        attempts: options?.attempts || 1,
        retry_errors: options?.retryErrors,
        role_check: options?.roleCheck,
        error,
      },
    })
  } catch (err) {
    console.error('Failed to log request:', err)
  }
}

/**
 * Main handler
 */
serve(async (req: Request): Promise<Response> => {
  const startTime = Date.now()
  const requestId = crypto.randomUUID()

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',
      },
    })
  }

  const url = new URL(req.url)
  const path = url.searchParams.get('path')

  // Validate path parameter
  if (!path) {
    return new Response(
      JSON.stringify({ ok: false, error: 'Missing path parameter' }),
      {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'X-IPAI-REQUEST-ID': requestId,
        },
      }
    )
  }

  // Validate path starts with allowed prefixes
  const allowedPrefixes = ['/ipai/', '/web/', '/api/']
  if (!allowedPrefixes.some((prefix) => path.startsWith(prefix))) {
    return new Response(
      JSON.stringify({
        ok: false,
        error: `Path must start with one of: ${allowedPrefixes.join(', ')}`,
      }),
      {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'X-IPAI-REQUEST-ID': requestId,
        },
      }
    )
  }

  try {
    // Verify JWT (optional - can be disabled for internal calls)
    const skipAuth = url.searchParams.get('skip_auth') === 'true'
    let user: Record<string, unknown> | undefined

    if (!skipAuth) {
      const authResult = await verifyJwt(req.headers.get('Authorization'))

      if (!authResult.valid) {
        await logRequest(path, req.method, 401, Date.now() - startTime, undefined, authResult.error, {
          requestId,
        })

        return new Response(
          JSON.stringify({ ok: false, error: authResult.error }),
          {
            status: 401,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
              'X-IPAI-REQUEST-ID': requestId,
            },
          }
        )
      }

      user = authResult.user
    }

    // Check role-based access control
    const roleCheck = checkRoleAccess(path, user)
    if (!roleCheck.allowed) {
      const errorMessage = `Access denied. Required roles: ${roleCheck.requiredRoles?.join(', ')}. User role: ${roleCheck.userRole || 'none'}`

      await logRequest(path, req.method, 403, Date.now() - startTime, user, errorMessage, {
        requestId,
        roleCheck,
      })

      return new Response(
        JSON.stringify({ ok: false, error: errorMessage }),
        {
          status: 403,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-IPAI-REQUEST-ID': requestId,
          },
        }
      )
    }

    // Get request body
    const body = new Uint8Array(await req.arrayBuffer())
    const contentType = req.headers.get('Content-Type') || 'application/json'

    // Forward to Odoo with retry logic
    const { response, attempts, retryErrors } = await forwardToOdoo(
      path,
      req.method,
      body,
      contentType,
      user,
      requestId
    )

    // Log the request with full context
    await logRequest(path, req.method, response.status, Date.now() - startTime, user, undefined, {
      attempts,
      retryErrors,
      requestId,
      roleCheck,
    })

    // Record cost metrics
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (supabaseUrl && serviceRoleKey) {
      const supabase = createClient(supabaseUrl, serviceRoleKey)
      await supabase.rpc('ops.record_edge_cost', {
        p_function_name: 'odoo-proxy',
        p_invocations: 1,
        p_execution_time_ms: Date.now() - startTime,
      }).catch((err: Error) => console.error('Failed to record cost:', err))
    }

    return response
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'

    await logRequest(path, req.method, 500, Date.now() - startTime, undefined, errorMessage, {
      requestId,
    })

    return new Response(
      JSON.stringify({ ok: false, error: errorMessage }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'X-IPAI-REQUEST-ID': requestId,
        },
      }
    )
  }
})
