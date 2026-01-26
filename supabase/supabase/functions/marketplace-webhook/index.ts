/**
 * Marketplace Webhook Handler
 * Edge Function for processing webhooks from external marketplace integrations
 *
 * Supported providers:
 * - GitHub (workflow_run, push, release)
 * - Google Drive (changes)
 * - AWS S3 (object events via SNS)
 * - Slack (events)
 * - n8n (workflow callbacks)
 */

import { serve } from 'https://deno.land/std@0.208.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

import { WebhookRequest, HandlerResponse, Provider } from './types.ts';
import { handleGitHubWebhook, verifyGitHubSignature } from './handlers/github.ts';
import { handleGoogleWebhook } from './handlers/google.ts';
import { handleS3Webhook } from './handlers/s3.ts';

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-hub-signature-256, x-github-event, x-github-delivery',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

/**
 * Get secret from Vault or environment
 */
async function getSecret(supabase: ReturnType<typeof createClient>, name: string): Promise<string | null> {
  // Try Vault first
  try {
    const { data, error } = await supabase.rpc('vault.decrypted_secrets', { secret_name: name });
    if (!error && data && data.length > 0) {
      return data[0].decrypted_secret;
    }
  } catch {
    // Vault not available, fall back to env
  }

  // Fall back to environment variable
  return Deno.env.get(name) || null;
}

/**
 * Main webhook handler
 */
async function handleWebhook(req: Request): Promise<Response> {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // Only accept POST
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Parse request
    const url = new URL(req.url);
    const pathParts = url.pathname.split('/').filter(Boolean);

    // Expected path: /marketplace-webhook/{provider}
    // e.g., /marketplace-webhook/github, /marketplace-webhook/google-drive
    const providerSlug = pathParts[pathParts.length - 1] || '';
    const provider = providerSlug.replace('-', '_') as Provider;

    // Get headers
    const headers: Record<string, string> = {};
    req.headers.forEach((value, key) => {
      headers[key.toLowerCase()] = value;
    });

    // Get raw body for signature verification
    const rawBody = await req.text();
    let payload: Record<string, unknown>;

    try {
      payload = JSON.parse(rawBody);
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid JSON payload' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Extract event type from headers or payload
    const eventType =
      headers['x-github-event'] ||
      headers['x-google-event'] ||
      headers['x-amz-sns-message-type'] ||
      (payload.event_type as string) ||
      (payload.type as string) ||
      'unknown';

    // Extract event ID for deduplication
    const eventId =
      headers['x-github-delivery'] ||
      headers['x-google-channel-id'] ||
      (payload.event_id as string) ||
      crypto.randomUUID();

    // Log incoming webhook event
    const { data: loggedEventId } = await supabase.rpc('log_webhook_event', {
      p_source: provider,
      p_event_type: eventType,
      p_event_id: eventId,
      p_payload: payload,
      p_headers: headers,
      p_signature: headers['x-hub-signature-256'] || headers['x-google-channel-token'] || null,
    });

    let response: HandlerResponse;

    // Route to appropriate handler
    switch (provider) {
      case 'github': {
        // Verify GitHub signature
        const webhookSecret = await getSecret(supabase, 'GITHUB_WEBHOOK_SECRET');
        const signature = headers['x-hub-signature-256'];

        if (webhookSecret && signature) {
          const isValid = await verifyGitHubSignature(rawBody, signature, webhookSecret);
          if (!isValid) {
            // Mark event as verification failed
            await supabase.rpc('mark_event_processed', {
              p_event_id: loggedEventId,
              p_error_message: 'Invalid webhook signature',
            });

            return new Response(JSON.stringify({ error: 'Invalid signature' }), {
              status: 401,
              headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            });
          }

          // Update event as verified
          await supabase
            .from('webhook_events')
            .update({ verified: true })
            .eq('id', loggedEventId);
        }

        // Get GitHub token for API calls
        const githubToken = await getSecret(supabase, 'GITHUB_TOKEN') || '';
        response = await handleGitHubWebhook(eventType, payload, supabase, githubToken);
        break;
      }

      case 'google_drive':
      case 'google_docs':
      case 'google_sheets':
      case 'gmail': {
        response = await handleGoogleWebhook(eventType, payload, supabase);
        break;
      }

      case 'aws_s3':
      case 'cloudflare_r2': {
        response = await handleS3Webhook(eventType, payload, supabase);
        break;
      }

      case 'slack': {
        // Slack URL verification challenge
        if (payload.type === 'url_verification') {
          return new Response(JSON.stringify({ challenge: payload.challenge }), {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          });
        }

        // Log and acknowledge Slack events
        response = {
          success: true,
          event_id: loggedEventId,
          details: { message: 'Slack event logged for processing' },
        };
        break;
      }

      case 'n8n': {
        // n8n workflow callbacks
        response = {
          success: true,
          event_id: loggedEventId,
          details: { message: 'n8n callback logged' },
        };
        break;
      }

      default: {
        response = {
          success: false,
          error: `Unknown provider: ${provider}`,
        };
      }
    }

    // Mark event as processed
    await supabase.rpc('mark_event_processed', {
      p_event_id: loggedEventId,
      p_error_message: response.success ? null : response.error,
    });

    // Return response
    const statusCode = response.success ? 200 : 500;
    return new Response(JSON.stringify(response), {
      status: statusCode,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Webhook handler error:', error);

    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error',
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}

// Health check endpoint
async function handleHealth(): Promise<Response> {
  return new Response(
    JSON.stringify({
      status: 'healthy',
      service: 'marketplace-webhook',
      timestamp: new Date().toISOString(),
    }),
    {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    }
  );
}

// Main server
serve(async (req: Request) => {
  const url = new URL(req.url);

  // Health check
  if (url.pathname.endsWith('/health') || url.pathname.endsWith('/_health')) {
    return handleHealth();
  }

  // Webhook handler
  return handleWebhook(req);
});
