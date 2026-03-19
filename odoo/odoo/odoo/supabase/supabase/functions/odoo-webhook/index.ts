import { createClient } from "https://esm.sh/v135/@supabase/supabase-js@2.47.10";

function timingSafeEqual(a: string, b: string) {
  const enc = new TextEncoder();
  const aa = enc.encode(a);
  const bb = enc.encode(b);
  if (aa.length !== bb.length) return false;
  let out = 0;
  for (let i = 0; i < aa.length; i++) out |= aa[i] ^ bb[i];
  return out === 0;
}

async function hmacSHA256(secret: string, msg: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const ODOO_WEBHOOK_SECRET = Deno.env.get("ODOO_WEBHOOK_SECRET")!;

  const raw = await req.text();
  const sig = req.headers.get("x-ipai-signature") ?? "";
  const ts = req.headers.get("x-ipai-timestamp") ?? "";
  const idem = req.headers.get("x-idempotency-key") ?? "";

  if (!ts || !idem || !sig) return new Response("Missing headers", { status: 400 });

  // Replay window (5 min)
  const now = Date.now();
  const tsMs = Number(ts);
  if (!Number.isFinite(tsMs) || Math.abs(now - tsMs) > 5 * 60 * 1000) {
    return new Response("Stale timestamp", { status: 401 });
  }

  // Signature = HMAC(secret, `${ts}.${raw}`)
  const expected = await hmacSHA256(ODOO_WEBHOOK_SECRET, `${ts}.${raw}`);
  if (!timingSafeEqual(expected, sig)) return new Response("Bad signature", { status: 401 });

  let body: any;
  try { body = JSON.parse(raw); } catch { return new Response("Bad JSON", { status: 400 }); }

  const event_type = body.event_type;
  const aggregate_type = body.aggregate_type;
  const aggregate_id = body.aggregate_id;
  const payload = body.payload ?? body;

  if (!event_type || !aggregate_type || !aggregate_id) {
    return new Response("Missing fields", { status: 400 });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  // Write outbox using RPC (integration schema not exposed via PostgREST)
  const { error: e1 } = await supabase.rpc("insert_outbox_event", {
    p_source: "odoo",
    p_event_type: event_type,
    p_aggregate_type: aggregate_type,
    p_aggregate_id: String(aggregate_id),
    p_payload: payload,
    p_idempotency_key: idem
  });

  if (e1) return new Response(`DB error: ${e1.message}`, { status: 500 });

  // Write event log
  await supabase.rpc("insert_event_log", {
    p_source: "odoo",
    p_event_type: event_type,
    p_aggregate_type: aggregate_type,
    p_aggregate_id: String(aggregate_id),
    p_payload: payload
  });

  return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "content-type": "application/json" } });
});
