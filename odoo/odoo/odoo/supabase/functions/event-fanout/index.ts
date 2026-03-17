/**
 * EVENT-FANOUT Edge Function
 *
 * Claims events from integration.outbox, resolves routing handlers via
 * ops.resolve_routes(), and dispatches to Slack / n8n / other handlers.
 *
 * Triggered by: pg_cron (every 30s) or direct POST invocation.
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SLACK_BOT_TOKEN,
 *       N8N_WEBHOOK_EVENT_URL, N8N_WEBHOOK_SECRET
 */
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const BATCH_SIZE = 25;

async function hmacSha256(secret: string, msg: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

interface OutboxEvent {
  id: string;
  source: string;
  event_type: string;
  aggregate_type: string;
  aggregate_id: string;
  payload: Record<string, unknown>;
  correlation_id: string | null;
}

interface Route {
  handler: string;
  handler_url: string | null;
  priority: number;
  config: Record<string, unknown>;
}

// --- Slack Block Kit message builder ---
function buildSlackNotifyBlocks(ev: OutboxEvent): Record<string, unknown> {
  const emoji =
    ev.event_type.includes("approved") ? ":white_check_mark:" :
    ev.event_type.includes("rejected") ? ":x:" :
    ev.event_type.includes("failed") ? ":rotating_light:" :
    ev.event_type.includes("submitted") ? ":inbox_tray:" :
    ":bell:";

  return {
    text: `${emoji} ${ev.event_type} — ${ev.aggregate_type}#${ev.aggregate_id}`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `${emoji} *${ev.event_type}*\n>${ev.aggregate_type} \`${ev.aggregate_id}\``,
        },
      },
      {
        type: "context",
        elements: [
          { type: "mrkdwn", text: `Source: \`${ev.source}\`` },
          ...(ev.correlation_id
            ? [{ type: "mrkdwn", text: `CID: \`${ev.correlation_id.slice(0, 8)}\`` }]
            : []),
        ],
      },
    ],
  };
}

function buildSlackApprovalBlocks(ev: OutboxEvent): Record<string, unknown> {
  const valuePayload = JSON.stringify({
    aggregate_type: ev.aggregate_type,
    aggregate_id: ev.aggregate_id,
    correlation_id: ev.correlation_id,
    event_type: ev.event_type,
  });

  const p = ev.payload as Record<string, unknown>;
  const amount = p.amount ? ` — ${p.currency ?? "PHP"} ${p.amount}` : "";
  const who = (p.employee_name as string) || (p.name as string) || ev.aggregate_id;

  return {
    text: `Approval required: ${ev.event_type}${amount}`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `:raised_hand: *Approval Required*\n*${ev.event_type}* from ${who}${amount}`,
        },
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: { type: "plain_text", text: "Approve" },
            style: "primary",
            action_id: "approval_approve",
            value: valuePayload,
          },
          {
            type: "button",
            text: { type: "plain_text", text: "Reject" },
            style: "danger",
            action_id: "approval_reject",
            value: valuePayload,
          },
        ],
      },
      {
        type: "context",
        elements: [
          { type: "mrkdwn", text: `Source: \`${ev.source}\` | CID: \`${(ev.correlation_id ?? "n/a").slice(0, 8)}\`` },
        ],
      },
    ],
  };
}

// --- Dispatch handlers ---
async function dispatchSlackNotify(
  ev: OutboxEvent,
  route: Route,
  slackToken: string,
  channel: string,
): Promise<void> {
  const body = { channel, ...buildSlackNotifyBlocks(ev) };
  const resp = await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${slackToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Slack notify failed: ${resp.status}`);
  const data = await resp.json() as Record<string, unknown>;
  if (!data.ok) throw new Error(`Slack API error: ${data.error}`);
}

async function dispatchSlackApproval(
  ev: OutboxEvent,
  route: Route,
  slackToken: string,
  channel: string,
): Promise<void> {
  const body = { channel, ...buildSlackApprovalBlocks(ev) };
  const resp = await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${slackToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Slack approval failed: ${resp.status}`);
  const data = await resp.json() as Record<string, unknown>;
  if (!data.ok) throw new Error(`Slack API error: ${data.error}`);
}

