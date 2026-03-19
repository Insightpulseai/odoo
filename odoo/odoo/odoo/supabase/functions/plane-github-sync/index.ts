// =============================================================================
// PLANE-GITHUB-SYNC — GitHub ↔ Plane issue state synchronization
// =============================================================================
// Purpose: Receive GitHub webhooks (PR merged, issue closed) and update
//          the linked Plane issue state via the Plane API.
//
// SSOT:    ssot/integrations/plane_github_sync.yaml
// Mapping: ssot/mappings/plane_github.yaml  (repo → plane_project_id)
// Contract: docs/architecture/PLANE_MARKETPLACE_INTEGRATIONS.md §GitHub
//
// Boundary rules:
//   - Idempotency key = GitHub delivery ID (X-GitHub-Delivery header)
//   - Every sync batch MUST write ops.runs + ops.run_events
//   - Mapping config is read from env (PLANE_GITHUB_MAPPING_JSON)
//   - No direct DB writes to work_plane.* from this function
//     (webhook ingest → ops.event_queue → worker pattern is for the
//      plane-webhook function; this function is the GitHub → Plane direction)
//
// Endpoints:
//   POST /plane-github-sync   { payload: GitHubWebhookPayload }
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GitHubPREvent {
  action: "opened" | "closed" | "merged" | "reopened" | string;
  pull_request: {
    id: number;
    number: number;
    title: string;
    body: string | null;
    merged: boolean;
    head: { ref: string };
    html_url: string;
  };
  repository: {
    full_name: string;
  };
}

interface GitHubIssueEvent {
  action: "opened" | "closed" | "reopened" | string;
  issue: {
    id: number;
    number: number;
    title: string;
    body: string | null;
    html_url: string;
  };
  repository: {
    full_name: string;
  };
}

interface PlaneMapping {
  repo_full_name: string;
  plane_project_id: string;
  plane_project_slug: string;
  pr_merge_state: string;
  issue_close_state: string;
  writeback_enabled: boolean;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-github-delivery, x-github-event",
};

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status,
  });
}

/**
 * Extract Plane issue ID from PR branch name or description.
 * Patterns: plane/{issue_id}  OR  #PLANE-{seq} (no direct UUID from seq — requires lookup).
 * Returns issue_id UUID if found via branch pattern, else null.
 */
function extractPlaneIssueId(branchRef: string, body: string | null): string | null {
  // Branch pattern: plane/{uuid} or feat/plane/{uuid}
  const branchMatch = branchRef.match(/plane\/([0-9a-f-]{36})/i);
  if (branchMatch) return branchMatch[1];

  // PR body pattern: plane-issue: {uuid}
  if (body) {
    const bodyMatch = body.match(/plane-issue:\s*([0-9a-f-]{36})/i);
    if (bodyMatch) return bodyMatch[1];
  }

  return null;
}

/**
 * Update a Plane issue state via the Plane REST API.
 */
async function updatePlaneIssueState(
  workspaceId: string,
  projectId: string,
  issueId: string,
  stateName: string,
  apiKey: string
): Promise<{ ok: boolean; error?: string }> {
  const url = `https://api.plane.so/api/v1/workspaces/${workspaceId}/projects/${projectId}/issues/${issueId}/`;

  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      "X-API-Key": apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ state: stateName }),
  });

  if (!response.ok) {
    const text = await response.text();
    return { ok: false, error: `Plane API ${response.status}: ${text}` };
  }

  return { ok: true };
}

/**
 * Write ops.runs + ops.run_events for audit trail.
 */
