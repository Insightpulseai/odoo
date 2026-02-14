#!/usr/bin/env node
import { Command } from "commander";
import fg from "fast-glob";
import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";
import { spawnSync } from "node:child_process";
import fetch from "node-fetch";
import { createClient } from "@supabase/supabase-js";

type Severity = "low" | "medium" | "high";
type Check =
  | { type: "glob_exists"; pattern: string; must_contain_regex?: string }
  | { type: "any_file_exists"; paths: string[] }
  | { type: "deny_glob"; pattern: string }
  | { type: "repo_regex_deny"; regex: string };

type Control = {
  id: string;
  title: string;
  severity: Severity;
  checks: Check[];
};

type ParityConfig = { controls: Control[] };

type Finding = {
  control_id: string;
  title: string;
  severity: Severity;
  status: "pass" | "fail";
  detail: string;
};

type CrawlResult = {
  url: string;
  status: "ok" | "error";
  markdown?: string;
  error?: string;
};

const program = new Command();

program
  .name("agentic-codebase-crawler")
  .description("Repo scan → detect missing parity controls → generate patch set → verify → emit artifacts into ops.*")
  .option("--repo-root <path>", "Repository root", process.cwd())
  .option("--config <path>", "Parity config YAML", "packages/agentic-codebase-crawler/templates/parity-controls.yml")
  .option("--out <path>", "Output dir", "ops/agentic-codebase-crawler/out")
  .option("--apply", "Apply generated patches", false)
  .option("--verify-cmd <cmd>", "Verification command (quoted)", "echo 'No verify command specified'")
  .option("--crawl-url <url...>", "Optional: crawl URLs and attach extracted markdown as artifacts")
  .option("--firecrawl-base <url>", "Firecrawl base URL", process.env.FIRECRAWL_BASE_URL || "https://api.firecrawl.dev")
  .option("--firecrawl-key <key>", "Firecrawl API key", process.env.FIRECRAWL_API_KEY || "")
  .option("--supabase-url <url>", "Supabase URL", process.env.SUPABASE_URL || "")
  .option("--supabase-service-role <key>", "Supabase service role key", process.env.SUPABASE_SERVICE_ROLE_KEY || "")
  .option("--actor <actor>", "Run actor (github-actions/local/n8n)", process.env.CRAWLER_ACTOR || "local")
  .option("--repo <repo>", "Repo identifier", process.env.GITHUB_REPOSITORY || "unknown")
  .option("--ref <ref>", "Git ref/sha", process.env.GITHUB_SHA || "unknown")
  .option("--skip-verify", "Skip verification step", false)
  .option("--skip-ops-emit", "Skip emitting to ops schema", false)
  .parse(process.argv);

const opts = program.opts();

function readText(p: string): string {
  return fs.readFileSync(p, "utf8");
}

function ensureDir(p: string) {
  fs.mkdirSync(p, { recursive: true });
}

function writeFile(p: string, content: string) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, content, "utf8");
}

function loadConfig(cfgPath: string): ParityConfig {
  const abs = path.isAbsolute(cfgPath) ? cfgPath : path.join(opts.repoRoot, cfgPath);
  if (!fs.existsSync(abs)) {
    throw new Error(`Config file not found: ${abs}`);
  }
  const doc = yaml.load(readText(abs)) as Record<string, unknown>;
  if (!doc || !Array.isArray(doc.controls)) {
    throw new Error(`Invalid config: ${abs}`);
  }
  return doc as ParityConfig;
}

function repoHasFile(repoRoot: string, rel: string): boolean {
  return fs.existsSync(path.join(repoRoot, rel));
}

function globMatches(repoRoot: string, pattern: string): string[] {
  return fg.sync(pattern, { cwd: repoRoot, dot: true, onlyFiles: true });
}

