// ops-github-webhook-ingest
// Receives inbound GitHub App webhook events, verifies HMAC-SHA256 signature,
// normalizes the payload, and stores it in ops.webhook_events.
//
// Schema: ops.webhook_events (20260223000004 + 20260302000050)
//
// Idempotency: delivery_id unique index prevents duplicate rows.
// Signature failures: logged + HTTP 401; payload is NOT stored.
// Unhandled events: stored with status='unhandled' + reason='unknown_event'.
//
// Supported events (spec/github-integrations/prd.md §FR-3):
//   issues, pull_request, check_run, check_suite, push, installation
//
// Failure mode: none (fail-open for storage errors; 401 only on bad sig)
// Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md
// Spec:    spec/github-integrations/prd.md

import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL     = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
// App-level webhook secret (ssot/secrets/registry.yaml: github_app_webhook_secret)
const WEBHOOK_SECRET   = Deno.env.get("GITHUB_APP_WEBHOOK_SECRET") ?? "";

// Max raw payload we will process (10 MB). Beyond this we store a stub + reason.
const MAX_PAYLOAD_BYTES = 10 * 1024 * 1024;

const SUPPORTED_EVENTS = new Set([
  "issues",
  "pull_request",
  "check_run",
  "check_suite",
  "push",
  "installation",
]);

// ── Constant-time HMAC-SHA256 signature verification ─────────────────────────

async function verifySignature(
  rawBody: Uint8Array,
  sigHeader: string | null,
  secret: string,
): Promise<boolean> {
  if (!sigHeader?.startsWith("sha256=")) return false;
  const expected = sigHeader.slice(7);   // hex string after "sha256="

  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, rawBody);
  const computed = Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  // Constant-time compare — prevents timing oracle
  if (computed.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < computed.length; i++) {
    diff |= computed.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return diff === 0;
}

// ── Header capture (safe subset only) ────────────────────────────────────────

