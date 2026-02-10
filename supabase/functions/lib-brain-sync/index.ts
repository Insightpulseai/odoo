// LIB Brain Sync - Edge Function
// Endpoints: POST /ingest, GET /pull, POST /webhook

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

// Configuration
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const LIB_SYNC_SECRET = Deno.env.get("LIB_SYNC_SECRET")!;

// Create Supabase client with service role
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

// Types
interface Event {
  event_ulid: string;
  device_id: string;
  event_type: string;
  entity_type: string;
  entity_key: string;
  payload: any;
  vector_clock: Record<string, number>;
  created_at: string;
}

interface IngestRequest {
  batch: Event[];
}

interface IngestResponse {
  ok: boolean;
  result?: {
    inserted_events: number;
    upserted_entities: number;
  };
  error?: string;
}

interface PullResponse {
  ok: boolean;
  events?: Event[];
  error?: string;
}

interface WebhookRequest {
  device_id: string;
  webhook_url: string;
  secret?: string;
}

interface WebhookResponse {
  ok: boolean;
  webhook_id?: number;
  error?: string;
}

// Validate sync secret header
function validateSecret(req: Request): boolean {
  const secret = req.headers.get("x-lib-sync-secret");
  return secret === LIB_SYNC_SECRET;
}

// CORS headers
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-lib-sync-secret",
};

// POST /ingest - Push events to shared brain
async function handleIngest(req: Request): Promise<Response> {
  try {
    // Validate secret
    if (!validateSecret(req)) {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid sync secret" }),
        { status: 401, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Parse batch
    const { batch }: IngestRequest = await req.json();

    if (!batch || !Array.isArray(batch)) {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid batch format" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Limit batch size
    if (batch.length > 500) {
      return new Response(
        JSON.stringify({ ok: false, error: "Batch too large (max 500 events)" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Call ingest RPC
    const { data, error } = await supabase.rpc("lib_shared_ingest_events", {
      batch: batch,
    });

    if (error) {
      console.error("Ingest RPC error:", error);
      return new Response(
        JSON.stringify({ ok: false, error: error.message }),
        { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Get result
    const result = data[0] || { inserted_events: 0, upserted_entities: 0 };

    // Trigger webhooks (non-blocking)
    if (result.inserted_events > 0) {
      triggerWebhooks().catch((err) => {
        console.error("Webhook trigger failed:", err);
      });
    }

    return new Response(
      JSON.stringify({ ok: true, result }),
      { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  } catch (err) {
    console.error("Ingest error:", err);
    return new Response(
      JSON.stringify({ ok: false, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  }
}

// GET /pull - Pull events from shared brain
async function handlePull(req: Request): Promise<Response> {
  try {
    // Validate secret
    if (!validateSecret(req)) {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid sync secret" }),
        { status: 401, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Parse query params
    const url = new URL(req.url);
    const afterId = parseInt(url.searchParams.get("after_id") || "0");
    const limit = parseInt(url.searchParams.get("limit") || "200");

    if (isNaN(afterId) || isNaN(limit)) {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid parameters" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Limit max results
    const safeLimit = Math.min(limit, 500);

    // Call pull RPC
    const { data, error } = await supabase.rpc("lib_shared_pull_events", {
      after_id: afterId,
      limit_n: safeLimit,
    });

    if (error) {
      console.error("Pull RPC error:", error);
      return new Response(
        JSON.stringify({ ok: false, error: error.message }),
        { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    return new Response(
      JSON.stringify({ ok: true, events: data || [] }),
      { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  } catch (err) {
    console.error("Pull error:", err);
    return new Response(
      JSON.stringify({ ok: false, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  }
}

// POST /webhook - Register device webhook
async function handleWebhook(req: Request): Promise<Response> {
  try {
    // Validate secret
    if (!validateSecret(req)) {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid sync secret" }),
        { status: 401, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Parse request
    const { device_id, webhook_url, secret }: WebhookRequest = await req.json();

    if (!device_id || !webhook_url) {
      return new Response(
        JSON.stringify({ ok: false, error: "Missing device_id or webhook_url" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Validate webhook URL
    try {
      new URL(webhook_url);
    } catch {
      return new Response(
        JSON.stringify({ ok: false, error: "Invalid webhook_url format" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Call register RPC
    const { data, error } = await supabase.rpc("lib_shared_register_webhook", {
      p_device_id: device_id,
      p_webhook_url: webhook_url,
      p_secret: secret || null,
    });

    if (error) {
      console.error("Webhook registration error:", error);
      return new Response(
        JSON.stringify({ ok: false, error: error.message }),
        { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    return new Response(
      JSON.stringify({ ok: true, webhook_id: data }),
      { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  } catch (err) {
    console.error("Webhook registration error:", err);
    return new Response(
      JSON.stringify({ ok: false, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  }
}

// Trigger webhooks for active devices (non-blocking)
async function triggerWebhooks(): Promise<void> {
  try {
    // Get active webhooks
    const { data: webhooks, error } = await supabase.rpc(
      "lib_shared_get_active_webhooks"
    );

    if (error) {
      console.error("Failed to get webhooks:", error);
      return;
    }

    if (!webhooks || webhooks.length === 0) {
      return;
    }

    // Get latest event ID for notification
    const { data: latestEvent } = await supabase
      .from("lib_shared.events")
      .select("id")
      .order("id", { ascending: false })
      .limit(1)
      .single();

    const afterId = latestEvent?.id || 0;

    // Trigger each webhook (with timeout)
    const promises = webhooks.map(async (webhook: any) => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

        const response = await fetch(webhook.webhook_url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(webhook.secret ? { "x-webhook-secret": webhook.secret } : {}),
          },
          body: JSON.stringify({
            event: "new_events",
            after_id: afterId,
            timestamp: new Date().toISOString(),
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          // Update last notified timestamp
          await supabase.rpc("lib_shared_mark_webhook_notified", {
            p_device_id: webhook.device_id,
          });
          console.log(`Webhook notified: ${webhook.device_id}`);
        } else {
          console.error(`Webhook failed: ${webhook.device_id} - Status ${response.status}`);
        }
      } catch (err) {
        console.error(`Webhook error: ${webhook.device_id} -`, err);
      }
    });

    // Wait for all webhooks (but don't block)
    await Promise.allSettled(promises);
  } catch (err) {
    console.error("Webhook trigger error:", err);
  }
}

// Main request handler
serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const url = new URL(req.url);
  const path = url.pathname;

  // Route requests
  if (path.endsWith("/ingest") && req.method === "POST") {
    return handleIngest(req);
  } else if (path.endsWith("/pull") && req.method === "GET") {
    return handlePull(req);
  } else if (path.endsWith("/webhook") && req.method === "POST") {
    return handleWebhook(req);
  } else if (path.endsWith("/health") && req.method === "GET") {
    return new Response(
      JSON.stringify({ status: "healthy", version: "1.1.0" }),
      { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  } else {
    return new Response(
      JSON.stringify({ error: "Not found" }),
      { status: 404, headers: { "Content-Type": "application/json", ...corsHeaders } }
    );
  }
});
