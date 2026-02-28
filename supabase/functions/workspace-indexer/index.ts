// supabase/functions/workspace-indexer/index.ts
// Triggered by Supabase DB webhook on work.pages and work.blocks.
// Maintains tsvector search index + optional OpenAI embeddings in work.search_index.
//
// Webhook payload shape (Supabase database webhook):
//   { type: "INSERT"|"UPDATE", schema: "work", table: "pages"|"blocks", record: {...}, old_record: {...} }
//
// Setup (run once in Supabase dashboard → Database → Webhooks):
//   Table: work.pages  → Events: INSERT, UPDATE → URL: <function-url>/workspace-indexer
//   Table: work.blocks → Events: INSERT, UPDATE → URL: <function-url>/workspace-indexer
//
// Environment variables required:
//   SUPABASE_URL           (auto-injected)
//   SUPABASE_SERVICE_ROLE_KEY (auto-injected)
//   OPENAI_API_KEY         (optional — skip embeddings if absent)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface WebhookPayload {
  type: "INSERT" | "UPDATE" | "DELETE";
  schema: string;
  table: string;
  record: Record<string, unknown> | null;
  old_record: Record<string, unknown> | null;
}

interface SearchIndexUpsert {
  source_table: string;
  source_id: string;
  space_id: string;
  title: string | null;
  body: string;
  search_vec: string | null; // raw text — Postgres generates tsvector via function
  embedding: number[] | null;
  updated_at: string;
}

/** Extract indexable text from a page record */
function extractPageText(record: Record<string, unknown>): { title: string; body: string } {
  return {
    title: String(record.title ?? ""),
    body: String(record.title ?? "") + " " + String(record.content ?? ""),
  };
}

/** Extract indexable text from a block record */
function extractBlockText(record: Record<string, unknown>): { title: string | null; body: string } {
  const content = record.content as Record<string, unknown> | null;
  if (!content) return { title: null, body: "" };

  // Most block types store displayable text in content.text or content.value
  const text =
    String(content.text ?? content.value ?? content.expression ?? "").trim();

  // For code blocks include the language as context
  const lang = content.language ? `[${content.language}] ` : "";
  return { title: null, body: lang + text };
}

/** Call OpenAI text-embedding-3-small to produce a 1536-dim vector */
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
  if (json.error) throw new Error(`OpenAI: ${json.error.message}`);
  return json.data[0].embedding as number[];
}

serve(async (req) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const openaiKey = Deno.env.get("OPENAI_API_KEY");

    if (!supabaseUrl || !serviceKey) {
      return new Response(
        JSON.stringify({ error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const supabase = createClient(supabaseUrl, serviceKey);

    const payload: WebhookPayload = await req.json();
    const { type, table, record } = payload;

    // Ignore deletes — search_index rows are cleaned up separately
    if (type === "DELETE" || !record) {
      return new Response(JSON.stringify({ skipped: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Only handle known tables
    if (table !== "pages" && table !== "blocks") {
      return new Response(
        JSON.stringify({ error: `Unknown table: ${table}` }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // Extract text
    let extracted: { title: string | null; body: string };
    if (table === "pages") {
      extracted = extractPageText(record);
    } else {
      extracted = extractBlockText(record);
    }

    // Skip if no meaningful text
    const fullText = ((extracted.title ?? "") + " " + extracted.body).trim();
    if (!fullText) {
      return new Response(JSON.stringify({ skipped: true, reason: "empty text" }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Optionally generate embedding
    let embedding: number[] | null = null;
    if (openaiKey) {
      try {
        embedding = await embed(fullText, openaiKey);
      } catch (embErr) {
        // Embedding failure is non-fatal; proceed without vector
        console.error("Embedding failed:", embErr);
      }
    }

    // Build search_index row — search_vec is maintained by work.work_search RPC using plainto_tsquery
    // We store the raw text; a Postgres GENERATED column or trigger handles the tsvector on search_index.
    const row: SearchIndexUpsert = {
      source_table: table,
      source_id: String(record.id),
      space_id: String(record.space_id),
      title: extracted.title,
      body: fullText,
      search_vec: null, // tsvector generated by DB trigger on search_index
      embedding,
      updated_at: new Date().toISOString(),
    };

    const { error } = await supabase
      .schema("work")
      .from("search_index")
      .upsert(row, {
        onConflict: "source_table,source_id",
        ignoreDuplicates: false,
      });

    if (error) throw error;

    return new Response(
      JSON.stringify({ ok: true, source_table: table, source_id: record.id }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("workspace-indexer error:", message);
    return new Response(
      JSON.stringify({ error: message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
