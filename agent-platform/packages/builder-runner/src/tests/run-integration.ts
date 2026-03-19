#!/usr/bin/env node
/**
 * Helper to run integration tests with Azure credentials.
 * Fetches API key via az CLI and sets env vars before running tests.
 */

import { execSync } from 'node:child_process';
import { resolve } from 'node:path';

// Fetch API key via az CLI
const key = execSync(
  'az cognitiveservices account keys list -n data-intel-ph-resource -g rg-data-intel-ph --query "key1" -o tsv',
  { encoding: 'utf-8' }
).trim();

if (!key) {
  console.error('Failed to retrieve API key from Azure');
  process.exit(1);
}

// Set env vars and run the test
process.env['AZURE_AI_FOUNDRY_ENDPOINT'] = 'https://data-intel-ph-resource.cognitiveservices.azure.com/';
process.env['AZURE_AI_FOUNDRY_PROJECT'] = 'data-intel-ph';
process.env['AZURE_FOUNDRY_API_KEY'] = key;
process.env['AZURE_MODEL_DEPLOYMENT'] = 'gpt-4.1';

console.log('Environment configured:');
console.log(`  AZURE_AI_FOUNDRY_ENDPOINT: ${process.env['AZURE_AI_FOUNDRY_ENDPOINT']}`);
console.log(`  AZURE_AI_FOUNDRY_PROJECT: ${process.env['AZURE_AI_FOUNDRY_PROJECT']}`);
console.log(`  AZURE_MODEL_DEPLOYMENT: ${process.env['AZURE_MODEL_DEPLOYMENT']}`);
console.log(`  AZURE_FOUNDRY_API_KEY: ${key.slice(0, 15)}...`);
console.log('');

// Run the actual test file
const testFile = resolve(__dirname, 'foundry-integration.test.js');
execSync(`node --test "${testFile}"`, {
  stdio: 'inherit',
  env: process.env,
});
