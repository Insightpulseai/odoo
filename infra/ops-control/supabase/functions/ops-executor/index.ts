import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.48.1";
import { parse as parseYaml } from "https://deno.land/std@0.224.0/yaml/mod.ts";

// ============================================================
// Types
// ============================================================

type RunbookKind = "deploy" | "healthcheck" | "spec" | "incident" | "schema_sync";
type EventLevel = "debug" | "info" | "warn" | "error" | "success";
type Integration = "Supabase" | "Vercel" | "GitHub" | "DigitalOcean" | "Kubernetes";
type RunStatus = "queued" | "running" | "succeeded" | "failed" | "canceled";

interface RunbookPlan {
  id: string;
  kind: RunbookKind;
  title: string;
  summary: string;
  inputs: any[];
  risks: any[];
  integrations: Integration[];
}

interface DbRun {
  id: string;
  env: "prod" | "staging" | "dev";
  kind: RunbookKind;
  plan: RunbookPlan;
  status: RunStatus;
  template_id?: string | null;
  input?: Record<string, unknown>;
  intent?: string;
}

interface Artifact {
  kind: "link" | "diff" | "file" | "log" | "manifest";
  title: string;
  value?: string;
  content?: string | null;
  url?: string | null;
}

// ============================================================
// CORS Headers
// ============================================================

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// ============================================================
// Helpers
// ============================================================

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function adminClient() {
  const url = Deno.env.get("SUPABASE_URL")!;
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  return createClient(url, key, {
    auth: { persistSession: false },
    db: { schema: "public" },
  });
}

async function emitEvent(
  sb: any,
  run_id: string,
  level: EventLevel,
  phase: string,
  message: string,
  data: any = {}
) {
  await sb.from("run_events").insert({ run_id, level, phase, message, data });
}

async function addArtifact(
  sb: any,
  run_id: string,
  kind: string,
  title: string,
  content?: string | null,
  url?: string | null,
  metadata: any = {}
) {
  await sb.from("artifacts").insert({
    run_id,
    kind,
    title,
    content: content ?? null,
    url: url ?? null,
    metadata,
  });
}

function interpolate(str: string, inputs: Record<string, unknown>) {
  return str.replaceAll(/{{\s*inputs\.([a-zA-Z0-9_]+)\s*}}/g, (_m, key) => {
    const v = inputs[key];
    return v === undefined || v === null ? "" : String(v);
  });
}

// ============================================================
// Run Executor (parallel-aware)
// ============================================================

