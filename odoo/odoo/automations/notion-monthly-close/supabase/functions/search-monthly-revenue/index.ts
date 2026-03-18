// =============================================================================
// Edge Function: search-monthly-revenue
// Natural language semantic search over monthly revenue insights
//
// Dependencies:
//   - SUPABASE_URL (env)
//   - SUPABASE_SERVICE_ROLE_KEY (env)
//   - OPENAI_API_KEY (env)
//
// Usage:
//   POST /search-monthly-revenue
//   Body: { companyId: number, query: string, matchCount?: number, maxDistance?: number }
//
// Returns:
//   { results: Array<{ id, company_id, month, revenue, summary, distance }> }
// =============================================================================

import { createClient } from "npm:@supabase/supabase-js@2.48.0";
import OpenAI from "npm:openai@4.73.0";

// Environment variables
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY")!;

// Initialize clients
const supabase = createClient(SUPABASE_URL, SERVICE_ROLE);
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

// Configuration
const EMBEDDING_MODEL = "text-embedding-3-small";
const DEFAULT_MATCH_COUNT = 10;
const DEFAULT_MAX_DISTANCE = 1.5;

interface SearchRequest {
  companyId: number;
  query: string;
  matchCount?: number;
  maxDistance?: number;
}

interface SearchResult {
  id: number;
  company_id: number;
  month: string;
  revenue: string;
  summary: string;
  distance: number;
}

/**
 * Generate embedding vector for search query
 */
async function embedQuery(query: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: EMBEDDING_MODEL,
    input: query,
  });

  return response.data[0].embedding;
}

/**
 * Validate search request
 */
function validateRequest(body: unknown): { valid: true; data: SearchRequest } | { valid: false; error: string } {
  if (!body || typeof body !== "object") {
    return { valid: false, error: "Request body is required" };
  }

  const data = body as Record<string, unknown>;

  if (!data.companyId || typeof data.companyId !== "number") {
    return { valid: false, error: "companyId is required and must be a number" };
  }

  if (!data.query || typeof data.query !== "string" || data.query.trim().length === 0) {
    return { valid: false, error: "query is required and must be a non-empty string" };
  }

  // Validate optional parameters
  let matchCount = DEFAULT_MATCH_COUNT;
  if (data.matchCount !== undefined) {
    if (typeof data.matchCount !== "number" || data.matchCount < 1 || data.matchCount > 100) {
      return { valid: false, error: "matchCount must be a number between 1 and 100" };
    }
    matchCount = data.matchCount;
  }

  let maxDistance = DEFAULT_MAX_DISTANCE;
  if (data.maxDistance !== undefined) {
    if (typeof data.maxDistance !== "number" || data.maxDistance <= 0) {
      return { valid: false, error: "maxDistance must be a positive number" };
    }
    maxDistance = data.maxDistance;
  }

  return {
    valid: true,
    data: {
      companyId: data.companyId as number,
      query: (data.query as string).trim(),
      matchCount,
      maxDistance,
    },
  };
}

/**
 * Main handler
 */
Deno.serve(async (req) => {
  // CORS headers for frontend access
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
  };

  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  // Validate environment
  if (!SUPABASE_URL || !SERVICE_ROLE || !OPENAI_API_KEY) {
    return new Response(
      JSON.stringify({ error: "Missing required environment variables" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }

  try {
    // Only accept POST requests
    if (req.method !== "POST") {
      return new Response(
        JSON.stringify({ error: "Method not allowed" }),
        { status: 405, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Parse and validate request body
    let body: unknown;
    try {
      body = await req.json();
    } catch {
      return new Response(
        JSON.stringify({ error: "Invalid JSON in request body" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const validation = validateRequest(body);
    if (!validation.valid) {
      return new Response(
        JSON.stringify({ error: validation.error }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const { companyId, query, matchCount, maxDistance } = validation.data;

    // Generate embedding for the search query
    const queryEmbedding = await embedQuery(query);

    // Call the SQL function for semantic search
    const { data, error } = await supabase.rpc(
      "search_monthly_revenue_insights",
      {
        p_company_id: companyId,
        p_query_embedding: queryEmbedding,
        p_match_count: matchCount,
        p_max_distance: maxDistance,
      }
    );

    if (error) {
      console.error("RPC error:", error);
      return new Response(
        JSON.stringify({ error: error.message }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const results: SearchResult[] = data ?? [];

    // Success response
    return new Response(
      JSON.stringify({
        results,
        meta: {
          query,
          companyId,
          matchCount: results.length,
          maxDistance,
        },
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Unhandled error:", error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