async function dispatchN8nEvent(
  ev: OutboxEvent,
  route: Route,
  n8nUrl: string,
  n8nSecret: string,
): Promise<void> {
  const payload = JSON.stringify({
    event_type: ev.event_type,
    aggregate_type: ev.aggregate_type,
    aggregate_id: ev.aggregate_id,
    payload: ev.payload,
    correlation_id: ev.correlation_id,
    source: ev.source,
  });
  const sig = await hmacSha256(n8nSecret, payload);
  const url = route.handler_url || n8nUrl;

  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-n8n-signature": sig,
      "x-correlation-id": ev.correlation_id ?? "",
    },
    body: payload,
  });
  if (!resp.ok) throw new Error(`n8n dispatch failed: ${resp.status}`);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204 });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const slackToken = Deno.env.get("SLACK_BOT_TOKEN") ?? "";
  const slackChannel = Deno.env.get("SLACK_EVENTS_CHANNEL") ?? "#ops-events";
  const n8nUrl = Deno.env.get("N8N_WEBHOOK_EVENT_URL") ?? "";
  const n8nSecret = Deno.env.get("N8N_WEBHOOK_SECRET") ?? "";

  const sb = createClient(supabaseUrl, serviceKey);

  // Claim batch from outbox
  const { data: events, error: claimErr } = await sb.rpc("claim_outbox", {
    p_limit: BATCH_SIZE,
    p_worker: "event-fanout",
  });

  if (claimErr) {
    return new Response(JSON.stringify({ error: claimErr.message }), {
      status: 500,
      headers: { "content-type": "application/json" },
    });
  }

  if (!events || events.length === 0) {
    return new Response(JSON.stringify({ ok: true, processed: 0 }), {
      headers: { "content-type": "application/json" },
    });
  }

  let processed = 0;
  let failed = 0;

  for (const ev of events as OutboxEvent[]) {
    try {
      // Resolve routes for this event type
      const { data: routes, error: routeErr } = await sb.rpc("resolve_routes", {
        p_event_type: ev.event_type,
      });

      if (routeErr || !routes || routes.length === 0) {
        // No routes — ack as done (audit-only event)
        await sb.rpc("ack_outbox", { p_id: ev.id });
        processed++;
        continue;
      }

      // Dispatch to each handler
      for (const route of routes as Route[]) {
        switch (route.handler) {
          case "slack-notify":
            if (slackToken) {
              await dispatchSlackNotify(ev, route, slackToken, slackChannel);
            }
            break;
          case "slack-approval":
            if (slackToken) {
              const approvalChannel = (route.config as Record<string, string>).channel || slackChannel;
              await dispatchSlackApproval(ev, route, slackToken, approvalChannel);
            }
            break;
          case "n8n-event-router":
            if (n8nUrl && n8nSecret) {
              await dispatchN8nEvent(ev, route, n8nUrl, n8nSecret);
            }
            break;
          default:
            console.warn(`[event-fanout] Unknown handler: ${route.handler}`);
        }
      }

      // All handlers succeeded — ack
      await sb.rpc("ack_outbox", { p_id: ev.id });
      processed++;
    } catch (err) {
      // Handler failed — fail_outbox for retry
      const msg = err instanceof Error ? err.message : String(err);
      await sb.rpc("fail_outbox", { p_id: ev.id, p_error: msg });
      failed++;
      console.error(`[event-fanout] Failed ${ev.event_type} ${ev.id}: ${msg}`);
    }
  }

  return new Response(
    JSON.stringify({ ok: true, processed, failed, total: events.length }),
    { headers: { "content-type": "application/json" } },
  );
});
