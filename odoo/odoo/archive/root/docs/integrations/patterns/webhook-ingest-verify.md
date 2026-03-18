# Webhook Ingest & Verify Pattern

## Purpose
Signed webhook ingestion pattern for external services (Stripe, GitHub, etc.) with signature verification and idempotency enforcement.

## Folder Layout
```
supabase/functions/webhook-<service>/
├── index.ts                 # Webhook handler
├── verify.ts                # Signature verification logic
└── README.md                # Service-specific webhook docs
```

## Required Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for database access
- `WEBHOOK_SECRET`: Service-specific webhook signing secret (e.g., Stripe webhook secret)

## Minimal Code Skeleton

**index.ts:**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import { verifySignature } from "./verify.ts"

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const webhookSecret = Deno.env.get('WEBHOOK_SECRET')!

serve(async (req) => {
  try {
    // Get signature from headers
    const signature = req.headers.get('stripe-signature') // or service-specific header
    const rawBody = await req.text()

    // Verify webhook signature
    const isValid = await verifySignature(rawBody, signature, webhookSecret)
    if (!isValid) {
      return new Response('Invalid signature', { status: 401 })
    }

    const event = JSON.parse(rawBody)
    const idempotencyKey = event.id // or service-specific event ID

    // Initialize Supabase client
    const supabase = createClient(supabaseUrl, supabaseServiceRoleKey)

    // Idempotency check: have we already processed this webhook?
    const { data: existing } = await supabase
      .from('ops.runs')
      .select('run_id')
      .eq('idempotency_key', idempotencyKey)
      .single()

    if (existing) {
      return new Response(
        JSON.stringify({ message: 'Already processed', run_id: existing.run_id }),
        { headers: { "Content-Type": "application/json" }, status: 200 }
      )
    }

    // Create ops.runs record
    const { data: run, error: runError } = await supabase
      .from('ops.runs')
      .insert({
        run_id: crypto.randomUUID(),
        function_name: 'webhook-service',
        idempotency_key: idempotencyKey,
        started_at: new Date().toISOString(),
        status: 'running',
        metadata: { event_type: event.type }
      })
      .select()
      .single()

    if (runError) throw runError

    // Process webhook payload
    // IMPORTANT: Route to exception queue if Odoo SOR conflict detected

    // Update run status
    await supabase
      .from('ops.runs')
      .update({ status: 'completed', completed_at: new Date().toISOString() })
      .eq('run_id', run.run_id)

    return new Response(
      JSON.stringify({ success: true, run_id: run.run_id }),
      { headers: { "Content-Type": "application/json" }, status: 200 }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { "Content-Type": "application/json" }, status: 500 }
    )
  }
})
```

**verify.ts:**
```typescript
export async function verifySignature(
  payload: string,
  signature: string | null,
  secret: string
): Promise<boolean> {
  if (!signature) return false

  try {
    // Example for HMAC SHA256 (adjust per service)
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"]
    )

    const signatureBuffer = hexToBuffer(signature)
    const dataBuffer = encoder.encode(payload)

    return await crypto.subtle.verify(
      "HMAC",
      key,
      signatureBuffer,
      dataBuffer
    )
  } catch {
    return false
  }
}

function hexToBuffer(hex: string): ArrayBuffer {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16)
  }
  return bytes.buffer
}
```

## Failure Modes
- **Invalid signature**: Always return 401, never process unsigned webhooks
- **Replay attacks**: Idempotency check prevents duplicate processing
- **Webhook timeout**: Service expects 2xx response within 30s; use async queue for long processing
- **Missing secret**: Function fails fast if `WEBHOOK_SECRET` not set

## SSOT/SOR Boundary Notes
- **Idempotency enforcement**: Use `ops.runs.idempotency_key` to prevent duplicate processing
- **Exception routing**: If webhook payload conflicts with Odoo SOR data, route to exception queue for human review
- **Audit trail**: Every webhook must emit `ops.runs` + `ops.run_events` regardless of outcome
- **No direct SOR writes**: Webhook handlers must NEVER write to Odoo-owned domains (invoices, payments, journal entries)
- **Signature verification**: ALWAYS verify webhook signature before processing (no exceptions)
