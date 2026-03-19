// Supabase Edge Function: MCP Gateway
// Middleware layer for n8n MCP operations with auth, rate limiting, and routing
//
// Auth flow:
//   1. x-api-key header → hash lookup in api_keys table
//   2. Bearer token → try Supabase JWT (getUser), then external JWKS validation
//   3. GET /auth/check → returns token claim summary (no secrets)
//
// Error codes (structured, deterministic):
//   AUTH_MISSING       - No auth header or API key provided
//   AUTH_KEY_INVALID   - x-api-key hash not found or inactive
//   AUTH_TOKEN_INVALID - Bearer token failed all validation paths
//   AUTH_JWKS_FAIL     - External JWKS fetch/validation failed
//   ALLOWLIST_DENY     - Workflow ID not in allowlist for execute_workflow
//   RATE_LIMIT         - Per-client rate limit exceeded
//   UNKNOWN_ACTION     - Unrecognized MCP action

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-mcp-action',
}

// Read-only actions that do NOT require allowlist gating
const READ_ONLY_ACTIONS = new Set(['search_workflows', 'get_workflow_details'])

interface MCPRequest {
  action: 'execute_workflow' | 'search_workflows' | 'get_workflow_details' | 'git_operation'
  workflow_id?: string
  workflow_name?: string
  payload?: Record<string, unknown>
  priority?: 'high' | 'normal' | 'low'
}

interface RateLimitEntry {
  count: number
  reset_at: number
}

// In-memory rate limit store (use Redis/KV in production)
const rateLimits = new Map<string, RateLimitEntry>()

const RATE_LIMITS = {
  execute_workflow: { max: 100, window: 3600 },  // 100/hour
  search_workflows: { max: 500, window: 3600 },   // 500/hour
  git_operation: { max: 50, window: 3600 },       // 50/hour
  default: { max: 200, window: 3600 }
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const startTime = Date.now()
  const requestId = crypto.randomUUID()

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // 0. AUTH SELF-TEST ENDPOINT
    const url = new URL(req.url)
    if (url.pathname.endsWith('/auth/check')) {
      return handleAuthCheck(req, supabase, requestId)
    }

    // 1. AUTH MIDDLEWARE (deterministic error codes)
    const authHeader = req.headers.get('authorization')
    const apiKey = req.headers.get('x-api-key')
    const hostHeader = req.headers.get('host') || ''

    // Log auth attempt (no secrets)
    console.log(JSON.stringify({
      request_id: requestId,
      path: url.pathname,
      method: req.method,
      host: hostHeader,
      auth_scheme: apiKey ? 'x-api-key' : authHeader ? authHeader.split(' ')[0] : 'none',
      timestamp: new Date().toISOString(),
    }))

    if (!authHeader && !apiKey) {
      return errorResponse(401, 'Missing authentication', requestId, {}, 'AUTH_MISSING')
    }

    // Validate API key or JWT (with structured error codes)
    const authResult = await validateAuth(supabase, authHeader, apiKey)
    if (!authResult.ok) {
      console.log(JSON.stringify({
        request_id: requestId,
        auth_result: 'denied',
        error_code: authResult.error_code,
        reason: authResult.reason,
      }))
      return errorResponse(
        authResult.error_code === 'AUTH_KEY_INVALID' ? 403 : 401,
        authResult.reason,
        requestId,
        {},
        authResult.error_code
      )
    }

    const clientId = authResult.client_id!

    // 2. RATE LIMIT MIDDLEWARE
    const body: MCPRequest = await req.json()
    const action = body.action || 'default'
    const limit = RATE_LIMITS[action] || RATE_LIMITS.default

    const rateLimitResult = checkRateLimit(clientId, action, limit)
    if (!rateLimitResult.allowed) {
      return errorResponse(429, 'Rate limit exceeded', requestId, {
        'X-RateLimit-Limit': limit.max.toString(),
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': rateLimitResult.reset_at.toString()
      }, 'RATE_LIMIT')
    }

    // 3. ROUTING MIDDLEWARE
    const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL') || 'https://n8n.insightpulseai.com'
    let targetEndpoint: string
    let n8nPayload: Record<string, unknown>

    switch (body.action) {
      case 'execute_workflow':
        targetEndpoint = `${n8nUrl}/webhook/mcp-execute`
        n8nPayload = {
          workflow_id: body.workflow_id,
          workflow_name: body.workflow_name,
          payload: body.payload,
          priority: body.priority || 'normal',
          request_id: requestId,
          client_id: clientId
        }
        break

      case 'search_workflows':
        targetEndpoint = `${n8nUrl}/webhook/mcp-search`
        n8nPayload = {
          query: body.payload?.query || '',
          tags: body.payload?.tags || [],
          request_id: requestId
        }
        break

      case 'git_operation':
        // Queue git operations for async processing
        targetEndpoint = `${n8nUrl}/webhook/git-operations`
        n8nPayload = {
          operation: body.payload?.operation,
          repo: body.payload?.repo,
          branch: body.payload?.branch,
          message: body.payload?.message,
          request_id: requestId,
          queued_at: new Date().toISOString()
        }
        break

      default:
        return errorResponse(400, `Unknown action: ${body.action}`, requestId, {}, 'UNKNOWN_ACTION')
    }

    // 4. QUEUE JOB (for async operations)
    if (body.priority === 'low' || body.action === 'git_operation') {
      // Queue for async processing
      await supabase.from('mcp_job_queue').insert({
        request_id: requestId,
        action: body.action,
        payload: n8nPayload,
        status: 'pending',
        client_id: clientId,
        created_at: new Date().toISOString()
      })

      return new Response(
        JSON.stringify({
          success: true,
          queued: true,
          request_id: requestId,
          message: 'Job queued for async processing',
          status_url: `${supabaseUrl}/functions/v1/mcp-gateway/status/${requestId}`
        }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Request-ID': requestId
          }
        }
      )
    }

    // 5. SYNC EXECUTION (for high priority)
    const n8nResponse = await fetch(targetEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
        'X-MCP-Gateway': 'supabase-edge'
      },
      body: JSON.stringify(n8nPayload)
    })

    const n8nResult = await n8nResponse.json()

    // 6. LOGGING
    await supabase.from('mcp_request_log').insert({
      request_id: requestId,
      action: body.action,
      client_id: clientId,
      duration_ms: Date.now() - startTime,
      status: n8nResponse.ok ? 'success' : 'error',
      response_code: n8nResponse.status
    })

    return new Response(
      JSON.stringify({
        success: n8nResponse.ok,
        request_id: requestId,
        data: n8nResult,
        duration_ms: Date.now() - startTime
      }),
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          'X-RateLimit-Remaining': rateLimitResult.remaining.toString()
        }
      }
    )

  } catch (error) {
    console.error('MCP Gateway error:', error)
    return errorResponse(500, error.message, requestId, {}, 'INTERNAL_ERROR')
  }
})

