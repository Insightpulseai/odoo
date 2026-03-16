// supabase/functions/ops-advisory-scan/index.ts
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.1";

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

serve(async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const token = req.headers.get("x-ops-advisory-token") || "";
  const expected = Deno.env.get("OPS_ADVISORY_SCAN_TOKEN") || "";
  if (!expected || token !== expected) return json(401, { error: "Unauthorized" });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supa = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

  // Example: flag projects with no builds in 7 days as 'reliability' warning
  const { data: projects, error: pErr } = await supa.from("ops.projects").select("id,name");
  if (pErr) return json(500, { error: pErr.message });

  const now = Date.now();
  let created = 0;

  for (const p of projects ?? []) {
    const { data: lastBuild, error: bErr } = await supa
      .from("ops.builds")
      .select("created_at")
      .eq("project_id", p.id)
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();

    if (bErr) continue;

    const last = lastBuild?.created_at ? new Date(lastBuild.created_at).getTime() : 0;
    const ageDays = last ? (now - last) / (1000 * 60 * 60 * 24) : 999;

    if (ageDays >= 7) {
      const { error: aErr } = await supa.from("ops.advisories").insert({
        project_id: p.id,
        severity: "warning",
        category: "reliability",
        title: "No recent builds",
        recommendation: "Trigger a rebuild and confirm pipelines are healthy.",
        evidence: { last_build_days_ago: Math.floor(ageDays) },
        status: "open",
      });
      if (!aErr) created++;
    }
  }

  return json(200, { advisories_created: created });
});
