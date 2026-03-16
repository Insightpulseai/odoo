/**
 * Lakehouse Executor - Edge Function
 *
 * Stateless worker that claims runs from the ops.runs queue,
 * executes phases, emits events, and registers artifacts.
 *
 * @module executor
 */

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2.38.0";
import { PhaseHandler, PhaseResult, RunContext, ExecutorConfig } from "./types.ts";
import { IngestHandler } from "./handlers/ingest.ts";
import { ValidateHandler } from "./handlers/validate.ts";
import { TransformHandler } from "./handlers/transform.ts";
import { PublishHandler } from "./handlers/publish.ts";
import { QueryHandler } from "./handlers/query.ts";

// ============================================================================
// CONFIGURATION
// ============================================================================

const config: ExecutorConfig = {
  executorId: Deno.env.get("EXECUTOR_ID") || crypto.randomUUID(),
  heartbeatIntervalMs: 30_000,
  maxRetries: 3,
  retryBackoffMs: 1000,
  phaseTimeoutMs: 300_000, // 5 minutes
};

// ============================================================================
// PHASE HANDLER REGISTRY
// ============================================================================

const phaseHandlers: Record<string, PhaseHandler> = {
  ingest: new IngestHandler(),
  validate: new ValidateHandler(),
  transform: new TransformHandler(),
  publish: new PublishHandler(),
  query: new QueryHandler(),
};

// ============================================================================
// SUPABASE CLIENT
// ============================================================================

function createSupabaseClient(): SupabaseClient {
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

  if (!supabaseUrl || !supabaseKey) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
  }

  return createClient(supabaseUrl, supabaseKey, {
    auth: { persistSession: false },
  });
}

// ============================================================================
// EXECUTOR LOOP
// ============================================================================

async function claimRun(supabase: SupabaseClient): Promise<RunContext | null> {
  const { data, error } = await supabase.rpc("claim_run", {
    p_executor: config.executorId,
  });

  if (error) {
    console.error("[executor] claim_run error:", error.message);
    return null;
  }

  if (!data || data.length === 0) {
    return null;
  }

  const row = data[0];
  return {
    runId: row.run_id,
    kind: row.kind,
    spec: row.spec,
    artifactBaseUri: row.artifact_base_uri,
  };
}

async function startRun(supabase: SupabaseClient, runId: string): Promise<boolean> {
  const { data, error } = await supabase.rpc("start_run", {
    p_run_id: runId,
  });

  if (error) {
    console.error("[executor] start_run error:", error.message);
    return false;
  }

  return data === true;
}

async function heartbeat(
  supabase: SupabaseClient,
  runId: string,
  phase: string
): Promise<boolean> {
  const { data, error } = await supabase.rpc("heartbeat_run", {
    p_run_id: runId,
    p_phase: phase,
  });

  if (error) {
    console.error("[executor] heartbeat error:", error.message);
    return false;
  }

  return data === true;
}

async function emitEvent(
  supabase: SupabaseClient,
  runId: string,
  level: "debug" | "info" | "warn" | "error",
  phase: string,
  message: string,
  data: Record<string, unknown> = {}
): Promise<void> {
  const { error } = await supabase.from("run_events").insert({
    run_id: runId,
    level,
    phase,
    message,
    data,
  });

  if (error) {
    console.error("[executor] emitEvent error:", error.message);
  }
}

async function registerArtifact(
  supabase: SupabaseClient,
  runId: string,
  kind: string,
  uri: string,
  sha256: string | null,
  sizeBytes: number | null,
  meta: Record<string, unknown> = {}
): Promise<void> {
  const { error } = await supabase.from("run_artifacts").insert({
    run_id: runId,
    kind,
    uri,
    sha256,
    size_bytes: sizeBytes,
    meta,
  });

  if (error) {
    console.error("[executor] registerArtifact error:", error.message);
  }
}

async function completeRun(supabase: SupabaseClient, runId: string): Promise<boolean> {
  const { data, error } = await supabase.rpc("complete_run", {
    p_run_id: runId,
  });

  if (error) {
    console.error("[executor] complete_run error:", error.message);
    return false;
  }

  return data === true;
}

async function failRun(
  supabase: SupabaseClient,
  runId: string,
  errorCode: string,
  errorMessage: string,
  errorData: Record<string, unknown> = {}
): Promise<boolean> {
  const { data, error } = await supabase.rpc("fail_run", {
    p_run_id: runId,
    p_error_code: errorCode,
    p_error_message: errorMessage,
    p_error_data: errorData,
  });

  if (error) {
    console.error("[executor] fail_run error:", error.message);
    return false;
  }

  return data === true;
}

