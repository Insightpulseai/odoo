#!/usr/bin/env node
// Extracts canonical Microsoft Fluent UI v9 design tokens to JSON.
// Output: design/tokens/fluent-base.json
//
// Prereq: run from a workspace where @fluentui/tokens is installed.
// Recommended host: web/packages/fluent-designer-theme
//   cd web/packages/fluent-designer-theme && pnpm add -D @fluentui/tokens
//   node ../../../scripts/design/extract_fluent_tokens.mjs

import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, '..', '..');
const OUT_PATH = resolve(REPO_ROOT, 'design', 'tokens', 'fluent-base.json');

let mod;
try {
  mod = await import('@fluentui/tokens');
} catch (err) {
  console.error('FAIL: @fluentui/tokens not installed in this workspace.');
  console.error('Run: cd web/packages/fluent-designer-theme && pnpm add -D @fluentui/tokens');
  console.error('Then re-run this script.');
  process.exit(1);
}

// @fluentui/tokens ships as CJS; ESM import surfaces real exports under .default
const t = mod.default ?? mod;

const themes = {
  webLightTheme: t.webLightTheme,
  webDarkTheme: t.webDarkTheme,
  teamsLightTheme: t.teamsLightTheme,
  teamsDarkTheme: t.teamsDarkTheme,
  teamsHighContrastTheme: t.teamsHighContrastTheme,
};

const output = {
  $schema: 'fluent-base/v1',
  source: '@fluentui/tokens',
  generatedAt: new Date().toISOString(),
  themes,
  typographyStyles: t.typographyStyles,
  tokens: t.tokens, // CSS-var references for runtime consumption
};

mkdirSync(dirname(OUT_PATH), { recursive: true });
writeFileSync(OUT_PATH, JSON.stringify(output, null, 2));

const themeKeys = Object.keys(themes);
const lt = themes.webLightTheme || {};
const ts = t.typographyStyles || {};
const cssVars = t.tokens || {};

console.log(`OK: wrote ${OUT_PATH}`);
console.log(`    themes:           ${themeKeys.join(', ')}`);
console.log(`    webLightTheme:    ${Object.keys(lt).length} resolved tokens`);
console.log(`    typographyStyles: ${Object.keys(ts).length} variants`);
console.log(`    tokens (vars):    ${Object.keys(cssVars).length} CSS vars`);
