// =============================================================================
// RUN-EXECUTOR - MCP Jobs Queue Executor
// =============================================================================
// Processes jobs from mcp_jobs.jobs queue with timeout handling
// Triggered by pg_cron via X-CRON-SECRET authenticated HTTP POST
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface Job {
  id: string;
  source: string;
  job_type: string;
  payload: Record<string, unknown>;
  priority: number;
  retry_count: number;
  max_retries: number;
  retry_delay_seconds: number;
  worker_id: string | null;
  status: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  scheduled_at: string | null;
  timeout_at: string | null;
  result: Record<string, unknown> | null;
  error: string | null;
}

interface ExecutionResult {
  ok: boolean;
  data?: Record<string, unknown>;
  error?: string;
}

type JobHandler = (
  job: Job,
  supabase: SupabaseClient
) => Promise<ExecutionResult>;

// -----------------------------------------------------------------------------
// CORS Headers
// -----------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-cron-secret",
};

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status,
  });
}

function generateWorkerId(): string {
  const hostname = Deno.env.get("DENO_DEPLOYMENT_ID") || "local";
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `executor-${hostname}-${timestamp}-${random}`;
}

// -----------------------------------------------------------------------------
// Job Handlers Registry
// -----------------------------------------------------------------------------

const HANDLERS: Record<string, JobHandler> = {
  // Sync operations
  sync_odoo: handleSyncOdoo,
  sync_supabase: handleSyncSupabase,

  // Notification operations
  notify: handleNotify,
  notify_slack: handleNotifySlack,
  notify_mattermost: handleNotifyMattermost,

  // ETL operations
  etl: handleETL,
  etl_bronze: handleETLBronze,
  etl_silver: handleETLSilver,
  etl_gold: handleETLGold,

  // Discovery operations
  discovery: handleDiscovery,
  infra_scan: handleInfraScan,

  // Default handler
  default: handleDefault,
};

// -----------------------------------------------------------------------------
// Handler Implementations
// -----------------------------------------------------------------------------

async function handleSyncOdoo(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { model, ids, operation } = job.payload as {
    model?: string;
    ids?: number[];
    operation?: string;
  };

  if (!model) {
    return { ok: false, error: "Missing model in payload" };
  }

  // Log progress
  await logEvent(supabase, job.id, "progress", `Syncing ${model}: ${operation || "read"}`);

  // TODO: Implement actual Odoo XML-RPC call
  // For now, simulate success
  await new Promise((resolve) => setTimeout(resolve, 100));

  return {
    ok: true,
    data: {
      model,
      ids: ids || [],
      operation: operation || "read",
      synced_at: new Date().toISOString(),
    },
  };
}

async function handleSyncSupabase(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { table, operation } = job.payload as {
    table?: string;
    operation?: string;
  };

  await logEvent(supabase, job.id, "progress", `Supabase sync: ${table || "unknown"}`);

  return {
    ok: true,
    data: {
      table,
      operation,
      synced_at: new Date().toISOString(),
    },
  };
}

async function handleNotify(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { channel, message } = job.payload as {
    channel?: string;
    message?: string;
  };

  if (!message) {
    return { ok: false, error: "Missing message in payload" };
  }

  await logEvent(supabase, job.id, "progress", `Sending notification to ${channel || "default"}`);

  // TODO: Implement actual notification dispatch
  return {
    ok: true,
    data: {
      channel: channel || "default",
      sent_at: new Date().toISOString(),
    },
  };
}

async function handleNotifySlack(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { webhook_url, text, blocks } = job.payload as {
    webhook_url?: string;
    text?: string;
    blocks?: unknown[];
  };

  const slackUrl = webhook_url || Deno.env.get("SLACK_WEBHOOK_URL");

  if (!slackUrl) {
    return { ok: false, error: "No Slack webhook URL configured" };
  }

  if (!text) {
    return { ok: false, error: "Missing text in payload" };
  }

  await logEvent(supabase, job.id, "progress", "Sending Slack notification");

  try {
    const resp = await fetch(slackUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, blocks }),
    });

    if (!resp.ok) {
      return { ok: false, error: `Slack API error: ${resp.status}` };
    }

    return { ok: true, data: { sent_at: new Date().toISOString() } };
  } catch (e) {
    return { ok: false, error: `Slack error: ${e}` };
  }
}

