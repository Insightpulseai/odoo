// =============================================================================
// pulser-intent-runner — Consumes Pulser slash command intents
// =============================================================================
// Contract:  docs/contracts/C-SLACK-01-pulser-slash-commands.md
// SSOT:      spec/odooops-console/prd.md (FR17 — Slack Interface)
// Migration: supabase/migrations/20260301000070_ops_taskbus_intents.sql
//
// Claims queued intents from ops.taskbus_intents, executes MVP commands
// (status, gates, mail latest), and posts results back to Slack.
// =============================================================================

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// ── Types ──────────────────────────────────────────────────────────────────

interface Intent {
  id: number;
  run_id: string;
  intent_type: string;
  args: Record<string, unknown>;
  requested_by: string;
  channel_id: string | null;
  response_url: string | null;
}

interface ExecutionResult {
  ok: boolean;
  text: string;
  blocks?: unknown[];
}

// ── PostgREST helpers ──────────────────────────────────────────────────────

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

// ── Claim next batch of intents ────────────────────────────────────────────

async function claimIntents(batchSize = 5): Promise<Intent[]> {
  const now = new Date().toISOString();

  // Fetch queued intents (oldest first)
  const queued = (await postgrest(
    "GET",
    `ops.taskbus_intents?status=eq.queued&order=created_at.asc&limit=${batchSize}&select=id,run_id,intent_type,args,requested_by,channel_id,response_url`,
  )) as Intent[] | null;

  if (!queued || queued.length === 0) return [];

  // Claim them
  const ids = queued.map((i) => i.id);
  await postgrest(
    "PATCH",
    `ops.taskbus_intents?id=in.(${ids.join(",")})`,
    { status: "claimed", claimed_at: now },
  );

  return queued;
}

// ── Update intent status ───────────────────────────────────────────────────

async function completeIntent(
  id: number,
  status: "success" | "failed",
  result?: Record<string, unknown>,
  errorMessage?: string,
): Promise<void> {
  await postgrest(
    "PATCH",
    `ops.taskbus_intents?id=eq.${id}`,
    {
      status,
      result: result ?? null,
      error_message: errorMessage ?? null,
      completed_at: new Date().toISOString(),
    },
  );
}

// ── Slack reply ────────────────────────────────────────────────────────────

async function postSlackReply(
  responseUrl: string,
  text: string,
  blocks?: unknown[],
): Promise<void> {
  const body: Record<string, unknown> = {
    response_type: "in_channel",
    replace_original: false,
    text,
  };
  if (blocks) body.blocks = blocks;

  const res = await fetch(responseUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    console.error(`Slack reply failed: ${res.status} ${await res.text()}`);
  }
}

// ── Command executors (MVP) ────────────────────────────────────────────────

async function executeStatus(): Promise<ExecutionResult> {
  // Fetch latest deployment/run
  const runs = (await postgrest(
    "GET",
    "ops.taskbus_intents?status=in.(success,failed)&order=completed_at.desc&limit=5&select=intent_type,status,args,completed_at,run_id",
  )) as Record<string, unknown>[] | null;

  // Fetch active droplets
  let dropletCount = 0;
  try {
    const droplets = (await postgrest(
      "GET",
      "ops.do_droplets?status=eq.active&select=do_id",
    )) as unknown[] | null;
    dropletCount = droplets?.length ?? 0;
  } catch { /* table may not exist yet */ }

  // Fetch latest DO ingest run
  let lastIngest: Record<string, unknown> | null = null;
  try {
    const ingestRuns = (await postgrest(
      "GET",
      "ops.do_ingest_runs?order=created_at.desc&limit=1&select=run_id,status,counts,created_at",
    )) as Record<string, unknown>[] | null;
    lastIngest = ingestRuns?.[0] ?? null;
  } catch { /* table may not exist yet */ }

  // Fetch capability count
  let capCount = 0;
  try {
    const caps = (await postgrest(
      "GET",
      "ops.capabilities?select=id",
    )) as unknown[] | null;
    capCount = caps?.length ?? 0;
  } catch { /* table may not exist yet */ }

  const lines = [
    ":satellite: *Pulser Status*",
    "",
    `*Active Droplets*: ${dropletCount}`,
    `*Capabilities Registered*: ${capCount}`,
    `*Last DO Ingest*: ${lastIngest ? `${lastIngest.status} at ${lastIngest.created_at}` : "none"}`,
    "",
    "*Recent Intents*:",
  ];

  if (runs && runs.length > 0) {
    for (const r of runs) {
      const icon = r.status === "success" ? ":white_check_mark:" : ":x:";
      lines.push(`  ${icon} \`${r.intent_type}\` (${r.run_id}) — ${r.completed_at}`);
    }
  } else {
    lines.push("  No completed intents yet.");
  }

  return { ok: true, text: lines.join("\n") };
}

