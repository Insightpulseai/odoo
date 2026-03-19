#!/usr/bin/env node
/**
 * Sync All
 * Runs all sync operations in sequence
 */

const { syncSpecToPrisma } = require('./spec-to-prisma');
const { syncSchemaToOpenAPI } = require('./schema-to-openapi');
const { syncSchemaToDocs } = require('./schema-to-docs');
const { syncDocsToKB } = require('./docs-to-kb');
const { generateMarkdown: generateTree } = require('./generate-tree');
const { generateMarkdown: generateSitemap } = require('./generate-sitemap');
const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '../..');

async function syncAll() {
  console.log('╔════════════════════════════════════════╗');
  console.log('║     InsightPulse Bidirectional Sync    ║');
  console.log('╚════════════════════════════════════════╝');
  console.log('');

  const startTime = Date.now();
  const results = [];

  // 1. Spec → Prisma
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 1: Spec → Prisma Schema');
  console.log('└─────────────────────────────────────────');
  try {
    await syncSpecToPrisma();
    results.push({ step: 'spec-to-prisma', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'spec-to-prisma', status: 'error', error: error.message });
  }
  console.log('');

  // 2. Schema → OpenAPI
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 2: Schema → OpenAPI');
  console.log('└─────────────────────────────────────────');
  try {
    await syncSchemaToOpenAPI();
    results.push({ step: 'schema-to-openapi', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'schema-to-openapi', status: 'error', error: error.message });
  }
  console.log('');

  // 3. Schema → Data Dictionary
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 3: Schema → Data Dictionary');
  console.log('└─────────────────────────────────────────');
  try {
    await syncSchemaToDocs();
    results.push({ step: 'schema-to-docs', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'schema-to-docs', status: 'error', error: error.message });
  }
  console.log('');

  // 4. Docs → KB
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 4: Docs → Knowledge Base');
  console.log('└─────────────────────────────────────────');
  try {
    await syncDocsToKB();
    results.push({ step: 'docs-to-kb', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'docs-to-kb', status: 'error', error: error.message });
  }
  console.log('');

  // 5. Generate TREE.md
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 5: Generate TREE.md');
  console.log('└─────────────────────────────────────────');
  try {
    const tree = generateTree();
    fs.writeFileSync(path.join(ROOT_DIR, 'TREE.md'), tree);
    console.log('  Generated TREE.md');
    results.push({ step: 'generate-tree', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'generate-tree', status: 'error', error: error.message });
  }
  console.log('');

  // 6. Generate SITEMAP.md
  console.log('┌─────────────────────────────────────────');
  console.log('│ Step 6: Generate SITEMAP.md');
  console.log('└─────────────────────────────────────────');
  try {
    const sitemap = generateSitemap();
    fs.writeFileSync(path.join(ROOT_DIR, 'SITEMAP.md'), sitemap);
    console.log('  Generated SITEMAP.md');
    results.push({ step: 'generate-sitemap', status: 'success' });
  } catch (error) {
    console.error('  Error:', error.message);
    results.push({ step: 'generate-sitemap', status: 'error', error: error.message });
  }
  console.log('');

  // Summary
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  const successful = results.filter(r => r.status === 'success').length;
  const failed = results.filter(r => r.status === 'error').length;

  console.log('╔════════════════════════════════════════╗');
  console.log('║              Sync Summary              ║');
  console.log('╠════════════════════════════════════════╣');
  console.log(`║  Duration: ${duration.padStart(6)}s                    ║`);
  console.log(`║  Success:  ${String(successful).padStart(6)} steps               ║`);
  console.log(`║  Failed:   ${String(failed).padStart(6)} steps               ║`);
  console.log('╚════════════════════════════════════════╝');

  // Return exit code
  return failed > 0 ? 1 : 0;
}

// Run if called directly
if (require.main === module) {
  syncAll()
    .then(code => process.exit(code))
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { syncAll };