function checkControl(repoRoot: string, c: Control): Finding[] {
  const findings: Finding[] = [];
  for (const chk of c.checks) {
    if (chk.type === "glob_exists") {
      const matches = globMatches(repoRoot, chk.pattern);
      if (matches.length === 0) {
        findings.push({
          control_id: c.id,
          title: c.title,
          severity: c.severity,
          status: "fail",
          detail: `No files matched glob: ${chk.pattern}`
        });
        continue;
      }
      if (chk.must_contain_regex) {
        const re = new RegExp(chk.must_contain_regex);
        const ok = matches.some((m) => re.test(readText(path.join(repoRoot, m))));
        findings.push({
          control_id: c.id,
          title: c.title,
          severity: c.severity,
          status: ok ? "pass" : "fail",
          detail: ok
            ? `Matched content regex in at least one file for glob: ${chk.pattern}`
            : `Files exist but did not match regex: ${chk.must_contain_regex}`
        });
      } else {
        findings.push({
          control_id: c.id,
          title: c.title,
          severity: c.severity,
          status: "pass",
          detail: `Found ${matches.length} file(s) for glob: ${chk.pattern}`
        });
      }
    }

    if (chk.type === "any_file_exists") {
      const found = chk.paths.find((p) => repoHasFile(repoRoot, p));
      findings.push({
        control_id: c.id,
        title: c.title,
        severity: c.severity,
        status: found ? "pass" : "fail",
        detail: found ? `Found: ${found}` : `None found: ${chk.paths.join(", ")}`
      });
    }

    if (chk.type === "deny_glob") {
      const matches = globMatches(repoRoot, chk.pattern);
      findings.push({
        control_id: c.id,
        title: c.title,
        severity: c.severity,
        status: matches.length === 0 ? "pass" : "fail",
        detail: matches.length === 0 ? `No forbidden matches for: ${chk.pattern}` : `Forbidden files present: ${matches.slice(0, 10).join(", ")}`
      });
    }

    if (chk.type === "repo_regex_deny") {
      const files = fg.sync(["**/*.*"], {
        cwd: repoRoot,
        dot: true,
        onlyFiles: true,
        ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**"]
      });
      const re = new RegExp(chk.regex);
      const hits: string[] = [];
      for (const f of files) {
        const p = path.join(repoRoot, f);
        try {
          const stat = fs.statSync(p);
          if (stat.size > 2_000_000) continue; // skip huge files
          const t = readText(p);
          if (re.test(t)) {
            hits.push(f);
            if (hits.length >= 10) break;
          }
        } catch {
          // Skip unreadable files
        }
      }
      findings.push({
        control_id: c.id,
        title: c.title,
        severity: c.severity,
        status: hits.length === 0 ? "pass" : "fail",
        detail: hits.length === 0 ? `No regex hits for: ${chk.regex}` : `Regex hits (sample): ${hits.join(", ")}`
      });
    }
  }
  return findings;
}

