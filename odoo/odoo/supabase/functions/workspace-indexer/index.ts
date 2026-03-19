// supabase/functions/workspace-indexer/index.ts
// Polling worker — claims items from work.index_queue, computes
// optional OpenAI embeddings, upserts into work.search_index, then acks each item.
//
// tsvector computation for pending items is handled DB-side by
// work.process_index_queue_tsvector() via pg_cron (migration 000003).
// This function handles the embedding pass only — it claims items that still
// lack an embedding vector and upserts them with the computed vector.
//
// Invocation:
//   - Supabase scheduled function (supabase/config.toml) — every 5 min
//   - taskbus: job_type "index_workspace", agent "workspace-indexer-agent"
//   - Manual: POST with Authorization: Bearer <service_role_key>
//
// Auth: service_role REQUIRED — rejects all other tokens without attempting JWT decode.
//
// Environment:
//   SUPABASE_URL              (auto-injected)
//   SUPABASE_SERVICE_ROLE_KEY (auto-injected; function will not start if absent)
//   OPENAI_API_KEY            (optional — no-op if absent; claimed items are re-acked)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const BATCH_SIZE = 10;
const WORKER_ID = "workspace-indexer-embed";
// Time budget: stay under Supabase 25s edge function CPU limit
const TIME_BUDGET_MS = 22_000;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// ---------------------------------------------------------------------------
// Auth: service_role only — hard reject anything else
// ---------------------------------------------------------------------------
function requireServiceRole(req: Request, serviceKey: string): string | null {
  if (!serviceKey) return "SUPABASE_SERVICE_ROLE_KEY is not set";
  const auth = req.headers.get("authorization") ?? "";
  if (auth !== `Bearer ${serviceKey}`) return "Unauthorized: service_role required";
  return null;
}

// ---------------------------------------------------------------------------
// Source text fetchers
// ---------------------------------------------------------------------------
async function fetchPageText(
  supabase: ReturnType<typeof createClient>,
  id: string,
): Promise<{ title: string; body: string } | null> {
  const { data } = await supabase
    .schema("work")
    .from("pages")
    .select("title, content")
    .eq("id", id)
    .maybeSingle();
  if (!data) return null;
  const title = String(data.title ?? "");
  return { title, body: (title + " " + String(data.content ?? "")).trim() };
}

async function fetchBlockText(
  supabase: ReturnType<typeof createClient>,
  id: string,
): Promise<{ title: null; body: string } | null> {
  const { data } = await supabase
    .schema("work")
    .from("blocks")
    .select("content")
    .eq("id", id)
    .maybeSingle();
  if (!data) return null;
  const c = data.content as Record<string, unknown> | null;
  if (!c) return { title: null, body: "" };
  const lang = c.language ? `[${String(c.language)}] ` : "";
  const text = String(c.text ?? c.value ?? c.expression ?? "").trim();
  return { title: null, body: lang + text };
}

// ---------------------------------------------------------------------------
// Embedding
// ---------------------------------------------------------------------------
async function embed(text: string, apiKey: string): Promise<number[]> {
  const res = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({ input: text.slice(0, 8192), model: "text-embedding-3-small" }),
  });
  const json = await res.json();
  if (json.error) throw new Error(`OpenAI: ${json.error.message}`);
  return json.data[0].embedding as number[];
}

