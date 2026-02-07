/**
 * OPS-HEALTH Edge Function
 * HMAC-secured endpoint for CI router to check alert state.
 * Returns DLQ count, error rate, and other health signals.
 */
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

function toHex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function hmacSha256(secret: string, msg: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return toHex(sig);
}

Deno.serve(async (req) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "content-type, x-ops-signature",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  const secret = Deno.env.get("OPS_HEALTH_HMAC_SECRET");
  if (!secret) {
    return new Response("Missing OPS_HEALTH_HMAC_SECRET", { status: 500 });
  }

  const sig = req.headers.get("x-ops-signature") || "";
  const raw = await req.text();
  const expected = await hmacSha256(secret, raw);
  if (sig !== expected) {
    return new Response("Unauthorized", { status: 401 });
  }

  let body: Record<string, unknown>;
  try {
    body = JSON.parse(raw);
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }

  const system = (body.system as string) || "erp.insightpulseai.com";
  const environment = (body.environment as string) || "prod";
  const windowMinutes = (body.window_minutes as number) || 60;

  const sb = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const st = await sb.rpc("get_alert_state", {
    p_system: system,
    p_environment: environment,
    p_window_minutes: windowMinutes,
  });

  if (st.error) {
    return new Response(st.error.message, { status: 500 });
  }

  return new Response(JSON.stringify(st.data), {
    headers: { "content-type": "application/json" },
  });
});