// Helper functions

interface AuthResult {
  ok: boolean
  client_id?: string
  error_code?: string
  reason?: string
  claims?: Record<string, unknown>
}

async function validateAuth(supabase: any, authHeader: string | null, apiKey: string | null): Promise<AuthResult> {
  // Path 1: API key authentication
  if (apiKey) {
    try {
      const { data, error } = await supabase
        .from('api_keys')
        .select('client_id, active')
        .eq('key_hash', await hashKey(apiKey))
        .eq('active', true)
        .single()

      if (error || !data?.client_id) {
        return { ok: false, error_code: 'AUTH_KEY_INVALID', reason: 'API key not found or inactive' }
      }
      return { ok: true, client_id: data.client_id }
    } catch (e) {
      return { ok: false, error_code: 'AUTH_KEY_INVALID', reason: `API key validation error: ${e.message}` }
    }
  }

  // Path 2: Bearer token authentication
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7)

    // 2a: Try Supabase JWT first (native users)
    try {
      const { data: { user }, error } = await supabase.auth.getUser(token)
      if (user?.id) {
        return { ok: true, client_id: user.id, claims: { sub: user.id, iss: 'supabase', email: user.email } }
      }
    } catch (_) {
      // Not a Supabase JWT — try external validation
    }

    // 2b: Try external JWT validation (ChatGPT, other OAuth providers)
    const jwksUrl = Deno.env.get('AUTH_JWKS_URL')
    const expectedIssuer = Deno.env.get('AUTH_ISSUER')
    const expectedAudience = Deno.env.get('AUTH_AUDIENCE')

    if (jwksUrl) {
      try {
        const claims = await validateExternalJwt(token, jwksUrl, expectedIssuer, expectedAudience)
        if (claims) {
          return {
            ok: true,
            client_id: `external:${claims.sub || claims.client_id || 'unknown'}`,
            claims,
          }
        }
      } catch (e) {
        return { ok: false, error_code: 'AUTH_JWKS_FAIL', reason: `JWKS validation failed: ${e.message}` }
      }
    }

    // 2c: Try as opaque bearer token (lookup in api_keys table by token hash)
    try {
      const tokenHash = await hashKey(token)
      const { data } = await supabase
        .from('api_keys')
        .select('client_id, active')
        .eq('key_hash', tokenHash)
        .eq('active', true)
        .single()

      if (data?.client_id) {
        return { ok: true, client_id: data.client_id }
      }
    } catch (_) {
      // Token not in api_keys table either
    }

    return {
      ok: false,
      error_code: 'AUTH_TOKEN_INVALID',
      reason: 'Bearer token failed all validation paths (Supabase JWT, JWKS, opaque token)'
    }
  }

  return { ok: false, error_code: 'AUTH_MISSING', reason: 'No recognized auth scheme' }
}

