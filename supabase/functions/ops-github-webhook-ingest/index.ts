// ops-github-webhook-ingest
// Single webhook ingress for all GitHub App events (ipai-integrations App).
//
// Pipeline:
//   GitHub webhook → verify HMAC-SHA256 → write ops.github_webhook_deliveries
//                                       → upsert ops.work_items (issues/PRs)
//                                       → enqueue ops.work_queue
//                                       → best-effort fan-out: n8n + Plane API
//
// Schema (20260301000065_ops_workitems_webhooks.sql):
//   ops.github_webhook_deliveries — delivery ledger (dedupe by delivery_id PK)
//   ops.work_items                — canonical work item upsert (by work_item_ref)
//   ops.work_queue                — async processor queue
//
// SSOT: ssot/integrations/github_apps.yaml
// Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md
// Spec:    spec/github-integrations/prd.md

import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL     = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const WEBHOOK_SECRET   = Deno.env.get("GITHUB_APP_WEBHOOK_SECRET") ?? "";

// Fan-out targets (best-effort; delivery ledger is durable regardless)
const N8N_WEBHOOK_URL  = Deno.env.get("N8N_WEBHOOK_GITHUB_URL") ?? "";
const N8N_FANOUT_SECRET= Deno.env.get("N8N_WEBHOOK_SECRET") ?? "";
const PLANE_API_BASE   = Deno.env.get("PLANE_API_BASE_URL") ?? "";
const PLANE_API_KEY    = Deno.env.get("PLANE_API_KEY") ?? "";

const MAX_PAYLOAD_BYTES = 10 * 1024 * 1024;

// ── HMAC-SHA256 ───────────────────────────────────────────────────────────────