function generatePatchSet(repoRoot: string, outDir: string, findings: Finding[]) {
  // Minimal "starter patch": create placeholder docs for failed controls
  const failed = findings.filter(f => f.status === "fail");
  const patchPlan: { file: string; content: string }[] = [];

  for (const f of failed) {
    if (f.control_id === "audit-logging") {
      patchPlan.push({
        file: "docs/security/AUDIT_LOGS.md",
        content:
`# Audit Logs (Parity Control)

This repo enforces an audit logging posture across:
- DB-level changes (DDL, privileged ops)
- Auth events (sign-in, token refresh, role changes)
- Admin/ops actions (migrations, secrets rotation, deploys)

## References
- Supabase Audit Logs documentation (platform feature)

## Implementation Checklist
- [ ] Enable/verify database logging strategy (extension or event sink)
- [ ] Export logs to centralized system (log drain)
- [ ] Confirm retention policy + access controls
`
      });
    }

    if (f.control_id === "network-restrictions") {
      patchPlan.push({
        file: "docs/security/NETWORK_RESTRICTIONS.md",
        content:
`# Network Restrictions (Parity Control)

This repo must document and enforce network restrictions where applicable:
- Restrict database ingress to known IP ranges / private networks
- Enforce TLS/SSL
- Ensure admin endpoints are not public

## References
- Supabase Network Restrictions documentation

## Implementation Checklist
- [ ] Define allowed IP ranges (prod + staging)
- [ ] Validate restriction is active for database connectivity
- [ ] Document exception process
`
      });
    }

    if (f.control_id === "backups-pitr") {
      patchPlan.push({
        file: "docs/ops/BACKUPS_RESTORE.md",
        content:
`# Backups & Restore Drill (Parity Control)

## Goals
- Ensure PITR/backups are configured
- Ensure restore drills are documented and tested

## Checklist
- [ ] Backup schedule confirmed
- [ ] Restore drill runbook exists
- [ ] Quarterly restore test recorded in ops.artifacts
`
      });
    }

    if (f.control_id === "agents-contract" && !repoHasFile(repoRoot, "AGENTS.md")) {
      patchPlan.push({
        file: "AGENTS.md",
        content:
`# Agent Operating Contract (SSOT)

## Canonical Workflow
1) Read Spec Kit (spec/<slug>/*) + spec/platforms/*
2) Implement scripts + config deterministically
3) Add tests + drift checks
4) Update runbooks
5) CI must reproduce locally

## Required outputs for any platform change
- Apply commands
- Test/verify commands
- Deploy/rollback commands
- Production validation commands

## Where to write things
- specs: spec/
- runbooks: docs/runbooks/
- scripts: scripts/
- workflows: .github/workflows/
`
      });
    }
  }

  ensureDir(outDir);
  const planPath = path.join(outDir, "patch-plan.json");
  writeFile(planPath, JSON.stringify({ generated_at: new Date().toISOString(), files: patchPlan }, null, 2));

  // Emit a unified patch script
  const patchScriptPath = path.join(outDir, "apply-patch.sh");
  const lines: string[] = [];
  lines.push("#!/usr/bin/env bash");
  lines.push("set -euo pipefail");
  lines.push("");
  lines.push("# Auto-generated patch script from agentic-codebase-crawler");
  lines.push(`# Generated: ${new Date().toISOString()}`);
  lines.push("");

  for (const p of patchPlan) {
    lines.push(`mkdir -p "$(dirname "${p.file}")"`);
    lines.push(`cat > "${p.file}" <<'PATCHEOF'`);
    lines.push(p.content);
    lines.push("PATCHEOF");
    lines.push("");
  }

  lines.push(`echo "[patch] Applied ${patchPlan.length} file(s)."`);

  writeFile(patchScriptPath, lines.join("\n") + "\n");
  fs.chmodSync(patchScriptPath, 0o755);

  return { planPath, patchScriptPath, patchCount: patchPlan.length };
}

