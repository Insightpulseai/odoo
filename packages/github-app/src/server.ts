/**
 * Pulser Bot — GitHub App Webhook Server
 *
 * Receives GitHub webhooks and creates work items in Master Control.
 * Implements "All Green" pattern: keep PRs mergeable via agent remediation.
 *
 * Capabilities (like Continue's All Green):
 * ✅ Addresses code review comments
 * ✅ Fixes failing CI checks
 * ✅ Resolves merge conflicts
 *
 * Events handled:
 * - issue_comment.created / pull_request_review_comment.created (triggers)
 * - pull_request_review.submitted (review feedback)
 * - pull_request.synchronize / pull_request.opened (merge conflicts)
 * - check_suite.completed / workflow_run.completed (CI failures)
 *
 * Usage:
 *   npm run dev
 *   # Webhook URL: http://localhost:3009/api/github/webhooks
 */

import "dotenv/config";
import { Probot, createNodeMiddleware } from "probot";
import http from "node:http";
import { z } from "zod";
import { createClient } from "@supabase/supabase-js";
import { request } from "undici";

// ============================================================================
// Environment Configuration
// ============================================================================

const Env = z
  .object({
    // GitHub App credentials
    APP_ID: z.string().min(1),
    WEBHOOK_SECRET: z.string().min(1),
    PRIVATE_KEY: z.string().min(1), // PEM string (can be multiline)

    // Supabase connection
    SUPABASE_URL: z.string().url().optional(),
    SUPABASE_SERVICE_KEY: z.string().optional(),

    // Runner API (fallback if no Supabase)
    RUNNER_BASE_URL: z.string().default("http://localhost:8788"),

    // Tenant configuration
    TENANT_ID: z.string().uuid().default("00000000-0000-0000-0000-000000000001"),

    // Server config
    PORT: z.string().default("3009"),
  })
  .parse(process.env);

// ============================================================================
// Supabase Client (optional)
// ============================================================================

const supabase =
  Env.SUPABASE_URL && Env.SUPABASE_SERVICE_KEY
    ? createClient(Env.SUPABASE_URL, Env.SUPABASE_SERVICE_KEY, {
        auth: { persistSession: false },
      })
    : null;

// ============================================================================
// Work Item Creation
// ============================================================================

interface WorkItemPayload {
  tenant_id: string;
  source: string;
  source_ref: string;
  title: string;
  lane: string;
  priority: number;
  payload: Record<string, unknown>;
}

async function createWorkItem(item: WorkItemPayload): Promise<{ id: string; status: string }> {
  // Prefer Supabase direct insert if available
  if (supabase) {
    const { data, error } = await supabase
      .schema("runtime")
      .from("work_items")
      .insert({
        tenant_id: item.tenant_id,
        source: item.source,
        source_ref: item.source_ref,
        title: item.title,
        lane: item.lane,
        priority: item.priority,
        payload: item.payload,
        status: "open",
      })
      .select("id, status")
      .single();

    if (error) {
      console.error("[github-app] Supabase insert error:", error);
      throw new Error(`Supabase error: ${error.message}`);
    }

    return { id: data.id, status: data.status };
  }

  // Fallback to runner API
  const res = await request(`${Env.RUNNER_BASE_URL}/v1/work-items`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(item),
  });

  const body = await res.body.json() as { work_item_id: string; status: string };
  return { id: body.work_item_id, status: body.status };
}

// ============================================================================
// Probot App Definition
// ============================================================================

const probot = new Probot({
  appId: Env.APP_ID,
  privateKey: Env.PRIVATE_KEY,
  secret: Env.WEBHOOK_SECRET,
});

