import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

// --- Supabase service client ---
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const sb = createClient(SUPABASE_URL, SERVICE_ROLE);

// --- Secrets (set via `supabase secrets set`) ---
const STRIPE_WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET") ?? "";
const STRIPE_TOLERANCE_SECONDS = Number(
  Deno.env.get("STRIPE_TOLERANCE_SECONDS") ?? "300",
);
const VERCEL_WEBHOOK_SECRET = Deno.env.get("VERCEL_WEBHOOK_SECRET") ?? "";
const N8N_WEBHOOK_SECRET = Deno.env.get("N8N_WEBHOOK_SECRET") ?? "";
const CLOUDFLARE_SHARED_SECRET = Deno.env.get("CLOUDFLARE_SHARED_SECRET") ?? "";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, stripe-signature, x-vercel-signature, x-webhook-secret, x-n8n-signature",
};

// Basic timing-safe compare
function safeEq(a: string, b: string) {
  const ae = new TextEncoder().encode(a);
  const be = new TextEncoder().encode(b);
  if (ae.length !== be.length) return false;
  let out = 0;
  for (let i = 0; i < ae.length; i++) out |= ae[i] ^ be[i];
  return out === 0;
}

function h(req: Request, k: string) {
  return req.headers.get(k) ?? req.headers.get(k.toLowerCase()) ?? "";
}

// Stripe signature verify (multi-sig + tolerance)
function parseStripeSigHeader(sig: string) {
  const out: { t?: number; v1: string[] } = { v1: [] };
  for (const part of sig.split(",")) {
    const [k, v] = part.split("=").map((x) => x.trim());
    if (k === "t") out.t = Number(v);
    if (k === "v1" && v) out.v1.push(v);
  }
  return out;
}

async function hmacSha256Hex(secret: string, msg: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(msg),
  );
  return Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function verifyStripe(req: Request, raw: string) {
  if (!STRIPE_WEBHOOK_SECRET) return false;
  const sig = h(req, "stripe-signature");
  if (!sig) return false;

  const parsed = parseStripeSigHeader(sig);
  if (!parsed.t || parsed.v1.length === 0) return false;

  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - parsed.t) > STRIPE_TOLERANCE_SECONDS) return false;

  const signedPayload = `${parsed.t}.${raw}`;
  const expected = await hmacSha256Hex(STRIPE_WEBHOOK_SECRET, signedPayload);

  // multi-sig: accept any v1 matching our secret output
  for (const v1 of parsed.v1) {
    if (safeEq(expected, v1)) return true;
  }
  return false;
}

// Vercel signature verify (HMAC)
async function hmacSha1Hex(secret: string, msg: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-1" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(msg),
  );
  return Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function verifyVercel(req: Request, raw: string) {
  if (!VERCEL_WEBHOOK_SECRET) return false;
  const sig = h(req, "x-vercel-signature") || h(req, "x-webhook-secret");
  if (!sig) return false;

  // Vercel generally is SHA-1
  const expected = await hmacSha1Hex(VERCEL_WEBHOOK_SECRET, raw);
  return safeEq(expected, sig);
}

// Shared secret fallbacks
function verifyN8n(req: Request) {
  if (!N8N_WEBHOOK_SECRET) return false;
  const secret = h(req, "x-n8n-signature") || h(req, "x-webhook-secret");
  return !!secret && safeEq(secret, N8N_WEBHOOK_SECRET);
}

function verifyCloudflare(req: Request) {
  if (!CLOUDFLARE_SHARED_SECRET) return false;
  const secret = h(req, "x-webhook-secret");
  return !!secret && safeEq(secret, CLOUDFLARE_SHARED_SECRET);
}

function inferEventType(integration: string, payload: any) {
  if (integration === "stripe") return payload?.type ?? null;
  if (integration === "vercel")
    return payload?.type ?? payload?.event ?? "vercel.event";
  if (integration === "n8n")
    return payload?.type ?? payload?.event ?? "n8n.event";
  if (integration === "resend")
    return payload?.type ?? payload?.event ?? "resend.event";
  if (integration === "cloudflare")
    return payload?.type ?? payload?.event ?? "cloudflare.event";
  return payload?.type ?? payload?.event ?? null;
}

function inferIdempotencyKey(integration: string, payload: any, req: Request) {
  const headerKey = h(req, "x-idempotency-key");
  if (payload?.id) return String(payload.id);
  if (payload?.event_id) return String(payload.event_id);
  if (integration === "stripe" && payload?.id) return String(payload.id);
  if (integration === "vercel" && payload?.id) return String(payload.id);
  return headerKey || null;
}

serve(async (req) => {
  if (req.method === "OPTIONS")
    return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST")
    return new Response("method not allowed", { status: 405 });

  const u = new URL(req.url);
  const integration = (
    u.searchParams.get("integration") || "unknown"
  ).toLowerCase();

  const raw = await req.text();
  let payload: any = {};
  try {
    payload = raw ? JSON.parse(raw) : {};
  } catch {
    payload = { raw };
  }

  // Strict valid signature routing
  let signatureValid = false;
  if (integration === "stripe") signatureValid = await verifyStripe(req, raw);
  else if (integration === "vercel")
    signatureValid = await verifyVercel(req, raw);
  else if (integration === "n8n") signatureValid = verifyN8n(req);
  else if (integration === "cloudflare") signatureValid = verifyCloudflare(req);
  else signatureValid = true;

  const eventType = inferEventType(integration, payload);
  const idem = inferIdempotencyKey(integration, payload, req);

  // 1. Ensure integration registry knows this
  await sb
    .from("ops.integrations")
    .upsert({ name: integration }, { onConflict: "name" });

  // 2. Insert to immutable webhook log
  const { data: ev, error: evErr } = await sb
    .from("ops.webhook_events")
    .insert({
      integration,
      event_type: eventType,
      idempotency_key: idem,
      signature_valid: signatureValid,
      headers: Object.fromEntries(req.headers.entries()),
      payload,
      status: "received",
    })
    .select("id")
    .single();

  if (evErr) {
    if (evErr.code === "23505")
      return new Response("ok_duplicate", {
        headers: corsHeaders,
        status: 200,
      });
    return new Response(JSON.stringify({ error: evErr.message }), {
      headers: corsHeaders,
      status: 500,
    });
  }

  // 3. Enqueue parsing to the jobs worker
  await sb.from("ops.jobs").insert({
    integration,
    job_type: eventType || `${integration}.event`,
    payload: { webhook_event_id: ev.id, payload },
    status: "queued",
  });

  // 4. Activity heartbeat
  await sb
    .from("ops.integrations")
    .update({ last_seen_at: new Date().toISOString() })
    .eq("name", integration);

  return new Response("ok", { headers: corsHeaders, status: 200 });
});
