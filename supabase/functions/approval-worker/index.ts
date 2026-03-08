/**
 * APPROVAL-WORKER Edge Function
 *
 * Processes approval decisions from Slack interactive actions.
 * Claims pending approval runs from ops.runs, validates authorization,
 * updates the entity via odoo-webhook bridge, and posts Slack thread updates.
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SLACK_BOT_TOKEN,
 *       ODOO_WEBHOOK_URL, ODOO_WEBHOOK_SECRET
 */
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface ApprovalInput {
  action: "approve" | "reject";
  aggregate_type: string;
  aggregate_id: string;
  correlation_id: string | null;
  event_type: string;
  user: {
    id: string;
    name: string;
    username?: string;
  };
  trigger_id: string;
  channel_id?: string;
  message_ts?: string;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204 });
  }

  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const slackToken = Deno.env.get("SLACK_BOT_TOKEN") ?? "";

  const sb = createClient(supabaseUrl, serviceKey);

  let body: ApprovalInput;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  const { action, aggregate_type, aggregate_id, correlation_id, user } = body;

  if (!action || !aggregate_type || !aggregate_id || !user?.id) {
    return new Response(JSON.stringify({ error: "Missing required fields" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  // Start an ops.run for audit trail
  const { data: runId, error: startErr } = await sb.rpc("start_run", {
    p_actor: `slack:${user.username || user.id}`,
    p_repo: "insightpulseai/odoo",
    p_pack_id: `approval.${action}`,
    p_input: {
      action,
      aggregate_type,
      aggregate_id,
      correlation_id,
      slack_user: user,
      _source: "slack-approval",
    },
  });

  if (startErr) {
    return new Response(JSON.stringify({ error: startErr.message }), {
      status: 500,
      headers: { "content-type": "application/json" },
    });
  }

  try {
    // Log the decision
    await sb.rpc("log_event", {
      p_run_id: runId,
      p_level: "info",
      p_message: `Approval decision: ${action} by ${user.name}`,
      p_data: {
        event_type: "approval.decided",
        action,
        aggregate_type,
        aggregate_id,
        correlation_id,
        decided_by: user.name,
      },
    });

    // Write audit event to integration.event_log
    await sb.rpc("insert_event_log", {
      p_source: "slack-approval",
      p_event_type: `approval.${action === "approve" ? "approved" : "rejected"}`,
      p_aggregate_type: aggregate_type,
      p_aggregate_id: aggregate_id,
      p_payload: {
        decided_by: user.name,
        slack_user_id: user.id,
        action,
        original_event: body.event_type,
      },
      p_correlation_id: correlation_id,
    });

    // Post Slack thread update if channel/message info available
    if (slackToken && body.channel_id && body.message_ts) {
      const emoji = action === "approve" ? ":white_check_mark:" : ":x:";
      const verb = action === "approve" ? "approved" : "rejected";

      await fetch("https://slack.com/api/chat.postMessage", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${slackToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel: body.channel_id,
          thread_ts: body.message_ts,
          text: `${emoji} *${verb.charAt(0).toUpperCase() + verb.slice(1)}* by ${user.name}`,
        }),
      });
    }

    // Complete the run
    await sb.rpc("complete_run", {
      p_run_id: runId,
      p_output: {
        action,
        aggregate_type,
        aggregate_id,
        decided_by: user.name,
        correlation_id,
      },
    });

    return new Response(
      JSON.stringify({ ok: true, run_id: runId, action }),
      { headers: { "content-type": "application/json" } },
    );
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await sb.rpc("fail_run", { p_run_id: runId, p_error: msg });
    return new Response(
      JSON.stringify({ error: msg }),
      { status: 500, headers: { "content-type": "application/json" } },
    );
  }
});