async function firecrawlScrape(url: string, baseUrl: string, apiKey: string): Promise<CrawlResult> {
  if (!apiKey) return { url, status: "error", error: "FIRECRAWL_API_KEY missing" };
  try {
    const res = await fetch(`${baseUrl.replace(/\/$/, "")}/v2/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
      body: JSON.stringify({ url, formats: ["markdown"] })
    });
    if (!res.ok) return { url, status: "error", error: `HTTP ${res.status}: ${await res.text()}` };
    const data = (await res.json()) as Record<string, unknown>;
    const innerData = data?.data as Record<string, unknown> | undefined;
    const md = (innerData?.markdown ?? data?.markdown ?? "") as string;
    return { url, status: "ok", markdown: md };
  } catch (e: unknown) {
    const err = e as Error;
    return { url, status: "error", error: err?.message || String(e) };
  }
}

function runVerify(cmd: string, repoRoot: string) {
  console.log(`[verify] Running: ${cmd}`);
  const parts = cmd.split(" ");
  const proc = spawnSync(parts[0], parts.slice(1), { cwd: repoRoot, stdio: "inherit", env: process.env, shell: true });
  return { ok: proc.status === 0, code: proc.status ?? -1 };
}

async function emitToOps(run: {
  supabaseUrl: string;
  serviceRole: string;
  actor: string;
  repo: string;
  ref: string;
}, payload: {
  findings: Finding[];
  patchPlanPath: string;
  patchScriptPath: string;
  verify: { ok: boolean; code: number };
  crawls: CrawlResult[];
  outDir: string;
}) {
  if (!run.supabaseUrl || !run.serviceRole) {
    console.log("[ops] Skipping ops emit: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set");
    return;
  }

  console.log("[ops] Emitting to ops schema...");
  const sb = createClient(run.supabaseUrl, run.serviceRole, { auth: { persistSession: false } });

  // Try using RPC first, fallback to direct insert
  let runId: string;
  try {
    const { data, error } = await sb.rpc("start_run", {
      p_actor: run.actor,
      p_repo: run.repo,
      p_ref: run.ref,
      p_pack_id: "agentic-codebase-crawler",
      p_input: { tool: "agentic-codebase-crawler", outDir: payload.outDir }
    });
    if (error) throw error;
    runId = data as string;
  } catch {
    // Fallback: direct insert to ops.runs
    const { data: runRow, error: runErr } = await sb.from("runs").insert({
      status: payload.verify.ok ? "completed" : "failed",
      actor: run.actor,
      repo: run.repo,
      ref: run.ref,
      pack_id: "agentic-codebase-crawler",
      input: { tool: "agentic-codebase-crawler", outDir: payload.outDir },
      output: {}
    }).select("id").single();

    if (runErr) throw runErr;
    runId = runRow.id as string;
  }

  const report = {
    generated_at: new Date().toISOString(),
    summary: {
      pass: payload.findings.filter(f => f.status === "pass").length,
      fail: payload.findings.filter(f => f.status === "fail").length
    },
    findings: payload.findings,
    verify: payload.verify,
    patchPlan: JSON.parse(readText(payload.patchPlanPath)),
    crawls: payload.crawls.map(c => ({ url: c.url, status: c.status, error: c.error, markdown_len: c.markdown?.length ?? 0 }))
  };

  // Try RPC first, fallback to direct insert
  try {
    await sb.rpc("add_artifact", {
      p_run_id: runId,
      p_kind: "report",
      p_uri: null,
      p_meta: { name: "parity-report.json", content: JSON.stringify(report, null, 2) }
    });
  } catch {
    await sb.from("artifacts").insert([
      { run_id: runId, kind: "report", uri: null, meta: { name: "parity-report.json", content: JSON.stringify(report, null, 2) } },
      { run_id: runId, kind: "diff", uri: null, meta: { name: "apply-patch.sh", content: readText(payload.patchScriptPath) } }
    ]);
  }

  for (const c of payload.crawls) {
    const content = c.status === "ok" ? (c.markdown ?? "") : (c.error ?? "");
    try {
      await sb.rpc("add_artifact", {
        p_run_id: runId,
        p_kind: "crawl",
        p_uri: c.url,
        p_meta: { name: `crawl-${c.url.replace(/https?:\/\//, "").replace(/[^\w.-]+/g, "_")}.md`, content, status: c.status }
      });
    } catch {
      // Best effort
    }
  }

  // Complete the run
  try {
    await sb.rpc("complete_run", {
      p_run_id: runId,
      p_output: report
    });
  } catch {
    // Best effort
  }

  console.log(`[ops] Emitted run: ${runId}`);
}

