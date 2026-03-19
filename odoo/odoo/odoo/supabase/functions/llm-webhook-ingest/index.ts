/**
 * llm-webhook-ingest — Supabase Edge Function
 *
 * Receives signed webhook payloads from ipai_llm_supabase_bridge (Odoo)
 * and ingests them into ops.run_events via the ops.ingest_bridge_event RPC.
 *
 * Security:
 *   - HMAC-SHA256 signature verification
 *   - Service role access (no user auth required for server-to-server)
 *   - Idempotent (duplicate events are safely ignored)
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const WEBHOOK_SECRET = Deno.env.get("LLM_BRIDGE_WEBHOOK_SECRET") || "";

Deno.serve(async (req: Request) => {
  // Only accept POST
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Read body
  const bodyBytes = new Uint8Array(await req.arrayBuffer());
  const bodyText = new TextDecoder().decode(bodyBytes);

  // Verify HMAC signature
  const signatureHeader = req.headers.get("X-Signature-256") || "";
  if (WEBHOOK_SECRET) {
    const expectedSig = await computeHmac(WEBHOOK_SECRET, bodyBytes);
    const providedSig = signatureHeader.replace("sha256=", "");

    if (!timingSafeEqual(expectedSig, providedSig)) {
      console.error("Signature verification failed");
      return new Response(JSON.stringify({ error: "Invalid signature" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }
  }

  // Parse payload
  let payload;
  try {
    payload = JSON.parse(bodyText);
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Initialize Supabase client with service role
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseKey);

  // Handle single event or batch
  const events = Array.isArray(payload) ? payload : [payload];
  const results = [];

  for (const event of events) {
    try {
      const { data, error } = await supabase.rpc("ingest_bridge_event", {
        p_event_type: event.event_type,
        p_idempotency_key: event.idempotency_key || null,
        p_odoo_db: event.odoo_db || null,
        p_odoo_model: event.source_model || null,
        p_odoo_id: event.source_id || null,
        p_odoo_event_id: event.event_id || null,
        p_payload: event.payload || {},
        p_timestamp: event.timestamp || new Date().toISOString(),
      });

      if (error) {
        console.error("RPC error:", error);
        results.push({ event_id: event.event_id, status: "error", detail: error.message });
      } else {
        results.push({ event_id: event.event_id, status: "ingested", id: data });
      }
    } catch (err) {
      console.error("Processing error:", err);
      results.push({ event_id: event.event_id, status: "error", detail: String(err) });
    }
  }

  const hasErrors = results.some((r) => r.status === "error");

  return new Response(
    JSON.stringify({
      ingested: results.filter((r) => r.status === "ingested").length,
      errors: results.filter((r) => r.status === "error").length,
      results,
    }),
    {
      status: hasErrors ? 207 : 200,
      headers: { "Content-Type": "application/json" },
    }
  );
});

// ---- Crypto helpers ----

async function computeHmac(secret: string, data: Uint8Array): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, data);
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}
