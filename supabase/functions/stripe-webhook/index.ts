// =============================================================================
// Edge Function: stripe-webhook
// Purpose:   Receive Stripe webhook events, verify signature, and persist
//            idempotently to ops.stripe_events via ops.ingest_stripe_event().
//
// Consumer:  Stripe webhook endpoint we_1T5kODHgVbKNXUzmfAs9Zbd5
// SSOT:      ssot/runtime/prod_settings.yaml :: payments.stripe.webhook
// Secret:    STRIPE_WEBHOOK_SIGNING_SECRET (env-scoped via _shared/env.ts)
// Migration: supabase/migrations/20260228000002_ops_stripe_events.sql
//
// HTTP responses:
//   200  event accepted (new or duplicate)
//   400  bad request (missing headers, bad signature, replay, unrecognised event)
//   500  database error — Stripe will retry on non-2xx
// =============================================================================

import { createClient } from "https://esm.sh/v135/@supabase/supabase-js@2.47.10";
import { getEnvSecret } from "../_shared/env.ts";

// ---------------------------------------------------------------------------
// Allowed events — mirrors ssot/runtime/prod_settings.yaml
// payments.stripe.webhook.allowed_events
// ---------------------------------------------------------------------------
const ALLOWED_EVENTS = new Set([
  "checkout.session.completed",
  "invoice.paid",
  "invoice.payment_failed",
  "customer.subscription.created",
  "customer.subscription.updated",
  "customer.subscription.deleted",
]);

// ---------------------------------------------------------------------------
// Crypto helpers
// ---------------------------------------------------------------------------

/** Compute HMAC-SHA256(secret, msg) → lowercase hex */
async function hmacSHA256(secret: string, msg: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(msg),
  );
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Constant-time string comparison to prevent timing attacks */
function timingSafeEqual(a: string, b: string): boolean {
  const enc = new TextEncoder();
  const aa = enc.encode(a);
  const bb = enc.encode(b);
  if (aa.length !== bb.length) return false;
  let out = 0;
  for (let i = 0; i < aa.length; i++) out |= aa[i] ^ bb[i];
  return out === 0;
}

// ---------------------------------------------------------------------------
// Stripe Stripe-Signature header parser
// Header format: t=<unix_seconds>,v1=<hex_hmac>[,v0=<deprecated>]
// ---------------------------------------------------------------------------
interface StripeSig {
  timestamp: number; // unix seconds
  v1: string;        // expected HMAC hex
}

function parseStripeSignature(header: string): StripeSig | null {
  const parts = header.split(",");
  let timestamp: number | null = null;
  let v1: string | null = null;

  for (const part of parts) {
    const eqIdx = part.indexOf("=");
    if (eqIdx === -1) continue;
    const k = part.slice(0, eqIdx).trim();
    const v = part.slice(eqIdx + 1).trim();
    if (k === "t") timestamp = parseInt(v, 10);
    if (k === "v1" && !v1) v1 = v; // take first v1
  }

  if (timestamp === null || !v1) return null;
  return { timestamp, v1 };
}

// ---------------------------------------------------------------------------
// Event field extraction
// ---------------------------------------------------------------------------
interface IngestArgs {
  p_event_id: string;
  p_type: string;
  p_customer_id: string | null;
  p_subscription_id: string | null;
  p_invoice_id: string | null;
  p_payload: Record<string, unknown>;
  p_stripe_created_at: string | null; // ISO8601
  p_webhook_id: string | null;
  p_api_version: string | null;
}

function extractArgs(event: Record<string, unknown>): IngestArgs {
  const obj = (event.data as Record<string, unknown>)?.object as
    | Record<string, unknown>
    | undefined ?? {};

  // customer_id: top-level customer field on the object
  const customerId =
    (obj.customer as string | null) ??
    (event.customer as string | null) ??
    null;

  // subscription_id: direct id if the object is a subscription, else nested
  const subscriptionId =
    (obj.object === "subscription" ? (obj.id as string) : null) ??
    (obj.subscription as string | null) ??
    null;

  // invoice_id: direct id if object is an invoice, else nested
  const invoiceId =
    (obj.object === "invoice" ? (obj.id as string) : null) ??
    (obj.invoice as string | null) ??
    null;

  // stripe_created_at: event.created is unix epoch seconds
  const createdEpoch = event.created as number | null;
  const stripeCreatedAt = createdEpoch
    ? new Date(createdEpoch * 1000).toISOString()
    : null;

  return {
    p_event_id: event.id as string,
    p_type: event.type as string,
    p_customer_id: customerId,
    p_subscription_id: subscriptionId,
    p_invoice_id: invoiceId,
    p_payload: event,
    p_stripe_created_at: stripeCreatedAt,
    p_webhook_id: null, // not exposed by Stripe in the event body
    p_api_version: (event.api_version as string | null) ?? null,
  };
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  // --- 1. Read raw body (must be bytes-identical to what Stripe signed) ---
  const rawBody = await req.text();

  // --- 2. Parse and verify Stripe-Signature header ---
  const sigHeader = req.headers.get("stripe-signature") ??
    req.headers.get("Stripe-Signature") ?? "";
  if (!sigHeader) {
    return new Response("Missing Stripe-Signature header", { status: 400 });
  }

  const parsed = parseStripeSignature(sigHeader);
  if (!parsed) {
    return new Response("Malformed Stripe-Signature header", { status: 400 });
  }

  // --- 3. Replay window: reject if event is older than 300 seconds ---
  const nowSeconds = Math.floor(Date.now() / 1000);
  if (Math.abs(nowSeconds - parsed.timestamp) > 300) {
    return new Response("Webhook timestamp outside tolerance window", {
      status: 400,
    });
  }

  // --- 4. Retrieve signing secret (environment-scoped via _shared/env.ts) ---
  let webhookSecret: string;
  try {
    webhookSecret = getEnvSecret("STRIPE_WEBHOOK_SIGNING_SECRET");
  } catch (e) {
    console.error("Missing STRIPE_WEBHOOK_SIGNING_SECRET:", e);
    return new Response("Webhook secret not configured", { status: 500 });
  }

  // --- 5. Compute and compare HMAC ---
  const signedPayload = `${parsed.timestamp}.${rawBody}`;
  const expectedHmac = await hmacSHA256(webhookSecret, signedPayload);
  if (!timingSafeEqual(expectedHmac, parsed.v1)) {
    return new Response("Signature verification failed", { status: 400 });
  }

  // --- 6. Parse event JSON ---
  let event: Record<string, unknown>;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return new Response("Invalid JSON body", { status: 400 });
  }

  const eventId = event.id as string | undefined;
  const eventType = event.type as string | undefined;

  if (!eventId || !eventType) {
    return new Response("Event missing id or type", { status: 400 });
  }

  // --- 7. Allowlist filter (SSOT: payments.stripe.webhook.allowed_events) ---
  if (!ALLOWED_EVENTS.has(eventType)) {
    // Return 200 so Stripe doesn't retry unhandled event types
    return new Response(
      JSON.stringify({ ok: true, ignored: true, reason: "event_not_in_allowlist" }),
      { status: 200, headers: { "content-type": "application/json" } },
    );
  }

  // --- 8. Persist via idempotent RPC ---
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );

  const args = extractArgs(event);

  const { data, error } = await supabase.schema("ops").rpc("ingest_stripe_event", args);

  if (error) {
    console.error("ops.ingest_stripe_event failed:", error);
    return new Response(`Database error: ${error.message}`, { status: 500 });
  }

  // data = { ok: true, deduped: boolean, event_id: string }
  const result = data as { ok: boolean; deduped: boolean; event_id: string };

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
});