async function executeGates(args: Record<string, unknown>): Promise<ExecutionResult> {
  const failuresOnly = args.failures_only === true;

  // Query advisor findings as gate proxy
  let findings: Record<string, unknown>[] = [];
  try {
    const filter = failuresOnly
      ? "ops.advisor_findings?status=eq.open&order=severity.asc,last_seen_at.desc&limit=10&select=check_id,category,severity,title,status"
      : "ops.advisor_findings?order=severity.asc,last_seen_at.desc&limit=10&select=check_id,category,severity,title,status";
    findings = ((await postgrest("GET", filter)) as Record<string, unknown>[] | null) ?? [];
  } catch { /* table may not exist */ }

  // Also check capabilities for gate-relevant info
  let gateCapabilities: Record<string, unknown>[] = [];
  try {
    gateCapabilities = ((await postgrest(
      "GET",
      "ops.capabilities?maturity=eq.prod&select=key,name,maturity",
    )) as Record<string, unknown>[] | null) ?? [];
  } catch { /* ignore */ }

  const lines = [
    `:shield: *Policy Gates*${failuresOnly ? " (failures only)" : ""}`,
    "",
  ];

  if (findings.length > 0) {
    for (const f of findings) {
      const icon = f.severity === "critical" ? ":red_circle:"
        : f.severity === "high" ? ":large_orange_circle:"
        : f.severity === "medium" ? ":large_yellow_circle:"
        : ":white_circle:";
      const statusIcon = f.status === "open" ? ":warning:" : ":white_check_mark:";
      lines.push(`${icon} ${statusIcon} *${f.title}* [${f.category}/${f.severity}] — ${f.status}`);
    }
  } else {
    lines.push(failuresOnly ? "No open gate failures." : "No gate findings recorded yet.");
  }

  if (gateCapabilities.length > 0) {
    lines.push("");
    lines.push(`*Prod-ready capabilities*: ${gateCapabilities.map((c) => c.key).join(", ")}`);
  }

  return { ok: true, text: lines.join("\n") };
}

async function executeMailLatest(args: Record<string, unknown>): Promise<ExecutionResult> {
  const envFilter = args.env ? `&env=eq.${args.env}` : "";

  let events: Record<string, unknown>[] = [];
  try {
    events = ((await postgrest(
      "GET",
      `mail_events?order=received_at.desc&limit=10${envFilter}&select=env,provider,message_id,subject,sender,recipient,transport,stamp,received_at`,
    )) as Record<string, unknown>[] | null) ?? [];
  } catch { /* table may not exist */ }

  const lines = [
    `:email: *Mail Events*${args.env ? ` (env=${args.env})` : ""}`,
    "",
  ];

  if (events.length > 0) {
    for (const e of events) {
      lines.push(
        `• *${e.subject}*\n  from: \`${e.sender}\` → \`${e.recipient}\`\n  transport: \`${e.transport}\` | env: \`${e.env}\` | ${e.stamp}`,
      );
    }
  } else {
    lines.push("No mail events captured yet.");
  }

  return { ok: true, text: lines.join("\n") };
}

