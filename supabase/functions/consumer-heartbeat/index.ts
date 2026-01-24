/**
 * consumer-heartbeat Edge Function
 *
 * Accepts heartbeat pings from config consumers (Odoo, n8n, web apps, etc.)
 * and updates their status in the Config Registry.
 *
 * POST body:
 * {
 *   consumer_type: 'odoo' | 'edge_fn' | 'web_app' | 'n8n' | 'mcp_server' | 'docker',
 *   consumer_key: string,
 *   environment?: string (default: 'prod'),
 *   applied_version_id?: string (uuid),
 *   status?: 'ok' | 'degraded' | 'failed' | 'unknown' | 'stale',
 *   metadata?: object,
 *   checks?: Array<{
 *     check_type: string,
 *     status: 'ok' | 'warn' | 'fail',
 *     detail?: object
 *   }>
 * }
 */

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

interface CheckResult {
  check_type: string;
  status: 'ok' | 'warn' | 'fail';
  detail?: Record<string, unknown>;
}

interface HeartbeatRequest {
  consumer_type: 'odoo' | 'edge_fn' | 'web_app' | 'n8n' | 'mcp_server' | 'docker';
  consumer_key: string;
  environment?: string;
  applied_version_id?: string;
  status?: string;
  metadata?: Record<string, unknown>;
  checks?: CheckResult[];
}

interface HeartbeatResponse {
  ok: boolean;
  consumer_id?: string;
  timestamp?: string;
  checks_recorded?: number;
  error?: string;
}

function validateRequest(body: unknown): { valid: true; data: HeartbeatRequest } | { valid: false; error: string } {
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Request body must be a JSON object' };
  }

  const req = body as Record<string, unknown>;

  const validTypes = ['odoo', 'edge_fn', 'web_app', 'n8n', 'mcp_server', 'docker'];
  if (!req.consumer_type || !validTypes.includes(req.consumer_type as string)) {
    return { valid: false, error: `consumer_type must be one of: ${validTypes.join(', ')}` };
  }

  if (!req.consumer_key || typeof req.consumer_key !== 'string') {
    return { valid: false, error: 'consumer_key is required' };
  }

  return {
    valid: true,
    data: {
      consumer_type: req.consumer_type as HeartbeatRequest['consumer_type'],
      consumer_key: req.consumer_key as string,
      environment: (req.environment as string) || 'prod',
      applied_version_id: req.applied_version_id as string | undefined,
      status: (req.status as string) || 'ok',
      metadata: req.metadata as Record<string, unknown> | undefined,
      checks: req.checks as CheckResult[] | undefined,
    },
  };
}

async function recordHeartbeat(
  supabase: SupabaseClient,
  req: HeartbeatRequest
): Promise<HeartbeatResponse> {
  // Record the heartbeat
  const { data: heartbeatResult, error: heartbeatError } = await supabase.rpc('consumer_heartbeat', {
    p_consumer_type: req.consumer_type,
    p_consumer_key: req.consumer_key,
    p_environment: req.environment,
    p_applied_version_id: req.applied_version_id || null,
    p_status: req.status || 'ok',
    p_metadata: req.metadata || {},
  });

  if (heartbeatError) {
    console.error('Heartbeat RPC error:', heartbeatError);
    return { ok: false, error: heartbeatError.message };
  }

  let checksRecorded = 0;

  // Record any checks
  if (req.checks && req.checks.length > 0) {
    for (const check of req.checks) {
      const { error: checkError } = await supabase.rpc('record_config_check', {
        p_consumer_type: req.consumer_type,
        p_consumer_key: req.consumer_key,
        p_environment: req.environment,
        p_check_type: check.check_type,
        p_status: check.status,
        p_detail: check.detail || {},
      });

      if (!checkError) {
        checksRecorded++;
      } else {
        console.warn('Check recording error:', checkError);
      }
    }
  }

  return {
    ok: true,
    consumer_id: heartbeatResult?.consumer_id,
    timestamp: heartbeatResult?.timestamp,
    checks_recorded: checksRecorded,
  };
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== 'POST') {
    return new Response(
      JSON.stringify({ ok: false, error: 'Method not allowed. Use POST.' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  try {
    const url = Deno.env.get('SUPABASE_URL');
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

    if (!url || !serviceKey) {
      throw new Error('Missing Supabase configuration');
    }

    const supabase = createClient(url, serviceKey, {
      auth: { persistSession: false },
    });

    // Parse and validate request body
    let body: unknown;
    try {
      body = await req.json();
    } catch {
      return new Response(
        JSON.stringify({ ok: false, error: 'Invalid JSON body' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const validation = validateRequest(body);
    if (!validation.valid) {
      return new Response(
        JSON.stringify({ ok: false, error: validation.error }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Record heartbeat
    const result = await recordHeartbeat(supabase, validation.data);

    return new Response(
      JSON.stringify(result),
      { status: result.ok ? 200 : 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Unexpected error:', error);
    return new Response(
      JSON.stringify({ ok: false, error: error instanceof Error ? error.message : 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
