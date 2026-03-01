// Supabase Edge Function: GitHub App Webhook Receiver
// Contract: C-19 (docs/contracts/GITHUB_APP_CONTRACT.md)
//
// Handles incoming GitHub App webhook events:
// - Verifies X-Hub-Signature-256 using HMAC-SHA256
// - Deduplicates by X-GitHub-Delivery against ops.github_events
// - Persists event durably before returning 200
// - Routes by X-GitHub-Event header to typed handlers

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const WEBHOOK_SECRET = Deno.env.get("GITHUB_WEBHOOK_SECRET")!;

async function verifySignature(
  secret: string,
  payload: string,
  signatureHeader: string,
): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
  const expected = "sha256=" + Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return expected === signatureHeader;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const signatureHeader = req.headers.get("x-hub-signature-256");
  const deliveryId = req.headers.get("x-github-delivery");
  const eventType = req.headers.get("x-github-event");
  const body = await req.text();

  // Verify signature
  if (!signatureHeader || !WEBHOOK_SECRET) {
    return new Response(JSON.stringify({ error: "Missing signature or secret" }), { status: 401 });
  }

  const valid = await verifySignature(WEBHOOK_SECRET, body, signatureHeader);
  if (!valid) {
    return new Response(JSON.stringify({ error: "Invalid signature" }), { status: 401 });
  }

  // Initialize Supabase client
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  // Deduplicate
  if (deliveryId) {
    const { data: existing } = await supabase
      .from("github_events")
      .select("delivery_id")
      .eq("delivery_id", deliveryId)
      .maybeSingle();

    if (existing) {
      return new Response(JSON.stringify({ ok: true, deduplicated: true }), { status: 200 });
    }
  }

  // Parse payload
  const payload = JSON.parse(body);
  const action = payload.action || null;
  const repoFullName = payload.repository?.full_name || null;
  const installationId = payload.installation?.id || null;

  // Persist to ops.github_events
  const { error: insertError } = await supabase
    .schema("ops")
    .from("github_events")
    .insert({
      delivery_id: deliveryId,
      event_type: eventType,
      action: action,
      repo_full_name: repoFullName,
      installation_id: installationId,
      payload: payload,
      processed: false,
    });

  if (insertError) {
    // If unique constraint violation, it's a duplicate
    if (insertError.code === "23505") {
      return new Response(JSON.stringify({ ok: true, deduplicated: true }), { status: 200 });
    }
    console.error("Insert error:", insertError);
    return new Response(JSON.stringify({ error: "Failed to persist event" }), { status: 500 });
  }

  // Route event (fire-and-forget processing)
  // For now, just log — handlers will be added in Phase 5
  console.log(`GitHub event: ${eventType}.${action || ""} from ${repoFullName}`);

  return new Response(
    JSON.stringify({ ok: true, delivery_id: deliveryId, event_type: eventType }),
    { status: 200, headers: { "Content-Type": "application/json" } },
  );
});
