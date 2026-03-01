// =============================================================================
// pulser-slack-handler — Slack /pulser slash command receiver
// =============================================================================
// Contract:  docs/contracts/C-SLACK-01-pulser-slash-commands.md
// SSOT:      spec/odooops-console/prd.md (FR17 — Slack Interface)
// Migration: supabase/migrations/20260301000070_ops_taskbus_intents.sql
//
// Receives Slack slash commands, validates + parses, enqueues an intent
// row in ops.taskbus_intents, returns an ephemeral response within 3s.
// Never executes long tasks in-request.
// =============================================================================

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const slackSigningSecret = Deno.env.get("SLACK_SIGNING_SECRET") ?? "";

// ── Types ──────────────────────────────────────────────────────────────────

interface ParsedCommand {
  intent_type: string;
  args: Record<string, unknown>;
}

interface SlackPayload {
  command: string;
  text: string;
  user_id: string;
  user_name: string;
  channel_id: string;
  channel_name: string;
  trigger_id: string;
  response_url: string;
  team_id: string;
}

// ── Slack request signature verification ───────────────────────────────────

async function verifySlackSignature(
  req: Request,
  body: string,
): Promise<boolean> {
  if (!slackSigningSecret) {
    console.warn("SLACK_SIGNING_SECRET not set — skipping verification");
    return true; // Allow in dev; in prod this env var must be set
  }

  const timestamp = req.headers.get("x-slack-request-timestamp") ?? "";
  const slackSignature = req.headers.get("x-slack-signature") ?? "";

  if (!timestamp || !slackSignature) return false;

  // Reject requests older than 5 minutes
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - parseInt(timestamp, 10)) > 300) return false;

  const sigBasestring = `v0:${timestamp}:${body}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(slackSigningSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(sigBasestring),
  );
  const hexSig = "v0=" + Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  return hexSig === slackSignature;
}

// ── Command parser ─────────────────────────────────────────────────────────

const VALID_INTENT_TYPES = new Set([
  "status", "deploy", "rollback", "builds", "gates",
  "migrate", "functions", "webhooks", "plane", "github",
  "mail", "fix", "help",
]);

export function parseCommand(text: string): ParsedCommand {
  const parts = text.trim().split(/\s+/);
  const subcommand = (parts[0] ?? "help").toLowerCase();
  const rest = parts.slice(1);

  // Route composite commands
  switch (subcommand) {
    case "status":
      return { intent_type: "status", args: {} };

    case "help":
      return { intent_type: "help", args: {} };

    case "deploy": {
      const env = rest[0] ?? "prod";
      const ref = rest[1] ?? "main";
      return { intent_type: "deploy", args: { env, ref } };
    }

    case "rollback": {
      const env = rest[0] ?? "prod";
      const toIdx = rest.indexOf("to");
      const target = toIdx >= 0 && rest[toIdx + 1] ? rest[toIdx + 1] : null;
      return { intent_type: "rollback", args: { env, ...(target ? { target } : {}) } };
    }

    case "builds": {
      const limitFlag = rest.indexOf("--limit");
      const limit = limitFlag >= 0 && rest[limitFlag + 1]
        ? parseInt(rest[limitFlag + 1], 10) || 5
        : 5;
      return { intent_type: "builds", args: { limit } };
    }

    case "gates": {
      const failuresOnly = rest.includes("--failures");
      return { intent_type: "gates", args: { failures_only: failuresOnly } };
    }

    case "migrate": {
      const env = rest[0] ?? "prod";
      const toFlag = rest.indexOf("--to");
      const migrationId = toFlag >= 0 && rest[toFlag + 1] ? rest[toFlag + 1] : null;
      return { intent_type: "migrate", args: { env, ...(migrationId ? { migration_id: migrationId } : {}) } };
    }

    case "functions": {
      const action = rest[0]?.toLowerCase();
      if (action === "deploy") {
        const name = rest[1] ?? "all";
        return { intent_type: "functions_deploy", args: { name } };
      }
      return { intent_type: "help", args: { error: `Unknown functions subcommand: ${action}` } };
    }

    case "webhooks": {
      const action = rest[0]?.toLowerCase();
      if (action === "verify") {
        return { intent_type: "webhooks_verify", args: {} };
      }
      return { intent_type: "help", args: { error: `Unknown webhooks subcommand: ${action}` } };
    }

    case "plane": {
      const action = rest[0]?.toLowerCase();
      if (action === "backfill") {
        const sinceFlag = rest.indexOf("--since");
        const since = sinceFlag >= 0 && rest[sinceFlag + 1] ? rest[sinceFlag + 1] : null;
        return { intent_type: "plane_backfill", args: { ...(since ? { since } : {}) } };
      }
      return { intent_type: "help", args: { error: `Unknown plane subcommand: ${action}` } };
    }

    case "github": {
      const action = rest[0]?.toLowerCase();
      if (action === "backfill") {
        const repoFlag = rest.indexOf("--repo");
        const repo = repoFlag >= 0 && rest[repoFlag + 1] ? rest[repoFlag + 1] : null;
        const sinceFlag = rest.indexOf("--since");
        const since = sinceFlag >= 0 && rest[sinceFlag + 1] ? rest[sinceFlag + 1] : null;
        return {
          intent_type: "github_backfill",
          args: { ...(repo ? { repo } : {}), ...(since ? { since } : {}) },
        };
      }
      return { intent_type: "help", args: { error: `Unknown github subcommand: ${action}` } };
    }

    case "mail": {
      const action = rest[0]?.toLowerCase();
      if (action === "latest") {
        const envFlag = rest.indexOf("--env");
        const env = envFlag >= 0 && rest[envFlag + 1] ? rest[envFlag + 1] : null;
        return { intent_type: "mail_latest", args: { ...(env ? { env } : {}) } };
      }
      if (action === "test") {
        const env = rest[1] ?? "dev";
        return { intent_type: "mail_test", args: { env } };
      }
      return { intent_type: "help", args: { error: `Unknown mail subcommand: ${action}` } };
    }

    case "odoo": {
      const action = rest[0]?.toLowerCase();
      const envFlag = rest.indexOf("--env");
      const env = envFlag >= 0 && rest[envFlag + 1] ? rest[envFlag + 1] : "prod";

      if (action === "healthcheck" || action === "health") {
        return {
          intent_type: "odoo.healthcheck",
          args: {
            env,
            include: { addons_paths: true, workers: true, modules_count: true, supabase_reachable: true },
          },
        };
      }
      if (action === "modules" || action === "modules.status") {
        return {
          intent_type: "odoo.modules.status",
          args: {
            env,
            limit: { installed_sample: 50 },
            allowlist: { profile: "oca_allowlist_v1", include_diff: true },
            risk: { include: true },
          },
        };
      }
      if (action === "config" || action === "config.snapshot") {
        return {
          intent_type: "odoo.config.snapshot",
          args: {
            env,
            redaction: {
              mode: "safe",
              include_keys: ["db_host", "db_port", "db_sslmode", "proxy_mode", "workers", "limit_time_real", "limit_time_cpu", "smtp_host", "smtp_port"],
            },
            fingerprint: {
              algorithm: "sha256",
              include_keys: ["db_host", "db_port", "proxy_mode", "workers", "limit_time_real", "limit_time_cpu", "smtp_host", "smtp_port"],
            },
          },
        };
      }
      return { intent_type: "help", args: { error: `Unknown odoo subcommand: ${action}` } };
    }

    case "fix": {
      const signalId = rest[0] ?? null;
      const scopeFlag = rest.indexOf("--scope");
      const scope = scopeFlag >= 0 && rest[scopeFlag + 1] ? rest[scopeFlag + 1] : null;
      if (!signalId) {
        return { intent_type: "help", args: { error: "fix requires a signal_id, gate, or build reference" } };
      }
      return { intent_type: "fix", args: { signal_id: signalId, ...(scope ? { scope } : {}) } };
    }

    default:
      return {
        intent_type: "help",
        args: { error: `Unknown command: ${subcommand}` },
      };
  }
}

// ── Help text ──────────────────────────────────────────────────────────────

function helpText(error?: string): string {
  const prefix = error ? `*Error*: ${error}\n\n` : "";
  return `${prefix}*Pulser* (ops runner) — commands

