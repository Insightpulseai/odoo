// supabase/functions/workspace-indexer/index.ts
// Polling worker — claims items from work.index_queue, computes tsvector text
// and optional embeddings, upserts into work.search_index, then acks each item.
//
// Invocation:
//   - Supabase pg_cron (every 2 min) via net.http_post — see migration 000003
//   - Taskbus worker: job_type "index_workspace", agent "workspace-indexer-agent"
//   - Manual POST with Authorization: Bearer <service_role_key>
//
// No DB webhooks required — queue is populated by triggers on work.pages/blocks.
//
// Environment variables (auto-injected + optional):
//   SUPABASE_URL              (auto-injected)
//   SUPABASE_SERVICE_ROLE_KEY (auto-injected)
//   OPENAI_API_KEY            (optional — skip embeddings if absent)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const BATCH_SIZE = 10;
const WORKER_ID = "workspace-indexer";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// ---------------------------------------------------------------------------
// Auth guard: only service_role callers may invoke this function
// ---------------------------------------------------------------------------
function isServiceRole(req: Request, serviceKey: string): boolean {
  const auth = req.headers.get("authorization") ?? "";
  return auth === `Bearer ${serviceKey}`;
}

// ---------------------------------------------------------------------------
// Source record fetchers
// ---------------------------------------------------------------------------
async function fetchPage(
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
  const body = title + " " + String(data.content ?? "");
  return { title, body: body.trim() };
}

async function fetchBlock(
  supabase: ReturnType<typeof createClient>,
  id: string,
): Promise<{ title: string | null; body: string } | null> {
  const { data } = await supabase
    .schema("work")
    .from("blocks")
    .select("content, type")
    .eq("id", id)
    .maybeSingle();

  if (!data) return null;
  const content = data.content as Record<string, unknown> | null;
  if (!content) return { title: null, body: "" };

  const text = String(content.text ?? content.value ?? content.expression ?? "").trim();
  const lang = content.language ? `[${String(content.language)}] ` : "";
  return { title: null, body: lang + text };
}

// ---------------------------------------------------------------------------
// OpenAI embedding (text-embedding-3-small, 1536 dims)
// ---------------------------------------------------------------------------
async function embed(text: string, apiKey: string): Promise<number[]> {
  const res = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ input: text.slice(0, 8192), model: "text-embedding-3-small" }),
  });
  const json = await res.json();
  if (json.error) throw new Error(`OpenAI embed: ${json.error.message}`);
  return json.data[0].embedding as number[];
}

// ---------------------------------------------------------------------------
// tsvector text: computed in Postgres via the existing search_index structure;
// we store raw body text here and let the DB generate tsvector via trigger.
// ---------------------------------------------------------------------------

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

  // Auth: require service_role
  if (!isServiceRole(req, serviceKey)) {
    return new Response(JSON.stringify({ error: "Unauthorized: service_role required" }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(supabaseUrl, serviceKey);

  // Claim a batch from the queue
  const { data: batch, error: claimErr } = await supabase
    .schema("work")
    .rpc("claim_index_batch", { p_batch_size: BATCH_SIZE, p_worker_id: WORKER_ID });

  if (claimErr) {
    console.error("claim_index_batch error:", claimErr.message);
    return new Response(JSON.stringify({ error: claimErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const items = batch as Array<{
    id: string;
    source_table: string;
    source_id: string;
    space_id: string;
  }>;

  if (!items || items.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, processed: 0, message: "queue empty" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  const results: Array<{ id: string; ok: boolean; error?: string }> = [];

  for (const item of items) {
    try {
      // Fetch source text
      let extracted: { title: string | null; body: string } | null = null;

      if (item.source_table === "pages") {
        extracted = await fetchPage(supabase, item.source_id);
      } else if (item.source_table === "blocks") {
        extracted = await fetchBlock(supabase, item.source_id);
      }

      if (!extracted || !extracted.body.trim()) {
        // Empty content — ack as done (nothing to index)
        await supabase.schema("work").rpc("ack_index", { p_id: item.id, p_ok: true });
        results.push({ id: item.id, ok: true });
        continue;
      }

      const fullText = ((extracted.title ?? "") + " " + extracted.body).trim();

      // Optional embedding
      let embedding: number[] | null = null;
      if (openaiKey) {
        try {
          embedding = await embed(fullText, openaiKey);
        } catch (embErr) {
          // Embedding failure is non-fatal; proceed without vector
          console.warn("Embedding skipped:", embErr instanceof Error ? embErr.message : embErr);
        }
      }

      // Upsert into search_index
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
            // search_vec: Postgres tsvector is generated by the DB trigger on search_index
            embedding,
            updated_at: new Date().toISOString(),
          },
          { onConflict: "source_table,source_id", ignoreDuplicates: false },
        );

      if (upsertErr) throw new Error(upsertErr.message);

      // Ack success
      await supabase.schema("work").rpc("ack_index", { p_id: item.id, p_ok: true });
      results.push({ id: item.id, ok: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`indexer error for item ${item.id}:`, message);

      // Ack failure — queue will retry with backoff (up to 5 attempts)
      await supabase.schema("work").rpc("ack_index", {
        p_id: item.id,
        p_ok: false,
        p_error: message,
      });

      results.push({ id: item.id, ok: false, error: message });
    }
  }

  const succeeded = results.filter((r) => r.ok).length;
  const failed = results.filter((r) => !r.ok).length;

  return new Response(
    JSON.stringify({ ok: true, processed: items.length, succeeded, failed, results }),
    { headers: { ...corsHeaders, "Content-Type": "application/json" } },
  );
});
