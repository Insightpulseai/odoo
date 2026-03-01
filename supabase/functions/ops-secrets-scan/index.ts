// =============================================================================
// ops-secrets-scan — Secrets Inventory Scanner Edge Function
// =============================================================================
// SSOT:      ssot/secrets/registry.yaml (v2_entries)
// Migration: supabase/migrations/20260302000010_ops_secret_inventory.sql
// Schedule:  Every 6 hours via ops.schedules / Vercel cron.
//
// Purpose:
//   1. For each registry entry, probe presence and validity via external APIs.
//   2. Upsert status into ops.secret_inventory.
//   3. Emit ops.convergence_findings for critical/high secrets that are missing/stale.
//   4. Write ops.maintenance_runs + events row.
//
// Probe strategies by consumer kind:
//   - github_secret   → GET /repos/Insightpulseai/odoo/actions/secrets/{name} with GITHUB_TOKEN
//   - vercel_env      → GET /v10/projects/{project}/env with VERCEL_TOKEN, check if name exists
//   - supabase_vault  → SELECT count(*) FROM vault.decrypted_secrets WHERE name = $1
//   - supabase token  → GET /v1/projects with SUPABASE_ACCESS_TOKEN
//   - other           → mark unknown (no probe available)
// =============================================================================

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const GITHUB_TOKEN = Deno.env.get("GITHUB_TOKEN") ?? "";
const VERCEL_TOKEN = Deno.env.get("VERCEL_TOKEN") ?? "";
const SUPABASE_ACCESS_TOKEN = Deno.env.get("SUPABASE_ACCESS_TOKEN") ?? "";
const CRON_SECRET = Deno.env.get("CRON_SECRET") ?? "";

const GITHUB_REPO = "Insightpulseai/odoo";

// ---------------------------------------------------------------------------
// Registry snapshot — hardcoded since Edge Functions cannot read files.
// Mirrors ssot/secrets/registry.yaml#v2_entries.
// ---------------------------------------------------------------------------

type HealthcheckKind = "http" | "jwt" | "presence" | "none";
type ConsumerKind = "github_secret" | "vercel_env" | "supabase_vault" | "keychain" | "odoo_config";

interface RegistryEntry {
  key: string;
  purpose: string;
  severity: "critical" | "high" | "medium" | "low";
  consumers: Array<{
    kind: ConsumerKind;
    project?: string;
    name: string;
  }>;
  rotation_cadence: string;
  healthcheck: {
    kind: HealthcheckKind;
    system: "supabase" | "vercel" | "github" | "digitalocean" | "mailgun" | "odoo";
    endpoint?: string;
    auth?: "bearer" | "basic" | "header";
    envVar?: string;
  };
}

