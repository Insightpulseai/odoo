/**
 * ops-ppm-rollup
 * Reads ssot/ppm/portfolio.yaml content (passed in request body as JSON),
 * upserts ops.ppm_initiatives, computes status rollups,
 * and writes ops.artifacts(kind=ppm_report).
 *
 * Called by: .github/workflows/ppm-portfolio-sync.yml on merge to main
 *            (also supports manual POST for on-demand refresh)
 *
 * POST /functions/v1/ops-ppm-rollup
 * Headers: Authorization: Bearer <service-role-key>
 * Body:    { initiatives: Initiative[] }
 *
 * Returns: { ok: true, initiatives_upserted: N, rollups_computed: N }
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

const VALID_STATUSES = new Set(["active", "on-hold", "completed", "cancelled"]);
const INIT_ID_RE = /^INIT-\d{3,}$/;
// spec_slug must be a safe relative path component (no ../ traversal)
const SPEC_SLUG_RE = /^[a-z0-9][a-z0-9-_/]{0,80}$/;

function validateInitiative(i: unknown, idx: number): Initiative {
  if (typeof i !== "object" || i === null) {
    throw new Error(`initiatives[${idx}]: must be an object`);
  }
  const obj = i as Record<string, unknown>;

  if (!obj.id || typeof obj.id !== "string" || !INIT_ID_RE.test(obj.id)) {
    throw new Error(`initiatives[${idx}].id must match INIT-NNN format, got: ${obj.id}`);
  }
  if (!obj.name || typeof obj.name !== "string" || obj.name.trim().length === 0) {
    throw new Error(`initiatives[${idx}].name must be a non-empty string`);
  }
  if (!obj.status || !VALID_STATUSES.has(obj.status as string)) {
    throw new Error(
      `initiatives[${idx}].status must be one of: ${[...VALID_STATUSES].join(", ")}, got: ${obj.status}`
    );
  }
  if (
    obj.spec_slug != null &&
    (typeof obj.spec_slug !== "string" || !SPEC_SLUG_RE.test(obj.spec_slug))
  ) {
    throw new Error(
      `initiatives[${idx}].spec_slug must be a safe relative path, got: ${obj.spec_slug}`
    );
  }

  return {
    id: obj.id as string,
    name: (obj.name as string).trim(),
    owner: typeof obj.owner === "string" ? obj.owner : null,
    status: obj.status as Initiative["status"],
    spec_slug: (obj.spec_slug as string | null) ?? null,
    github_label: (obj.github_label as string | null) ?? null,
    start_date: (obj.start_date as string | null) ?? null,
    target_date: (obj.target_date as string | null) ?? null,
  };
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  // Require service-role token (Supabase validates this automatically when
  // the function is invoked via REST — we just ensure it's present)
  const auth = req.headers.get("Authorization");
  if (!auth?.startsWith("Bearer ")) {
    return new Response(JSON.stringify({ error: "Authorization header required" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false },
  });

  // Parse + validate body
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Request body must be valid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!Array.isArray(body.initiatives) || body.initiatives.length === 0) {
    return new Response(
      JSON.stringify({
        error: "Body must contain a non-empty initiatives array. " +
               "Parse ssot/ppm/portfolio.yaml and POST { initiatives: [...] }",
      }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const initiatives: Initiative[] = [];
  for (let idx = 0; idx < body.initiatives.length; idx++) {
    try {
      initiatives.push(validateInitiative(body.initiatives[idx], idx));
    } catch (e) {
      return new Response(
        JSON.stringify({ error: e instanceof Error ? e.message : String(e) }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }
  }

  // Upsert ppm_initiatives
  const rows = initiatives.map((i) => ({
    initiative_id: i.id,
    name: i.name,
    owner: i.owner,
    status: i.status,
    spec_slug: i.spec_slug,
    github_label: i.github_label,
    start_date: i.start_date,
    target_date: i.target_date,
  }));

  const { error: upsertErr } = await supabase
    .schema("ops")
    .from("ppm_initiatives")
    .upsert(rows, { onConflict: "initiative_id" });

  if (upsertErr) {
    console.error("upsert error:", upsertErr.message);
    return new Response(JSON.stringify({ error: `DB upsert failed: ${upsertErr.message}` }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Compute rollups
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const rollups = [];

  for (const i of initiatives) {
    const { count: blockingCount } = await supabase
      .schema("ops")
      .from("convergence_findings")
      .select("id", { count: "exact", head: true })
      .eq("severity", "critical")
      .eq("resolved", false);

    const { count: mergedPRs } = await supabase
      .schema("ops")
      .from("runs")
      .select("id", { count: "exact", head: true })
      .eq("kind", "agent")
      .eq("status", "completed")
      .gte("updated_at", thirtyDaysAgo);

    const { data: lastRun } = await supabase
      .schema("ops")
      .from("runs")
      .select("status, updated_at")
      .ilike("task_description", `%${i.id}%`)
      .order("updated_at", { ascending: false })
      .limit(1)
      .maybeSingle();

    rollups.push({
      initiative_id: i.id,
      blocking_findings: blockingCount ?? 0,
      merged_prs_30d: mergedPRs ?? 0,
      last_run_status: lastRun?.status ?? null,
      last_run_at: lastRun?.updated_at ?? null,
    });
  }

  const { error: rollupErr } = await supabase
    .schema("ops")
    .from("ppm_status_rollups")
    .insert(rollups);

  if (rollupErr) {
    // Log but non-fatal — report can still be generated
    console.error("rollup insert error:", rollupErr.message);
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

  // Write artifact (graceful if ops.artifacts not yet available)
  try {
    await supabase
      .schema("ops")
      .from("artifacts")
      .insert({
        kind: "ppm_report",
        name: `ppm_report_${new Date().toISOString().split("T")[0]}`,
        path: "ops/ppm/reports/",
        metadata: { report_md: reportMd, initiative_count: initiatives.length },
      });
  } catch (e) {
    console.warn("ops.artifacts write skipped:", e instanceof Error ? e.message : String(e));
  }

  return new Response(
    JSON.stringify({
      ok: true,
      initiatives_upserted: initiatives.length,
      rollups_computed: rollups.length,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
