// supabase/functions/workspace-ask-docs/index.ts
// RAG retrieval endpoint over work.* schema.
//
// POST body: { question: string, space_id: string, top_k?: number }
// Response:  { answer: string, citations: Citation[], model: string }
//
// Auth: requires authenticated JWT (anon key + Supabase Auth) OR service_role.
//       Authenticated users are scope-checked against work.permissions.
//
// Strategy:
//   1. Full-text search via work.work_search() RPC (always, from work.search_index)
//   2. Optional pgvector similarity on work.search_index (if OPENAI_API_KEY present)
//   3. Merge results (deduplicate by source_id), take top_k
//   4. Call Anthropic Claude (primary) or OpenAI GPT (fallback) for grounded answer
//   5. If no provider key: return 503 KEY_MISSING with SSOT registry reference
//
// SSOT secret registry: ssot/secrets/registry.yaml
//   - anthropic_api_key (preferred, consumers += supabase_edge:workspace-ask-docs)
//   - openai_api_key    (fallback,  consumers += supabase_edge:workspace-ask-docs)
//
// Environment variables:
//   SUPABASE_URL              (auto-injected)
//   SUPABASE_SERVICE_ROLE_KEY (auto-injected)
//   SUPABASE_ANON_KEY         (auto-injected — used for user JWT verification)
//   ANTHROPIC_API_KEY         (preferred LLM provider)
//   OPENAI_API_KEY            (optional: fallback LLM + enables vector similarity)

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
  /** Stable opaque ID: "page:<uuid>" or "block:<uuid>" — safe to persist in external refs */
  id: string;
  source_table: string;
  source_id: string;
  title: string | null;
  snippet: string;    // up to 400 chars of relevant context
  rank: number;       // higher = more relevant
}

// ---------------------------------------------------------------------------
// Auth helpers
// ---------------------------------------------------------------------------

/**
 * Returns the authenticated caller identity:
 *   { role: "service_role" } — service_role bearer token
 *   { role: "authenticated", userId: string } — verified Supabase JWT
 *   null — not authorized
 */
async function resolveAuth(
  req: Request,
  supabaseUrl: string,
  anonKey: string,
  serviceKey: string,
): Promise<{ role: "service_role" } | { role: "authenticated"; userId: string } | null> {
  const auth = req.headers.get("authorization") ?? "";

  // service_role path (internal callers, cron, taskbus)
  if (auth === `Bearer ${serviceKey}`) {
    return { role: "service_role" };
  }

  // JWT path (authenticated users)
  if (auth.startsWith("Bearer ")) {
    const token = auth.slice(7);
    const userClient = createClient(supabaseUrl, anonKey);
    const { data, error } = await userClient.auth.getUser(token);
    if (error || !data.user) return null;
    return { role: "authenticated", userId: data.user.id };
  }

  return null;
}

/**
 * Verify the caller is a member of the requested space.
 * Returns true for service_role callers (bypass).
 */
async function isMember(
  supabase: ReturnType<typeof createClient>,
  spaceId: string,
  userId: string | null,
): Promise<boolean> {
  if (userId === null) return true; // service_role — already trusted

  const { data } = await supabase
    .schema("work")
    .from("permissions")
    .select("id")
    .eq("space_id", spaceId)
    .eq("user_id", userId)
    .maybeSingle();

  return data !== null;
}

// ---------------------------------------------------------------------------
// Retrieval
// ---------------------------------------------------------------------------

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
    console.error("FTS error:", error.message);
    return [];
  }

  return (data ?? []).map((row: Record<string, unknown>) => {
    const table = String(row.source_table ?? "");
    const sid = String(row.id ?? row.source_id ?? "");
    return {
      id: `${table}:${sid}`,
      source_table: table,
      source_id: sid,
      title: row.title ? String(row.title) : null,
      snippet: String(row.snippet ?? row.body ?? "").slice(0, 400),
      rank: typeof row.rank === "number" ? row.rank : 0,
    };
  });
}

