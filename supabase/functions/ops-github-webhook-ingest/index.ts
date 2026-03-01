// ops-github-webhook-ingest
// Receives inbound GitHub App webhook events, verifies HMAC-SHA256 signature,
// normalizes the payload, and stores it in ops.webhook_events.
//
// Supported events (see spec/github-integrations/prd.md §FR-3):
//   issues, pull_request, check_run, check_suite, push, installation
//
// Failure mode: none (fail-open storage — unrecognized events stored with
//               status='unhandled'; signature failures return HTTP 401 and
//               are NOT stored)
//
// Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md
// Spec:    spec/github-integrations/prd.md

import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL      = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY  = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
// App-level webhook secret (see ssot/secrets/registry.yaml: github_app_webhook_secret)
const WEBHOOK_SECRET    = Deno.env.get("GITHUB_APP_WEBHOOK_SECRET") ?? "";

const SUPPORTED_EVENTS = new Set([
  "issues",
  "pull_request",
  "check_run",
  "check_suite",
  "push",
  "installation",
]);

// ── Signature verification ────────────────────────────────────────────────────

async function verifySignature(
  rawBody: Uint8Array,
  sigHeader: string | null,
  secret: string,
): Promise<boolean> {
  if (!sigHeader?.startsWith("sha256=")) return false;
  const expected = sigHeader.slice(7);

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

  // Timing-safe compare
  if (computed.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < computed.length; i++) {
    diff |= computed.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return diff === 0;
}

// ── Event normalizers ─────────────────────────────────────────────────────────

function normalizeIssues(payload: Record<string, unknown>) {
  const issue = payload["issue"] as Record<string, unknown> | undefined;
  const repo  = payload["repository"] as Record<string, unknown> | undefined;
  return {
    external_id:  String(issue?.["number"] ?? ""),
    title:        String(issue?.["title"] ?? ""),
    status:       String(payload["action"] ?? ""),
    source:       "github",
    metadata: {
      action:     payload["action"],
      issue_url:  issue?.["html_url"],
      repo:       repo?.["full_name"],
      assignee:   (issue?.["assignee"] as Record<string, unknown> | null)?.["login"] ?? null,
    },
  };
}

function normalizePullRequest(payload: Record<string, unknown>) {
  const pr    = payload["pull_request"] as Record<string, unknown> | undefined;
  const repo  = payload["repository"]   as Record<string, unknown> | undefined;
  return {
    external_id: String(pr?.["number"] ?? ""),
    title:       String(pr?.["title"] ?? ""),
    status:      String(payload["action"] ?? ""),
    source:      "github",
    metadata: {
      action:    payload["action"],
      pr_url:    pr?.["html_url"],
      repo:      repo?.["full_name"],
      branch:    (pr?.["head"] as Record<string, unknown> | undefined)?.["ref"],
      merged:    pr?.["merged"],
    },
  };
}

function normalizeCheckRun(payload: Record<string, unknown>) {
  const run   = payload["check_run"] as Record<string, unknown> | undefined;
  const repo  = payload["repository"] as Record<string, unknown> | undefined;
  return {
    external_id: String(run?.["id"] ?? ""),
    title:       String(run?.["name"] ?? ""),
    status:      String(run?.["conclusion"] ?? run?.["status"] ?? ""),
    source:      "github",
    metadata: {
      action:      payload["action"],
      check_name:  run?.["name"],
      conclusion:  run?.["conclusion"],
      repo:        repo?.["full_name"],
      head_sha:    run?.["head_sha"],
    },
  };
}

function normalizePush(payload: Record<string, unknown>) {
  const repo = payload["repository"] as Record<string, unknown> | undefined;
  return {
    external_id: String(payload["after"] ?? ""),
    title:       `push to ${String(payload["ref"] ?? "")}`,
    status:      "pushed",
    source:      "github",
    metadata: {
      ref:         payload["ref"],
      before:      payload["before"],
      after:       payload["after"],
      repo:        repo?.["full_name"],
      pusher:      (payload["pusher"] as Record<string, unknown> | undefined)?.["name"],
      commits:     (payload["commits"] as unknown[])?.length ?? 0,
    },
  };
}

function normalizeInstallation(payload: Record<string, unknown>) {
  const app = payload["installation"] as Record<string, unknown> | undefined;
  return {
    external_id: String(app?.["id"] ?? ""),
    title:       `installation ${String(payload["action"] ?? "")}`,
    status:      String(payload["action"] ?? ""),
    source:      "github",
    metadata: {
      action:         payload["action"],
      app_id:         app?.["app_id"],
      target_type:    app?.["target_type"],
      account:        (app?.["account"] as Record<string, unknown> | undefined)?.["login"],
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

  const eventType = req.headers.get("X-GitHub-Event") ?? "unknown";
  const deliveryId = req.headers.get("X-GitHub-Delivery") ?? crypto.randomUUID();
  const sigHeader  = req.headers.get("X-Hub-Signature-256");

  // Read raw body for signature verification
  const rawBody = new Uint8Array(await req.arrayBuffer());

  // ── Signature check ────────────────────────────────────────────────────────
  if (WEBHOOK_SECRET) {
    const valid = await verifySignature(rawBody, sigHeader, WEBHOOK_SECRET);
    if (!valid) {
      console.error(`ops-github-webhook-ingest: invalid signature delivery=${deliveryId} event=${eventType}`);
      return new Response(
        JSON.stringify({ error: "AUTH.INVALID_SIGNATURE", message: "X-Hub-Signature-256 verification failed" }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      );
    }
  } else {
    // Secret not yet provisioned — log warning but allow (facilitates initial setup)
    console.warn(`ops-github-webhook-ingest: GITHUB_APP_WEBHOOK_SECRET not set — skipping signature check delivery=${deliveryId}`);
  }

  // ── Parse payload ──────────────────────────────────────────────────────────
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(new TextDecoder().decode(rawBody));
  } catch {
    return new Response(
      JSON.stringify({ error: "invalid_payload", message: "JSON parse failed" }),
      { status: 400, headers: { "Content-Type": "application/json" } },
    );
  }

  // ── Normalize ─────────────────────────────────────────────────────────────
  let normalized: Record<string, unknown>;
  let status = "unhandled";

  if (SUPPORTED_EVENTS.has(eventType)) {
    status = "queued";
    switch (eventType) {
      case "issues":
        normalized = normalizeIssues(payload);
        break;
      case "pull_request":
        normalized = normalizePullRequest(payload);
        break;
      case "check_run":
      case "check_suite":
        normalized = normalizeCheckRun(payload);
        break;
      case "push":
        normalized = normalizePush(payload);
        break;
      case "installation":
        normalized = normalizeInstallation(payload);
        break;
      default:
        normalized = { external_id: deliveryId, title: eventType, status: "unhandled", source: "github", metadata: {} };
    }
  } else {
    normalized = {
      external_id: deliveryId,
      title: eventType,
      status: "unhandled",
      source: "github",
      metadata: { raw_event: eventType, action: payload["action"] ?? null },
    };
  }

  // ── Store ──────────────────────────────────────────────────────────────────
  const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

  const row = {
    delivery_id:  deliveryId,
    event_type:   eventType,
    source:       "github",
    status,
    external_id:  String(normalized["external_id"] ?? ""),
    title:        String(normalized["title"] ?? ""),
    metadata:     normalized["metadata"] ?? {},
    raw_payload:  payload,
    received_at:  new Date().toISOString(),
  };

  const { error: insertErr } = await supabase
    .schema("ops")
    .from("webhook_events")
    .insert(row);

  if (insertErr) {
    console.error("ops-github-webhook-ingest insert error:", insertErr.message);
    return new Response(
      JSON.stringify({ error: "storage_failed", message: insertErr.message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }

  return new Response(
    JSON.stringify({ ok: true, delivery_id: deliveryId, event_type: eventType, status }),
    { status: 200, headers: { "Content-Type": "application/json" } },
  );
});