async function executePhase(
  supabase: SupabaseClient,
  ctx: RunContext,
  phase: string,
  phaseSpec: Record<string, unknown>
): Promise<PhaseResult> {
  const handler = phaseHandlers[phase];
  if (!handler) {
    return {
      success: false,
      errorCode: "UNKNOWN_PHASE",
      errorMessage: `No handler registered for phase: ${phase}`,
    };
  }

  // Emit phase started event
  await emitEvent(supabase, ctx.runId, "info", phase, `Phase ${phase} started`);

  // Set up heartbeat interval
  const heartbeatInterval = setInterval(async () => {
    await heartbeat(supabase, ctx.runId, phase);
  }, config.heartbeatIntervalMs);

  try {
    // Execute the phase handler
    const result = await handler.execute(ctx, phaseSpec, {
      emitEvent: (level, message, data) =>
        emitEvent(supabase, ctx.runId, level, phase, message, data),
      registerArtifact: (kind, uri, sha256, sizeBytes, meta) =>
        registerArtifact(supabase, ctx.runId, kind, uri, sha256, sizeBytes, meta),
      heartbeat: () => heartbeat(supabase, ctx.runId, phase),
    });

    // Emit phase completed event
    if (result.success) {
      await emitEvent(supabase, ctx.runId, "info", phase, `Phase ${phase} succeeded`, {
        artifacts: result.artifacts || [],
      });
    } else {
      await emitEvent(supabase, ctx.runId, "error", phase, `Phase ${phase} failed`, {
        errorCode: result.errorCode,
        errorMessage: result.errorMessage,
      });
    }

    return result;
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    await emitEvent(supabase, ctx.runId, "error", phase, `Phase ${phase} threw exception`, {
      error: errorMessage,
    });

    return {
      success: false,
      errorCode: "PHASE_EXCEPTION",
      errorMessage,
    };
  } finally {
    clearInterval(heartbeatInterval);
  }
}

async function executeRun(supabase: SupabaseClient, ctx: RunContext): Promise<void> {
  console.log(`[executor] Starting run ${ctx.runId} (kind: ${ctx.kind})`);

  // Start the run
  const started = await startRun(supabase, ctx.runId);
  if (!started) {
    console.error(`[executor] Failed to start run ${ctx.runId}`);
    return;
  }

  // Get phases from spec
  const phases = (ctx.spec.phases as string[]) || ["ingest", "validate", "transform", "publish"];
  const phaseSpecs = (ctx.spec.phase_specs as Record<string, Record<string, unknown>>) || {};

  // Execute each phase in order
  for (const phase of phases) {
    const phaseSpec = phaseSpecs[phase] || {};

    // Update heartbeat with current phase
    await heartbeat(supabase, ctx.runId, phase);

    // Execute the phase
    const result = await executePhase(supabase, ctx, phase, phaseSpec);

    if (!result.success) {
      // Phase failed - fail the run
      await failRun(
        supabase,
        ctx.runId,
        result.errorCode || "PHASE_FAILED",
        result.errorMessage || `Phase ${phase} failed`,
        { phase, phaseSpec }
      );
      return;
    }
  }

  // All phases succeeded - complete the run
  await completeRun(supabase, ctx.runId);
  console.log(`[executor] Run ${ctx.runId} completed successfully`);
}

// ============================================================================
// HTTP HANDLER
// ============================================================================

async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname;

  // Health check
  if (path === "/health" || path === "/") {
    return new Response(
      JSON.stringify({
        status: "ok",
        executor_id: config.executorId,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // Trigger executor loop (POST /run)
  if (path === "/run" && req.method === "POST") {
    try {
      const supabase = createSupabaseClient();

      // Try to claim a run
      const ctx = await claimRun(supabase);
      if (!ctx) {
        return new Response(
          JSON.stringify({ status: "idle", message: "No runs available" }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      // Execute the run (async, don't await for long-running jobs)
      // For Edge Functions, we need to complete within the timeout
      await executeRun(supabase, ctx);

      return new Response(
        JSON.stringify({
          status: "completed",
          run_id: ctx.runId,
          kind: ctx.kind,
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      console.error("[executor] Error:", errorMessage);

      return new Response(
        JSON.stringify({ status: "error", error: errorMessage }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  }

  // List available phase handlers (GET /handlers)
  if (path === "/handlers" && req.method === "GET") {
    return new Response(
      JSON.stringify({
        handlers: Object.keys(phaseHandlers),
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // 404 for unknown paths
  return new Response(
    JSON.stringify({ error: "Not found" }),
    {
      status: 404,
      headers: { "Content-Type": "application/json" },
    }
  );
}

// ============================================================================
// START SERVER
// ============================================================================

serve(handler);
