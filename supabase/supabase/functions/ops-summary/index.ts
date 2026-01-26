/**
 * OPS-SUMMARY Edge Function
 * HMAC-secured proxy for Odoo to read deployment/incident summaries.
 * Keeps service role key out of Odoo.
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

  const secret = Deno.env.get("OPS_SUMMARY_HMAC_SECRET");
  if (!secret) {
    return new Response("Missing OPS_SUMMARY_HMAC_SECRET", { status: 500 });
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

  const system = (body.system as string) || "erp.insightpulseai.net";
  const environment = (body.environment as string) || "prod";

  const sb = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const dep = await sb.rpc("get_deployment_summary", {
    p_system: system,
    p_environment: environment,
  });
  const inc = await sb.rpc("get_incident_summary", {
    p_system: system,
    p_environment: environment,
  });

  if (dep.error) {
    return new Response(dep.error.message, { status: 500 });
  }
  if (inc.error) {
    return new Response(inc.error.message, { status: 500 });
  }

  return new Response(
    JSON.stringify({ deployment: dep.data, incidents: inc.data }),
    {
      headers: { "content-type": "application/json" },
    }
  );
});
