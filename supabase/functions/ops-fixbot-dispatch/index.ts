// =============================================================================
// ops-fixbot-dispatch — FixBot Agent Dispatcher Edge Function
// =============================================================================
// SSOT:      ssot/agents/fixbot_policy.yaml
// Migration: supabase/migrations/20260301000070_ops_convergence_maintenance.sql
//
// Purpose:   On gate/build failure, create an ops.agent_runs row with a pre-filled
//            Agent Relay Template prompt, then optionally invoke @claude or enqueue
//            for async processing.
//
// Trigger:   Called from ops-convergence-scan or manually via API.
// =============================================================================

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// ---------------------------------------------------------------------------
// PostgREST helper
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
    headers["Prefer"] = "return=representation";
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
// FixBot policy (inline subset — full policy in ssot/agents/fixbot_policy.yaml)
// ---------------------------------------------------------------------------

const ALLOWED_KINDS = ["fix_build", "fix_gate", "fix_migration", "fix_webhook"] as const;
type FixKind = (typeof ALLOWED_KINDS)[number];

const PROMPT_TEMPLATE = `You are FixBot. Your job is to fix the failing signal and open a PR.

CONTEXT
- repo: Insightpulseai/odoo
- failing signal: {signal_name}
- trigger ref: {trigger_ref}
- evidence: {evidence_links}

GUARDRAILS
- PR-only. Do not push to main.
- Do not touch ssot/secrets/*.
- Keep changes minimal.
- Run tests and the relevant policy gates locally/CI.
- If you can't fix within the allowed scope, open a PR that adds diagnostics + a clear next step.

TASK
1) Reproduce the failure using repo scripts/tests.
2) Implement the smallest fix.
3) Update/add tests to prevent regression.
4) Open a PR with:
   - summary
   - root cause
   - evidence links
   - verification steps
Return:
- PR URL
- files changed
- test results`;

function buildPrompt(
  signalName: string,
  triggerRef: string,
  evidenceLinks: string,
): string {
  return PROMPT_TEMPLATE
    .replace("{signal_name}", signalName)
    .replace("{trigger_ref}", triggerRef)
    .replace("{evidence_links}", evidenceLinks);
}

// ---------------------------------------------------------------------------
// Dispatch logic
// ---------------------------------------------------------------------------

interface DispatchRequest {
  kind: FixKind;
  signal_name: string;
  trigger_source: string;  // vercel | github | supabase | manual
  trigger_ref: string;
  evidence_links?: string;
}

async function dispatchFixBot(
  req: DispatchRequest,
): Promise<{ ok: boolean; run_id?: string; error?: string }> {
  // Validate kind
  if (!ALLOWED_KINDS.includes(req.kind)) {
    return { ok: false, error: `Invalid kind: ${req.kind}. Allowed: ${ALLOWED_KINDS.join(", ")}` };
  }

  const prompt = buildPrompt(
    req.signal_name,
    req.trigger_ref,
    req.evidence_links ?? "none",
  );

  // Create agent run
  const rows = (await postgrest("POST", "ops.agent_runs", {
    kind: req.kind,
    trigger_source: req.trigger_source,
    trigger_ref: req.trigger_ref,
    prompt,
    status: "queued",
    metadata: {
      signal_name: req.signal_name,
      dispatched_at: new Date().toISOString(),
    },
  })) as Array<{ id: string }>;

  const runId = rows[0].id;

  // Log dispatch event
  await postgrest("POST", "ops.agent_events", {
    run_id: runId,
    event_type: "fixbot.dispatched",
    payload: {
      kind: req.kind,
      signal_name: req.signal_name,
      trigger_source: req.trigger_source,
      trigger_ref: req.trigger_ref,
    },
  });

  // TODO: invoke @claude integration endpoint or enqueue via Inngest
  // For now, the agent run is created and awaits external pickup.

  return { ok: true, run_id: runId };
}

// ---------------------------------------------------------------------------
// Deno.serve entrypoint
// ---------------------------------------------------------------------------

Deno.serve(async (req: Request) => {
  // Auth guard
  const authHeader = req.headers.get("authorization");
  if (authHeader !== `Bearer ${serviceKey}`) {
    return new Response(JSON.stringify({ ok: false, error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const body = (await req.json()) as DispatchRequest;

    if (!body.kind || !body.signal_name || !body.trigger_source || !body.trigger_ref) {
      return new Response(
        JSON.stringify({
          ok: false,
          error: "Missing required fields: kind, signal_name, trigger_source, trigger_ref",
        }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    const result = await dispatchFixBot(body);
    const status = result.ok ? 200 : 400;

    return new Response(JSON.stringify(result), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return new Response(
      JSON.stringify({ ok: false, error: message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