// ---------------------------------------------------------------------------
// Structured logger
// ---------------------------------------------------------------------------
function log(
  level: "INFO" | "WARN" | "ERROR",
  msg: string,
  meta?: Record<string, unknown>,
) {
  console.log(JSON.stringify({ level, msg, ...meta, ts: new Date().toISOString() }));
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------
serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  const openaiKey = Deno.env.get("OPENAI_API_KEY");

  // Hard auth check — never attempt JWT decode for this worker
  const authErr = requireServiceRole(req, serviceKey);
  if (authErr) {
    log("WARN", authErr);
    return new Response(JSON.stringify({ error: authErr }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  if (!openaiKey) {
    log("INFO", "OPENAI_API_KEY not set — embedding pass skipped; tsvector handled by pg_cron");
    return new Response(
      JSON.stringify({ ok: true, processed: 0, message: "no embedding key; tsvector handled by pg_cron" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  const supabase = createClient(supabaseUrl, serviceKey);
  const startMs = Date.now();

  // Claim a batch
  const { data: batch, error: claimErr } = await supabase
    .schema("work")
    .rpc("claim_index_batch", { p_batch_size: BATCH_SIZE, p_worker_id: WORKER_ID });

  if (claimErr) {
    log("ERROR", "claim_index_batch failed", { error: claimErr.message });
    return new Response(JSON.stringify({ error: claimErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const items = (batch ?? []) as Array<{
    id: string; source_table: string; source_id: string; space_id: string;
  }>;

  if (items.length === 0) {
    log("INFO", "queue empty");
    return new Response(
      JSON.stringify({ ok: true, processed: 0, message: "queue empty" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  log("INFO", "batch claimed", { count: items.length });

  const results: Array<{ id: string; source_id: string; ok: boolean; duration_ms: number; error?: string }> = [];

  for (const item of items) {
    // Time budget guard — stop before Supabase kills the function
    if (Date.now() - startMs > TIME_BUDGET_MS) {
      log("WARN", "time budget exceeded — acking remaining items as pending", {
        remaining: items.length - results.length,
      });
      // Re-release remaining items back to queue
      for (const remaining of items.slice(results.length)) {
        await supabase.schema("work").rpc("ack_index", {
          p_id: remaining.id, p_ok: false,
          p_error: "time_budget_exceeded — will retry",
        });
      }
      break;
    }

    const itemStart = Date.now();
    try {
      // Fetch source text
      let extracted: { title: string | null; body: string } | null = null;
      if (item.source_table === "pages") extracted = await fetchPageText(supabase, item.source_id);
      else if (item.source_table === "blocks") extracted = await fetchBlockText(supabase, item.source_id);

      if (!extracted || !extracted.body.trim()) {
        await supabase.schema("work").rpc("ack_index", { p_id: item.id, p_ok: true });
        results.push({ id: item.id, source_id: item.source_id, ok: true, duration_ms: Date.now() - itemStart });
        continue;
      }

      const fullText = ((extracted.title ?? "") + " " + extracted.body).trim();

      // Compute embedding
      const embedding = await embed(fullText, openaiKey);

      // Upsert into search_index — only update embedding + body (tsvector set by pg_cron pass)
      const { error: upsertErr } = await supabase
        .schema("work")
        .from("search_index")
        .upsert(
          {
            source_table: item.source_table,
            source_id: item.source_id,
            space_id: item.space_id,
            title: extracted.title ?? null,
            body: fullText,
            embedding,
            updated_at: new Date().toISOString(),
          },
          { onConflict: "source_table,source_id", ignoreDuplicates: false },
        );

      if (upsertErr) throw new Error(upsertErr.message);

      await supabase.schema("work").rpc("ack_index", { p_id: item.id, p_ok: true });
      const duration_ms = Date.now() - itemStart;
      log("INFO", "indexed", { queue_id: item.id, source_table: item.source_table, source_id: item.source_id, duration_ms });
      results.push({ id: item.id, source_id: item.source_id, ok: true, duration_ms });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      const duration_ms = Date.now() - itemStart;
      log("ERROR", "index failed", { queue_id: item.id, source_table: item.source_table, source_id: item.source_id, error: message, duration_ms });
      await supabase.schema("work").rpc("ack_index", { p_id: item.id, p_ok: false, p_error: message });
      results.push({ id: item.id, source_id: item.source_id, ok: false, duration_ms, error: message });
    }
  }

  const succeeded = results.filter((r) => r.ok).length;
  const failed = results.filter((r) => !r.ok).length;
  const total_ms = Date.now() - startMs;

  log("INFO", "batch complete", { processed: results.length, succeeded, failed, total_ms });

  return new Response(
    JSON.stringify({ ok: true, processed: results.length, succeeded, failed, total_ms, results }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