async function writeOpsRun(
  supabase: ReturnType<typeof createClient>,
  {
    deliveryId,
    repoFullName,
    event,
    status,
    issueId,
    error,
    severity,
    reason,
  }: {
    deliveryId: string;
    repoFullName: string;
    event: string;
    status: "success" | "skipped" | "error";
    issueId?: string;
    error?: string;
    /** Audit severity override — defaults to "info" for skipped, "error" for errors */
    severity?: "info" | "warning" | "error";
    /** Machine-readable skip reason surfaced in Advisor posture scan */
    reason?: string;
  }
): Promise<void> {
  const idempotencyKey = `plane_github_sync:${deliveryId}`;
  const auditSeverity = severity ?? (status === "error" ? "error" : "info");

  await supabase.from("ops.runs").upsert(
    {
      idempotency_key: idempotencyKey,
      integration: "plane_github_sync",
      status: status === "error" ? "failed" : "done",
      metadata: { repo: repoFullName, event, github_delivery_id: deliveryId },
    },
    { onConflict: "idempotency_key", ignoreDuplicates: true }
  );

  await supabase.from("ops.run_events").insert({
    idempotency_key: `${idempotencyKey}:event`,
    integration: "plane_github_sync",
    event_type: event,
    status,
    metadata: {
      repo: repoFullName,
      plane_issue_id: issueId,
      severity: auditSeverity,
      ...(reason ? { reason } : {}),
      ...(error ? { error } : {}),
    },
  });
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

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  const planeApiKey = Deno.env.get("PLANE_API_KEY");
  const planeWorkspaceId = Deno.env.get("PLANE_WORKSPACE_ID");
  const mappingJson = Deno.env.get("PLANE_GITHUB_MAPPING_JSON");

  if (!planeApiKey || !planeWorkspaceId) {
    return jsonResponse({ ok: false, error: "PLANE_API_KEY or PLANE_WORKSPACE_ID not set" }, 500);
  }

  // Parse repo → project mappings from env
  // In production, this is loaded from ssot/mappings/plane_github.yaml
  // and injected as a JSON env var at deploy time.
  let mappings: PlaneMapping[] = [];
  if (mappingJson) {
    try {
      mappings = JSON.parse(mappingJson) as PlaneMapping[];
    } catch {
      return jsonResponse({ ok: false, error: "Invalid PLANE_GITHUB_MAPPING_JSON" }, 500);
    }
  }

  const deliveryId = req.headers.get("X-GitHub-Delivery") ?? "unknown";
  const githubEvent = req.headers.get("X-GitHub-Event") ?? "unknown";

  let body: GitHubPREvent | GitHubIssueEvent;
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ ok: false, error: "Invalid JSON body" }, 400);
  }

  const repoFullName = body.repository.full_name;
  const mapping = mappings.find((m) => m.repo_full_name === repoFullName);

  if (!mapping) {
    await writeOpsRun(supabase, {
      deliveryId,
      repoFullName,
      event: githubEvent,
      status: "skipped",
      severity: "info",
      reason: "repo_not_in_mapping",
    });
    return jsonResponse({ ok: true, status: "skipped", reason: "repo_not_in_mapping" });
  }

  // Mapping exists but plane_project_id not yet populated.
  // "Merge now, activate later" — return 200 so GitHub does not retry.
  // Advisor posture scan surfaces MAPPING_MISSING repos via ops.run_events.
  if (!mapping.plane_project_id || mapping.plane_project_id.trim() === "") {
    await writeOpsRun(supabase, {
      deliveryId,
      repoFullName,
      event: githubEvent,
      status: "skipped",
      severity: "info",
      reason: "MAPPING_MISSING",
    });
    return jsonResponse({ ok: true, status: "ignored", reason: "MAPPING_MISSING" });
  }

  // Handle pull_request events
  if (githubEvent === "pull_request") {
    const pr = (body as GitHubPREvent).pull_request;
    const action = (body as GitHubPREvent).action;

    if (action !== "closed" || !pr.merged) {
      // Only act on merged PRs
      return jsonResponse({ ok: true, status: "skipped", reason: "pr_not_merged" });
    }

    const issueId = extractPlaneIssueId(pr.head.ref, pr.body);
    if (!issueId) {
      await writeOpsRun(supabase, {
        deliveryId,
        repoFullName,
        event: "pull_request.merged",
        status: "skipped",
      });
      return jsonResponse({ ok: true, status: "skipped", reason: "no_plane_issue_link" });
    }

    const result = await updatePlaneIssueState(
      planeWorkspaceId,
      mapping.plane_project_id,
      issueId,
      mapping.pr_merge_state ?? "Done",
      planeApiKey
    );

    await writeOpsRun(supabase, {
      deliveryId,
      repoFullName,
      event: "pull_request.merged",
      status: result.ok ? "success" : "error",
      issueId,
      error: result.error,
    });

    return jsonResponse({ ok: result.ok, plane_issue_id: issueId, error: result.error });
  }

  // Handle issues events
  if (githubEvent === "issues") {
    const issue = (body as GitHubIssueEvent).issue;
    const action = (body as GitHubIssueEvent).action;

    if (action !== "closed") {
      return jsonResponse({ ok: true, status: "skipped", reason: "issue_not_closed" });
    }

    const issueId = extractPlaneIssueId("", issue.body);
    if (!issueId) {
      await writeOpsRun(supabase, {
        deliveryId,
        repoFullName,
        event: "issues.closed",
        status: "skipped",
      });
      return jsonResponse({ ok: true, status: "skipped", reason: "no_plane_issue_link" });
    }

    const result = await updatePlaneIssueState(
      planeWorkspaceId,
      mapping.plane_project_id,
      issueId,
      mapping.issue_close_state ?? "Done",
      planeApiKey
    );

    await writeOpsRun(supabase, {
      deliveryId,
      repoFullName,
      event: "issues.closed",
      status: result.ok ? "success" : "error",
      issueId,
      error: result.error,
    });

    return jsonResponse({ ok: result.ok, plane_issue_id: issueId, error: result.error });
  }

  // Unknown event — record and skip
  await writeOpsRun(supabase, {
    deliveryId,
    repoFullName,
    event: githubEvent,
    status: "skipped",
  });
  return jsonResponse({ ok: true, status: "skipped", reason: `unhandled_event:${githubEvent}` });
});
