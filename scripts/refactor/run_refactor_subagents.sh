#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/out/refactor"
mkdir -p "${OUT}"

log(){ printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*" >&2; }

# ---- install tools (idempotent) ----
# Uses npm; swap to pnpm/yarn if needed.
install_tools() {
  log "Installing analysis tools (dev deps)…"
  npm -s i -D \
    jscpd \
    depcheck \
    ts-prune \
    eslint \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    semgrep \
    npm-audit-resolver >/dev/null 2>&1 || true
}

# ---- subagent 1: duplicates ----
dupes() {
  log "Subagent: duplicate code patterns"
  npx -s jscpd \
    --path "${ROOT}" \
    --reporters "json,markdown" \
    --output "${OUT}/dupes" \
    --ignore "**/node_modules/**,**/dist/**,**/.next/**,**/build/**,**/out/**,**/coverage/**" \
    --min-lines 8 --min-tokens 80 \
    > "${OUT}/dupes.log" 2>&1 || true
}

# ---- subagent 2: unused exports / dead code ----
deadcode() {
  log "Subagent: unused exports + dead code"
  # depcheck catches unused deps; ts-prune catches unused exports (TS projects)
  npx -s depcheck --json > "${OUT}/depcheck.json" 2> "${OUT}/depcheck.log" || true
  npx -s ts-prune -p "${ROOT}/tsconfig.json" > "${OUT}/ts-prune.txt" 2> "${OUT}/ts-prune.log" || true
}

# ---- subagent 3: error handling consistency ----
errhandling() {
  log "Subagent: error handling consistency"
  # Heuristics report: try/catch without rethrow, bare catches, console.error, etc.
  # Adjust globs as needed.
  rg -n --hidden --glob '!**/node_modules/**' --glob '!**/dist/**' --glob '!**/.next/**' \
    'catch\s*\(|throw\s+new\s+Error|console\.error|process\.exit\(|return\s+res\.status\(|new\s+(Http|Api)Error' \
    "${ROOT}" > "${OUT}/error-handling.grep.txt" || true

  # ESLint (if repo already has config, this will just run it)
  if [ -f "${ROOT}/eslint.config.js" ] || [ -f "${ROOT}/.eslintrc" ] || [ -f "${ROOT}/.eslintrc.json" ]; then
    npx -s eslint . -f json -o "${OUT}/eslint.json" > "${OUT}/eslint.log" 2>&1 || true
  else
    cat > "${OUT}/eslint-min.config.cjs" <<'JS'
module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  ignorePatterns: ["node_modules", "dist", "build", "out", ".next", "coverage"],
  rules: {
    "no-console": ["warn", { allow: ["warn", "error"] }],
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/no-throw-literal": "error"
  }
};
JS
    npx -s eslint . -c "${OUT}/eslint-min.config.cjs" -f json -o "${OUT}/eslint.json" > "${OUT}/eslint.log" 2>&1 || true
  fi
}

# ---- subagent 4: security vulnerabilities ----
security() {
  log "Subagent: security vulnerabilities"
  # npm audit
  npm -s audit --json > "${OUT}/npm-audit.json" 2> "${OUT}/npm-audit.log" || true

  # semgrep (fast baseline rules)
  npx -s semgrep --version >/dev/null 2>&1 || true
  semgrep --config=auto --json --quiet --output "${OUT}/semgrep.json" "${ROOT}" > "${OUT}/semgrep.log" 2>&1 || true
}

# ---- merge into prioritized action plan ----
compile_report() {
  log "Compiling prioritized action plan"
  node - <<'NODE'
const fs = require("fs");
const path = require("path");
const OUT = path.resolve(process.cwd(), "out/refactor");

function readJson(p){ try { return JSON.parse(fs.readFileSync(p,"utf8")); } catch { return null; } }
function readTxt(p){ try { return fs.readFileSync(p,"utf8"); } catch { return ""; } }
function exists(p){ return fs.existsSync(p); }

const dupesMd = exists(path.join(OUT,"dupes","jscpd-report.md")) ? readTxt(path.join(OUT,"dupes","jscpd-report.md")) : "";
const depcheck = readJson(path.join(OUT,"depcheck.json")) || {};
const tsprune = readTxt(path.join(OUT,"ts-prune.txt"));
const eslint = readJson(path.join(OUT,"eslint.json")) || [];
const audit = readJson(path.join(OUT,"npm-audit.json")) || {};
const semgrep = readJson(path.join(OUT,"semgrep.json")) || {};
const ehGrep = readTxt(path.join(OUT,"error-handling.grep.txt"));

const findings = [];
const add = (area, severity, title, evidence, suggestedFix) =>
  findings.push({area, severity, title, evidence, suggestedFix});

const sevRank = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };
const sortFindings = () =>
  findings.sort((a,b)=> (sevRank[b.severity]-sevRank[a.severity]) || a.area.localeCompare(b.area));

