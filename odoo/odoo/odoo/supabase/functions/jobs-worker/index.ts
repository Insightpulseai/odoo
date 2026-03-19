import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const sb = createClient(SUPABASE_URL, SERVICE_ROLE);

const WORKER_ID = Deno.env.get("WORKER_ID") || `worker-${crypto.randomUUID()}`;

const STRIPE_API_KEY = Deno.env.get("STRIPE_API_KEY") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const VERCEL_TOKEN = Deno.env.get("VERCEL_TOKEN") ?? "";

// --- job claim via Atomic SQL RPC ---
async function claimJob() {
  const { data: claimed, error } = await sb.rpc("claim_jobs", {
    p_worker_id: WORKER_ID,
    p_limit: 1,
  });
  if (error) {
    console.error("claim RPC error:", error);
    return null;
  }
  return claimed?.[0] ?? null;
}

async function done(jobId: number, webhookId?: number) {
  await sb
    .from("ops.jobs")
    .update({ status: "done", last_error: null })
    .eq("id", jobId);
  if (webhookId) {
    await sb
      .from("ops.webhook_events")
      .update({ status: "processed", processed_at: new Date().toISOString() })
      .eq("id", webhookId);
  }
}

async function fail(job: any, err: string) {
  const dead = job.attempts + 1 >= job.max_attempts;
  await sb
    .from("ops.jobs")
    .update({
      status: dead ? "dead" : "queued",
      locked_at: null,
      locked_by: null,
      last_error: err,
      run_after: new Date(
        Date.now() + Math.min(60_000, 2 ** job.attempts * 1000),
      ).toISOString(),
    })
    .eq("id", job.id);

  await sb
    .from("ops.integrations")
    .update({
      last_error_at: new Date().toISOString(),
      error_count: (job.attempts || 0) + 1,
    })
    .eq("name", job.integration);
}

// --- integration handlers ---

async function handleVercel(job: any) {
  const p = job.payload?.payload ?? job.payload;
  const deployment = p?.deployment ?? p;

  let url = deployment?.url ?? deployment?.deployment?.url ?? null;
  let status = deployment?.state ?? deployment?.status ?? null;
  let projectId = deployment?.projectId ?? deployment?.project?.id ?? null;
  let providerId = deployment?.id ?? null;

  if (VERCEL_TOKEN && providerId && !url) {
    const r = await fetch(
      `https://api.vercel.com/v13/deployments/${providerId}`,
      {
        headers: { Authorization: `Bearer ${VERCEL_TOKEN}` },
      },
    );
    if (r.ok) {
      const d = await r.json();
      url = d?.url ?? url;
      status = d?.readyState ?? status;
      projectId = d?.projectId ?? projectId;
    }
  }

  await sb.from("ops.deployments").insert({
    provider: "vercel",
    provider_id: providerId,
    project_id: projectId,
    env: p?.target ?? p?.environment ?? null,
    url,
    status,
    raw_event_id: job.payload?.webhook_event_id ?? null,
  });
}

async function handleStripe(job: any) {
  const p = job.payload?.payload ?? job.payload;
  const evtType = job.job_type;
  const evtId = p?.id ?? null;

  const obj = p?.data?.object ?? {};
  const amount = obj?.amount_paid ?? obj?.amount_total ?? obj?.amount ?? null;
  const currency = obj?.currency ?? null;
  const customer = obj?.customer ?? null;

  await sb.from("ops.billing_events").insert({
    provider: "stripe",
    provider_id: evtId,
    customer_id: customer ? String(customer) : null,
    event_type: evtType,
    amount: typeof amount === "number" ? amount : null,
    currency: currency ? String(currency) : null,
    raw_event_id: job.payload?.webhook_event_id ?? null,
  });
}

async function handleResend(job: any) {
  const p = job.payload?.payload ?? job.payload;

  if (job.job_type === "email.send") {
    if (!RESEND_API_KEY) throw new Error("RESEND_API_KEY not set");
    const { to, subject, html, from } = p;
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from, to, subject, html }),
    });
    const out = await r.json();
    if (!r.ok) throw new Error(`Resend send failed: ${JSON.stringify(out)}`);

    await sb.from("ops.email_events").insert({
      provider: "resend",
      provider_id: out?.id ?? null,
      to_email: Array.isArray(to) ? to[0] : to,
      template: p?.template ?? null,
      status: "sent",
      raw_event_id: job.payload?.webhook_event_id ?? null,
    });
    return;
  }

  await sb.from("ops.email_events").insert({
    provider: "resend",
    provider_id: p?.id ?? null,
    to_email: p?.to ?? null,
    template: p?.template ?? null,
    status: job.job_type,
    raw_event_id: job.payload?.webhook_event_id ?? null,
  });
}

async function handleN8n(job: any) {
  console.log(`[n8n] Processed job ${job.id}`);
}

async function handleCloudflare(job: any) {
  console.log(`[cloudflare] Processed worker callback ${job.id}`);
}

async function dispatch(job: any) {
  const integration = (job.integration || "").toLowerCase();

  switch (integration) {
    case "vercel":
      return handleVercel(job);
    case "stripe":
      return handleStripe(job);
    case "resend":
      return handleResend(job);
    case "n8n":
      return handleN8n(job);
    case "cloudflare":
      return handleCloudflare(job);
    default:
      throw new Error(`Unknown integration ${integration}`);
  }
}

serve(async () => {
  const job = await claimJob();
  if (!job) return new Response("no jobs", { status: 200 });

  try {
    await dispatch(job);
    await done(job.id, job.payload?.webhook_event_id);
    return new Response(JSON.stringify({ status: "ok", processed: job.id }), {
      status: 200,
    });
  } catch (e: any) {
    await fail(job, String(e?.message || e));
    return new Response(
      JSON.stringify({ status: "retry", error: String(e?.message || e) }),
      { status: 500 },
    );
  }
});
