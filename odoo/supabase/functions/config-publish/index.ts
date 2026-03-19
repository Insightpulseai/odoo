/**
 * config-publish Edge Function
 *
 * Accepts config artifacts from CI/CD and publishes them to the Config Registry.
 * Git is SSOT; this function creates versioned snapshots in Supabase.
 *
 * POST body:
 * {
 *   kind: 'design_tokens' | 'workflow' | 'seed_bundle' | 'odoo_config' | 'feature_flag',
 *   slug: string,
 *   name?: string,
 *   description?: string,
 *   version: string,
 *   git_sha: string,
 *   content_json?: object,
 *   content_text?: string,
 *   auto_promote?: boolean (default: true)
 * }
 */

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

interface PublishRequest {
  kind: 'design_tokens' | 'workflow' | 'seed_bundle' | 'odoo_config' | 'feature_flag';
  slug: string;
  name?: string;
  description?: string;
  version: string;
  git_sha: string;
  content_json?: Record<string, unknown>;
  content_text?: string;
  auto_promote?: boolean;
}

interface PublishResponse {
  ok: boolean;
  artifact_id?: string;
  version_id?: string;
  deduped?: boolean;
  promoted?: boolean;
  error?: string;
  message?: string;
}

function validateRequest(body: unknown): { valid: true; data: PublishRequest } | { valid: false; error: string } {
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Request body must be a JSON object' };
  }

  const req = body as Record<string, unknown>;

  const validKinds = ['design_tokens', 'workflow', 'seed_bundle', 'odoo_config', 'feature_flag'];
  if (!req.kind || !validKinds.includes(req.kind as string)) {
    return { valid: false, error: `kind must be one of: ${validKinds.join(', ')}` };
  }

  if (!req.slug || typeof req.slug !== 'string' || req.slug.length < 1) {
    return { valid: false, error: 'slug is required and must be a non-empty string' };
  }

  if (!req.version || typeof req.version !== 'string') {
    return { valid: false, error: 'version is required' };
  }

  if (!req.git_sha || typeof req.git_sha !== 'string') {
    return { valid: false, error: 'git_sha is required' };
  }

  if (!req.content_json && !req.content_text) {
    return { valid: false, error: 'Either content_json or content_text is required' };
  }

  return {
    valid: true,
    data: {
      kind: req.kind as PublishRequest['kind'],
      slug: req.slug as string,
      name: (req.name as string) || req.slug as string,
      description: req.description as string | undefined,
      version: req.version as string,
      git_sha: req.git_sha as string,
      content_json: req.content_json as Record<string, unknown> | undefined,
      content_text: req.content_text as string | undefined,
      auto_promote: req.auto_promote !== false, // default true
    },
  };
}

async function publishConfig(
  supabase: SupabaseClient,
  req: PublishRequest
): Promise<PublishResponse> {
  // Call the RPC function that handles upsert + deduplication
  const { data, error } = await supabase.rpc('publish_config_version', {
    p_kind: req.kind,
    p_slug: req.slug,
    p_name: req.name,
    p_description: req.description || null,
    p_version: req.version,
    p_git_sha: req.git_sha,
    p_content_json: req.content_json || null,
    p_content_text: req.content_text || null,
    p_auto_promote: req.auto_promote,
  });

  if (error) {
    console.error('RPC error:', error);
    return { ok: false, error: error.message };
  }

  return data as PublishResponse;
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

    // Publish the config
    const result = await publishConfig(supabase, validation.data);

    const status = result.ok ? (result.deduped ? 200 : 201) : 500;
    return new Response(
      JSON.stringify(result),
      { status, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Unexpected error:', error);
    return new Response(
      JSON.stringify({ ok: false, error: error instanceof Error ? error.message : 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
