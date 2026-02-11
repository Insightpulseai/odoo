#!/usr/bin/env node

/**
 * Smoke test script - validates build output exists and is structured correctly
 */

import { existsSync, statSync } from "fs";
import { join } from "path";

const NEXT_DIR = ".next";
const REQUIRED_FILES = [
  ".next/BUILD_ID",
  ".next/build-manifest.json",
  ".next/prerender-manifest.json",
];

function main() {
  console.log("Running smoke tests...\n");

  // Check .next directory exists
  if (!existsSync(NEXT_DIR)) {
    console.error(`FAIL: ${NEXT_DIR} directory does not exist. Run 'pnpm build' first.`);
    process.exit(1);
  }

  // Check required build artifacts
  let allPassed = true;
  for (const file of REQUIRED_FILES) {
    if (existsSync(file)) {
      const stats = statSync(file);
      console.log(`OK: ${file} (${stats.size} bytes)`);
    } else {
      console.error(`FAIL: ${file} not found`);
      allPassed = false;
    }
  }

  // Check server directory
  const serverDir = join(NEXT_DIR, "server");
  if (existsSync(serverDir)) {
    console.log(`OK: ${serverDir} exists`);
  } else {
    console.error(`FAIL: ${serverDir} not found`);
    allPassed = false;
  }

  console.log("");

  if (allPassed) {
    console.log("All smoke tests passed.");
    process.exit(0);
  } else {
    console.error("Some smoke tests failed.");
    process.exit(1);
  }
}

main();
