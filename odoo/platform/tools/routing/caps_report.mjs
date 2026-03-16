#!/usr/bin/env node
/**
 * Routing + Caps Report Tool
 *
 * Analyzes backlog against routing matrix and generates caps report.
 *
 * Usage:
 *   node tools/routing/caps_report.mjs \
 *     --routing config/routing_matrix.yml \
 *     --backlog .artifacts/backlog.json \
 *     --out .artifacts/caps_report.json \
 *     --md .artifacts/pr_gate_summary.md
 */

import fs from "fs";
import path from "path";
import yaml from "js-yaml";

// ============================================================================
// CLI ARGS
// ============================================================================

function arg(name, defaultValue = "") {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : defaultValue;
}

const routingPath = arg("--routing", "config/routing_matrix.yml");
const backlogPath = arg("--backlog", ".artifacts/backlog.json");
const outJson = arg("--out", ".artifacts/caps_report.json");
const outMd = arg("--md", ".artifacts/pr_gate_summary.md");

// ============================================================================
// VALIDATION
// ============================================================================

if (!fs.existsSync(routingPath)) {
  console.error(`Routing matrix not found: ${routingPath}`);
  process.exit(2);
}

if (!fs.existsSync(backlogPath)) {
  console.error(`Backlog not found: ${backlogPath}`);
  process.exit(2);
}

// ============================================================================
// LOAD DATA
// ============================================================================

const routing = yaml.load(fs.readFileSync(routingPath, "utf8"));
const backlog = JSON.parse(fs.readFileSync(backlogPath, "utf8"));

const caps = routing.caps || {};
const labelsToRoute = routing.labels_to_route || {};
const bypassLabels = new Set(routing.bypass_labels || []);

// ============================================================================
// ANALYSIS
// ============================================================================

function routeToTeam(labels) {
  for (const label of labels) {
    const routeConfig = labelsToRoute[label];
    if (routeConfig?.team) {
      return routeConfig.team;
    }
  }
  return "Unrouted";
}

function getPriority(labels) {
  const priorities = ["P0", "P1", "P2", "P3"];
  for (const p of priorities) {
    if (labels.includes(p)) {
      return p;
    }
  }
  return "P3"; // Default
}

function getSeverity(labels) {
  const severities = ["Sev0", "Sev1", "Sev2", "Sev3"];
  for (const s of severities) {
    if (labels.some((l) => l.toLowerCase().includes(s.toLowerCase()))) {
      return s;
    }
  }
  return null;
}

function shouldBypass(labels) {
  return labels.some((l) => bypassLabels.has(l));
}

// Group items by team
const byTeam = {};
const openItems = backlog.items.filter((x) => x.state === "open" && x.type === "issue");

for (const item of openItems) {
  const labels = item.labels || [];
  const team = routeToTeam(labels);
  const priority = getPriority(labels);
  const severity = getSeverity(labels);
  const bypassed = shouldBypass(labels);

  if (!byTeam[team]) {
    byTeam[team] = { total: 0, p0p1: 0, bypassed: 0, items: [] };
  }

  byTeam[team].total += 1;
  if (priority === "P0" || priority === "P1") {
    byTeam[team].p0p1 += 1;
  }
  if (bypassed) {
    byTeam[team].bypassed += 1;
  }

  byTeam[team].items.push({
    number: item.number,
    title: item.title,
    url: item.html_url,
    priority,
    severity,
    labels,
    bypassed,
  });
}

// Check for violations
const violations = [];
for (const [team, stats] of Object.entries(byTeam)) {
  const cap = caps[team];
  if (!cap) continue;

  // Only count non-bypassed items for cap enforcement
  const effectiveTotal = stats.total - stats.bypassed;
  const effectiveP0P1 = stats.items.filter(
    (x) => !x.bypassed && (x.priority === "P0" || x.priority === "P1")
  ).length;

  if (cap.max_open_total != null && effectiveTotal > cap.max_open_total) {
    violations.push({
      team,
      type: "max_open_total",
      value: effectiveTotal,
      cap: cap.max_open_total,
      message: `${team} has ${effectiveTotal} open items (cap: ${cap.max_open_total})`,
    });
  }

  if (cap.max_open_p0_p1 != null && effectiveP0P1 > cap.max_open_p0_p1) {
    violations.push({
      team,
      type: "max_open_p0_p1",
      value: effectiveP0P1,
      cap: cap.max_open_p0_p1,
      message: `${team} has ${effectiveP0P1} P0/P1 items (cap: ${cap.max_open_p0_p1})`,
    });
  }
}

// ============================================================================
// OUTPUT
// ============================================================================

const report = {
  repo: backlog.repo,
  generated_at: new Date().toISOString(),
  summary: {
    total_open_issues: openItems.length,
    teams_analyzed: Object.keys(byTeam).length,
    violations_count: violations.length,
    has_violations: violations.length > 0,
  },
  by_team: byTeam,
  violations,
};

// Write JSON
const outJsonDir = path.dirname(outJson);
if (outJsonDir && !fs.existsSync(outJsonDir)) {
  fs.mkdirSync(outJsonDir, { recursive: true });
}
fs.writeFileSync(outJson, JSON.stringify(report, null, 2));
console.log(`Wrote: ${outJson}`);

// Generate Markdown
let md = `## PR Gate Summary\n\n`;
md += `**Repo:** \`${backlog.repo}\`\n`;
md += `**Generated:** ${report.generated_at}\n\n`;

md += `### Routing + Caps Report\n\n`;
md += `| Team | Open Total | Open P0/P1 | Bypassed | Cap Total | Cap P0/P1 | Status |\n`;
md += `|------|----------:|----------:|----------:|----------:|----------:|--------|\n`;

for (const [team, stats] of Object.entries(byTeam).sort((a, b) => a[0].localeCompare(b[0]))) {
  const cap = caps[team] || {};
  const capTotal = cap.max_open_total ?? "-";
  const capP0P1 = cap.max_open_p0_p1 ?? "-";

  const effectiveTotal = stats.total - stats.bypassed;
  const effectiveP0P1 = stats.items.filter(
    (x) => !x.bypassed && (x.priority === "P0" || x.priority === "P1")
  ).length;

  const totalOk = cap.max_open_total == null || effectiveTotal <= cap.max_open_total;
  const p0p1Ok = cap.max_open_p0_p1 == null || effectiveP0P1 <= cap.max_open_p0_p1;
  const status = totalOk && p0p1Ok ? "✅ OK" : "❌ VIOLATION";

  md += `| ${team} | ${stats.total} | ${stats.p0p1} | ${stats.bypassed} | ${capTotal} | ${capP0P1} | ${status} |\n`;
}

if (violations.length > 0) {
  md += `\n### ⚠️ Violations\n\n`;
  for (const v of violations) {
    md += `- **${v.team}** exceeded **${v.type}**: ${v.value} > ${v.cap}\n`;
  }
} else {
  md += `\n### ✅ No Violations\n\nAll teams within capacity limits.\n`;
}

// Summary stats
md += `\n### Summary\n\n`;
md += `- Total open issues analyzed: ${openItems.length}\n`;
md += `- Teams: ${Object.keys(byTeam).length}\n`;
md += `- Violations: ${violations.length}\n`;

// Write Markdown
const outMdDir = path.dirname(outMd);
if (outMdDir && !fs.existsSync(outMdDir)) {
  fs.mkdirSync(outMdDir, { recursive: true });
}
fs.writeFileSync(outMd, md);
console.log(`Wrote: ${outMd}`);