*MVP*
• \`/pulser status\`
  - Show deployment convergence (git vs deployed), blockers (migrations/functions/secrets), and last failed gate.
  - Example: \`/pulser status\`

• \`/pulser gates --failures\`
  - Show current failing policy gates with evidence links.
  - Example: \`/pulser gates --failures\`

• \`/pulser mail latest [--env prod|stage|dev]\`
  - Show latest mail-catcher events (subject/from/to/transport/stamp).
  - Example: \`/pulser mail latest --env stage\`

*Odoo*
• \`/pulser odoo healthcheck [--env prod|stage|dev]\`
  - Odoo health: version, db, modules count, connectivity.

• \`/pulser odoo modules [--env prod]\`
  - Installed modules + allowlist diff summary.

• \`/pulser odoo config [--env prod]\`
  - Safe config fingerprint (no secrets).

*Extended*
• \`/pulser deploy <env> <ref>\` — Enqueue deploy intent
• \`/pulser rollback <env> [to <sha>]\` — Rollback environment
• \`/pulser builds [--limit N]\` — Latest CI builds
• \`/pulser migrate <env> [--to <id>]\` — Apply migration
• \`/pulser functions deploy <name|all>\` — Deploy Edge Function
• \`/pulser fix <signal_id|gate|build>\` — Enqueue agent fix run

*Output contract*
Every command enqueues an intent and returns quickly.
You'll receive a \`run_id\` and an Ops Console link for evidence.

*Links*
• Ops Console: https://odooops-console.vercel.app
• Runbooks: https://odooops-console.vercel.app/runbooks`;
}