async function executeRun(sb: any, run: DbRun, workerId: string) {
  const run_id = run.id;
  const inputs: Record<string, unknown> = run.input ?? {};
  const log: string[] = [];

  await emitEvent(sb, run_id, "info", "start", "Run started", {
    workerId,
    intent: run.intent,
    template_id: run.template_id,
  });

  // Heartbeat loop (keeps "alive" signal)
  const hb = setInterval(async () => {
    await sb.rpc("heartbeat_run", { p_run_id: run_id, p_worker: workerId });
  }, 2000);

  try {
    // Load template YAML (optional)
    let steps: any[] = [];
    if (run.template_id) {
      const { data: t } = await sb
        .from("run_templates")
        .select("*")
        .eq("id", run.template_id)
        .maybeSingle();
      const template = t?.template_yaml ? parseYaml(t.template_yaml) : null;
      steps = Array.isArray((template as any)?.steps) ? (template as any).steps : [];
    }

    if (steps.length === 0) {
      // Default steps based on kind
      if (run.kind === "deploy") {
        steps = [
          { id: "validate", title: "Validate inputs", kind: "system", action: "validate" },
          { id: "build", title: "Build application", kind: "system", action: "build" },
          { id: "migrate", title: "Run migrations", kind: "system", action: "migrate" },
          { id: "deploy", title: "Deploy to target", kind: "system", action: "deploy" },
        ];
      } else if (run.kind === "spec") {
        steps = [
          { id: "analyze", title: "Analyze requirements", kind: "system", action: "analyze" },
          { id: "generate", title: "Generate spec docs", kind: "system", action: "generate" },
          { id: "pr", title: "Create PR", kind: "tool", tool: "github", action: "create_pr" },
        ];
      } else {
        steps = [
          { id: "plan", title: "Plan steps", kind: "system", action: "plan" },
          { id: "execute", title: "Execute actions", kind: "system", action: "execute" },
          { id: "finalize", title: "Finalize", kind: "system", action: "finalize" },
        ];
      }
    }

    await emitEvent(sb, run_id, "info", "plan_steps", "Planned steps", {
      steps: steps.map((s) => ({
        id: s.id,
        title: s.title,
        kind: s.kind,
        tool: s.tool,
        action: s.action,
      })),
    });

    // Execute steps
    for (const [i, step] of steps.entries()) {
      // Check if canceled
      const { data: latest } = await sb.from("runs").select("status").eq("id", run_id).maybeSingle();
      if (latest?.status === "canceled") {
        await emitEvent(sb, run_id, "warn", "canceled", "Run canceled", {});
        clearInterval(hb);
        return;
      }

      const phase = `step:${step.id ?? i}`;
      const title = step.title ?? step.id ?? `Step ${i}`;
      await emitEvent(sb, run_id, "info", "execute_steps", `Executing: ${title}`, { step });

      log.push(`[execute] ${title}`);

      if (step.kind === "tool") {
        const tool = String(step.tool ?? "unknown");
        const action = String(step.action ?? "unknown");
        const rawArgs = step.args ?? {};
        const args: Record<string, unknown> = {};
        for (const [k, v] of Object.entries(rawArgs)) {
          args[k] = typeof v === "string" ? interpolate(v, inputs) : v;
        }

        await emitEvent(sb, run_id, "info", phase, `Tool call: ${tool}.${action}`, { args });

        // TODO: replace simulation with real MCP bridge
        await emitEvent(sb, run_id, "debug", phase, "Tool result (simulated)", {
          ok: true,
          tool,
          action,
        });
      } else {
        // System step simulation
        await new Promise((r) => setTimeout(r, 500 + Math.random() * 1000));
        await emitEvent(sb, run_id, "success", phase, `✓ ${title}`, {});
      }

      await new Promise((r) => setTimeout(r, 250)); // makes streaming feel "alive"
    }

    const provenance = {
      run_id,
      workerId,
      status: "succeeded",
      template_id: run.template_id,
      created_at: run.created_at,
      finished_at: new Date().toISOString(),
    };

    await addArtifact(sb, run_id, "manifest", "provenance.manifest.json", JSON.stringify(provenance, null, 2));
    await addArtifact(sb, run_id, "log", "run.log", log.join("\n"));

    await sb.from("runs").update({
      status: "succeeded" as RunStatus,
      output: { provenance },
      error: null,
    }).eq("id", run_id);

    await emitEvent(sb, run_id, "info", "finalize", "Run succeeded", {});
  } catch (e) {
    await sb.from("runs").update({ status: "failed" as RunStatus, error: String(e) }).eq("id", run_id);
    await emitEvent(sb, run_id, "error", "finalize", "Run failed", { error: String(e) });
  } finally {
    clearInterval(hb);
  }
}

// ============================================================
// Main Handler (supports /run and /claim)
// ============================================================

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ ok: false, error: "POST only" }, 405);
  }

  const url = new URL(req.url);
  const path = url.pathname.split("/").pop() ?? "run";
  const sb = adminClient();

  try {
    const body = await req.json().catch(() => ({}));

    // /run: run a specific run_id (existing behavior, UI-triggered)
    if (path === "run") {
      const run_id = body?.run_id;
      const workerId = body?.worker_id ?? "edge-single";
      if (!run_id) return json({ ok: false, error: "Missing run_id" }, 400);

      const { data: run } = await sb.from("runs").select("*").eq("id", run_id).maybeSingle();
      if (!run) return json({ ok: false, error: "Run not found" }, 404);

      // Allow single-run start from UI: flip to running if still queued
      if (run.status === "queued") {
        await sb
          .from("runs")
          .update({
            status: "running",
            claimed_by: workerId,
            claimed_at: new Date().toISOString(),
            heartbeat_at: new Date().toISOString(),
          })
          .eq("id", run_id);
      }

      await executeRun(sb, run, workerId);
      return json({ ok: true, run_id });
    }

    // /claim: workers call this to claim N runs and execute them (parallel workers)
    if (path === "claim") {
      const workerId = body?.worker_id ?? "worker";
      const limit = Number(body?.limit ?? 1);
      const { data: claimed, error } = await sb.rpc("claim_runs", {
        p_worker: workerId,
        p_limit: limit,
      });
      if (error) return json({ ok: false, error: error.message }, 400);

      const runs = Array.isArray(claimed) ? claimed : [];
      for (const run of runs) {
        await executeRun(sb, run, workerId);
      }

      return json({ ok: true, claimed: runs.map((r: any) => r.id) });
    }

    return json({ ok: false, error: "Unknown endpoint" }, 404);
  } catch (e) {
    console.error("Executor error:", e);
    return json({ ok: false, error: String(e) }, 500);
  }
});