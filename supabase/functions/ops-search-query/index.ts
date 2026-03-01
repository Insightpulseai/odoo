/**
 * ops-search-query
 * Full-text search across ops.ppm_initiatives, ops.runs, ops.convergence_findings.
 *
 * POST /functions/v1/ops-search-query
 * Body: { query: string, limit?: number }
 * Auth: anon or service_role
 *
 * Returns: { results: SearchResult[] }
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface SearchResult {
  type: "initiative" | "run" | "finding";
  id: string;
  title: string;
  status: string | null;
  link: string;
  rank: number;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  // Use anon key for search (RLS controls access)
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

  // Forward auth header if provided
  const authHeader = req.headers.get("Authorization");
  const key = authHeader?.startsWith("Bearer ") ? authHeader.slice(7) : anonKey;

  const supabase = createClient(supabaseUrl, key, {
    auth: { persistSession: false },
  });

  let query = "";
  let limit = 20;
  try {
    const body = await req.json();
    query = (body.query ?? "").trim();
    limit = Math.min(body.limit ?? 20, 50);
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!query) {
    return new Response(JSON.stringify({ results: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  const results: SearchResult[] = [];

  // Search ppm_initiatives
  const { data: initiatives } = await supabase
    .from("ppm_initiatives")
    .select("initiative_id, name, status")
    .textSearch("name", query, { type: "websearch" })
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

  // Search ops.runs
  const { data: runs } = await supabase
    .from("runs")
    .select("id, task_description, status, agent_id")
    .textSearch("task_description", query, { type: "websearch" })
    .limit(limit);

  for (const r of runs ?? []) {
    results.push({
      type: "run",
      id: r.id,
      title: r.task_description ?? `Run ${r.id.slice(0, 8)}`,
      status: r.status,
      link: `/runs/${r.id}`,
      rank: 2,
    });
  }

  // Search convergence_findings
  const { data: findings } = await supabase
    .from("convergence_findings")
    .select("id, message, category, severity")
    .textSearch("message", query, { type: "websearch" })
    .limit(limit);

  for (const f of findings ?? []) {
    results.push({
      type: "finding",
      id: f.id,
      title: f.message ?? `Finding ${f.id.slice(0, 8)}`,
      status: f.severity,
      link: `/findings/${f.id}`,
      rank: 3,
    });
  }

  // Sort by rank (initiatives first) then limit
  results.sort((a, b) => a.rank - b.rank);

  return new Response(
    JSON.stringify({ results: results.slice(0, limit) }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