async function hmacHex(secret: string, body: Uint8Array): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, body);
  return Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function verifySignature(body: Uint8Array, sigHeader: string | null, secret: string): Promise<boolean> {
  if (!sigHeader?.startsWith("sha256=")) return false;
  const expected = sigHeader.slice(7);
  const computed = await hmacHex(secret, body);
  if (computed.length !== expected.length) return false;
  // Constant-time compare
  let diff = 0;
  for (let i = 0; i < computed.length; i++) {
    diff |= computed.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return diff === 0;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function str(v: unknown): string { return typeof v === "string" ? v : (v == null ? "" : String(v)); }
function num(v: unknown): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

// ── Work-item normalizer ──────────────────────────────────────────────────────
// Maps GitHub issue/PR payload → ops.work_items columns.

function normalizeWorkItem(
  eventType: string,
  payload: Record<string, unknown>,
  repoFullName: string,
): {
  work_item_ref: string;
  external_id: string;
  title: string;
  status: string;
  url: string | null;
  assignee: string | null;
} | null {
  const issue = payload["issue"] as Record<string, unknown> | null;
  const pr    = payload["pull_request"] as Record<string, unknown> | null;
  const src   = issue ?? pr;
  if (!src) return null;

  const number = num(src["number"]);
  if (!number) return null;

  const prefix = pr ? "pr" : "iss";
  const action  = str(payload["action"]);

  // Map GitHub state/action → our status vocabulary
  const rawState = str(src["state"] || "");
  const merged   = pr && payload["pull_request"] != null && (pr["merged"] === true);
  const status   =
    merged                  ? "merged" :
    action === "closed"     ? "closed" :
    rawState === "closed"   ? "closed" :
    "open";

  const login = (src["assignee"] as Record<string, unknown> | null)?.["login"];

  return {
    work_item_ref: `github:${repoFullName}#${number}`,
    external_id:   `${prefix}_${number}`,
    title:         str(src["title"]) || `${eventType} #${number}`,
    status,
    url:           str(src["html_url"]) || null,
    assignee:      login ? str(login) : null,
  };
}

// ── Fan-out helpers ───────────────────────────────────────────────────────────

async function fanOutN8N(raw: Uint8Array, eventType: string, deliveryId: string) {
  if (!N8N_WEBHOOK_URL) return;
  const headers: Record<string, string> = {
    "Content-Type":      "application/json",
    "X-GitHub-Event":    eventType,
    "X-GitHub-Delivery": deliveryId,
  };
  if (N8N_FANOUT_SECRET) {
    headers["X-IPAI-Signature"] = `sha256=${await hmacHex(N8N_FANOUT_SECRET, raw)}`;
  }
  await fetch(N8N_WEBHOOK_URL, { method: "POST", headers, body: raw }).catch((e) =>
    console.warn(`n8n fan-out failed delivery=${deliveryId}:`, e?.message),
  );
}

async function fanOutPlane(
  workItem: { work_item_ref: string; title: string; url: string | null },
) {
  if (!PLANE_API_BASE || !PLANE_API_KEY) return;
  await fetch(`${PLANE_API_BASE}/integrations/external-items/upsert`, {
    method: "POST",
    headers: {
      "Content-Type":  "application/json",
      "Authorization": `Bearer ${PLANE_API_KEY}`,
    },
    body: JSON.stringify({
      external_id:      workItem.work_item_ref,
      title:            workItem.title,
      description_html: workItem.url ? `<p><a href="${workItem.url}">${workItem.url}</a></p>` : undefined,
    }),
  }).catch((e) =>
    console.warn(`Plane fan-out failed ref=${workItem.work_item_ref}:`, e?.message),
  );
}

// ── Main handler ──────────────────────────────────────────────────────────────

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405, headers: { "Content-Type": "application/json" },
    });
  }

  const eventType  = req.headers.get("X-GitHub-Event") ?? "unknown";
  const deliveryId = req.headers.get("X-GitHub-Delivery") ?? crypto.randomUUID();
  const sigHeader  = req.headers.get("X-Hub-Signature-256");

  const buf = await req.arrayBuffer();
  const raw = new Uint8Array(buf);

  // ── Size guard ─────────────────────────────────────────────────────────────
  if (raw.byteLength > MAX_PAYLOAD_BYTES) {
    console.warn(`payload_too_large delivery=${deliveryId} size=${raw.byteLength}`);
    return new Response(
      JSON.stringify({ error: "payload_too_large", delivery_id: deliveryId }),
      { status: 413, headers: { "Content-Type": "application/json" } },
    );
  }

  // ── Signature verification ─────────────────────────────────────────────────
  if (WEBHOOK_SECRET) {
    const valid = await verifySignature(raw, sigHeader, WEBHOOK_SECRET);
    if (!valid) {
      console.error(`bad_signature delivery=${deliveryId} event=${eventType}`);
      return new Response(
        JSON.stringify({ error: "AUTH.INVALID_SIGNATURE", delivery_id: deliveryId }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      );
    }
  } else {
    console.warn(`no_webhook_secret — sig check skipped delivery=${deliveryId}`);
  }

  // ── Parse payload ──────────────────────────────────────────────────────────
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(new TextDecoder().decode(raw));
  } catch {
    return new Response(
      JSON.stringify({ error: "invalid_payload", delivery_id: deliveryId }),
      { status: 400, headers: { "Content-Type": "application/json" } },
    );
  }

  const action       = str(payload["action"]) || null;
  const repo         = (payload["repository"] as Record<string, unknown> | null);
  const repoFullName = str(repo?.["full_name"]) || "unknown/unknown";

  const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

  // ── 1. Delivery ledger (durable; dedupe by PK delivery_id) ────────────────
  const { error: delivErr } = await supabase
    .schema("ops")
    .from("github_webhook_deliveries")
    .insert({
      delivery_id: deliveryId,
      event_type:  eventType,
      payload,
      status:      "received",
    })
    .on("conflict", "delivery_id", { ignoreDuplicates: true } as never);

  if (delivErr && !delivErr.message.includes("duplicate")) {
    console.error("delivery insert error:", delivErr.message);
  }

  // ── 2. Work-item upsert (issues + PRs only) ───────────────────────────────
  let workItemRef: string | null = null;

  if (eventType === "issues" || eventType === "pull_request") {
    const wi = normalizeWorkItem(eventType, payload, repoFullName);
    if (wi) {
      const { error: wiErr } = await supabase
        .schema("ops")
        .from("work_items")
        .upsert(
          {
            work_item_ref: wi.work_item_ref,
            system:        "github",
            external_id:   wi.external_id,
            project_ref:   repoFullName,
            title:         wi.title,
            status:        wi.status,
            url:           wi.url,
            assignee:      wi.assignee,
            updated_at:    new Date().toISOString(),
          },
          { onConflict: "work_item_ref" },
        );
      if (wiErr) {
        console.error("work_item upsert error:", wiErr.message);
      } else {
        workItemRef = wi.work_item_ref;
        // Fan out to Plane (async, best-effort)
        fanOutPlane(wi).catch(() => {});
      }
    }
  }

  // ── 3. Work queue (async processing trigger) ──────────────────────────────
  const { error: qErr } = await supabase
    .schema("ops")
    .from("work_queue")
    .insert({
      source:      "github",
      delivery_id: deliveryId,
      status:      "queued",
    });
  if (qErr) console.warn("work_queue insert error:", qErr.message);

  // ── 4. n8n fan-out (async, best-effort, all events) ──────────────────────
  fanOutN8N(raw, eventType, deliveryId).catch(() => {});

  // ── 5. Update delivery status ─────────────────────────────────────────────
  await supabase
    .schema("ops")
    .from("github_webhook_deliveries")
    .update({ status: "processed" })
    .eq("delivery_id", deliveryId)
    .catch(() => {});

  return new Response(
    JSON.stringify({
      ok:           true,
      delivery_id:  deliveryId,
      event_type:   eventType,
      action,
      repo:         repoFullName,
      work_item_ref: workItemRef,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } },
  );
});
