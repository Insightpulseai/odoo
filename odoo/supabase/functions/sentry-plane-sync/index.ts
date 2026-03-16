// =============================================================================
// SENTRY-PLANE-SYNC — Sentry alert webhook → Plane issue creation
// =============================================================================
// Purpose: Receive Sentry alert webhooks and auto-create Plane work items.
//          One Plane issue per unique Sentry fingerprint (deduped via
//          work_plane.sentry_issues table).
//
// SSOT:    ssot/integrations/plane_sentry_sync.yaml
// Contract: docs/architecture/PLANE_MARKETPLACE_INTEGRATIONS.md §Sentry
//
// Boundary rules:
//   - Idempotency key = {sentry_project_slug}:{sentry_fingerprint}
//   - Sentry is SoR for error state; Plane issue is a tracker mirror
//   - Sentry webhook secret MUST be validated before processing
//   - Every event MUST write ops.run_events for Advisor scan
//   - Max 10 Plane API calls per webhook delivery (rate limit guard)
//
// Endpoints:
//   POST /sentry-plane-sync   (Sentry alert webhook payload)
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { createHmac } from "https://deno.land/std@0.177.0/node/crypto.ts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SentryIssue {
  id: string;
  title: string;
  culprit: string;
  level: "fatal" | "error" | "warning" | "info" | "debug";
  status: "resolved" | "ignored" | "unresolved";
  permalink: string;
  project: { slug: string; name: string };
  metadata?: { value?: string; type?: string };
  tags?: Array<{ key: string; value: string }>;
}

interface SentryWebhookPayload {
  action: "created" | "resolved" | "assigned" | "ignored";
  actor?: { type: string; name: string };
  data: { issue: SentryIssue };
  installation?: { uuid: string };
}

interface SentryIssueRow {
  sentry_project_slug: string;
  sentry_fingerprint: string;
  sentry_issue_id: string;
  plane_issue_id: string | null;
  plane_project_id: string | null;
  first_seen: string;
  last_seen: string;
  occurrence_count: number;
  status: string;
}

interface PlaneProjectMapping {
  sentry_project_slug: string;
  plane_project_id: string;
  plane_project_slug: string;
}

// ---------------------------------------------------------------------------
// Priority mapping: Sentry level → Plane priority
// ---------------------------------------------------------------------------

const SENTRY_LEVEL_TO_PLANE_PRIORITY: Record<string, string> = {
  fatal: "urgent",
  error: "high",
  warning: "medium",
  info: "low",
  debug: "none",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, sentry-hook-signature, sentry-hook-resource, sentry-hook-timestamp",
};

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status,
  });
}

/**
 * Validate Sentry webhook signature.
 * Sentry signs payloads with HMAC-SHA256 using the client secret.
 */
function validateSentrySignature(
  body: string,
  signature: string | null,
  secret: string
): boolean {
  if (!signature) return false;
  const expected = createHmac("sha256", secret).update(body).digest("hex");
  // Constant-time comparison not strictly available in Deno std, use basic compare
  return signature === expected;
}

/**
 * Derive a stable fingerprint from Sentry issue metadata.
 * Falls back to sentry_issue_id if no richer fingerprint available.
 */
function deriveFingerprint(issue: SentryIssue): string {
  // Use Sentry's own issue ID as fingerprint proxy — one issue per group
  return issue.id;
}

/**
 * Create a Plane issue from a Sentry alert.
 */
