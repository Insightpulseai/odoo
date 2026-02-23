/**
 * email-dispatcher/index.ts
 * Supabase Edge Function — Email notification dispatcher
 *
 * Claim → Render template → Send via zoho-mail-bridge → Mark done/fail
 * Pattern mirrors jobs-worker/index.ts (claim/dispatch/mark loop).
 *
 * Queue: ops.email_notification_events
 * Delivery: zoho-mail-bridge?action=send_email
 * Triggered by: tick/index.ts (fire-and-forget, every tick cycle)
 *
 * Required Edge Function secrets:
 *   BRIDGE_SHARED_SECRET  — shared secret for zoho-mail-bridge x-bridge-secret header
 *   ZOHO_FROM_EMAIL       — sender address e.g. noreply@insightpulseai.com
 *   SUPABASE_URL          — auto-injected by Supabase runtime
 *   SUPABASE_SERVICE_ROLE_KEY — auto-injected by Supabase runtime
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const BRIDGE_SECRET = Deno.env.get("BRIDGE_SHARED_SECRET") ?? "";
const FROM_EMAIL = Deno.env.get("ZOHO_FROM_EMAIL") ?? "noreply@insightpulseai.com";
const BATCH_SIZE = 10;
const MAX_ATTEMPTS = 3;

// Edge Function URL resolver — matches tick/index.ts pattern
const mailBridgeUrl =
  `${SUPABASE_URL.replace(".supabase.co", ".functions.supabase.co")}/functions/v1/zoho-mail-bridge?action=send_email`;

const sb = createClient(SUPABASE_URL, SERVICE_ROLE);

// Exponential backoff: attempt 1 → 5 min, attempt 2 → 30 min, attempt ≥3 → dead
function backoffMinutes(attempt: number): number | null {
  if (attempt === 1) return 5;
  if (attempt === 2) return 30;
  return null; // → dead
}

// ── Template renderer ───────────────────────────────────────────────────────
// v1 templates: task_assigned, task_stage_changed
// payload is the inner task payload from ops.email_notification_events.payload

interface RenderResult {
  subject: string;
  htmlBody: string;
}

function renderTemplate(
  template: string,
  payload: Record<string, unknown>,
): RenderResult {
  const taskName = String(payload.task_name ?? "Unknown task");
  const projectName = String(payload.project_name ?? "Finance PPM");
  const stage = String(payload.new_stage ?? payload.status ?? "");

  switch (template) {
    case "task_assigned":
      return {
        subject: `Task assigned: ${taskName}`,
        htmlBody: `
<p>Hello,</p>
<p>You have been assigned to task <strong>${taskName}</strong>
in project <em>${projectName}</em>.</p>
<p>Please log in to Odoo to review and action this task.</p>
<p style="font-size:11px;color:#888">
  This is an automated notification from InsightPulse AI Finance PPM.
</p>`.trim(),
      };

    case "task_stage_changed":
      return {
        subject: `Task updated: ${taskName} → ${stage}`,
        htmlBody: `
<p>Hello,</p>
<p>Task <strong>${taskName}</strong> in project <em>${projectName}</em>
has been moved to stage <strong>${stage}</strong>.</p>
<p>Please log in to Odoo to review the updated task.</p>
<p style="font-size:11px;color:#888">
  This is an automated notification from InsightPulse AI Finance PPM.
</p>`.trim(),
      };

    default:
      throw new Error(`Unknown email template: ${template}`);
  }
}

// ── Mark helpers ─────────────────────────────────────────────────────────────

async function markSent(notificationId: number): Promise<void> {
  await sb
    .from("email_notification_events")
    .update({ status: "sent", completed_at: new Date().toISOString() })
    .eq("id", notificationId);
}

async function markFailed(
  notificationId: number,
  attempt: number,
  error: string,
): Promise<void> {
  const backoff = backoffMinutes(attempt);
  const nextStatus = backoff === null || attempt >= MAX_ATTEMPTS ? "dead" : "failed";
  const nextAttemptAt = backoff
    ? new Date(Date.now() + backoff * 60_000).toISOString()
    : null;

  await sb.from("email_notification_events").update({
    status: nextStatus,
    attempts: attempt,
    error,
    ...(nextAttemptAt ? { next_attempt_at: nextAttemptAt } : {}),
  }).eq("id", notificationId);
}

async function recordDelivery(
  notificationId: number,
  attempt: number,
  status: "sent" | "failed",
  error?: string,
): Promise<void> {
  await sb.from("email_deliveries").insert({
    notification_id: notificationId,
    provider: "zoho",
    attempt_number: attempt,
    status,
    ...(error ? { error } : {}),
  });
}

// ── Main handler ─────────────────────────────────────────────────────────────

serve(async () => {
  if (!BRIDGE_SECRET) {
    console.error("[email-dispatcher] BRIDGE_SHARED_SECRET not set — skipping dispatch");
    return new Response(
      JSON.stringify({ error: "BRIDGE_SHARED_SECRET not configured" }),
      { status: 503 },
    );
  }

  // 1. Claim a batch atomically
  const { data: notifications, error: claimErr } = await sb.rpc(
    "claim_email_notifications",
    { p_batch: BATCH_SIZE },
  );

  if (claimErr) {
    console.error("[email-dispatcher] claim RPC error:", claimErr.message);
    return new Response(JSON.stringify({ error: claimErr.message }), { status: 500 });
  }

  if (!notifications?.length) {
    return new Response(JSON.stringify({ claimed: 0, sent: 0, failed: 0 }), {
      status: 200,
    });
  }

  let sent = 0;
  let failed = 0;

  for (const n of notifications) {
    const attempt = (n.attempts ?? 0) + 1;

    try {
      // 2. Render email template
      const { subject, htmlBody } = renderTemplate(n.template, n.payload ?? {});

      // 3. Send via zoho-mail-bridge
      const bridgeRes = await fetch(mailBridgeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-bridge-secret": BRIDGE_SECRET,
        },
        body: JSON.stringify({
          from: FROM_EMAIL,
          to: n.recipient_email,
          subject,
          htmlBody,
        }),
      });

      if (!bridgeRes.ok) {
        const errText = await bridgeRes.text();
        throw new Error(`zoho-mail-bridge ${bridgeRes.status}: ${errText}`);
      }

      // 4. Mark notification sent
      await markSent(n.id);
      await recordDelivery(n.id, attempt, "sent");
      sent++;
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      console.error(`[email-dispatcher] notification ${n.id} attempt ${attempt} failed:`, errMsg);
      await markFailed(n.id, attempt, errMsg);
      await recordDelivery(n.id, attempt, "failed", errMsg);
      failed++;
    }
  }

  console.log(
    `[email-dispatcher] claimed=${notifications.length} sent=${sent} failed=${failed}`,
  );

  return new Response(
    JSON.stringify({ claimed: notifications.length, sent, failed }),
    { status: 200 },
  );
});
