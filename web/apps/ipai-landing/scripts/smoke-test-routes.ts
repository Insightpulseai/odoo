#!/usr/bin/env npx tsx
/**
 * Route & link smoke test for the InsightPulseAI landing site.
 *
 * Statically analyzes App.tsx to verify:
 * 1. Every PageId in the type union has a case in renderPage
 * 2. Every setPage('xxx') call uses a valid PageId
 * 3. No href="#" placeholders exist
 * 4. Every page component exists and is referenced
 * 5. All CTAs (Get Started, Book Demo, etc.) have onClick or href
 *
 * Run: npx tsx scripts/smoke-test-routes.ts
 */

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const APP_PATH = resolve(__dirname, '../src/App.tsx');
const source = readFileSync(APP_PATH, 'utf-8');

let failures = 0;
let passes = 0;

function assert(condition: boolean, label: string) {
  if (condition) {
    passes++;
    console.log(`  PASS  ${label}`);
  } else {
    failures++;
    console.log(`  FAIL  ${label}`);
  }
}

console.log('\n=== Route & Link Smoke Test ===\n');

// 1. Extract PageId union members
const pageIdMatch = source.match(/type PageId\s*=\s*([^;]+);/);
if (!pageIdMatch) {
  console.log('FAIL: Could not find PageId type definition');
  process.exit(1);
}
const pageIds = pageIdMatch[1].match(/'([^']+)'/g)?.map(s => s.replace(/'/g, '')) ?? [];
console.log(`Found ${pageIds.length} PageId values: ${pageIds.join(', ')}\n`);

// 2. Check every PageId has a case in renderPage
console.log('--- renderPage coverage ---');
for (const id of pageIds) {
  assert(source.includes(`case '${id}':`), `renderPage has case for '${id}'`);
}

// 3. Check every setPage('xxx') call uses a valid PageId
console.log('\n--- setPage call validity ---');
const setPageCalls = source.matchAll(/setPage\('([^']+)'\)/g);
const invalidSetPages: string[] = [];
for (const match of setPageCalls) {
  if (!pageIds.includes(match[1])) {
    invalidSetPages.push(match[1]);
  }
}
assert(invalidSetPages.length === 0, `All setPage() calls use valid PageIds${invalidSetPages.length ? ` (invalid: ${invalidSetPages.join(', ')})` : ''}`);

// Also check setPage calls in map arrays like `page: 'xxx' as PageId`
const asPageIdCalls = source.matchAll(/page:\s*'([^']+)'\s*as\s*PageId/g);
const invalidAsPages: string[] = [];
for (const match of asPageIdCalls) {
  if (!pageIds.includes(match[1])) {
    invalidAsPages.push(match[1]);
  }
}
assert(invalidAsPages.length === 0, `All 'xxx' as PageId casts use valid PageIds${invalidAsPages.length ? ` (invalid: ${invalidAsPages.join(', ')})` : ''}`);

// 4. No href="#" placeholders
console.log('\n--- No placeholder links ---');
const hrefHashCount = (source.match(/href="#"/g) || []).length;
assert(hrefHashCount === 0, `No href="#" placeholders (found ${hrefHashCount})`);

const hrefHashPoundCount = (source.match(/href=["']#[^"']*["']/g) || []).filter(h => h === 'href="#"').length;
assert(hrefHashPoundCount === 0, `No bare # hrefs (found ${hrefHashPoundCount})`);

// 5. Check that key CTA buttons have onClick or href
console.log('\n--- CTA wiring ---');
const lines = source.split('\n');
const deadCtas: string[] = [];
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (/<button/.test(line) && !/onClick/.test(line) && !/aria-label/.test(line)) {
    // Check if next line contains CTA text
    const nextLine = lines[i + 1] || '';
    const ctaWords = ['Get Started', 'Book Demo', 'Log In', 'Request', 'See Careers', 'Contact Sales', 'Watch Demo'];
    for (const word of ctaWords) {
      if (nextLine.includes(word)) {
        deadCtas.push(`line ${i + 1}: ${word}`);
      }
    }
  }
}
assert(deadCtas.length === 0, `All CTA buttons have onClick handlers${deadCtas.length ? ` (dead: ${deadCtas.join('; ')})` : ''}`);

// 6. Check mobile nav exists
console.log('\n--- Mobile nav ---');
assert(source.includes('mobileOpen'), 'Mobile nav state exists');
assert(source.includes('xl:hidden'), 'Hamburger button is hidden on desktop');
assert(source.includes('mobilNav'), 'Mobile nav handler exists');

// 7. Check URL hash sync
console.log('\n--- URL hash routing ---');
assert(source.includes('popstate'), 'Browser back/forward handler exists');
assert(source.includes('pushState'), 'Hash push on navigation exists');
assert(source.includes('pageIdFromHash'), 'Hash-to-page parser exists');

// 8. Check external URLs are real (not placeholder)
console.log('\n--- External URLs ---');
const externalUrlsMatch = source.match(/const EXTERNAL_URLS\s*=\s*\{([^}]+)\}/);
if (externalUrlsMatch) {
  const urlBlock = externalUrlsMatch[1];
  assert(!urlBlock.includes("'#'"), 'No placeholder # in EXTERNAL_URLS');
  assert(!urlBlock.includes("''"), 'No empty strings in EXTERNAL_URLS');
  assert(urlBlock.includes('https://'), 'EXTERNAL_URLS contain real https URLs');
}

// 9. Page components exist
console.log('\n--- Page components ---');
const expectedComponents = [
  'HomePage', 'ProductsPage', 'SolutionsPage', 'DocsPage', 'TrustPage',
  'ContactPage', 'MarketingPage', 'MediaPage', 'RetailPage', 'FinancePage',
  'ResourcesPage', 'PricingPage', 'CompanyPage', 'MarketingUseCasesPage',
  'MediaReferencePatternsPage', 'PrivacyPage', 'TermsPage', 'CareersPage',
  'NewsroomPage', 'LoginPage'
];
for (const comp of expectedComponents) {
  assert(source.includes(`const ${comp}`), `${comp} component exists`);
}

// Summary
console.log(`\n=== Results: ${passes} passed, ${failures} failed ===\n`);
process.exit(failures > 0 ? 1 : 0);
