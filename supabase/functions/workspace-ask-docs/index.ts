// supabase/functions/workspace-ask-docs/index.ts
// RAG retrieval endpoint over work.* schema.
//
// POST body: { question: string, space_id: string, top_k?: number }
// Response:  { answer: string, citations: Citation[], model: string }
//
// Strategy:
//   1. Full-text search via work.work_search() RPC (always)
//   2. Optional vector similarity search via pgvector if OPENAI_API_KEY present
//   3. Merge results (deduplicate by source_id), take top_k
//   4. Build prompt → call Claude (or OpenAI) for grounded answer with citations
//
// Environment variables:
//   SUPABASE_URL              (auto-injected)
//   SUPABASE_SERVICE_ROLE_KEY (auto-injected)
//   OPENAI_API_KEY            (optional — enables vector search + uses GPT-4o)
//   ANTHROPIC_API_KEY         (preferred — uses Claude claude-sonnet-4-6 when set)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface AskRequest {
  question: string;
  space_id: string;
  top_k?: number;
}

interface Citation {
  source_table: string;
  source_id: string;
  title: string | null;
  snippet: string;
  score?: number;
}

interface SearchIndexRow {
  source_table: string;
  source_id: string;
  title: string | null;
  body: string;
  embedding?: number[] | null;
}

/** Full-text search via the work.work_search() RPC */
async function ftsSearch(
  supabase: ReturnType<typeof createClient>,
  queryText: string,
  spaceId: string,
  limit: number,
): Promise<Citation[]> {
  const { data, error } = await supabase.schema("work").rpc("work_search", {
    query_text: queryText,
    p_space_id: spaceId,
    p_limit: limit,
  });

  if (error) {
    console.error("FTS search error:", error.message);
    return [];
  }

  return (data ?? []).map((row: Record<string, unknown>) => ({
    source_table: String(row.source_table ?? row.source ?? ""),
    source_id: String(row.id ?? row.source_id ?? ""),
    title: row.title ? String(row.title) : null,
    snippet: String(row.snippet ?? row.body ?? "").slice(0, 400),
    score: typeof row.rank === "number" ? row.rank : undefined,
  }));
}

/** Embed query text via OpenAI, then do pgvector similarity on work.search_index */
async function vectorSearch(
  supabase: ReturnType<typeof createClient>,
  question: string,
  spaceId: string,
  limit: number,
  openaiKey: string,
): Promise<Citation[]> {
  // 1. Embed the question
  const embedRes = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${openaiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ input: question.slice(0, 8192), model: "text-embedding-3-small" }),
  });

  const embedJson = await embedRes.json();
  if (embedJson.error) {
    console.error("Embed error:", embedJson.error.message);
    return [];
  }

  const queryEmbedding: number[] = embedJson.data[0].embedding;

  // 2. Vector similarity query
  const { data, error } = await supabase
    .schema("work")
    .from("search_index")
    .select("source_table, source_id, title, body")
    .eq("space_id", spaceId)
    .not("embedding", "is", null)
    .order(`embedding <-> '[${queryEmbedding.join(",")}]'`)
    .limit(limit);

  if (error) {
    console.error("Vector search error:", error.message);
    return [];
  }

  return (data ?? []).map((row: SearchIndexRow, i: number) => ({
    source_table: row.source_table,
    source_id: row.source_id,
    title: row.title ?? null,
    snippet: row.body.slice(0, 400),
    score: limit - i, // rank by result order (pgvector orders by distance)
  }));
}

/** Merge FTS + vector results, deduplicate by source_id, return top_k */
function mergeResults(fts: Citation[], vec: Citation[], topK: number): Citation[] {
  const seen = new Set<string>();
  const merged: Citation[] = [];

  for (const c of [...fts, ...vec]) {
    const key = `${c.source_table}:${c.source_id}`;
    if (!seen.has(key)) {
      seen.add(key);
      merged.push(c);
    }
    if (merged.length >= topK) break;
  }

  return merged;
}

/** Build the RAG prompt */
function buildPrompt(question: string, citations: Citation[]): string {
  const context = citations
    .map((c, i) => {
      const header = c.title ? `[${i + 1}] ${c.title}` : `[${i + 1}] (${c.source_table}:${c.source_id})`;
      return `${header}\n${c.snippet}`;
    })
    .join("\n\n---\n\n");

  return `You are a helpful workspace assistant. Answer the question using ONLY the provided context.
Cite sources using [N] notation matching the context headers.
If the context does not contain enough information, say "I don't have enough information in the workspace to answer this."

CONTEXT:
${context}

QUESTION: ${question}

ANSWER:`;
}

/** Call Anthropic Claude */
async function callClaude(prompt: string, anthropicKey: string): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": anthropicKey,
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-6",
      max_tokens: 1024,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const json = await res.json();
  if (json.error) throw new Error(`Anthropic: ${json.error.message}`);
  return json.content[0].text as string;
}

/** Call OpenAI GPT-4o (fallback when no Anthropic key) */
async function callGPT(prompt: string, openaiKey: string): Promise<string> {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${openaiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      max_tokens: 1024,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const json = await res.json();
  if (json.error) throw new Error(`OpenAI: ${json.error.message}`);
  return json.choices[0].message.content as string;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST required" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const anthropicKey = Deno.env.get("ANTHROPIC_API_KEY");
    const openaiKey = Deno.env.get("OPENAI_API_KEY");

    if (!supabaseUrl || !serviceKey) {
      return new Response(
        JSON.stringify({ error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    if (!anthropicKey && !openaiKey) {
      return new Response(
        JSON.stringify({ error: "Set ANTHROPIC_API_KEY or OPENAI_API_KEY to enable answers" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const body: AskRequest = await req.json();
    const { question, space_id, top_k = 6 } = body;

    if (!question?.trim() || !space_id) {
      return new Response(
        JSON.stringify({ error: "question and space_id are required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const supabase = createClient(supabaseUrl, serviceKey);

    // 1. Full-text search (always)
    const ftsResults = await ftsSearch(supabase, question, space_id, top_k);

    // 2. Vector search (only if OpenAI key present)
    let vecResults: Citation[] = [];
    if (openaiKey) {
      vecResults = await vectorSearch(supabase, question, space_id, top_k, openaiKey);
    }

    // 3. Merge
    const citations = mergeResults(ftsResults, vecResults, top_k);

    if (citations.length === 0) {
      return new Response(
        JSON.stringify({
          answer: "I don't have enough information in the workspace to answer this.",
          citations: [],
          model: "none",
        }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // 4. LLM answer
    const prompt = buildPrompt(question, citations);
    let answer: string;
    let model: string;

    if (anthropicKey) {
      answer = await callClaude(prompt, anthropicKey);
      model = "claude-sonnet-4-6";
    } else {
      answer = await callGPT(prompt, openaiKey!);
      model = "gpt-4o-mini";
    }

    return new Response(
      JSON.stringify({ answer, citations, model }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("workspace-ask-docs error:", message);
    return new Response(
      JSON.stringify({ error: message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
