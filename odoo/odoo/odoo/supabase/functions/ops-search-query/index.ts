/**
 * ops-search-query
 * Full-text search across allowlisted ops tables.
 * Requires authenticated Supabase user token (anon access blocked).
 *
 * POST /functions/v1/ops-search-query
 * Headers: Authorization: Bearer <supabase-user-jwt>
 * Body:    { query: string, sources?: string[], limit?: number }
 *
 * Returns: { results: SearchResult[] }
 *
 * Sources (allowlist from ssot/search/sources.yaml):
 *   ppm_initiatives   → ops.ppm_initiatives
 *   ops_runs          → ops.runs
 *   convergence_findings → ops.convergence_findings
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const MAX_QUERY_LEN = 200;
const MAX_LIMIT     = 50;
const DEFAULT_LIMIT = 20;

// Safe allowlist — matches ssot/search/sources.yaml
const ALLOWED_SOURCES = new Set(["ppm_initiatives", "ops_runs", "convergence_findings"]);

interface SearchResult {
  type: "initiative" | "run" | "finding";
  id: string;
  title: string;
  status: string | null;
  link: string;
  rank: number;
}

function sanitizeQuery(raw: string): string {
  // Trim, truncate, strip characters that could confuse tsquery
  return raw.trim().slice(0, MAX_QUERY_LEN).replace(/['"\\;]/g, " ").trim();
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  // Require authenticated JWT — reject anon and service-role
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return new Response(
      JSON.stringify({ error: "Authorization header with user JWT required" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }
  const userToken = authHeader.slice(7);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

  // Create client with user's JWT so RLS applies correctly
  const supabase = createClient(supabaseUrl, anonKey, {
    auth: { persistSession: false },
    global: { headers: { Authorization: `Bearer ${userToken}` } },
  });

  // Validate that the token belongs to a real user (getUser call)
  const { error: userErr } = await supabase.auth.getUser(userToken);
  if (userErr) {
    return new Response(
      JSON.stringify({ error: "Invalid or expired authentication token" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  // Parse body
  let rawQuery = "";
  let sourcesFilter: string[] | null = null;
  let limit = DEFAULT_LIMIT;
  try {
    const body = await req.json();
    rawQuery = typeof body.query === "string" ? body.query : "";
    limit = Math.min(typeof body.limit === "number" ? body.limit : DEFAULT_LIMIT, MAX_LIMIT);
    if (Array.isArray(body.sources)) {
      sourcesFilter = body.sources.filter((s: unknown) => typeof s === "string" && ALLOWED_SOURCES.has(s));
    }
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const query = sanitizeQuery(rawQuery);
  if (!query) {
    return new Response(
      JSON.stringify({ results: [] }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  const activeSources = sourcesFilter ?? [...ALLOWED_SOURCES];
  const results: SearchResult[] = [];

  // Search ppm_initiatives (uses generated fts column)
  if (activeSources.includes("ppm_initiatives")) {
    const { data: initiatives } = await supabase
      .schema("ops")
      .from("ppm_initiatives")
      .select("initiative_id, name, status")
      .textSearch("fts", query, { type: "websearch" })
      .limit(limit);

    for (const i of initiatives ?? []) {
      results.push({
        type: "initiative",
        id: i.initiative_id,
        title: i.name,
        status: i.status,
        link: `/tools/ppm?id=${i.initiative_id}`,
        rank: 1,
      });
    }
  }

  // Search ops.runs (task_description FTS)
  if (activeSources.includes("ops_runs")) {
    const { data: runs } = await supabase
      .schema("ops")
      .from("runs")
      .select("id, task_description, status")
      .textSearch("task_description", query, { type: "websearch" })
      .limit(limit);

    for (const r of runs ?? []) {
      results.push({
        type: "run",
        id: r.id,
        title: (r.task_description ?? `Run ${(r.id as string).slice(0, 8)}`).slice(0, 120),
        status: r.status,
        link: `/runs/${r.id}`,
        rank: 2,
      });
    }
  }

  // Search convergence_findings
  if (activeSources.includes("convergence_findings")) {
    const { data: findings } = await supabase
      .schema("ops")
      .from("convergence_findings")
      .select("id, message, severity")
      .textSearch("message", query, { type: "websearch" })
      .limit(limit);

    for (const f of findings ?? []) {
      results.push({
        type: "finding",
        id: f.id,
        title: (f.message ?? `Finding ${(f.id as string).slice(0, 8)}`).slice(0, 120),
        status: f.severity,
        link: `/findings/${f.id}`,
        rank: 3,
      });
    }
  }

  results.sort((a, b) => a.rank - b.rank);

  return new Response(
    JSON.stringify({ results: results.slice(0, limit) }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