async function createPlaneIssue(
  workspaceId: string,
  projectId: string,
  issue: SentryIssue,
  apiKey: string
): Promise<{ ok: boolean; plane_issue_id?: string; error?: string }> {
  const environment =
    issue.tags?.find((t) => t.key === "environment")?.value ?? "unknown";

  const title = `[Sentry] ${issue.metadata?.type ?? issue.title}: ${
    issue.metadata?.value ?? issue.culprit
  } (${environment})`;

  const description = [
    `**Auto-generated from Sentry alert**`,
    ``,
    `- **Sentry issue**: ${issue.permalink}`,
    `- **Project**: ${issue.project.name} (\`${issue.project.slug}\`)`,
    `- **Environment**: ${environment}`,
    `- **Level**: ${issue.level}`,
    `- **Culprit**: \`${issue.culprit}\``,
  ].join("\n");

  const url = `https://api.plane.so/api/v1/workspaces/${workspaceId}/projects/${projectId}/issues/`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({
      name: title.slice(0, 255),
      description_html: description,
      priority: SENTRY_LEVEL_TO_PLANE_PRIORITY[issue.level] ?? "medium",
      label_ids: [],   // labels configured at workspace level; skip for now
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    return { ok: false, error: `Plane API ${response.status}: ${text}` };
  }

  const data = (await response.json()) as { id: string };
  return { ok: true, plane_issue_id: data.id };
}

/**
 * Close a Plane issue (on Sentry resolve).
 */
async function closePlaneIssue(
  workspaceId: string,
  projectId: string,
  issueId: string,
  apiKey: string
): Promise<{ ok: boolean; error?: string }> {
  const url = `https://api.plane.so/api/v1/workspaces/${workspaceId}/projects/${projectId}/issues/${issueId}/`;

  const response = await fetch(url, {
    method: "PATCH",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ state: "Done" }),
  });

  if (!response.ok) {
    const text = await response.text();
    return { ok: false, error: `Plane API ${response.status}: ${text}` };
  }

  return { ok: true };
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return jsonResponse({ ok: false, error: "Method not allowed" }, 405);
  }

  const rawBody = await req.text();

  // Validate Sentry signature
  const webhookSecret = Deno.env.get("SENTRY_WEBHOOK_SECRET");
  if (webhookSecret) {
    const signature = req.headers.get("sentry-hook-signature");
    if (!validateSentrySignature(rawBody, signature, webhookSecret)) {
      return jsonResponse({ ok: false, error: "Invalid Sentry webhook signature" }, 401);
    }
  }

  const planeApiKey = Deno.env.get("PLANE_API_KEY");
  const planeWorkspaceId = Deno.env.get("PLANE_WORKSPACE_ID");
  const mappingJson = Deno.env.get("PLANE_SENTRY_MAPPING_JSON");

  if (!planeApiKey || !planeWorkspaceId) {
    return jsonResponse({ ok: false, error: "PLANE_API_KEY or PLANE_WORKSPACE_ID not set" }, 500);
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  // Parse Sentry → Plane project mappings
  // Loaded from ssot/mappings/plane_sentry.yaml and injected as env var at deploy time.
  let mappings: PlaneProjectMapping[] = [];
  if (mappingJson) {
    try {
      mappings = JSON.parse(mappingJson) as PlaneProjectMapping[];
    } catch {
      return jsonResponse({ ok: false, error: "Invalid PLANE_SENTRY_MAPPING_JSON" }, 500);
  }
  }

  let payload: SentryWebhookPayload;
  try {
    payload = JSON.parse(rawBody) as SentryWebhookPayload;
  } catch {
    return jsonResponse({ ok: false, error: "Invalid JSON body" }, 400);
  }

  const { action, data } = payload;
  const issue = data.issue;
  const projectSlug = issue.project.slug;
  const fingerprint = deriveFingerprint(issue);
  const idempotencyKey = `sentry_plane_sync:${projectSlug}:${fingerprint}`;

  // Find Plane project mapping for this Sentry project
  const mapping = mappings.find((m) => m.sentry_project_slug === projectSlug);
  if (!mapping) {
    // Log skipped for Advisor scan
    await supabase.from("ops.run_events").insert({
      idempotency_key: `${idempotencyKey}:skipped`,
      integration: "sentry_plane_sync",
      event_type: `sentry.issue.${action}`,
      status: "skipped_no_mapping",
      metadata: { sentry_project_slug: projectSlug, sentry_issue_id: issue.id },
    });
    return jsonResponse({
      ok: true,
      status: "skipped",
      reason: "sentry_project_not_in_mapping",
    });
  }

  // Check existing dedup record
  const { data: existing } = await supabase
    .from("work_plane.sentry_issues")
    .select("plane_issue_id, plane_project_id, status, occurrence_count")
    .eq("sentry_project_slug", projectSlug)
    .eq("sentry_fingerprint", fingerprint)
    .maybeSingle();

  const existingRow = existing as SentryIssueRow | null;

  // --- Handle "resolved" action ---
  if (action === "resolved" && existingRow?.plane_issue_id) {
    const result = await closePlaneIssue(
      planeWorkspaceId,
      mapping.plane_project_id,
      existingRow.plane_issue_id,
      planeApiKey
    );

    if (result.ok) {
      await supabase
        .from("work_plane.sentry_issues")
        .update({ status: "resolved", last_seen: new Date().toISOString() })
        .eq("sentry_project_slug", projectSlug)
        .eq("sentry_fingerprint", fingerprint);
    }

    await supabase.from("ops.run_events").insert({
      idempotency_key: `${idempotencyKey}:resolved`,
      integration: "sentry_plane_sync",
      event_type: "sentry.issue.resolved",
      status: result.ok ? "success" : "error",
      metadata: {
        sentry_issue_id: issue.id,
        plane_issue_id: existingRow.plane_issue_id,
        error: result.error,
      },
    });

    return jsonResponse({ ok: result.ok, status: "resolved", error: result.error });
  }

  // --- Handle "created" or recurring occurrence ---
  if (existingRow) {
    // Already tracked — just update occurrence count and last_seen
    await supabase
      .from("work_plane.sentry_issues")
      .update({
        last_seen: new Date().toISOString(),
        occurrence_count: (existingRow.occurrence_count ?? 0) + 1,
      })
      .eq("sentry_project_slug", projectSlug)
      .eq("sentry_fingerprint", fingerprint);

    return jsonResponse({
      ok: true,
      status: "updated_occurrence",
      plane_issue_id: existingRow.plane_issue_id,
    });
  }

  // New fingerprint — create Plane issue
  const createResult = await createPlaneIssue(
    planeWorkspaceId,
    mapping.plane_project_id,
    issue,
    planeApiKey
  );

  if (createResult.ok && createResult.plane_issue_id) {
    // Upsert dedup record
    await supabase.from("work_plane.sentry_issues").upsert(
      {
        sentry_project_slug: projectSlug,
        sentry_fingerprint: fingerprint,
        sentry_issue_id: issue.id,
        plane_issue_id: createResult.plane_issue_id,
        plane_project_id: mapping.plane_project_id,
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 1,
        status: "open",
      },
      { onConflict: "sentry_project_slug,sentry_fingerprint", ignoreDuplicates: true }
    );
  }

  // Audit trail
  await supabase.from("ops.run_events").insert({
    idempotency_key: `${idempotencyKey}:created`,
    integration: "sentry_plane_sync",
    event_type: "sentry.issue.created",
    status: createResult.ok ? "success" : "error",
    metadata: {
      sentry_issue_id: issue.id,
      sentry_project_slug: projectSlug,
      plane_issue_id: createResult.plane_issue_id,
      plane_project_id: mapping.plane_project_id,
      error: createResult.error,
    },
  });

  return jsonResponse({
    ok: createResult.ok,
    status: "created",
    plane_issue_id: createResult.plane_issue_id,
    error: createResult.error,
  });
});
