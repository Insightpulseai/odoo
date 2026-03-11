/**
 * Master Seed Script - Seeds all engines
 *
 * Usage:
 *   npx tsx tools/seed_all.ts
 *   npx tsx tools/seed_all.ts --dry-run
 *   npx tsx tools/seed_all.ts --engines=te-cheq,ppm
 */

import { spawn } from 'child_process';
import * as path from 'path';

const ENGINES = [
  { name: 'te-cheq', script: 'seed_te_cheq.ts' },
  { name: 'retail-intel', script: 'seed_retail_intel.ts' },
  { name: 'ppm', script: 'seed_ppm.ts' },
  { name: 'doc-ocr', script: 'seed_doc_ocr.ts' },
];

function log(message: string) {
  console.log(`[Seed All] ${message}`);
}

async function runSeed(scriptPath: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const proc = spawn('npx', ['tsx', scriptPath, ...args], {
      stdio: 'inherit',
      cwd: process.cwd(),
    });

    proc.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Seed script exited with code ${code}`));
      }
    });

    proc.on('error', reject);
  });
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');

  // Parse --engines flag
  const enginesArg = args.find(a => a.startsWith('--engines='));
  const selectedEngines = enginesArg
    ? enginesArg.split('=')[1].split(',').map(e => e.trim())
    : ENGINES.map(e => e.name);

  log(`Starting master seed (dry-run: ${dryRun})`);
  log(`Selected engines: ${selectedEngines.join(', ')}`);

  const seedArgs = dryRun ? ['--dry-run'] : [];
  let failed = false;

  for (const engine of ENGINES) {
    if (!selectedEngines.includes(engine.name)) {
      log(`Skipping ${engine.name}`);
      continue;
    }

    log(`\n========================================`);
    log(`Seeding: ${engine.name}`);
    log(`========================================\n`);

    try {
      const scriptPath = path.join(__dirname, engine.script);
      await runSeed(scriptPath, seedArgs);
      log(`✅ ${engine.name} completed`);
    } catch (error) {
      console.error(`❌ ${engine.name} failed:`, error);
      failed = true;
      // Continue with other engines
    }
  }

  if (failed) {
    log('\n⚠️  Some seeds failed - check logs above');
    process.exit(1);
  } else {
    log('\n✅ All seeds completed successfully!');
  }
}

main().catch((error) => {
  console.error('Master seed failed:', error);
  process.exit(1);
});
