#!/usr/bin/env node

/**
 * Asset Check Script
 * Validates that required assets for solution pages exist
 * Run: node scripts/check-assets.mjs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const publicDir = path.join(rootDir, 'public');

// Required assets for financial services page
// Set required: true for production-critical assets
// Set required: false for optional/placeholder assets
const FINANCIAL_SERVICES_ASSETS = [
  // Background
  { path: 'solutions/financial-services/bg/camo-pattern-bg.webp', required: false },

  // Hero images
  { path: 'solutions/financial-services/hero/desktop-app.webp', required: false },
  { path: 'solutions/financial-services/hero/mobile-app.webp', required: false },

  // Customer logos (SVG preferred)
  { path: 'solutions/financial-services/logos/aig.svg', required: false },
  { path: 'solutions/financial-services/logos/bnp-paribas.svg', required: false },
  { path: 'solutions/financial-services/logos/worldline.svg', required: false },
  { path: 'solutions/financial-services/logos/pnc.svg', required: false },
  { path: 'solutions/financial-services/logos/deloitte.svg', required: false },
  { path: 'solutions/financial-services/logos/kpmg.svg', required: false },

  // Use case images
  { path: 'solutions/financial-services/use-cases/q4-reporting.webp', required: false },
  { path: 'solutions/financial-services/use-cases/fraud-detection.webp', required: false },
  { path: 'solutions/financial-services/use-cases/incident-response.webp', required: false },

  // Resource thumbnails
  { path: 'solutions/financial-services/resources/balancing-the-books.webp', required: false },
  { path: 'solutions/financial-services/resources/every-minute-matters.webp', required: false },
  { path: 'solutions/financial-services/resources/mission-critical-brief.webp', required: false },
  { path: 'solutions/financial-services/resources/bank-case-study.webp', required: false },

  // Partner logos
  { path: 'solutions/financial-services/partners/carahsoft.svg', required: false },
  { path: 'solutions/financial-services/partners/hashicorp.svg', required: false },
  { path: 'solutions/financial-services/partners/redpill-linpro.svg', required: false },
  { path: 'solutions/financial-services/partners/eficode.svg', required: false },

  // OG image
  { path: 'solutions/financial-services/og-image.webp', required: false },
];

function checkAssets() {
  console.log('🔍 Checking solution page assets...\n');

  const missing = [];
  const optional = [];
  const found = [];

  for (const asset of FINANCIAL_SERVICES_ASSETS) {
    const fullPath = path.join(publicDir, asset.path);
    const exists = fs.existsSync(fullPath);

    if (exists) {
      found.push(asset.path);
    } else if (asset.required) {
      missing.push(asset.path);
    } else {
      optional.push(asset.path);
    }
  }

  // Report found assets
  if (found.length > 0) {
    console.log(`✅ Found ${found.length} assets:`);
    found.forEach((p) => console.log(`   ${p}`));
    console.log();
  }

  // Report optional missing assets
  if (optional.length > 0) {
    console.log(`⚠️  Missing ${optional.length} optional assets (using fallbacks):`);
    optional.forEach((p) => console.log(`   ${p}`));
    console.log();
  }

  // Report required missing assets
  if (missing.length > 0) {
    console.log(`❌ Missing ${missing.length} required assets:`);
    missing.forEach((p) => console.log(`   ${p}`));
    console.log();
    console.log('Please add the missing required assets before deploying.');
    process.exit(1);
  }

  console.log('✨ Asset check passed!');
  console.log(`   ${found.length} found, ${optional.length} optional missing, ${missing.length} required missing`);
}

// Ensure directories exist
function ensureDirectories() {
  const dirs = [
    'solutions/financial-services/bg',
    'solutions/financial-services/hero',
    'solutions/financial-services/logos',
    'solutions/financial-services/use-cases',
    'solutions/financial-services/resources',
    'solutions/financial-services/partners',
  ];

  for (const dir of dirs) {
    const fullPath = path.join(publicDir, dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      console.log(`📁 Created directory: ${dir}`);
    }
  }
}

// Run
ensureDirectories();
checkAssets();