async function executeBuilds(args: Record<string, unknown>): Promise<ExecutionResult> {
  const limit = (args.limit as number) || 5;

  let builds: Record<string, unknown>[] = [];
  try {
    builds = ((await postgrest(
      "GET",
      `ops.builds?order=created_at.desc&limit=${limit}&select=id,status,git_sha,git_ref,created_at,duration_ms`,
    )) as Record<string, unknown>[] | null) ?? [];
  } catch { /* table may not exist yet */ }

  const lines = [`:hammer_and_wrench: *Latest Builds* (limit=${limit})`, ""];

  if (builds.length > 0) {
    for (const b of builds) {
      const icon = b.status === "success" ? ":white_check_mark:"
        : b.status === "failed" ? ":x:"
        : ":hourglass_flowing_sand:";
      lines.push(
        `${icon} \`${(b.git_sha as string)?.substring(0, 7) ?? "?"}\` on \`${b.git_ref}\` — ${b.status} (${b.duration_ms ?? "?"}ms) — ${b.created_at}`,
      );
    }
  } else {
    lines.push("No builds recorded yet.");
  }

  return { ok: true, text: lines.join("\n") };
}

// Stub executors for non-MVP commands (enqueue acknowledgment only)
function stubExecutor(intentType: string, args: Record<string, unknown>): ExecutionResult {
  return {
    ok: true,
    text: `:construction: \`${intentType}\` is queued for execution.\nArgs: \`${JSON.stringify(args)}\`\n\n_This command is not yet fully implemented. The intent has been recorded for future processing._`,
  };
}

// ── Intent dispatcher ──────────────────────────────────────────────────────

async function executeIntent(intent: Intent): Promise<ExecutionResult> {
  switch (intent.intent_type) {
    case "status":
      return await executeStatus();
    case "gates":
      return await executeGates(intent.args);
    case "mail_latest":
      return await executeMailLatest(intent.args);
    case "builds":
      return await executeBuilds(intent.args);
    case "deploy":
    case "rollback":
    case "migrate":
    case "functions_deploy":
    case "webhooks_verify":
    case "plane_backfill":
    case "github_backfill":
    case "mail_test":
    case "fix":
      return stubExecutor(intent.intent_type, intent.args);
    default:
      return { ok: false, text: `Unknown intent type: ${intent.intent_type}` };
  }
}

// ── Main handler ───────────────────────────────────────────────────────────

Deno.serve(async (req: Request): Promise<Response> => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
      },
    });
  }

  // Accept GET (cron) or POST (manual trigger)
  if (req.method !== "GET" && req.method !== "POST") {
    return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }

  try {
    // Claim batch
    const intents = await claimIntents(5);

    if (intents.length === 0) {
      return Response.json({ ok: true, message: "No intents in queue", processed: 0 });
    }

    console.log(`pulser-intent-runner: claimed ${intents.length} intent(s)`);

    const results: { run_id: string; status: string; intent_type: string }[] = [];

    for (const intent of intents) {
      try {
        // Mark as running
        await postgrest("PATCH", `ops.taskbus_intents?id=eq.${intent.id}`, {
          status: "running",
        });

        // Execute
        const result = await executeIntent(intent);

        // Mark complete
        await completeIntent(
          intent.id,
          result.ok ? "success" : "failed",
          { text: result.text },
          result.ok ? undefined : result.text,
        );

        // Post to Slack if response_url available
        if (intent.response_url) {
          const header = result.ok ? ":white_check_mark:" : ":x:";
          await postSlackReply(
            intent.response_url,
            `${header} *\`/pulser ${intent.intent_type}\`* (run_id: \`${intent.run_id}\`)\n\n${result.text}`,
            result.blocks,
          );
        }

        results.push({
          run_id: intent.run_id,
          status: result.ok ? "success" : "failed",
          intent_type: intent.intent_type,
        });

        console.log(
          `pulser-intent-runner: ${intent.run_id} ${intent.intent_type} → ${result.ok ? "success" : "failed"}`,
        );
      } catch (err) {
        const msg = (err as Error).message ?? "Unknown error";
        console.error(`pulser-intent-runner: ${intent.run_id} failed:`, msg);

        await completeIntent(intent.id, "failed", undefined, msg);

        if (intent.response_url) {
          await postSlackReply(
            intent.response_url,
            `:x: *\`/pulser ${intent.intent_type}\`* failed: ${msg}`,
          );
        }

        results.push({
          run_id: intent.run_id,
          status: "failed",
          intent_type: intent.intent_type,
        });
      }
    }

    return Response.json({ ok: true, processed: results.length, results });
  } catch (err) {
    const message = (err as Error).message ?? "Internal error";
    console.error("pulser-intent-runner fatal:", message);
    return Response.json({ ok: false, error: message }, { status: 500 });
  }
});