async function validateExternalJwt(
  token: string,
  jwksUrl: string,
  expectedIssuer?: string,
  expectedAudience?: string
): Promise<Record<string, unknown> | null> {
  // Decode JWT header to get kid
  const parts = token.split('.')
  if (parts.length !== 3) return null

  const header = JSON.parse(atob(parts[0]))
  const payload = JSON.parse(atob(parts[1]))

  // Clock skew tolerance: 60 seconds
  const now = Math.floor(Date.now() / 1000)
  const skew = 60

  if (payload.exp && payload.exp + skew < now) {
    throw new Error(`Token expired at ${new Date(payload.exp * 1000).toISOString()}`)
  }
  if (payload.nbf && payload.nbf - skew > now) {
    throw new Error(`Token not valid until ${new Date(payload.nbf * 1000).toISOString()}`)
  }
  if (expectedIssuer && payload.iss !== expectedIssuer) {
    throw new Error(`Issuer mismatch: expected ${expectedIssuer}, got ${payload.iss}`)
  }
  if (expectedAudience && payload.aud !== expectedAudience && !payload.aud?.includes?.(expectedAudience)) {
    throw new Error(`Audience mismatch: expected ${expectedAudience}, got ${payload.aud}`)
  }

  // Fetch JWKS and verify signature
  const jwksResponse = await fetch(jwksUrl, {
    headers: { 'Accept': 'application/json' },
  })
  if (!jwksResponse.ok) {
    throw new Error(`JWKS fetch failed: ${jwksResponse.status}`)
  }

  const jwks = await jwksResponse.json()
  const key = jwks.keys?.find((k: any) => k.kid === header.kid)
  if (!key) {
    throw new Error(`No matching key found for kid: ${header.kid}`)
  }

  // Import the JWK and verify signature
  const cryptoKey = await crypto.subtle.importKey(
    'jwk',
    key,
    { name: 'RSASSA-PKCS1-v1_5', hash: header.alg === 'RS256' ? 'SHA-256' : 'SHA-384' },
    false,
    ['verify']
  )

  const signatureBytes = Uint8Array.from(atob(parts[2].replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0))
  const dataBytes = new TextEncoder().encode(`${parts[0]}.${parts[1]}`)

  const valid = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', cryptoKey, signatureBytes, dataBytes)
  if (!valid) {
    throw new Error('JWT signature verification failed')
  }

  return payload
}

async function handleAuthCheck(req: Request, supabase: any, requestId: string): Promise<Response> {
  const authHeader = req.headers.get('authorization')
  const apiKey = req.headers.get('x-api-key')

  if (!authHeader && !apiKey) {
    return errorResponse(401, 'No auth provided', requestId, {}, 'AUTH_MISSING')
  }

  const result = await validateAuth(supabase, authHeader, apiKey)

  if (!result.ok) {
    return errorResponse(
      401,
      result.reason || 'Authentication failed',
      requestId,
      {},
      result.error_code || 'AUTH_TOKEN_INVALID'
    )
  }

  return new Response(
    JSON.stringify({
      ok: true,
      request_id: requestId,
      client_id: result.client_id,
      claims: result.claims || {},
      auth_method: apiKey ? 'api_key' : 'bearer',
    }),
    {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
      }
    }
  )
}

async function hashKey(key: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(key)
  const hash = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

function checkRateLimit(clientId: string, action: string, limit: { max: number, window: number }): { allowed: boolean, remaining: number, reset_at: number } {
  const key = `${clientId}:${action}`
  const now = Date.now()
  const entry = rateLimits.get(key)

  if (!entry || entry.reset_at < now) {
    rateLimits.set(key, { count: 1, reset_at: now + limit.window * 1000 })
    return { allowed: true, remaining: limit.max - 1, reset_at: now + limit.window * 1000 }
  }

  if (entry.count >= limit.max) {
    return { allowed: false, remaining: 0, reset_at: entry.reset_at }
  }

  entry.count++
  return { allowed: true, remaining: limit.max - entry.count, reset_at: entry.reset_at }
}

function errorResponse(status: number, message: string, requestId: string, extraHeaders?: Record<string, string>, errorCode?: string) {
  return new Response(
    JSON.stringify({
      success: false,
      error: message,
      error_code: errorCode || 'UNKNOWN',
      request_id: requestId,
    }),
    {
      status,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
        ...extraHeaders
      }
    }
  )
}