/* --- SECURITY --- */
const vulns = audit?.metadata?.vulnerabilities || null;
if (vulns) {
  for (const [k,v] of Object.entries(vulns)) {
    if (v > 0) add("security", k, `npm audit: ${v} ${k} vulnerabilities`, "out/refactor/npm-audit.json", "Patch/upgrade deps; consider overrides/resolutions; add CI gate for critical/high.");
  }
}
if (semgrep?.results?.length) {
  add("security", "high", `Semgrep findings: ${semgrep.results.length}`, "out/refactor/semgrep.json", "Triage by ruleId; fix injections, unsafe eval, SSRF, authz gaps; add semgrep baseline + CI.");
}

/* --- DEAD CODE / UNUSED --- */
if (depcheck?.dependencies?.length || depcheck?.devDependencies?.length) {
  add("dead-code", "medium", `Unused deps: ${(depcheck.dependencies||[]).length} deps, ${(depcheck.devDependencies||[]).length} devDeps`, "out/refactor/depcheck.json", "Remove unused deps; replace transitive-only imports; re-run tests.");
}
if (tsprune.trim()) {
  const lines = tsprune.trim().split("\n").slice(0, 50);
  add("dead-code", "medium", `Unused exports (ts-prune) sample: ${lines.length} lines`, "out/refactor/ts-prune.txt", "Delete/inline unused exports; or mark as public API via barrel files; ensure typecheck passes.");
}

/* --- DUPES --- */
if (dupesMd.trim()) {
  add("refactor", "low", "Duplicate code detected (jscpd)", "out/refactor/dupes/jscpd-report.md", "Extract shared helpers/components; centralize constants; prefer single DAL/utility modules.");
}

/* --- ERROR HANDLING --- */
const eslintCount = Array.isArray(eslint) ? eslint.reduce((n,f)=> n + (f.messages?.length||0), 0) : 0;
if (eslintCount > 0) {
  add("quality", "medium", `ESLint issues: ${eslintCount}`, "out/refactor/eslint.json", "Standardize error types; enforce no-console; unify API error envelopes; add lint to CI.");
}
if (ehGrep.trim()) {
  add("quality", "low", "Error-handling hotspots detected (grep heuristics)", "out/refactor/error-handling.grep.txt", "Adopt single error class + helper; consistent logging; avoid swallowing errors; unify HTTP responses.");
}

sortFindings();

const md = [];
md.push("# Codebase Refactoring Analysis — Prioritized Action Plan");
md.push("");
md.push("## Top Priorities (sorted by severity)");
md.push("");
for (const f of findings) {
  md.push(`- **[${f.severity.toUpperCase()}] ${f.area}: ${f.title}**`);
  md.push(`  - Evidence: \`${f.evidence}\``);
  md.push(`  - Suggested fix: ${f.suggestedFix}`);
}
md.push("");
md.push("## Raw Artifacts");
md.push("- `out/refactor/dupes/` (jscpd)");
md.push("- `out/refactor/depcheck.json`");
md.push("- `out/refactor/ts-prune.txt`");
md.push("- `out/refactor/eslint.json` + `eslint.log`");
md.push("- `out/refactor/npm-audit.json`");
md.push("- `out/refactor/semgrep.json`");
md.push("- `out/refactor/error-handling.grep.txt`");
md.push("");

fs.writeFileSync(path.join(OUT, "ACTION_PLAN.md"), md.join("\n"));
console.log("Wrote out/refactor/ACTION_PLAN.md");
NODE
}

main() {
  install_tools

  # Run all 4 "subagents" in parallel
  dupes & p1=$!
  deadcode & p2=$!
  errhandling & p3=$!
  security & p4=$!

  wait $p1 $p2 $p3 $p4

  compile_report
  log "Done. Open out/refactor/ACTION_PLAN.md"
}

main "$@"