const REGISTRY_SNAPSHOT: RegistryEntry[] = [
  {
    key: "supabase_access_token",
    purpose: "Supabase Management API PAT used by Supabase CLI and CI deploy workflows",
    severity: "critical",
    consumers: [{ kind: "github_secret", name: "SUPABASE_ACCESS_TOKEN" }],
    rotation_cadence: "90d",
    healthcheck: {
      kind: "http",
      system: "supabase",
      endpoint: "https://api.supabase.com/v1/projects",
      auth: "bearer",
      envVar: "SUPABASE_ACCESS_TOKEN",
    },
  },
  {
    key: "supabase_service_role_key",
    purpose: "Supabase project service role key — bypasses RLS for Edge Functions and ops-console API routes",
    severity: "critical",
    consumers: [
      { kind: "github_secret", name: "SUPABASE_SERVICE_ROLE_KEY" },
      { kind: "vercel_env", project: "odooops-console", name: "SUPABASE_SERVICE_ROLE_KEY" },
    ],
    rotation_cadence: "90d",
    healthcheck: {
      kind: "presence",
      system: "vercel",
      envVar: "SUPABASE_SERVICE_ROLE_KEY",
    },
  },
  {
    key: "supabase_anon_key",
    purpose: "Supabase project anon key (public-safe) for ops-console public queries with RLS enforced",
    severity: "high",
    consumers: [
      { kind: "vercel_env", project: "odooops-console", name: "NEXT_PUBLIC_SUPABASE_ANON_KEY" },
    ],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "presence",
      system: "vercel",
      envVar: "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    },
  },
  {
    key: "plane_webhook_secret",
    purpose: "Shared HMAC secret for verifying inbound Plane.so webhook payloads in ops-console",
    severity: "high",
    consumers: [
      { kind: "supabase_vault", name: "plane_webhook_secret" },
      { kind: "vercel_env", project: "odooops-console", name: "PLANE_WEBHOOK_SECRET" },
    ],
    rotation_cadence: "180d",
    healthcheck: {
      kind: "presence",
      system: "supabase",
      envVar: "plane_webhook_secret",
    },
  },
  {
    key: "github_webhook_secret",
    purpose: "Shared HMAC-SHA256 secret for verifying inbound GitHub webhook payloads",
    severity: "high",
    consumers: [
      { kind: "supabase_vault", name: "github_webhook_secret" },
      { kind: "vercel_env", project: "odooops-console", name: "GITHUB_WEBHOOK_SECRET" },
    ],
    rotation_cadence: "180d",
    healthcheck: {
      kind: "presence",
      system: "supabase",
      envVar: "github_webhook_secret",
    },
  },
  {
    key: "vercel_token",
    purpose: "Vercel API PAT used by CI workflows to trigger and manage Vercel deployments",
    severity: "medium",
    consumers: [{ kind: "github_secret", name: "VERCEL_TOKEN" }],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "http",
      system: "vercel",
      endpoint: "https://api.vercel.com/v10/projects/odooops-console/env",
      auth: "bearer",
      envVar: "VERCEL_TOKEN",
    },
  },
  {
    key: "cloudflare_api_token",
    purpose: "Cloudflare scoped API token for Terraform DNS apply via CI",
    severity: "medium",
    consumers: [{ kind: "github_secret", name: "CF_DNS_EDIT_TOKEN" }],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "none",
      system: "github",
      envVar: "CF_DNS_EDIT_TOKEN",
    },
  },
  {
    key: "digitalocean_access_token",
    purpose: "DigitalOcean API token for doctl, App Platform and Ops Advisor DO scan adapter",
    severity: "high",
    consumers: [
      { kind: "github_secret", name: "DO_ACCESS_TOKEN" },
      { kind: "supabase_vault", name: "digitalocean_api_token" },
    ],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "none",
      system: "digitalocean",
      envVar: "DO_ACCESS_TOKEN",
    },
  },
  {
    key: "mailgun_api_key",
    purpose: "Mailgun API key for webhook verification and optional management API queries",
    severity: "low",
    consumers: [{ kind: "supabase_vault", name: "mailgun_api_key" }],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "none",
      system: "mailgun",
      envVar: "mailgun_api_key",
    },
  },
  {
    key: "zoho_mail_smtp_password",
    purpose: "Zoho Mail SMTP app-specific password for Odoo outbound email",
    severity: "medium",
    consumers: [{ kind: "odoo_config", name: "ir.mail_server.smtp_pass" }],
    rotation_cadence: "365d",
    healthcheck: {
      kind: "none",
      system: "odoo",
    },
  },
];

// ---------------------------------------------------------------------------
// PostgREST helper (raw fetch)
// ---------------------------------------------------------------------------

async function postgrest(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders: Record<string, string> = {},
): Promise<unknown> {
  const headers: Record<string, string> = {
    apikey: SERVICE_KEY,
    Authorization: `Bearer ${SERVICE_KEY}`,
    "Content-Type": "application/json",
    ...extraHeaders,
  };
  if (method === "POST" || method === "PATCH") {
    headers["Prefer"] = "resolution=merge-duplicates,return=representation";
  }
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`PostgREST ${method} ${path}: ${res.status} ${text}`);
  }
  return text ? JSON.parse(text) : null;
}