async function main() {
  console.log("=== Agentic Codebase Crawler ===");
  console.log(`[config] repo-root: ${opts.repoRoot}`);
  console.log(`[config] config: ${opts.config}`);
  console.log(`[config] out: ${opts.out}`);

  const repoRoot = path.resolve(opts.repoRoot);
  const outDir = path.resolve(repoRoot, opts.out);
  ensureDir(outDir);

  // Load parity controls config
  console.log("\n[1/5] Loading parity controls...");
  const cfg = loadConfig(opts.config);
  console.log(`[1/5] Loaded ${cfg.controls.length} controls`);

  // Check all controls
  console.log("\n[2/5] Checking controls...");
  const findings = cfg.controls.flatMap((c) => checkControl(repoRoot, c));
  const summary = {
    pass: findings.filter(f => f.status === "pass").length,
    fail: findings.filter(f => f.status === "fail").length,
    total: findings.length
  };

  console.log(`[2/5] Results: ${summary.pass} pass, ${summary.fail} fail`);

  // Print findings
  for (const f of findings) {
    const icon = f.status === "pass" ? "✓" : "✗";
    const sev = f.severity === "high" ? "HIGH" : f.severity === "medium" ? "MED" : "LOW";
    console.log(`  ${icon} [${sev}] ${f.control_id}: ${f.title}`);
    if (f.status === "fail") {
      console.log(`      ${f.detail}`);
    }
  }

  writeFile(path.join(outDir, "findings.json"), JSON.stringify({ summary, findings }, null, 2));

  // Generate patch set
  console.log("\n[3/5] Generating patch set...");
  const { planPath, patchScriptPath, patchCount } = generatePatchSet(repoRoot, outDir, findings);
  console.log(`[3/5] Generated ${patchCount} patch file(s)`);

  if (opts.apply && patchCount > 0) {
    console.log("[3/5] Applying patches...");
    spawnSync("bash", [patchScriptPath], { cwd: repoRoot, stdio: "inherit" });
  }

  // Optional: Firecrawl URLs
  const crawls: CrawlResult[] = [];
  if (Array.isArray(opts.crawlUrl) && opts.crawlUrl.length > 0) {
    console.log("\n[4/5] Crawling URLs...");
    for (const u of opts.crawlUrl) {
      console.log(`  Crawling: ${u}`);
      crawls.push(await firecrawlScrape(u, opts.firecrawlBase, opts.firecrawlKey));
    }
    writeFile(path.join(outDir, "crawls.json"), JSON.stringify(crawls, null, 2));
  } else {
    console.log("\n[4/5] No URLs to crawl (skipped)");
  }

  // Run verification
  let verify = { ok: true, code: 0 };
  if (!opts.skipVerify) {
    console.log("\n[5/5] Running verification...");
    verify = runVerify(String(opts.verifyCmd), repoRoot);
    console.log(`[5/5] Verification ${verify.ok ? "PASSED" : "FAILED"} (code: ${verify.code})`);
  } else {
    console.log("\n[5/5] Verification skipped");
  }
  writeFile(path.join(outDir, "verify.json"), JSON.stringify(verify, null, 2));

  // Emit to ops.* (optional)
  if (!opts.skipOpsEmit) {
    try {
      await emitToOps({
        supabaseUrl: String(opts.supabaseUrl),
        serviceRole: String(opts.supabaseServiceRole),
        actor: String(opts.actor),
        repo: String(opts.repo),
        ref: String(opts.ref),
      }, { findings, patchPlanPath: planPath, patchScriptPath, verify, crawls, outDir });
    } catch (e: unknown) {
      const err = e as Error;
      // Do not fail the run if ops emission fails (treat as best-effort)
      console.log(`[ops] Emission failed (best-effort): ${err?.message || String(e)}`);
      writeFile(path.join(outDir, "ops_emit_error.txt"), err?.message || String(e));
    }
  }

  // Summary
  console.log("\n=== Summary ===");
  console.log(`Controls: ${summary.pass}/${summary.total} passed`);
  console.log(`Patches: ${patchCount} generated`);
  console.log(`Verify: ${verify.ok ? "PASSED" : "FAILED"}`);
  console.log(`Output: ${outDir}`);

  const exitCode = summary.fail > 0 ? 1 : (verify.ok ? 0 : 2);
  process.exit(exitCode);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
