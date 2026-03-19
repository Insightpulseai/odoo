/**
 * Idempotent GitHub Issue manager for Vercel integrations drift.
 *
 * - Opens/updates an issue when drift is detected.
 * - Closes the issue when integrations are back in sync.
 * - Uses a stable marker comment to locate the issue idempotently.
 */

import type { DiffResult } from "./diff.js";

const MARKER_PREFIX = "<!-- vercel-integrations-drift::";
const MARKER_SUFFIX = " -->";

function marker(teamId: string): string {
  return `${MARKER_PREFIX}${teamId}${MARKER_SUFFIX}`;
}

interface GitHubIssue {
  number: number;
  state: string;
  html_url: string;
}

async function findExistingIssue(
  ghToken: string,
  repo: string,
  teamId: string
): Promise<GitHubIssue | null> {
  const q = encodeURIComponent(`repo:${repo} "${MARKER_PREFIX}${teamId}" is:issue`);
  const res = await fetch(`https://api.github.com/search/issues?q=${q}&per_page=1`, {
    headers: {
      Authorization: `Bearer ${ghToken}`,
      Accept: "application/vnd.github+json",
    },
  });
  if (!res.ok) throw new Error(`GitHub search failed: ${res.status}`);
  const data = await res.json();
  return data.items?.[0] ?? null;
}

function buildIssueBody(diff: DiffResult): string {
  const lines: string[] = [
    marker(diff.team_id),
    "",
    `## Vercel Integrations Drift — Team \`${diff.team_id}\``,
    "",
    `**Snapshot range**: ${diff.before_captured_at} → ${diff.after_captured_at}`,
    "",
  ];

  if (diff.added.length > 0) {
    lines.push("### ➕ Added");
    for (const i of diff.added) {
      lines.push(`- \`${i.slug}\` (${i.name}) — status: ${i.status}`);
    }
    lines.push("");
  }

  if (diff.removed.length > 0) {
    lines.push("### ➖ Removed");
    for (const i of diff.removed) {
      lines.push(`- \`${i.slug}\` (${i.name})`);
    }
    lines.push("");
  }

  if (diff.changed.length > 0) {
    lines.push("### ✏️ Changed");
    for (const c of diff.changed) {
      lines.push(`- \`${c.after.slug}\`: fields changed: ${c.fields.join(", ")}`);
    }
    lines.push("");
  }

  lines.push("---");
  lines.push(
    "_This issue is managed automatically by the Vercel Integrations Diff Engine. " +
      "It will be closed automatically when integrations return to a stable state._"
  );

  return lines.join("\n");
}

export async function syncGitHubIssue(
  ghToken: string,
  repo: string, // "owner/repo"
  diff: DiffResult
): Promise<{ action: "opened" | "updated" | "closed" | "noop"; issue_url?: string }> {
  const existing = await findExistingIssue(ghToken, repo, diff.team_id);

  if (!diff.has_drift) {
    // No drift — close issue if open
    if (existing && existing.state === "open") {
      const res = await fetch(
        `https://api.github.com/repos/${repo}/issues/${existing.number}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${ghToken}`,
            Accept: "application/vnd.github+json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            state: "closed",
            body:
              buildIssueBody(diff) +
              "\n\n✅ **Drift resolved** — integrations are back in sync.",
          }),
        }
      );
      if (!res.ok) throw new Error(`GitHub close failed: ${res.status}`);
      return { action: "closed", issue_url: existing.html_url };
    }
    return { action: "noop" };
  }

  // Drift detected — open or update issue
  const body = buildIssueBody(diff);
  const title = `[Vercel Drift] Integrations changed for team ${diff.team_id}`;

  if (existing) {
    const res = await fetch(
      `https://api.github.com/repos/${repo}/issues/${existing.number}`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${ghToken}`,
          Accept: "application/vnd.github+json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, body, state: "open" }),
      }
    );
    if (!res.ok) throw new Error(`GitHub update failed: ${res.status}`);
    const updated: GitHubIssue = await res.json();
    return { action: "updated", issue_url: updated.html_url };
  } else {
    const res = await fetch(`https://api.github.com/repos/${repo}/issues`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ghToken}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
        body,
        labels: ["ops", "vercel", "drift"],
      }),
    });
    if (!res.ok) throw new Error(`GitHub create failed: ${res.status}`);
    const created: GitHubIssue = await res.json();
    return { action: "opened", issue_url: created.html_url };
  }
}
