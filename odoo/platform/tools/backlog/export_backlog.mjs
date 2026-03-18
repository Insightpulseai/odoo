#!/usr/bin/env node
/**
 * Backlog Export Tool
 *
 * Exports open issues and PRs from GitHub for routing and caps analysis.
 *
 * Usage:
 *   GH_TOKEN=xxx node tools/backlog/export_backlog.mjs --repo owner/repo --out backlog.json
 *
 * Environment:
 *   GH_TOKEN - GitHub personal access token (required)
 */

import fs from "fs";
import path from "path";

// ============================================================================
// CLI ARGS
// ============================================================================

function arg(name, defaultValue = "") {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : defaultValue;
}

const repoFull = arg("--repo");
const outPath = arg("--out", ".artifacts/backlog.json");
const includeClosedDays = parseInt(arg("--include-closed-days", "0"), 10);

// ============================================================================
// VALIDATION
// ============================================================================

if (!repoFull) {
  console.error("Usage: export_backlog.mjs --repo owner/repo [--out path.json]");
  console.error("Missing --repo owner/repo");
  process.exit(2);
}

const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
if (!token) {
  console.error("Missing GH_TOKEN or GITHUB_TOKEN environment variable");
  process.exit(2);
}

const [owner, repo] = repoFull.split("/");
if (!owner || !repo) {
  console.error("Invalid --repo format. Expected: owner/repo");
  process.exit(2);
}

// ============================================================================
// GITHUB API
// ============================================================================

const headers = {
  Authorization: `Bearer ${token}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
};

async function ghGet(url) {
  const res = await fetch(url, { headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub API error: ${res.status} ${res.statusText} - ${text}`);
  }
  return res.json();
}

async function fetchAllPages(baseUrl, maxPages = 10) {
  const items = [];
  let page = 1;

  while (page <= maxPages) {
    const url = `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}page=${page}&per_page=100`;
    const data = await ghGet(url);

    if (!Array.isArray(data) || data.length === 0) {
      break;
    }

    items.push(...data);
    page++;
  }

  return items;
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  console.log(`Exporting backlog for: ${owner}/${repo}`);

  // Fetch open issues (includes PRs)
  const openIssues = await fetchAllPages(
    `https://api.github.com/repos/${owner}/${repo}/issues?state=open`
  );

  // Optionally fetch recently closed
  let recentlyClosed = [];
  if (includeClosedDays > 0) {
    const since = new Date();
    since.setDate(since.getDate() - includeClosedDays);
    recentlyClosed = await fetchAllPages(
      `https://api.github.com/repos/${owner}/${repo}/issues?state=closed&since=${since.toISOString()}`
    );
  }

  const allIssues = [...openIssues, ...recentlyClosed];

  // Normalize data
  const normalized = allIssues.map((issue) => ({
    id: issue.id,
    number: issue.number,
    type: issue.pull_request ? "pr" : "issue",
    state: issue.state,
    title: issue.title,
    labels: (issue.labels || []).map((l) => (typeof l === "string" ? l : l.name)),
    assignees: (issue.assignees || []).map((a) => a.login),
    milestone: issue.milestone?.title || null,
    created_at: issue.created_at,
    updated_at: issue.updated_at,
    closed_at: issue.closed_at,
    html_url: issue.html_url,
  }));

  // Separate PRs and issues
  const issues = normalized.filter((x) => x.type === "issue");
  const prs = normalized.filter((x) => x.type === "pr");

  // Build output
  const backlog = {
    repo: repoFull,
    exported_at: new Date().toISOString(),
    summary: {
      total_items: normalized.length,
      open_issues: issues.filter((x) => x.state === "open").length,
      open_prs: prs.filter((x) => x.state === "open").length,
      closed_included: includeClosedDays > 0 ? includeClosedDays : 0,
    },
    items: normalized,
  };

  // Write output
  const outDir = path.dirname(outPath);
  if (outDir && !fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  fs.writeFileSync(outPath, JSON.stringify(backlog, null, 2));
  console.log(`Wrote: ${outPath}`);
  console.log(`  Total items: ${normalized.length}`);
  console.log(`  Open issues: ${backlog.summary.open_issues}`);
  console.log(`  Open PRs: ${backlog.summary.open_prs}`);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
