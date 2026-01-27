#!/usr/bin/env node
import fs from "node:fs";
import process from "node:process";

const schemaPath = process.argv[2];

if (!schemaPath) {
  console.error("Usage: validate_json_schema.mjs <schema.json>");
  process.exit(1);
}

if (!fs.existsSync(schemaPath)) {
  console.error(`Schema not found: ${schemaPath}`);
  process.exit(1);
}

try {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  console.log(`✓ Valid JSON schema: ${schemaPath}`);
  process.exit(0);
} catch (err) {
  console.error(`✗ Invalid JSON: ${schemaPath}`);
  console.error(err.message);
  process.exit(1);
}