// ---------------------------------------------------------------------------
// Probe: check GitHub Actions secret presence
// ---------------------------------------------------------------------------

async function probeGithubSecret(secretName: string): Promise<{
  status: "ok" | "missing" | "unknown";
  statusCode: number;
  error?: string;
}> {
  if (!GITHUB_TOKEN) {
    return { status: "unknown", statusCode: 0, error: "GITHUB_TOKEN not available" };
  }
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/actions/secrets/${secretName}`,
      {
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
        },
      },
    );
    if (res.status === 200) return { status: "ok", statusCode: 200 };
    if (res.status === 404) return { status: "missing", statusCode: 404 };
    const text = await res.text();
    return { status: "unknown", statusCode: res.status, error: text.slice(0, 200) };
  } catch (err) {
    return { status: "unknown", statusCode: 0, error: String(err) };
  }
}

// ---------------------------------------------------------------------------
// Probe: check Vercel environment variable presence
// ---------------------------------------------------------------------------

async function probeVercelEnv(envVarName: string, project = "odooops-console"): Promise<{
  status: "ok" | "missing" | "unknown";
  statusCode: number;
  error?: string;
}> {
  if (!VERCEL_TOKEN) {
    return { status: "unknown", statusCode: 0, error: "VERCEL_TOKEN not available" };
  }
  try {
    const res = await fetch(
      `https://api.vercel.com/v10/projects/${project}/env`,
      {
        headers: {
          Authorization: `Bearer ${VERCEL_TOKEN}`,
        },
      },
    );
    if (!res.ok) {
      const text = await res.text();
      return { status: "unknown", statusCode: res.status, error: text.slice(0, 200) };
    }
    const data = await res.json() as { envs?: Array<{ key: string }> };
    const envs = data.envs ?? [];
    const found = envs.some((e) => e.key === envVarName);
    return { status: found ? "ok" : "missing", statusCode: res.status };
  } catch (err) {
    return { status: "unknown", statusCode: 0, error: String(err) };
  }
}

// ---------------------------------------------------------------------------
// Probe: check Supabase Management API token validity
// ---------------------------------------------------------------------------

async function probeSupabaseToken(): Promise<{
  status: "ok" | "missing" | "stale" | "unknown";
  statusCode: number;
  error?: string;
}> {
  if (!SUPABASE_ACCESS_TOKEN) {
    return { status: "missing", statusCode: 0, error: "SUPABASE_ACCESS_TOKEN env var absent" };
  }
  try {
    const res = await fetch("https://api.supabase.com/v1/projects", {
      headers: {
        Authorization: `Bearer ${SUPABASE_ACCESS_TOKEN}`,
      },
    });
    if (res.status === 200) return { status: "ok", statusCode: 200 };
    if (res.status === 401) return { status: "stale", statusCode: 401, error: "Token invalid or expired" };
    const text = await res.text();
    return { status: "unknown", statusCode: res.status, error: text.slice(0, 200) };
  } catch (err) {
    return { status: "unknown", statusCode: 0, error: String(err) };
  }
}

// ---------------------------------------------------------------------------
// Probe: check Supabase Vault secret presence
// ---------------------------------------------------------------------------

async function probeSupabaseVault(vaultSecretName: string): Promise<{
  status: "ok" | "missing" | "unknown";
  statusCode: number;
  error?: string;
}> {
  try {
    const result = await postgrest(
      "GET",
      `vault.decrypted_secrets?name=eq.${encodeURIComponent(vaultSecretName)}&select=id`,
    ) as Array<{ id: string }>;
    if (Array.isArray(result) && result.length > 0) {
      return { status: "ok", statusCode: 200 };
    }
    return { status: "missing", statusCode: 200, error: `Vault secret '${vaultSecretName}' not found` };
  } catch (err) {
    return { status: "unknown", statusCode: 0, error: String(err) };
  }
}