probot.load((app) => {
  app.log.info("Pulser Bot loaded");

  // -------------------------------------------------------------------------
  // Handle PR comments with /pulser trigger
  // -------------------------------------------------------------------------
  app.on(
    ["issue_comment.created", "pull_request_review_comment.created"],
    async (context) => {
      const comment = (context.payload as any).comment;
      const body = comment?.body || "";
      const repo = context.payload.repository;
      const owner = repo?.owner?.login;
      const repoName = repo?.name;

      // Check for trigger phrase
      if (!body.includes("/pulser") && !body.includes("@pulser")) {
        return;
      }

      app.log.info(`[pulser] Triggered by comment in ${owner}/${repoName}`);

      const issue = (context.payload as any).issue;
      const prUrl = issue?.pull_request?.html_url || issue?.html_url;
      const prNumber = issue?.number;

      // Extract command from comment (e.g., "/pulser fix lint")
      const commandMatch = body.match(/(?:\/pulser|@pulser)\s+(.+?)(?:\n|$)/i);
      const command = commandMatch?.[1]?.trim() || "remediate";

      try {
        const result = await createWorkItem({
          tenant_id: Env.TENANT_ID,
          source: "github_pr",
          source_ref: prUrl,
          title: `Pulser: ${repoName}#${prNumber} - ${command}`,
          lane: "DEV",
          priority: 2,
          payload: {
            owner,
            repo: repoName,
            pr_number: prNumber,
            pr_url: prUrl,
            command,
            triggered_by: comment?.user?.login,
            comment_id: comment?.id,
            comment_body: body,
          },
        });

        // Reply to PR
        await context.octokit.issues.createComment({
          owner: owner!,
          repo: repoName!,
          issue_number: prNumber,
          body: `🤖 **Pulser Bot** queued remediation run.

| Field | Value |
|-------|-------|
| Work Item | \`${result.id}\` |
| Command | \`${command}\` |
| Status | ${result.status} |

I'll analyze the PR and apply fixes if needed.`,
        });

        app.log.info(`[pulser] Created work item ${result.id}`);
      } catch (error) {
        app.log.error(`[pulser] Failed to create work item: ${error}`);

        await context.octokit.issues.createComment({
          owner: owner!,
          repo: repoName!,
          issue_number: prNumber,
          body: `⚠️ **Pulser Bot** failed to queue remediation.

\`\`\`
${error instanceof Error ? error.message : String(error)}
\`\`\``,
        });
      }
    }
  );

  // -------------------------------------------------------------------------
  // Handle CI check failures
  // -------------------------------------------------------------------------
  app.on("check_suite.completed", async (context) => {
    const checkSuite = context.payload.check_suite;
    const repo = context.payload.repository;

    // Only act on failures
    if (checkSuite.conclusion !== "failure") {
      return;
    }

    // Skip if no PRs associated
    const prs = checkSuite.pull_requests || [];
    if (prs.length === 0) {
      return;
    }

    app.log.info(`[pulser] Check suite failed for ${repo.full_name}`);

    for (const pr of prs) {
      const prUrl = `https://github.com/${repo.full_name}/pull/${pr.number}`;

      try {
        // Check if work item already exists for this PR + check suite
        const sourceRef = `${prUrl}#check_suite_${checkSuite.id}`;

        await createWorkItem({
          tenant_id: Env.TENANT_ID,
          source: "github_pr",
          source_ref: sourceRef,
          title: `CI Failed: ${repo.name}#${pr.number}`,
          lane: "DEV",
          priority: 2,
          payload: {
            owner: repo.owner.login,
            repo: repo.name,
            pr_number: pr.number,
            pr_url: prUrl,
            check_suite_id: checkSuite.id,
            conclusion: checkSuite.conclusion,
            head_sha: checkSuite.head_sha,
            head_branch: checkSuite.head_branch,
          },
        });

        app.log.info(`[pulser] Created work item for PR #${pr.number} check failure`);
      } catch (error) {
        // May fail on duplicate - that's OK
        app.log.warn(`[pulser] Could not create work item: ${error}`);
      }
    }
  });

  // -------------------------------------------------------------------------
  // Handle workflow run failures
  // -------------------------------------------------------------------------
  app.on("workflow_run.completed", async (context) => {
    const workflowRun = context.payload.workflow_run;
    const repo = context.payload.repository;

    // Only act on failures
    if (workflowRun.conclusion !== "failure") {
      return;
    }

    // Skip if no PRs associated
    const prs = workflowRun.pull_requests || [];
    if (prs.length === 0) {
      return;
    }

    app.log.info(`[pulser] Workflow ${workflowRun.name} failed for ${repo.full_name}`);

    for (const pr of prs) {
      const prUrl = `https://github.com/${repo.full_name}/pull/${pr.number}`;

      try {
        const sourceRef = `${prUrl}#workflow_${workflowRun.id}`;

        await createWorkItem({
          tenant_id: Env.TENANT_ID,
          source: "github_pr",
          source_ref: sourceRef,
          title: `Workflow Failed: ${workflowRun.name} - ${repo.name}#${pr.number}`,
          lane: "DEV",
          priority: 2,
          payload: {
            owner: repo.owner.login,
            repo: repo.name,
            pr_number: pr.number,
            pr_url: prUrl,
            workflow_run_id: workflowRun.id,
            workflow_name: workflowRun.name,
            conclusion: workflowRun.conclusion,
            head_sha: workflowRun.head_sha,
            head_branch: workflowRun.head_branch,
            logs_url: workflowRun.logs_url,
          },
        });

        app.log.info(`[pulser] Created work item for workflow failure`);
      } catch (error) {
        app.log.warn(`[pulser] Could not create work item: ${error}`);
      }
    }
  });

  // -------------------------------------------------------------------------
  // Handle merge conflicts
  // -------------------------------------------------------------------------
  app.on(
    ["pull_request.opened", "pull_request.synchronize", "pull_request.reopened"],
    async (context) => {
      const pr = context.payload.pull_request;
      const repo = context.payload.repository;

      // GitHub needs time to compute mergeable status
      // On synchronize, mergeable might be null initially
      if (pr.mergeable === null) {
        app.log.debug(`[pulser] PR #${pr.number} mergeable status pending, will check on next event`);
        return;
      }

      // Only act on merge conflicts
      if (pr.mergeable !== false) {
        return;
      }

      // Check if it's actually a conflict (not other merge issues)
      if (pr.mergeable_state !== "dirty") {
        app.log.debug(`[pulser] PR #${pr.number} not mergeable but state is ${pr.mergeable_state}, skipping`);
        return;
      }

      app.log.info(`[pulser] Merge conflict detected for ${repo.full_name}#${pr.number}`);

      try {
        const sourceRef = `${pr.html_url}#merge_conflict_${pr.head.sha.substring(0, 7)}`;

        const result = await createWorkItem({
          tenant_id: Env.TENANT_ID,
          source: "github_pr",
          source_ref: sourceRef,
          title: `Merge Conflict: ${repo.name}#${pr.number}`,
          lane: "DEV",
          priority: 2,
          payload: {
            owner: repo.owner.login,
            repo: repo.name,
            pr_number: pr.number,
            pr_url: pr.html_url,
            pr_title: pr.title,
            base_branch: pr.base.ref,
            head_branch: pr.head.ref,
            head_sha: pr.head.sha,
            mergeable_state: pr.mergeable_state,
            conflict_type: "merge_conflict",
            author: pr.user?.login,
          },
        });

        // Comment on PR about conflict detection
        await context.octokit.issues.createComment({
          owner: repo.owner.login,
          repo: repo.name,
          issue_number: pr.number,
          body: `🔀 **Pulser Bot** detected a merge conflict.

| Field | Value |
|-------|-------|
| Work Item | \`${result.id}\` |
| Base Branch | \`${pr.base.ref}\` |
| Head Branch | \`${pr.head.ref}\` |
| Status | Analyzing conflict... |

I'll attempt to resolve the conflict automatically. If manual intervention is needed, I'll provide guidance.`,
        });

        app.log.info(`[pulser] Created work item ${result.id} for merge conflict`);
      } catch (error) {
        app.log.warn(`[pulser] Could not create merge conflict work item: ${error}`);
      }
    }
  );

  // -------------------------------------------------------------------------
  // Handle code review comments (changes requested)
  // -------------------------------------------------------------------------
  app.on("pull_request_review.submitted", async (context) => {
    const review = context.payload.review;
    const pr = context.payload.pull_request;
    const repo = context.payload.repository;

    // Only act on reviews requesting changes
    if (review.state !== "changes_requested") {
      return;
    }

    // Skip if no review body (just approval/rejection without comments)
    if (!review.body || review.body.trim().length === 0) {
      app.log.debug(`[pulser] Review on PR #${pr.number} has no body, skipping`);
      return;
    }

    app.log.info(`[pulser] Changes requested on ${repo.full_name}#${pr.number}`);

    try {
      const sourceRef = `${pr.html_url}#review_${review.id}`;

      const result = await createWorkItem({
        tenant_id: Env.TENANT_ID,
        source: "github_pr",
        source_ref: sourceRef,
        title: `Review Feedback: ${repo.name}#${pr.number}`,
        lane: "DEV",
        priority: 2,
        payload: {
          owner: repo.owner.login,
          repo: repo.name,
          pr_number: pr.number,
          pr_url: pr.html_url,
          pr_title: pr.title,
          review_id: review.id,
          review_state: review.state,
          review_body: review.body,
          reviewer: review.user?.login,
          head_sha: pr.head.sha,
          feedback_type: "changes_requested",
        },
      });

      // Reply to the review
      await context.octokit.issues.createComment({
        owner: repo.owner.login,
        repo: repo.name,
        issue_number: pr.number,
        body: `🔍 **Pulser Bot** received review feedback from @${review.user?.login}.

| Field | Value |
|-------|-------|
| Work Item | \`${result.id}\` |
| Reviewer | @${review.user?.login} |
| Status | Analyzing feedback... |

I'll analyze the requested changes and propose fixes.`,
      });

      app.log.info(`[pulser] Created work item ${result.id} for review feedback`);
    } catch (error) {
      app.log.warn(`[pulser] Could not create review feedback work item: ${error}`);
    }
  });

  // -------------------------------------------------------------------------
  // Handle review thread comments (inline code review)
  // -------------------------------------------------------------------------
  app.on("pull_request_review_thread.resolved", async (context) => {
    // Log when threads are resolved (for tracking)
    const thread = context.payload.thread;
    const pr = context.payload.pull_request;
    const repo = context.payload.repository;

    app.log.info(
      `[pulser] Review thread resolved on ${repo.full_name}#${pr.number} by ${context.payload.sender?.login}`
    );
  });
});

// ============================================================================
// HTTP Server
// ============================================================================

const middleware = createNodeMiddleware(probot, {
  probot,
  webhooksPath: "/api/github/webhooks",
});

const server = http.createServer(middleware);

const port = Number(Env.PORT);
server.listen(port, () => {
  console.log(`[github-app] Pulser Bot listening on :${port}`);
  console.log(`[github-app] Webhook path: /api/github/webhooks`);
  console.log(`[github-app] Supabase: ${supabase ? "connected" : "not configured (using runner API)"}`);
});
