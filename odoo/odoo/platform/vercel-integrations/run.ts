/**
 * Entry point for the Vercel Integrations Diff Engine.
 *
 * Run via: tsx platform/vercel-integrations/run.ts
 * Called by: .github/workflows/vercel-integrations-diff.yml (daily cron)
 *
 * Required env vars:
 *   VERCEL_API_TOKEN        — Vercel API token (for future snapshot capture step)
 *   SUPABASE_URL            — Supabase project URL
 *   SUPABASE_SERVICE_ROLE_KEY — Supabase service role key
 *   SLACK_WEBHOOK_URL       — Slack incoming webhook (optional; skipped if absent)
 *   GH_TOKEN                — GitHub token with issues:write
 *   GH_REPO                 — GitHub repo (owner/repo)
 */

import { fetchLatestSnapshots, diffSnapshots } from "./diff.js";
import { syncGitHubIssue } from "./github_issues.js";
import { slackNotify } from "./slack_notify.js";
import { writeFileSync } from "fs";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const GH_TOKEN = process.env.GH_TOKEN;
const GH_REPO = process.env.GH_REPO;
const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;
// VERCEL_TEAM_IDS: comma-separated list of Vercel team IDs to monitor
const VERCEL_TEAM_IDS = (process.env.VERCEL_TEAM_IDS ?? "").split(",").filter(Boolean);

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY || !GH_TOKEN || !GH_REPO) {
  console.error("Missing required env vars: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GH_TOKEN, GH_REPO");
  process.exit(1);
}

async function run(): Promise<void> {
  if (VERCEL_TEAM_IDS.length === 0) {
    console.log("No VERCEL_TEAM_IDS configured — nothing to diff.");
    return;
  }

  for (const teamId of VERCEL_TEAM_IDS) {
    console.log(`\n--- Processing team: ${teamId} ---`);

    const snapshots = await fetchLatestSnapshots(SUPABASE_URL!, SUPABASE_SERVICE_ROLE_KEY!, teamId);
    if (!snapshots) {
      console.log(`  Not enough snapshots for ${teamId} (need ≥ 2). Skipping.`);
      continue;
    }

    const [before, after] = snapshots;
    const diff = diffSnapshots(before, after);

    // Save diff artifact
    const artifactPath = `/tmp/vercel-integrations-diff-${teamId}-${Date.now()}.json`;
    writeFileSync(artifactPath, JSON.stringify(diff, null, 2));
    console.log(`  Diff saved to ${artifactPath}`);

    if (diff.has_drift) {
      console.log(`  DRIFT DETECTED: +${diff.added.length} added, -${diff.removed.length} removed, ~${diff.changed.length} changed`);
    } else {
      console.log("  No drift detected.");
    }

    // Sync GitHub Issue
    const issueResult = await syncGitHubIssue(GH_TOKEN!, GH_REPO!, diff);
    console.log(`  GitHub Issue: ${issueResult.action}${issueResult.issue_url ? ` → ${issueResult.issue_url}` : ""}`);

    // Slack notification (optional)
    if (SLACK_WEBHOOK_URL) {
      await slackNotify(SLACK_WEBHOOK_URL, diff, issueResult.issue_url);
      if (diff.has_drift) console.log("  Slack notified.");
    }
  }

  console.log("\nDone.");
}

run().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
