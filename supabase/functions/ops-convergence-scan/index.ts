// =============================================================================
// ops-convergence-scan — Deployment Convergence Scanner Edge Function
// =============================================================================
// SSOT:      ssot/maintenance/convergence.yaml
// Migration: supabase/migrations/20260301000070_ops_convergence_maintenance.sql
// Schedule:  Every 15 minutes via ops.schedules / Vercel cron.
//
// Purpose:   Detect drift between git HEAD and deployed SHA per environment.
//            Produces ops.convergence_findings rows for each unmet requirement.
// =============================================================================

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// ---------------------------------------------------------------------------
// PostgREST helper (raw fetch — no SDK dependency)
// ---------------------------------------------------------------------------

async function postgrest(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders: Record<string, string> = {},
): Promise<unknown> {
  const headers: Record<string, string> = {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    "Content-Type": "application/json",
    ...extraHeaders,
  };
  if (method === "POST") {
    headers["Prefer"] = "resolution=merge-duplicates,return=representation";
  }
  const res = await fetch(`${supabaseUrl}/rest/v1/${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PostgREST ${method} ${path}: ${res.status} ${text}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ---------------------------------------------------------------------------
// RPC helper — calls Supabase stored procedures
// ---------------------------------------------------------------------------

async function rpc(fnName: string, params: Record<string, unknown>): Promise<unknown> {
  const res = await fetch(`${supabaseUrl}/rest/v1/rpc/${fnName}`, {
    method: "POST",
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`RPC ${fnName}: ${res.status} ${text}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ---------------------------------------------------------------------------
// Finding kinds (from ssot/maintenance/convergence.yaml)
// ---------------------------------------------------------------------------

type FindingKind =
  | "deploy_failed"
  | "deploy_behind"
  | "canceled_superseded"
  | "migrations_pending"
  | "function_missing"
  | "env_missing"
  | "vault_missing"
  | "dns_planned"
  | "gate_failed"
  | "webhook_unverified"
  | "awaiting_auth";

// ---------------------------------------------------------------------------
// Core scan logic
// ---------------------------------------------------------------------------

interface ScanResult {
  env: string;
  findings: Array<{
    kind: FindingKind;
    key: string;
    evidence: Record<string, unknown>;
    suggested_action: string;
  }>;
}

async function scanEnvironment(env: string): Promise<ScanResult> {
  const findings: ScanResult["findings"] = [];

  // 1. Check latest deployment status
  const deployments = (await postgrest(
    "GET",
    `ops.deployments?env=eq.${env}&order=created_at.desc&limit=1`,
  )) as Array<{
    id: string;
    status: string;
    git_sha: string;
    deployment_url: string;
  }> | null;

  if (deployments && deployments.length > 0) {
    const latest = deployments[0];

    if (latest.status === "failed") {
      findings.push({
        kind: "deploy_failed",
        key: `deploy:${latest.id}`,
        evidence: { deployment_id: latest.id, git_sha: latest.git_sha },
        suggested_action: "Investigate build logs and fix forward or revert.",
      });
    }

    if (latest.status === "canceled") {
      findings.push({
        kind: "canceled_superseded",
        key: `deploy:${latest.id}`,
        evidence: { deployment_id: latest.id },
        suggested_action: "Informational — build was superseded by a newer commit.",
      });
    }
  }

  // 2. Check latest builds for the environment
  const builds = (await postgrest(
    "GET",
    `ops.builds?order=created_at.desc&limit=1`,
  )) as Array<{
    id: string;
    status: string;
    git_sha: string;
  }> | null;

  if (builds && builds.length > 0 && deployments && deployments.length > 0) {
    const latestBuild = builds[0];
    const latestDeploy = deployments[0];

    if (
      latestBuild.git_sha &&
      latestDeploy.git_sha &&
      latestBuild.git_sha !== latestDeploy.git_sha
    ) {
      findings.push({
        kind: "deploy_behind",
        key: `sha:${latestBuild.git_sha.slice(0, 8)}`,
        evidence: {
          build_sha: latestBuild.git_sha,
          deployed_sha: latestDeploy.git_sha,
        },
        suggested_action: "Deploy latest build to update environment.",
      });
    }
  }

  // 3. Check gate status
  const failedGates = (await postgrest(
    "GET",
    `ops.gate_runs?status=eq.failed&order=created_at.desc&limit=5`,
  )) as Array<{ gate_name: string; id: string }> | null;

  if (failedGates) {
    for (const gate of failedGates) {
      findings.push({
        kind: "gate_failed",
        key: `gate:${gate.gate_name}`,
        evidence: { gate_run_id: gate.id },
        suggested_action: `Fix failing gate: ${gate.gate_name}`,
      });
    }
  }

  return { env, findings };
}

async function runConvergenceScan(): Promise<{
  run_id: string;
  total_findings: number;
  environments: ScanResult[];
}> {
  // Create maintenance run
  const runRows = (await postgrest("POST", "ops.maintenance_runs", {
    chore_id: "convergence_scan",
    chore_name: "Deployment Convergence Scan",
    status: "running",
    started_at: new Date().toISOString(),
  })) as Array<{ id: string }>;

  const runId = runRows[0].id;

  const environments = ["prod", "stage"];
  const results: ScanResult[] = [];
  let totalFindings = 0;

  for (const env of environments) {
    try {
      const result = await scanEnvironment(env);
      results.push(result);

      // Upsert findings
      for (const finding of result.findings) {
        await rpc("upsert_convergence_finding", {
          p_env: env,
          p_kind: finding.kind,
          p_key: finding.key,
          p_status: "open",
          p_evidence: finding.evidence,
          p_suggested_action: finding.suggested_action,
        });
        totalFindings++;
      }

      // Log event
      await postgrest("POST", "ops.maintenance_run_events", {
        run_id: runId,
        level: result.findings.length > 0 ? "warn" : "info",
        message: `Scanned ${env}: ${result.findings.length} findings`,
        data: { env, findings_count: result.findings.length },
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      await postgrest("POST", "ops.maintenance_run_events", {
        run_id: runId,
        level: "error",
        message: `Error scanning ${env}: ${message}`,
        data: { env, error: message },
      });
    }
  }

  // Complete maintenance run
  await postgrest(
    "PATCH",
    `ops.maintenance_runs?id=eq.${runId}`,
    {
      status: totalFindings > 0 ? "completed" : "completed",
      completed_at: new Date().toISOString(),
      findings_count: totalFindings,
      evidence: { environments: results.map((r) => r.env), total_findings: totalFindings },
    },
    { Prefer: "return=representation" },
  );

  return { run_id: runId, total_findings: totalFindings, environments: results };
}

// ---------------------------------------------------------------------------
// Deno.serve entrypoint
// ---------------------------------------------------------------------------

Deno.serve(async (req: Request) => {
  // Auth guard: require service role or CRON_SECRET
  const authHeader = req.headers.get("authorization");
  const cronSecret = Deno.env.get("CRON_SECRET");

  if (authHeader !== `Bearer ${serviceKey}` && authHeader !== `Bearer ${cronSecret}`) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const result = await runConvergenceScan();
    return new Response(
      JSON.stringify({ ok: true, ...result }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return new Response(
      JSON.stringify({ ok: false, error: message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
