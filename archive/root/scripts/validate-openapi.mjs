#!/usr/bin/env node
/**
 * OpenAPI Contract Validator
 *
 * Validates that OpenAPI contracts meet the Lakehouse Executor Contract requirements.
 *
 * Usage:
 *   node scripts/validate-openapi.mjs contracts/lakehouse-executor.openapi.yaml
 */

import fs from "node:fs";
import path from "node:path";

const REQUIRED_PATHS = [
  "/v1/health",
  "/v1/runs",
  "/v1/runs/{run_id}",
];

const REQUIRED_SCHEMAS = [
  "RunSubmit",
  "RunAccepted",
  "RunStatus",
];

function die(msg, code = 1) {
  console.error(`[openapi-validate] FAIL: ${msg}`);
  process.exit(code);
}

function main() {
  const file = process.argv[2];

  if (!file) {
    console.error("Usage: node scripts/validate-openapi.mjs <openapi.yaml>");
    process.exit(2);
  }

  if (!fs.existsSync(file)) {
    die(`File not found: ${file}`);
  }

  const txt = fs.readFileSync(file, "utf8");

  // Check OpenAPI version
  if (!txt.includes("openapi: 3.")) {
    die("OpenAPI file missing 'openapi: 3.x.x' version declaration");
  }

  // Check required paths
  for (const reqPath of REQUIRED_PATHS) {
    // Handle path variations (with or without quotes, with colon)
    const pathPatterns = [
      `${reqPath}:`,
      `"${reqPath}":`,
      `'${reqPath}':`,
    ];

    const found = pathPatterns.some(p => txt.includes(p));
    if (!found) {
      die(`Contract missing required path: ${reqPath}`);
    }
  }

  // Check required schemas
  for (const schema of REQUIRED_SCHEMAS) {
    if (!txt.includes(schema)) {
      die(`Contract missing required schema: ${schema}`);
    }
  }

  // Check for info section
  if (!txt.includes("info:")) {
    die("Contract missing 'info:' section");
  }

  // Check for title
  if (!txt.includes("title:")) {
    die("Contract missing 'title:' in info section");
  }

  // Check for version
  if (!txt.includes("version:")) {
    die("Contract missing 'version:' in info section");
  }

  // Check components section exists
  if (!txt.includes("components:")) {
    die("Contract missing 'components:' section");
  }

  // Check schemas section exists
  if (!txt.includes("schemas:")) {
    die("Contract missing 'schemas:' section under components");
  }

  console.log("[openapi-validate] OK: Contract structure valid");
  console.log(`  - OpenAPI 3.x declaration: present`);
  console.log(`  - Required paths: ${REQUIRED_PATHS.length} found`);
  console.log(`  - Required schemas: ${REQUIRED_SCHEMAS.length} found`);
}

main();