async function vectorSearch(
  supabase: ReturnType<typeof createClient>,
  question: string,
  spaceId: string,
  limit: number,
  openaiKey: string,
): Promise<Citation[]> {
  // Embed the question
  const embedRes = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: { Authorization: `Bearer ${openaiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({ input: question.slice(0, 8192), model: "text-embedding-3-small" }),
  });
  const embedJson = await embedRes.json();
  if (embedJson.error) {
    console.error("Embed error:", embedJson.error.message);
    return [];
  }
  const queryEmbedding: number[] = embedJson.data[0].embedding;

  // Vector similarity — order by cosine distance
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

  return (data ?? []).map(
    (row: { source_table: string; source_id: string; title: string | null; body: string }, i: number) => ({
      id: `${row.source_table}:${row.source_id}`,
      source_table: row.source_table,
      source_id: row.source_id,
      title: row.title ?? null,
      snippet: row.body.slice(0, 400),
      // rank: invert position (closest = highest rank); pgvector orders by distance ASC
      rank: limit - i,
    }),
  );
}

/**
 * Merge FTS + vector results:
 *   1. Deduplicate by stable `id` ("table:uuid")
 *   2. Sum ranks for items appearing in both result sets
 *   3. Sort: rank DESC, then id ASC (deterministic tie-break)
 *   4. Return top_k
 */
function mergeResults(fts: Citation[], vec: Citation[], topK: number): Citation[] {
  const map = new Map<string, Citation>();

  for (const c of [...fts, ...vec]) {
    if (map.has(c.id)) {
      // Item in both sets — sum ranks for combined score
      map.get(c.id)!.rank += c.rank;
    } else {
      map.set(c.id, { ...c });
    }
  }

  return Array.from(map.values())
    .sort((a, b) => {
      if (b.rank !== a.rank) return b.rank - a.rank;   // rank DESC
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;  // id ASC (stable tie-break)
    })
    .slice(0, topK);
}

// ---------------------------------------------------------------------------
// LLM answer generation
// ---------------------------------------------------------------------------

function buildPrompt(question: string, citations: Citation[]): string {
  const context = citations
    .map((c, i) => {
      const header = c.title
        ? `[${i + 1}] ${c.title} (${c.source_table}:${c.source_id})`
        : `[${i + 1}] (${c.source_table}:${c.source_id})`;
      return `${header}\n${c.snippet}`;
    })
    .join("\n\n---\n\n");

  return `You are a helpful workspace assistant. Answer the question using ONLY the provided context.
Cite sources using [N] notation matching the context headers.
If the context does not contain enough information, say exactly: "I don't have enough information in the workspace to answer this."
Do not fabricate information.

CONTEXT:
${context}

QUESTION: ${question}

ANSWER:`;
}

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

async function callGPT(prompt: string, openaiKey: string): Promise<string> {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${openaiKey}`, "Content-Type": "application/json" },
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

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------

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

  const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY") ?? "";
  const anthropicKey = Deno.env.get("ANTHROPIC_API_KEY");
  const openaiKey = Deno.env.get("OPENAI_API_KEY");

  // ── Provider check first (fail fast, SSOT-aligned error) ──────────────────
  if (!anthropicKey && !openaiKey) {
    return new Response(
      JSON.stringify({
        error: "KEY_MISSING",
        message:
          "No LLM provider key configured. " +
          "Set ANTHROPIC_API_KEY (preferred) or OPENAI_API_KEY in Supabase secrets. " +
          "Register consumers in ssot/secrets/registry.yaml under anthropic_api_key or openai_api_key.",
        ssot_ref: "ssot/secrets/registry.yaml#anthropic_api_key",
      }),
      { status: 503, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }

  // ── Auth ──────────────────────────────────────────────────────────────────
  const caller = await resolveAuth(req, supabaseUrl, anonKey, serviceKey);
  if (!caller) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const body: AskRequest = await req.json();
    const { question, space_id, top_k = 6 } = body;

    if (!question?.trim() || !space_id) {
      return new Response(
        JSON.stringify({ error: "question and space_id are required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // Use service_role client for all DB ops (search_index RLS requires membership check)
    const supabase = createClient(supabaseUrl, serviceKey);

    // ── Space membership gate ─────────────────────────────────────────────
    const userId = caller.role === "authenticated" ? caller.userId : null;
    if (!(await isMember(supabase, space_id, userId))) {
      return new Response(
        JSON.stringify({ error: "Forbidden: not a member of this space" }),
        { status: 403, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // ── Retrieval ──────────────────────────────────────────────────────────
    const ftsResults = await ftsSearch(supabase, question, space_id, top_k);
    const vecResults = openaiKey
      ? await vectorSearch(supabase, question, space_id, top_k, openaiKey)
      : [];
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

    // ── LLM answer — Anthropic preferred, OpenAI fallback ─────────────────
    const prompt = buildPrompt(question, citations);
    let answer: string;
    let model: string;

    if (anthropicKey) {
      answer = await callClaude(prompt, anthropicKey);
      model = "claude-sonnet-4-6";
    } else {
      // openaiKey is guaranteed non-null here (we checked both above)
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
