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
  | "dns_placeholder"
  | "gate_failed"
  | "webhook_unverified"
  | "awaiting_auth"
  | "token_stale";

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

// ---------------------------------------------------------------------------
// External checks: Vercel env vars + Supabase management token health
// ---------------------------------------------------------------------------

interface ExternalFinding {
  kind: FindingKind;
  key: string;
  evidence: Record<string, unknown>;
  suggested_action: string;
}

async function checkVercelEnvVars(): Promise<ExternalFinding[]> {
  const findings: ExternalFinding[] = [];
  const vercelToken = Deno.env.get("VERCEL_TOKEN");
  const vercelProjectId = Deno.env.get("VERCEL_PROJECT_ID") ?? "odooops-console";

  if (!vercelToken) {
    // Cannot check — VERCEL_TOKEN not configured in this function's env
    return findings;
  }

  let resp: Response;
  try {
    resp = await fetch(
      `https://api.vercel.com/v10/projects/${vercelProjectId}/env`,
      { headers: { Authorization: `Bearer ${vercelToken}` } },
    );
  } catch (_err) {
    // Network error — skip check rather than emitting false positive
    return findings;
  }

  if (!resp.ok) {
    // Non-200 means token invalid or project not found — do not emit env_missing
    return findings;
  }

  const body = await resp.json() as { envs?: Array<{ key: string }> };
  const envKeys = (body.envs ?? []).map((e) => e.key);

  const requiredEnvVars = [
    "PLANE_WEBHOOK_SECRET",
    "GITHUB_WEBHOOK_SECRET",
  ] as const;

  for (const required of requiredEnvVars) {
    if (!envKeys.includes(required)) {
      findings.push({
        kind: "env_missing",
        key: `${required}@vercel:${vercelProjectId}`,
        evidence: {
          project: vercelProjectId,
          missing_key: required,
          runbook: "docs/runbooks/failures/ENV.VERCEL.WEBHOOK_SECRETS.md",
        },
        suggested_action: `Set ${required} in Vercel project ${vercelProjectId}. See runbook ENV.VERCEL.WEBHOOK_SECRETS.md.`,
      });
    }
  }

  return findings;
}

async function checkSupabaseTokenHealth(): Promise<ExternalFinding[]> {
  const findings: ExternalFinding[] = [];
  const sbAccessToken = Deno.env.get("SUPABASE_ACCESS_TOKEN");

  if (!sbAccessToken) {
    // Token not configured — cannot check
    return findings;
  }

  let resp: Response;
  try {
    resp = await fetch("https://api.supabase.com/v1/projects", {
      headers: { Authorization: `Bearer ${sbAccessToken}` },
    });
  } catch (_err) {
    // Network error — skip rather than false positive
    return findings;
  }

  if (resp.status === 401 || resp.status === 403) {
    findings.push({
      kind: "token_stale",
      key: "supabase_access_token",
      evidence: {
        http_status: resp.status,
        runbook: "docs/runbooks/failures/AUTH.SUPABASE.TOKEN_STALE.md",
        rotation_interval_days: 90,
      },
      suggested_action:
        "Rotate SUPABASE_ACCESS_TOKEN: generate new token in Supabase Dashboard → Account → Access Tokens, then update GitHub secret. See runbook AUTH.SUPABASE.TOKEN_STALE.md.",
    });
  }

  return findings;
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

  // ---------------------------------------------------------------------------
  // External checks (run once, not per-environment)
  // ---------------------------------------------------------------------------
  try {
    const vercelFindings = await checkVercelEnvVars();
    const tokenFindings = await checkSupabaseTokenHealth();
    const externalFindings = [...vercelFindings, ...tokenFindings];

    for (const finding of externalFindings) {
      await rpc("upsert_convergence_finding", {
        p_env: "prod",
        p_kind: finding.kind,
        p_key: finding.key,
        p_status: "open",
        p_evidence: finding.evidence,
        p_suggested_action: finding.suggested_action,
      });
      totalFindings++;
    }

    if (externalFindings.length > 0) {
      await postgrest("POST", "ops.maintenance_run_events", {
        run_id: runId,
        level: "warn",
        message: `External checks: ${externalFindings.length} findings (Vercel env: ${vercelFindings.length}, Supabase token: ${tokenFindings.length})`,
        data: { vercel_findings: vercelFindings.length, token_findings: tokenFindings.length },
      });
    } else {
      await postgrest("POST", "ops.maintenance_run_events", {
        run_id: runId,
        level: "info",
        message: "External checks: 0 findings",
        data: { vercel_findings: 0, token_findings: 0 },
      });
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await postgrest("POST", "ops.maintenance_run_events", {
      run_id: runId,
      level: "error",
      message: `Error in external checks: ${message}`,
      data: { error: message },
    });
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
