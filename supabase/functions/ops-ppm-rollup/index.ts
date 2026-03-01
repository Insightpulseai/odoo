/**
 * ops-ppm-rollup
 * Reads ssot/ppm/portfolio.yaml (passed in request body or env),
 * upserts ops.ppm_initiatives, computes status rollups,
 * and writes ops.artifacts(kind=ppm_report).
 *
 * POST /functions/v1/ops-ppm-rollup
 * Body: { initiatives?: Initiative[] }   // optional override; defaults to env PORTFOLIO_YAML
 * Auth: service_role key required
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface Initiative {
  id: string;
  name: string;
  owner: string | null;
  status: "active" | "on-hold" | "completed" | "cancelled";
  spec_slug: string | null;
  github_label: string | null;
  start_date: string | null;
  target_date: string | null;
}

interface RollupRow {
  initiative_id: string;
  blocking_findings: number;
  merged_prs_30d: number;
  last_run_status: string | null;
  last_run_at: string | null;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false },
  });

  // Parse initiatives from body or fall back to env
  let initiatives: Initiative[] = [];
  try {
    const body = await req.json().catch(() => ({}));
    if (body.initiatives && Array.isArray(body.initiatives)) {
      initiatives = body.initiatives;
    } else {
      const raw = Deno.env.get("PORTFOLIO_YAML_JSON");
      if (raw) initiatives = JSON.parse(raw);
    }
  } catch {
    return new Response(JSON.stringify({ error: "No initiatives provided" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (initiatives.length === 0) {
    return new Response(JSON.stringify({ error: "initiatives array is empty" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Upsert ppm_initiatives
  const rows = initiatives.map((i) => ({
    initiative_id: i.id,
    name: i.name,
    owner: i.owner ?? null,
    status: i.status,
    spec_slug: i.spec_slug ?? null,
    github_label: i.github_label ?? null,
    start_date: i.start_date ?? null,
    target_date: i.target_date ?? null,
  }));

  const { error: upsertErr } = await supabase
    .from("ppm_initiatives")
    .upsert(rows, { onConflict: "initiative_id" });

  if (upsertErr) {
    return new Response(JSON.stringify({ error: upsertErr.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Compute rollups
  const rollups: RollupRow[] = [];
  for (const i of initiatives) {
    // Blocking findings count
    const { count: blockingCount } = await supabase
      .from("convergence_findings")
      .select("id", { count: "exact", head: true })
      .eq("severity", "critical")
      .eq("resolved", false)
      .limit(1);

    // Merged PRs in last 30d (runs with kind=agent, completed)
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const { count: mergedPRs } = await supabase
      .from("runs")
      .select("id", { count: "exact", head: true })
      .eq("kind", "agent")
      .eq("status", "completed")
      .gte("updated_at", thirtyDaysAgo)
      .limit(1);

    // Most recent run for this initiative
    const { data: lastRun } = await supabase
      .from("runs")
      .select("status, updated_at")
      .ilike("task_description", `%${i.id}%`)
      .order("updated_at", { ascending: false })
      .limit(1)
      .single();

    rollups.push({
      initiative_id: i.id,
      blocking_findings: blockingCount ?? 0,
      merged_prs_30d: mergedPRs ?? 0,
      last_run_status: lastRun?.status ?? null,
      last_run_at: lastRun?.updated_at ?? null,
    });
  }

  const { error: rollupErr } = await supabase
    .from("ppm_status_rollups")
    .insert(rollups);

  if (rollupErr) {
    console.error("rollup insert error:", rollupErr.message);
    // Non-fatal — continue to report
  }

  // Build Markdown report
  const reportLines = [
    `# PPM Weekly Report — ${new Date().toISOString().split("T")[0]}`,
    "",
    "| ID | Name | Status | Blockers | PRs (30d) |",
    "|----|------|--------|----------|-----------|",
  ];
  for (let idx = 0; idx < initiatives.length; idx++) {
    const i = initiatives[idx];
    const r = rollups[idx];
    const blockerFlag = r.blocking_findings > 0 ? `⚠️ ${r.blocking_findings}` : "0";
    reportLines.push(
      `| ${i.id} | ${i.name} | ${i.status} | ${blockerFlag} | ${r.merged_prs_30d} |`
    );
  }
  const reportMd = reportLines.join("\n");

  // Write artifact — gracefully skip if ops.artifacts not available
  try {
    await supabase.from("artifacts").insert({
      kind: "ppm_report",
      name: `ppm_report_${new Date().toISOString().split("T")[0]}`,
      path: "ops/ppm/reports/",
      metadata: { report_md: reportMd, initiative_count: initiatives.length },
    });
  } catch {
    console.warn("ops.artifacts not available — skipping artifact write");
  }

  return new Response(
    JSON.stringify({
      ok: true,
      initiatives_upserted: initiatives.length,
      rollups_computed: rollups.length,
      report_lines: reportLines.length,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
