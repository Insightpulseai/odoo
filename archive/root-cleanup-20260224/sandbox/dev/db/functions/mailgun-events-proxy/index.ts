// ═══════════════════════════════════════════════════════════════════════════════
// Supabase Edge Function: mailgun-events-proxy
// ═══════════════════════════════════════════════════════════════════════════════
// Purpose: Receive Mailgun webhook events and store in Supabase
// Version: 1.0.0
// Date: 2026-01-28
// ═══════════════════════════════════════════════════════════════════════════════

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { createHmac } from 'https://deno.land/std@0.168.0/node/crypto.ts'

// ───────────────────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────────────────

interface MailgunEvent {
  event: string
  timestamp: number
  'Message-Id': string
  recipient: string
  sender?: string
  subject?: string
  'message-id'?: string
  'delivery-status'?: string
  code?: number
  description?: string
  message?: string
  'client-type'?: string
  'client-os'?: string
  'client-name'?: string
  'device-type'?: string
  'user-agent'?: string
  ip?: string
  country?: string
  region?: string
  city?: string
  url?: string
  error?: string
  reason?: string
  severity?: string
  tags?: string[]
  campaigns?: string[]
  'user-variables'?: Record<string, any>
}

interface MailgunWebhook {
  signature: {
    timestamp: string
    token: string
    signature: string
  }
  'event-data': MailgunEvent
}

interface EmailEventInsert {
  event_type: string
  event_timestamp: string
  message_id: string
  recipient: string
  sender?: string
  subject?: string
  mailgun_id?: string
  mailgun_timestamp?: number
  mailgun_token?: string
  mailgun_signature?: string
  delivery_status?: string
  delivery_code?: number
  delivery_description?: string
  delivery_message?: string
  client_type?: string
  client_os?: string
  client_name?: string
  device_type?: string
  user_agent?: string
  ip_address?: string
  country?: string
  region?: string
  city?: string
  url?: string
  error_code?: string
  error_reason?: string
  severity?: string
  tags?: string[]
  campaigns?: string[]
  user_variables?: Record<string, any>
  raw_payload: Record<string, any>
}

// ───────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────────────────

/**
 * Verify Mailgun webhook signature
 */
function verifyMailgunSignature(
  timestamp: string,
  token: string,
  signature: string,
  signingKey: string
): boolean {
  if (!timestamp || !token || !signature || !signingKey) {
    return false
  }

  const hmac = createHmac('sha256', signingKey)
  hmac.update(`${timestamp}${token}`)
  const digest = hmac.digest('hex')

  return digest === signature
}

/**
 * Transform Mailgun event to Supabase schema
 */
function transformEvent(webhook: MailgunWebhook): EmailEventInsert {
  const eventData = webhook['event-data']
  const signature = webhook.signature

  return {
    event_type: eventData.event,
    event_timestamp: new Date(eventData.timestamp * 1000).toISOString(),
    message_id: eventData['Message-Id'] || eventData['message-id'] || '',
    recipient: eventData.recipient,
    sender: eventData.sender,
    subject: eventData.subject,
    mailgun_id: eventData['Message-Id'] || eventData['message-id'],
    mailgun_timestamp: eventData.timestamp,
    mailgun_token: signature.token,
    mailgun_signature: signature.signature,
    delivery_status: eventData['delivery-status'],
    delivery_code: eventData.code,
    delivery_description: eventData.description,
    delivery_message: eventData.message,
    client_type: eventData['client-type'],
    client_os: eventData['client-os'],
    client_name: eventData['client-name'],
    device_type: eventData['device-type'],
    user_agent: eventData['user-agent'],
    ip_address: eventData.ip,
    country: eventData.country,
    region: eventData.region,
    city: eventData.city,
    url: eventData.url,
    error_code: eventData.error,
    error_reason: eventData.reason,
    severity: eventData.severity,
    tags: eventData.tags,
    campaigns: eventData.campaigns,
    user_variables: eventData['user-variables'],
    raw_payload: webhook,
  }
}

// ───────────────────────────────────────────────────────────────────────────────
// Main Handler
// ───────────────────────────────────────────────────────────────────────────────

serve(async (req: Request) => {
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  }

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Only accept POST requests
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        {
          status: 405,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    // Parse webhook payload
    const webhook: MailgunWebhook = await req.json()

    // Get signing key from environment
    const signingKey = Deno.env.get('MAILGUN_WEBHOOK_SIGNING_KEY')

    // Verify signature (optional for testing, required for production)
    if (signingKey) {
      const { timestamp, token, signature } = webhook.signature

      if (!verifyMailgunSignature(timestamp, token, signature, signingKey)) {
        console.error('Invalid Mailgun signature')
        return new Response(
          JSON.stringify({ error: 'Invalid signature' }),
          {
            status: 403,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          }
        )
      }
    }

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Transform and insert event
    const eventInsert = transformEvent(webhook)

    const { data, error } = await supabase
      .from('email.events')
      .insert([eventInsert])
      .select()

    if (error) {
      console.error('Supabase insert error:', error)
      return new Response(
        JSON.stringify({ error: 'Database insert failed', details: error.message }),
        {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    console.log('Event stored:', {
      event_type: eventInsert.event_type,
      recipient: eventInsert.recipient,
      message_id: eventInsert.message_id,
    })

    // Return success
    return new Response(
      JSON.stringify({
        ok: true,
        event_id: data[0].id,
        event_type: eventInsert.event_type,
        recipient: eventInsert.recipient,
      }),
      {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  } catch (error) {
    console.error('Edge function error:', error)

    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})

// ═══════════════════════════════════════════════════════════════════════════════
// Usage:
// ═══════════════════════════════════════════════════════════════════════════════
//
// Deploy:
//   supabase functions deploy mailgun-events-proxy \
//     --project-ref spdtwktxdalcfigzeqrz
//
// Set secrets:
//   supabase secrets set MAILGUN_WEBHOOK_SIGNING_KEY=your_key_here \
//     --project-ref spdtwktxdalcfigzeqrz
//
// Configure Mailgun webhook:
//   curl -u "api:${MAILGUN_API_KEY}" \
//     https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks \
//     -F id=tracking \
//     -F url="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/mailgun-events-proxy"
//
// Test locally:
//   supabase functions serve mailgun-events-proxy --env-file .env.local
//
//   curl -X POST http://localhost:54321/functions/v1/mailgun-events-proxy \
//     -H "Content-Type: application/json" \
//     -d @test-event.json
//
// ═══════════════════════════════════════════════════════════════════════════════
