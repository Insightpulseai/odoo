#!/usr/bin/env node
/**
 * PR Gate Enforcement Tool
 *
 * Fails the PR if caps violations are detected.
 *
 * Usage:
 *   node tools/pr-gate/enforce_gate.mjs --caps .artifacts/caps_report.json
 *
 * Exit codes:
 *   0 - Gate passed
 *   1 - Gate failed (violations detected)
 *   2 - Input error
 */

import fs from "fs";

// ============================================================================
// CLI ARGS
// ============================================================================

function arg(name, defaultValue = "") {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : defaultValue;
}

function hasFlag(name) {
  return process.argv.includes(name);
}

const capsPath = arg("--caps", ".artifacts/caps_report.json");
const strict = hasFlag("--strict");
const allowWarnings = hasFlag("--allow-warnings");

// ============================================================================
// VALIDATION
// ============================================================================

if (!fs.existsSync(capsPath)) {
  console.error(`Caps report not found: ${capsPath}`);
  console.error("Run caps_report.mjs first.");
  process.exit(2);
}

// ============================================================================
// ANALYSIS
// ============================================================================

const report = JSON.parse(fs.readFileSync(capsPath, "utf8"));
const violations = report.violations || [];

console.log("=".repeat(60));
console.log("PR GATE ENFORCEMENT");
console.log("=".repeat(60));
console.log(`Repo: ${report.repo}`);
console.log(`Generated: ${report.generated_at}`);
console.log(`Total open issues: ${report.summary?.total_open_issues || 0}`);
console.log(`Teams analyzed: ${report.summary?.teams_analyzed || 0}`);
console.log(`Violations: ${violations.length}`);
console.log("=".repeat(60));

if (violations.length > 0) {
  console.log("\n⚠️  VIOLATIONS DETECTED:\n");

  for (const v of violations) {
    console.log(`  ❌ ${v.team}: ${v.type}`);
    console.log(`     Current: ${v.value}, Cap: ${v.cap}`);
    if (v.message) {
      console.log(`     ${v.message}`);
    }
    console.log();
  }

  if (strict) {
    console.log("PR GATE FAILED: Caps violations detected (strict mode).");
    process.exit(1);
  } else if (!allowWarnings) {
    console.log("PR GATE FAILED: Caps violations detected.");
    console.log("Use --allow-warnings to proceed anyway.");
    process.exit(1);
  } else {
    console.log("⚠️  PR GATE WARNING: Proceeding with violations (--allow-warnings).");
    process.exit(0);
  }
} else {
  console.log("\n✅ PR GATE PASSED: All teams within capacity limits.\n");
  process.exit(0);
}