async function handleNotifyMattermost(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  // Mattermost is deprecated, log warning and skip
  await logEvent(supabase, job.id, "progress", "Mattermost deprecated - skipping notification");
  return {
    ok: true,
    data: { skipped: true, reason: "Mattermost deprecated, use Slack" },
  };
}

async function handleETL(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { pipeline, source, target } = job.payload as {
    pipeline?: string;
    source?: string;
    target?: string;
  };

  await logEvent(supabase, job.id, "progress", `Running ETL pipeline: ${pipeline || "default"}`);

  return {
    ok: true,
    data: {
      pipeline: pipeline || "default",
      source,
      target,
      completed_at: new Date().toISOString(),
    },
  };
}

async function handleETLBronze(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  await logEvent(supabase, job.id, "progress", "ETL Bronze layer processing");
  return { ok: true, data: { layer: "bronze", processed_at: new Date().toISOString() } };
}

async function handleETLSilver(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  await logEvent(supabase, job.id, "progress", "ETL Silver layer processing");
  return { ok: true, data: { layer: "silver", processed_at: new Date().toISOString() } };
}

async function handleETLGold(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  await logEvent(supabase, job.id, "progress", "ETL Gold layer processing");
  return { ok: true, data: { layer: "gold", processed_at: new Date().toISOString() } };
}

async function handleDiscovery(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { target } = job.payload as { target?: string };
  await logEvent(supabase, job.id, "progress", `Discovery scan: ${target || "all"}`);
  return { ok: true, data: { target, discovered_at: new Date().toISOString() } };
}

async function handleInfraScan(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const { provider } = job.payload as { provider?: string };
  await logEvent(supabase, job.id, "progress", `Infra scan: ${provider || "all"}`);
  return { ok: true, data: { provider, scanned_at: new Date().toISOString() } };
}

async function handleDefault(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  await logEvent(supabase, job.id, "progress", `Default handler for job_type: ${job.job_type}`);
  return {
    ok: true,
    data: {
      job_type: job.job_type,
      payload: job.payload,
      note: "Processed by default handler",
    },
  };
}

// -----------------------------------------------------------------------------
// Event Logging
// -----------------------------------------------------------------------------

async function logEvent(
  supabase: SupabaseClient,
  jobId: string,
  eventType: string,
  message: string,
  metadata: Record<string, unknown> = {}
): Promise<void> {
  try {
    await supabase.from("mcp_jobs.job_events").insert({
      job_id: jobId,
      event_type: eventType,
      message,
      metadata,
    });
  } catch (e) {
    console.error(`Failed to log event for job ${jobId}:`, e);
  }
}

// -----------------------------------------------------------------------------
// Main Executor Logic
// -----------------------------------------------------------------------------

async function executeJob(job: Job, supabase: SupabaseClient): Promise<ExecutionResult> {
  const handler = HANDLERS[job.job_type] || HANDLERS.default;
  return await handler(job, supabase);
}

async function processNextJob(
  supabase: SupabaseClient,
  workerId: string,
  sourceFilter: string | null = null,
  timeoutMinutes = 5
): Promise<{ processed: boolean; jobId?: string; result?: ExecutionResult }> {
  // Claim next job atomically
  const { data: jobId, error: claimError } = await supabase.rpc("mcp_jobs.claim_next_job", {
    p_worker_id: workerId,
    p_source_filter: sourceFilter,
    p_timeout_minutes: timeoutMinutes,
  });

  if (claimError) {
    console.error("Failed to claim job:", claimError);
    return { processed: false };
  }

  if (!jobId) {
    // No jobs available
    return { processed: false };
  }

  // Fetch full job details
  const { data: job, error: fetchError } = await supabase
    .from("mcp_jobs.jobs")
    .select("*")
    .eq("id", jobId)
    .single();

  if (fetchError || !job) {
    console.error("Failed to fetch job details:", fetchError);
    return { processed: false };
  }

  console.log(`Processing job ${jobId}: ${job.job_type} from ${job.source}`);

  try {
    // Execute job
    const result = await executeJob(job as Job, supabase);

    if (result.ok) {
      // Complete job
      await supabase.rpc("mcp_jobs.complete_job", {
        p_job_id: jobId,
        p_result: result.data || {},
      });
      console.log(`Job ${jobId} completed successfully`);
    } else {
      // Fail job (will retry or move to DLQ)
      await supabase.rpc("mcp_jobs.fail_job", {
        p_job_id: jobId,
        p_error: result.error || "Unknown error",
      });
      console.log(`Job ${jobId} failed: ${result.error}`);
    }

    return { processed: true, jobId, result };
  } catch (e) {
    // Unexpected error - fail job
    const errorMessage = e instanceof Error ? e.message : String(e);
    await supabase.rpc("mcp_jobs.fail_job", {
      p_job_id: jobId,
      p_error: errorMessage,
      p_error_stack: e instanceof Error ? e.stack : undefined,
    });
    console.error(`Job ${jobId} crashed:`, e);
    return { processed: true, jobId, result: { ok: false, error: errorMessage } };
  }
}