// ---------------------------------------------------------------------------
// Determine status for a single registry entry
// ---------------------------------------------------------------------------

interface ProbeResult {
  status: "ok" | "missing" | "stale" | "unknown";
  statusCode: number;
  error?: string;
  observed: Record<string, unknown>;
}

async function probeEntry(entry: RegistryEntry): Promise<ProbeResult> {
  const observed: Record<string, unknown> = {};

  // Special case: supabase_access_token — probe the Management API directly
  if (entry.key === "supabase_access_token") {
    const r = await probeSupabaseToken();
    observed["supabase_management_api"] = r.status;
    return { status: r.status, statusCode: r.statusCode, error: r.error, observed };
  }

  // For entries with Vercel env consumers, probe Vercel
  const vercelConsumers = entry.consumers.filter((c) => c.kind === "vercel_env");
  for (const vc of vercelConsumers) {
    const r = await probeVercelEnv(vc.name, vc.project ?? "odooops-console");
    observed[`vercel_env.${vc.name}`] = r.status;
    if (r.status === "missing") {
      return { status: "missing", statusCode: r.statusCode, error: r.error, observed };
    }
  }

  // For entries with GitHub secret consumers, probe GitHub
  const ghConsumers = entry.consumers.filter((c) => c.kind === "github_secret");
  for (const gc of ghConsumers) {
    const r = await probeGithubSecret(gc.name);
    observed[`github_secret.${gc.name}`] = r.status;
    if (r.status === "missing") {
      return { status: "missing", statusCode: r.statusCode, error: r.error, observed };
    }
  }

  // For entries with Supabase Vault consumers, probe Vault
  const vaultConsumers = entry.consumers.filter((c) => c.kind === "supabase_vault");
  for (const vc of vaultConsumers) {
    const r = await probeSupabaseVault(vc.name);
    observed[`supabase_vault.${vc.name}`] = r.status;
    if (r.status === "missing") {
      return { status: "missing", statusCode: r.statusCode, error: r.error, observed };
    }
  }

  // If nothing actionable probed, mark unknown
  if (Object.keys(observed).length === 0) {
    return {
      status: "unknown",
      statusCode: 0,
      error: "No probe configured for consumer kinds",
      observed,
    };
  }

  // All probed consumers are ok
  const allOk = Object.values(observed).every((v) => v === "ok");
  return {
    status: allOk ? "ok" : "unknown",
    statusCode: 200,
    observed,
  };
}

// ---------------------------------------------------------------------------
// Compute next_rotation_at from cadence string
// ---------------------------------------------------------------------------

function nextRotationAt(cadence: string): string | null {
  const now = new Date();
  const match = cadence.match(/^(\d+)(d|y)$/);
  if (!match) return null;
  const n = parseInt(match[1], 10);
  const unit = match[2];
  if (unit === "d") now.setDate(now.getDate() + n);
  else if (unit === "y") now.setFullYear(now.getFullYear() + n);
  return now.toISOString();
}

// ---------------------------------------------------------------------------
// Main scan logic
// ---------------------------------------------------------------------------