// ── PostgREST helper ───────────────────────────────────────────────────────

async function enqueueIntent(
  intent: ParsedCommand,
  slackPayload: SlackPayload,
): Promise<{ run_id: string }> {
  const requestId = slackPayload.trigger_id || crypto.randomUUID();

  const row = {
    request_id: requestId,
    intent_type: intent.intent_type,
    args: intent.args,
    requested_by: slackPayload.user_id,
    channel_id: slackPayload.channel_id,
    response_url: slackPayload.response_url,
    status: "queued",
  };

  const res = await fetch(`${supabaseUrl}/rest/v1/ops.taskbus_intents`, {
    method: "POST",
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
    },
    body: JSON.stringify(row),
  });

  if (!res.ok) {
    const text = await res.text();
    // Check for unique constraint violation (duplicate request_id = idempotent)
    if (res.status === 409 || text.includes("duplicate key")) {
      // Fetch existing intent by request_id
      const existing = await fetch(
        `${supabaseUrl}/rest/v1/ops.taskbus_intents?request_id=eq.${encodeURIComponent(requestId)}&select=run_id`,
        {
          headers: {
            apikey: serviceKey,
            Authorization: `Bearer ${serviceKey}`,
            Accept: "application/json",
          },
        },
      );
      const rows = await existing.json() as { run_id: string }[];
      if (rows.length > 0) return { run_id: rows[0].run_id };
    }
    throw new Error(`PostgREST insert taskbus_intents: ${res.status} ${text}`);
  }

  const rows = await res.json() as { run_id: string }[];
  return { run_id: rows[0].run_id };
}

// ── Slack response helpers ─────────────────────────────────────────────────

function slackEphemeral(text: string, blocks?: unknown[]): Response {
  const body: Record<string, unknown> = {
    response_type: "ephemeral",
    text,
  };
  if (blocks) body.blocks = blocks;
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

// ── Main handler ───────────────────────────────────────────────────────────

Deno.serve(async (req: Request): Promise<Response> => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "content-type",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Read body as text for signature verification
  const bodyText = await req.text();

  // Verify Slack signature
  const validSig = await verifySlackSignature(req, bodyText);
  if (!validSig) {
    console.error("pulser-slack-handler: invalid Slack signature");
    return new Response(JSON.stringify({ ok: false, error: "invalid signature" }), {
      status: 403,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Parse form-urlencoded Slack payload
  const params = new URLSearchParams(bodyText);
  const slackPayload: SlackPayload = {
    command: params.get("command") ?? "/pulser",
    text: params.get("text") ?? "",
    user_id: params.get("user_id") ?? "",
    user_name: params.get("user_name") ?? "",
    channel_id: params.get("channel_id") ?? "",
    channel_name: params.get("channel_name") ?? "",
    trigger_id: params.get("trigger_id") ?? "",
    response_url: params.get("response_url") ?? "",
    team_id: params.get("team_id") ?? "",
  };

  console.log(
    `pulser-slack-handler: user=${slackPayload.user_name} cmd="${slackPayload.text}"`,
  );

  // Parse command
  const parsed = parseCommand(slackPayload.text);

  // Handle help immediately (no enqueue needed)
  if (parsed.intent_type === "help") {
    return slackEphemeral(helpText(parsed.args.error as string | undefined));
  }

  // Enqueue intent
  try {
    const { run_id } = await enqueueIntent(parsed, slackPayload);

    const ackText =
      `:white_check_mark: *Queued*: \`${parsed.intent_type}\`\n` +
      `run_id: \`${run_id}\`\n` +
      `args: \`${JSON.stringify(parsed.args)}\``;

    console.log(`pulser-slack-handler: queued run_id=${run_id} type=${parsed.intent_type}`);
    return slackEphemeral(ackText);
  } catch (err) {
    const message = (err as Error).message ?? "Internal error";
    console.error("pulser-slack-handler: enqueue failed:", message);
    return slackEphemeral(`:x: Failed to enqueue: ${message}`);
  }
});
