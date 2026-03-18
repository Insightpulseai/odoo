/**
 * Ops Advisor Scorer
 *
 * Evaluates the ruleset against live platform sources and writes results
 * to ops.advisor_runs / ops.advisor_findings / ops.advisor_scores via
 * direct Supabase REST (service role key — server-only, never client).
 *
 * Usage: tsx platform/advisor/scorer.ts [--dry-run]
 */

import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { createHash } from "crypto";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Rule {
  id: string;
  pillar: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description?: string;
  remediation?: string;
  source: string;
}

interface Finding {
  rule_id: string;
  pillar: string;
  severity: string;
  fingerprint: string;
  title: string;
  description?: string;
  remediation?: string;
  resource_ref?: string;
}

type Pillar = "cost" | "security" | "reliability" | "operational_excellence" | "performance";

const SEVERITY_WEIGHT: Record<string, number> = {
  critical: 25,
  high: 10,
  medium: 5,
  low: 2,
  info: 0,
};

const PILLARS: Pillar[] = [
  "cost",
  "security",
  "reliability",
  "operational_excellence",
  "performance",
];

// ─── Supabase REST helpers ────────────────────────────────────────────────────

function supabaseHeaders(serviceRoleKey: string) {
  return {
    apikey: serviceRoleKey,
    Authorization: `Bearer ${serviceRoleKey}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
  };
}

async function supabaseInsert<T>(
  supabaseUrl: string,
  serviceRoleKey: string,
  table: string,
  row: Record<string, unknown>
): Promise<T> {
  const res = await fetch(`${supabaseUrl}/rest/v1/${table}`, {
    method: "POST",
    headers: supabaseHeaders(serviceRoleKey),
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    throw new Error(`Supabase insert into ${table} failed: ${res.status} ${await res.text()}`);
  }
  const rows: T[] = await res.json();
  return rows[0];
}

async function supabaseUpdate(
  supabaseUrl: string,
  serviceRoleKey: string,
  table: string,
  id: string,
  patch: Record<string, unknown>
): Promise<void> {
  const res = await fetch(`${supabaseUrl}/rest/v1/${table}?id=eq.${id}`, {
    method: "PATCH",
    headers: supabaseHeaders(serviceRoleKey),
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    throw new Error(`Supabase update on ${table} failed: ${res.status} ${await res.text()}`);
  }
}

// ─── Scoring ─────────────────────────────────────────────────────────────────

function computeScore(findings: Finding[], pillar: string): number {
  const pillarFindings = findings.filter((f) => f.pillar === pillar);
  if (pillarFindings.length === 0) return 100;

  const deduction = pillarFindings.reduce(
    (sum, f) => sum + (SEVERITY_WEIGHT[f.severity] ?? 0),
    0
  );
  return Math.max(0, 100 - deduction);
}

function fingerprint(ruleId: string, resourceRef: string): string {
  return createHash("sha256").update(`${ruleId}::${resourceRef}`).digest("hex").slice(0, 16);
}

// ─── Mock source evaluation (scaffold) ───────────────────────────────────────
// Real sources live in platform/advisor/sources/*.ts
// Until those are wired up, the scorer returns an empty finding list (100% health).

async function evaluateRule(_rule: Rule): Promise<Finding | null> {
  // TODO: Route to sources/vercel.ts, sources/supabase.ts, sources/digitalocean.ts
  // based on rule.source. Return null if rule passes, Finding if it fails.
  return null;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export async function runAdvisorScan(opts: {
  supabaseUrl: string;
  serviceRoleKey: string;
  teamId?: string;
  triggeredBy?: string;
  dryRun?: boolean;
}): Promise<{ runId: string; scores: Record<Pillar, number>; findingCount: number }> {
  const { supabaseUrl, serviceRoleKey, teamId = "default", triggeredBy = "system", dryRun = false } = opts;

  // Load ruleset
  const rulesetPath = join(__dirname, "ruleset.yaml");
  // Simple YAML parse (only needs to read rule ids + metadata — no complex YAML needed)
  const rulesetRaw = readFileSync(rulesetPath, "utf-8");
  const rules = parseRulesetYaml(rulesetRaw);

  console.log(`[advisor] ${rules.length} rules loaded, team=${teamId}, dry_run=${dryRun}`);

  // Create run record
  let runId = "dry-run";
  if (!dryRun) {
    const run = await supabaseInsert<{ id: string }>(
      supabaseUrl, serviceRoleKey, "ops.advisor_runs",
      { team_id: teamId, triggered_by: triggeredBy, status: "running" }
    );
    runId = run.id;
    console.log(`[advisor] Run created: ${runId}`);
  }

  // Evaluate rules
  const findings: Finding[] = [];
  for (const rule of rules) {
    const finding = await evaluateRule(rule);
    if (finding) {
      finding.fingerprint = fingerprint(finding.rule_id, finding.resource_ref ?? teamId);
      findings.push(finding);
    }
  }

  console.log(`[advisor] ${findings.length} findings`);

  // Write findings (upsert by fingerprint to avoid dupes)
  if (!dryRun && findings.length > 0) {
    for (const f of findings) {
      const res = await fetch(`${supabaseUrl}/rest/v1/ops.advisor_findings`, {
        method: "POST",
        headers: { ...supabaseHeaders(serviceRoleKey), Prefer: "resolution=merge-duplicates" },
        body: JSON.stringify({ ...f, run_id: runId }),
      });
      if (!res.ok) console.warn(`[advisor] Finding upsert failed: ${res.status}`);
    }
  }

  // Compute scores per pillar
  const scores = {} as Record<Pillar, number>;
  const findingCounts: Record<Pillar, Record<string, number>> = {} as never;

  for (const pillar of PILLARS) {
    scores[pillar] = computeScore(findings, pillar);
    const pf = findings.filter((f) => f.pillar === pillar);
    findingCounts[pillar] = {
      critical: pf.filter((f) => f.severity === "critical").length,
      high: pf.filter((f) => f.severity === "high").length,
      medium: pf.filter((f) => f.severity === "medium").length,
      low: pf.filter((f) => f.severity === "low").length,
      info: pf.filter((f) => f.severity === "info").length,
    };

    if (!dryRun) {
      await supabaseInsert(supabaseUrl, serviceRoleKey, "ops.advisor_scores", {
        run_id: runId,
        pillar,
        score: scores[pillar],
        finding_counts: findingCounts[pillar],
      });
    }
  }

  // Update run status
  if (!dryRun) {
    const summary = {
      total_findings: findings.length,
      by_severity: {
        critical: findings.filter((f) => f.severity === "critical").length,
        high: findings.filter((f) => f.severity === "high").length,
        medium: findings.filter((f) => f.severity === "medium").length,
        low: findings.filter((f) => f.severity === "low").length,
        info: findings.filter((f) => f.severity === "info").length,
      },
      by_pillar: scores,
    };
    await supabaseUpdate(supabaseUrl, serviceRoleKey, "ops.advisor_runs", runId, {
      status: "complete",
      finished_at: new Date().toISOString(),
      summary,
    });
  }

  return { runId, scores, findingCount: findings.length };
}

// ─── Minimal YAML ruleset parser ─────────────────────────────────────────────

function parseRulesetYaml(yaml: string): Rule[] {
  const rules: Rule[] = [];
  const ruleBlocks = yaml.split(/^  - id:/m).slice(1);
  for (const block of ruleBlocks) {
    const get = (key: string) =>
      block.match(new RegExp(`^    ${key}: (.+)$`, "m"))?.[1]?.trim() ?? "";
    rules.push({
      id: block.split("\n")[0].trim(),
      pillar: get("pillar"),
      severity: (get("severity") as Rule["severity"]) ?? "info",
      title: get("title").replace(/^"|"$/g, ""),
      description: get("description").replace(/^"|"$/g, "") || undefined,
      remediation: get("remediation").replace(/^"|"$/g, "") || undefined,
      source: get("source"),
    });
  }
  return rules.filter((r) => r.id && r.pillar);
}

// ─── CLI entrypoint ──────────────────────────────────────────────────────────

if (import.meta.url === `file://${process.argv[1]}`) {
  const dryRun = process.argv.includes("--dry-run");
  const supabaseUrl = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";

  if (!supabaseUrl || !serviceRoleKey) {
    console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
    process.exit(1);
  }

  runAdvisorScan({ supabaseUrl, serviceRoleKey, dryRun })
    .then(({ runId, scores, findingCount }) => {
      console.log(`\nRun: ${runId}`);
      console.log("Scores:", scores);
      console.log(`Findings: ${findingCount}`);
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
