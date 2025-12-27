// Supabase Edge Function: MCP Gateway
// Middleware layer for n8n MCP operations with auth, rate limiting, and routing

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-mcp-action',
}

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
    // 1. AUTH MIDDLEWARE
    const authHeader = req.headers.get('authorization')
    const apiKey = req.headers.get('x-api-key')

    if (!authHeader && !apiKey) {
      return errorResponse(401, 'Missing authentication', requestId)
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Validate API key or JWT
    const clientId = await validateAuth(supabase, authHeader, apiKey)
    if (!clientId) {
      return errorResponse(403, 'Invalid authentication', requestId)
    }

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
      })
    }

    // 3. ROUTING MIDDLEWARE
    const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL') || 'https://n8n.insightpulseai.net'
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
        return errorResponse(400, `Unknown action: ${body.action}`, requestId)
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
    return errorResponse(500, error.message, requestId)
  }
})

// Helper functions
async function validateAuth(supabase: any, authHeader: string | null, apiKey: string | null): Promise<string | null> {
  if (apiKey) {
    const { data } = await supabase
      .from('api_keys')
      .select('client_id, active')
      .eq('key_hash', await hashKey(apiKey))
      .eq('active', true)
      .single()
    return data?.client_id || null
  }

  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7)
    const { data: { user } } = await supabase.auth.getUser(token)
    return user?.id || null
  }

  return null
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

function errorResponse(status: number, message: string, requestId: string, extraHeaders?: Record<string, string>) {
  return new Response(
    JSON.stringify({ success: false, error: message, request_id: requestId }),
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