async function reapStuckJobs(supabase: SupabaseClient): Promise<number> {
  const { data, error } = await supabase.rpc("mcp_jobs.reap_stuck_jobs", {
    p_default_timeout_minutes: 5,
  });

  if (error) {
    console.error("Failed to reap stuck jobs:", error);
    return 0;
  }

  const reaped = data?.length || 0;
  if (reaped > 0) {
    console.log(`Reaped ${reaped} stuck jobs`);
  }

  return reaped;
}

// -----------------------------------------------------------------------------
// HTTP Server
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  // Validate X-CRON-SECRET for cron-triggered requests
  const cronSecret = Deno.env.get("CRON_SECRET");
  const providedSecret = req.headers.get("x-cron-secret");

  // Allow requests with valid cron secret OR with service_role auth
  const authHeader = req.headers.get("authorization");
  const isServiceRole = authHeader?.includes(Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "");
  const isValidCron = cronSecret && providedSecret === cronSecret;

  if (!isValidCron && !isServiceRole) {
    return jsonResponse({ error: "Unauthorized: Invalid or missing X-CRON-SECRET" }, 401);
  }

  // Initialize Supabase client
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseKey);

  const workerId = generateWorkerId();
  const url = new URL(req.url);
  const path = url.pathname.split("/").pop();

  try {
    // Handle different endpoints
    if (req.method === "POST") {
      if (path === "reap") {
        // Reap stuck jobs only
        const reaped = await reapStuckJobs(supabase);
        return jsonResponse({ ok: true, reaped, timestamp: new Date().toISOString() });
      }

      // Default: process jobs
      const body = await req.json().catch(() => ({}));
      const maxJobs = body.max_jobs || 10;
      const sourceFilter = body.source_filter || null;
      const timeoutMinutes = body.timeout_minutes || 5;

      // First, reap any stuck jobs
      const reaped = await reapStuckJobs(supabase);

      // Process up to maxJobs
      const results: Array<{ jobId: string; result: ExecutionResult }> = [];
      let processed = 0;

      for (let i = 0; i < maxJobs; i++) {
        const outcome = await processNextJob(supabase, workerId, sourceFilter, timeoutMinutes);
        if (!outcome.processed) break;
        if (outcome.jobId && outcome.result) {
          results.push({ jobId: outcome.jobId, result: outcome.result });
        }
        processed++;
      }

      return jsonResponse({
        ok: true,
        worker_id: workerId,
        processed,
        reaped,
        results,
        timestamp: new Date().toISOString(),
      });
    }

    if (req.method === "GET") {
      if (path === "health") {
        // Health check
        const { count, error } = await supabase
          .from("mcp_jobs.jobs")
          .select("*", { count: "exact", head: true })
          .eq("status", "queued");

        return jsonResponse({
          ok: !error,
          queued_jobs: count || 0,
          worker_id: workerId,
          timestamp: new Date().toISOString(),
        });
      }

      if (path === "stats") {
        // Job statistics
        const { data: stats, error } = await supabase
          .from("mcp_jobs.jobs")
          .select("status")
          .gte("created_at", new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

        if (error) {
          return jsonResponse({ ok: false, error: error.message }, 500);
        }

        const statusCounts: Record<string, number> = {};
        for (const row of stats || []) {
          statusCounts[row.status] = (statusCounts[row.status] || 0) + 1;
        }

        return jsonResponse({
          ok: true,
          last_24h: statusCounts,
          timestamp: new Date().toISOString(),
        });
      }
    }

    return jsonResponse({ error: "Not Found" }, 404);
  } catch (e) {
    console.error("Executor error:", e);
    return jsonResponse(
      { ok: false, error: e instanceof Error ? e.message : String(e) },
      500
    );
  }
});