async function runSecretsScan(): Promise<{
  run_id: string;
  total: number;
  missing: number;
  stale: number;
  ok: number;
  unknown: number;
}> {
  const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

  // Create maintenance run
  const { data: runRows, error: runErr } = await supabase
    .from("ops.maintenance_runs")
    .insert({
      chore_id: "secrets_scan",
      chore_name: "Secrets Inventory Scan",
      status: "running",
      started_at: new Date().toISOString(),
    })
    .select("id");

  if (runErr || !runRows?.length) {
    throw new Error(`Failed to create maintenance run: ${runErr?.message}`);
  }

  const runId = runRows[0].id as string;
  let totalMissing = 0;
  let totalStale = 0;
  let totalOk = 0;
  let totalUnknown = 0;

  for (const entry of REGISTRY_SNAPSHOT) {
    let probeResult: ProbeResult;
    try {
      probeResult = await probeEntry(entry);
    } catch (err) {
      probeResult = {
        status: "unknown",
        statusCode: 0,
        error: String(err),
        observed: {},
      };
    }

    // Upsert into ops.secret_inventory
    const { error: upsertErr } = await supabase
      .from("ops.secret_inventory")
      .upsert(
        {
          key: entry.key,
          purpose: entry.purpose,
          severity_if_missing: entry.severity,
          desired_consumers: entry.consumers,
          observed: probeResult.observed,
          status: probeResult.status,
          probe_status_code: probeResult.statusCode || null,
          probe_error: probeResult.error ?? null,
          last_checked_at: new Date().toISOString(),
          next_rotation_at: nextRotationAt(entry.rotation_cadence),
        },
        { onConflict: "key" },
      );

    if (upsertErr) {
      console.error(`Failed to upsert secret_inventory for ${entry.key}:`, upsertErr);
    }

    // Tally
    if (probeResult.status === "ok") totalOk++;
    else if (probeResult.status === "missing") totalMissing++;
    else if (probeResult.status === "stale") totalStale++;
    else totalUnknown++;

    // Emit convergence finding for critical/high missing or stale secrets
    if (
      (probeResult.status === "missing" || probeResult.status === "stale") &&
      (entry.severity === "critical" || entry.severity === "high")
    ) {
      try {
        await postgrest(
          "POST",
          "ops.convergence_findings",
          {
            env: "prod",
            kind: "vault_missing",
            key: `secret:${entry.key}`,
            status: "open",
            evidence: {
              secret_key: entry.key,
              probe_status: probeResult.status,
              probe_error: probeResult.error,
              severity: entry.severity,
            },
            suggested_action: `Provision missing secret '${entry.key}' (severity: ${entry.severity}). See ssot/secrets/registry.yaml#v2_entries.`,
          },
          { Prefer: "resolution=merge-duplicates,return=representation" },
        );
      } catch (err) {
        console.error(`Failed to emit convergence finding for ${entry.key}:`, err);
      }
    }

    // Log event
    await supabase.from("ops.maintenance_run_events").insert({
      run_id: runId,
      level: probeResult.status === "ok" ? "info" : probeResult.status === "unknown" ? "warn" : "error",
      message: `Secret '${entry.key}': ${probeResult.status}`,
      data: {
        key: entry.key,
        status: probeResult.status,
        severity: entry.severity,
        observed: probeResult.observed,
      },
    });
  }

  // Complete maintenance run
  await supabase
    .from("ops.maintenance_runs")
    .update({
      status: "completed",
      completed_at: new Date().toISOString(),
      findings_count: totalMissing + totalStale,
      evidence: {
        total: REGISTRY_SNAPSHOT.length,
        ok: totalOk,
        missing: totalMissing,
        stale: totalStale,
        unknown: totalUnknown,
      },
    })
    .eq("id", runId);

  return {
    run_id: runId,
    total: REGISTRY_SNAPSHOT.length,
    missing: totalMissing,
    stale: totalStale,
    ok: totalOk,
    unknown: totalUnknown,
  };
}

// ---------------------------------------------------------------------------
// Deno.serve entrypoint
// ---------------------------------------------------------------------------

Deno.serve(async (req: Request) => {
  // Auth guard: require service role or CRON_SECRET
  const authHeader = req.headers.get("authorization");

  if (
    authHeader !== `Bearer ${SERVICE_KEY}` &&
    (CRON_SECRET === "" || authHeader !== `Bearer ${CRON_SECRET}`)
  ) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const result = await runSecretsScan();
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