function captureHeaders(req: Request): Record<string, string> {
  const keep = [
    "x-github-event",
    "x-github-delivery",
    "x-hub-signature-256",
    "content-type",
    "user-agent",
  ];
  const out: Record<string, string> = {};
  for (const k of keep) {
    const v = req.headers.get(k);
    if (v) out[k] = v;
  }
  return out;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function str(v: unknown): string  { return typeof v === "string" ? v : (v == null ? "" : String(v)); }
function num(v: unknown): number | null {
  if (v == null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function extractCommon(payload: Record<string, unknown>) {
  const repo    = payload["repository"]   as Record<string, unknown> | null ?? {};
  const install = payload["installation"] as Record<string, unknown> | null ?? {};
  const sender  = payload["sender"]       as Record<string, unknown> | null ?? {};
  return {
    action:          str(payload["action"]) || null,
    repo_full_name:  str(repo["full_name"]) || null,
    installation_id: num(install["id"]),
    sender_login:    str(sender["login"])   || null,
  };
}

// ── Event normalizers ─────────────────────────────────────────────────────────
// Returns { status, reason, event_type } — column values that override defaults

function normalizeIssues(payload: Record<string, unknown>) {
  const issue = payload["issue"] as Record<string, unknown> | null ?? {};
  return {
    status:     "queued" as const,
    reason:     null as string | null,
    event_type: "issues",
    extra_meta: {
      issue_number: num(issue["number"]),
      issue_url:    str(issue["html_url"]) || null,
      title:        str(issue["title"]) || null,
    },
  };
}

function normalizePullRequest(payload: Record<string, unknown>) {
  const pr = payload["pull_request"] as Record<string, unknown> | null ?? {};
  return {
    status:     "queued" as const,
    reason:     null as string | null,
    event_type: "pull_request",
    extra_meta: {
      pr_number: num(pr["number"]),
      pr_url:    str(pr["html_url"]) || null,
      title:     str(pr["title"]) || null,
      branch:    str((pr["head"] as Record<string, unknown> | null)?.["ref"]) || null,
      merged:    pr["merged"] === true,
    },
  };
}

function normalizeCheckRun(payload: Record<string, unknown>) {
  const run = payload["check_run"] as Record<string, unknown> | null ?? {};
  return {
    status:     "queued" as const,
    reason:     null as string | null,
    event_type: str(payload["action"] === "check_suite" ? "check_suite" : "check_run"),
    extra_meta: {
      check_name:  str(run["name"]) || null,
      conclusion:  str(run["conclusion"]) || null,
      head_sha:    str(run["head_sha"]) || null,
    },
  };
}

function normalizePush(payload: Record<string, unknown>) {
  return {
    status:     "queued" as const,
    reason:     null as string | null,
    event_type: "push",
    extra_meta: {
      ref:     str(payload["ref"]) || null,
      before:  str(payload["before"]) || null,
      after:   str(payload["after"]) || null,
      commits: num((payload["commits"] as unknown[])?.length ?? 0),
    },
  };
}

function normalizeInstallation(payload: Record<string, unknown>) {
  return {
    status:     "queued" as const,
    reason:     null as string | null,
    event_type: "installation",
    extra_meta: {
      app_id:      num((payload["installation"] as Record<string, unknown> | null)?.["app_id"]),
      target_type: str((payload["installation"] as Record<string, unknown> | null)?.["target_type"]) || null,
    },
  };
}

// ── Main handler ──────────────────────────────────────────────────────────────

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const eventType  = req.headers.get("X-GitHub-Event") ?? "unknown";
  const deliveryId = req.headers.get("X-GitHub-Delivery") ?? crypto.randomUUID();
  const sigHeader  = req.headers.get("X-Hub-Signature-256");
  const headers    = captureHeaders(req);

  // ── Read raw body ──────────────────────────────────────────────────────────
  const buf = await req.arrayBuffer();
  const rawBody = new Uint8Array(buf);

  // ── Payload size guard ─────────────────────────────────────────────────────
  if (rawBody.byteLength > MAX_PAYLOAD_BYTES) {
    // Store a stub row so we have an audit trail, but don't try to parse
    const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);
    await supabase.schema("ops").from("webhook_events").insert({
      integration:    "github",
      event_type:     eventType,
      idempotency_key: deliveryId,
      delivery_id:    deliveryId,
      signature_valid: false,
      headers,
      payload:        { truncated: true, original_size: rawBody.byteLength },
      status:         "unhandled",
      reason:         "payload_too_large",
    });
    console.warn(`ops-github-webhook-ingest: payload_too_large delivery=${deliveryId} size=${rawBody.byteLength}`);
    return new Response(
      JSON.stringify({ error: "payload_too_large", delivery_id: deliveryId }),
      { status: 413, headers: { "Content-Type": "application/json" } },
    );
  }

  // ── Signature verification ─────────────────────────────────────────────────
  let signatureValid = false;
  if (WEBHOOK_SECRET) {
    signatureValid = await verifySignature(rawBody, sigHeader, WEBHOOK_SECRET);
    if (!signatureValid) {
      // Do NOT store rejected payloads — log only
      console.error(
        `ops-github-webhook-ingest: invalid signature delivery=${deliveryId} event=${eventType}`,
      );
      return new Response(
        JSON.stringify({
          error:       "AUTH.INVALID_SIGNATURE",
          message:     "X-Hub-Signature-256 verification failed",
          delivery_id: deliveryId,
        }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      );
    }
  } else {
    // Secret not provisioned — log warning but allow (initial setup / ping test)
    console.warn(
      `ops-github-webhook-ingest: GITHUB_APP_WEBHOOK_SECRET not set — skipping sig check delivery=${deliveryId}`,
    );
    signatureValid = false;   // record the fact that sig was not checked
  }

  // ── Parse payload ──────────────────────────────────────────────────────────
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(new TextDecoder().decode(rawBody));
  } catch {
    return new Response(
      JSON.stringify({ error: "invalid_payload", message: "JSON parse failed", delivery_id: deliveryId }),
      { status: 400, headers: { "Content-Type": "application/json" } },
    );
  }

  // ── Normalize ─────────────────────────────────────────────────────────────
  const common = extractCommon(payload);
  let norm: { status: "queued" | "unhandled"; reason: string | null; event_type: string; extra_meta: Record<string, unknown> };

  if (SUPPORTED_EVENTS.has(eventType)) {
    switch (eventType) {
      case "issues":
        norm = normalizeIssues(payload);
        break;
      case "pull_request":
        norm = normalizePullRequest(payload);
        break;
      case "check_run":
      case "check_suite":
        norm = normalizeCheckRun(payload);
        break;
      case "push":
        norm = normalizePush(payload);
        break;
      case "installation":
        norm = normalizeInstallation(payload);
        break;
      default:
        norm = { status: "unhandled", reason: "schema_mismatch", event_type: eventType, extra_meta: {} };
    }
  } else {
    const reason = payload["action"] == null ? "missing_action" : "unknown_event";
    norm = { status: "unhandled", reason, event_type: eventType, extra_meta: {} };
  }

  // ── Upsert (idempotency on delivery_id) ───────────────────────────────────
  const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

  const row = {
    integration:     "github",
    event_type:      norm.event_type,
    idempotency_key: deliveryId,   // existing unique index: (integration, idempotency_key)
    delivery_id:     deliveryId,   // new column with dedicated unique index
    signature_valid: signatureValid,
    received_at:     new Date().toISOString(),
    headers,
    payload,
    status:          norm.status,
    reason:          norm.reason,
    action:          common.action,
    repo_full_name:  common.repo_full_name,
    installation_id: common.installation_id,
    sender_login:    common.sender_login,
  };

  const { error: insertErr } = await supabase
    .schema("ops")
    .from("webhook_events")
    .upsert(row, {
      onConflict:        "integration,idempotency_key",
      ignoreDuplicates:  true,   // replay: keep first, discard re-deliveries silently
    });

  if (insertErr) {
    console.error("ops-github-webhook-ingest insert error:", insertErr.message);
    return new Response(
      JSON.stringify({ error: "storage_failed", message: insertErr.message, delivery_id: deliveryId }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }

  return new Response(
    JSON.stringify({
      ok:          true,
      delivery_id: deliveryId,
      event_type:  norm.event_type,
      action:      common.action,
      status:      norm.status,
      ...(norm.reason ? { reason: norm.reason } : {}),
    }),
    { status: 200, headers: { "Content-Type": "application/json" } },
  );
});
