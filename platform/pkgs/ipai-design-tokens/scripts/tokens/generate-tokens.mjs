#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Navigate to package root
const packageRoot = path.resolve(__dirname, "../..");
const tokensPath = path.join(packageRoot, "tokens/source/tokens.json");

console.log("🎨 IPAI Design Token Generator");
console.log("================================\n");

// Read master tokens
console.log(`📖 Reading tokens from: ${tokensPath}`);
const tokens = JSON.parse(fs.readFileSync(tokensPath, "utf8"));

// Flatten nested token structure
function flatten(obj, prefix = "") {
  const flat = {};
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "object" && !Array.isArray(value)) {
      Object.assign(flat, flatten(value, path));
    } else {
      flat[path] = value;
    }
  }
  return flat;
}

const flat = flatten(tokens);

// Generate CSS Variables
console.log("\n📝 Generating CSS variables...");
const cssVars = `:root {
  /* Core Banking Palette - IPAI Design System */
  /* Generated from tokens/source/tokens.json */
${Object.entries(flat)
  .map(([k, v]) => `  --ipai-${k.replace(/\./g, "-")}: ${v};`)
  .join("\n")}
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  :root {
    /* Override specific tokens for dark mode */
    --ipai-color-bg: #0B1F33;
    --ipai-color-surface: #0F2A44;
    --ipai-color-text-primary: #FFFFFF;
    --ipai-color-text-secondary: #B8C7D6;
    --ipai-color-border: #1A3A5A;
  }
}
`;

// Generate Tailwind Preset
console.log("📝 Generating Tailwind preset...");
const tailwindPreset = `/**
 * IPAI Design Tokens - Tailwind CSS Preset
 * Auto-generated from tokens/source/tokens.json
 * DO NOT EDIT MANUALLY - Run 'pnpm generate:tokens' to regenerate
 */
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: "${tokens.color.bg}",
        surface: "${tokens.color.surface}",
        canvas: "${tokens.color.canvas}",
        primary: "${tokens.color.primary}",
        "primary-deep": "${tokens.color.primaryDeep}",
        "primary-hover": "${tokens.color.primaryHover}",
        accent: {
          green: "${tokens.color.accent.green}",
          "green-hover": "${tokens.color.accent.greenHover}",
          teal: "${tokens.color.accent.teal}",
          "teal-hover": "${tokens.color.accent.tealHover}",
          amber: "${tokens.color.accent.amber}",
          "amber-hover": "${tokens.color.accent.amberHover}",
        },
        semantic: {
          success: "${tokens.color.semantic.success}",
          warning: "${tokens.color.semantic.warning}",
          error: "${tokens.color.semantic.error}",
          info: "${tokens.color.semantic.info}",
        },
        border: "${tokens.color.border}",
        "border-light": "${tokens.color.borderLight}",
        "border-dark": "${tokens.color.borderDark}",
        text: {
          primary: "${tokens.color.text.primary}",
          secondary: "${tokens.color.text.secondary}",
          tertiary: "${tokens.color.text.tertiary}",
          "on-accent": "${tokens.color.text.onAccent}",
        },
      },
      spacing: {
        gap: "${tokens.spacing.gap}",
        "gap-sm": "${tokens.spacing.gapSm}",
        "gap-lg": "${tokens.spacing.gapLg}",
      },
      borderRadius: {
        DEFAULT: "${tokens.radius.default}",
        sm: "${tokens.radius.sm}",
        lg: "${tokens.radius.lg}",
        full: "${tokens.radius.full}",
      },
      boxShadow: {
        DEFAULT: "${tokens.shadow.default}",
        soft: "${tokens.shadow.soft}",
        lg: "${tokens.shadow.lg}",
        inner: "${tokens.shadow.inner}",
      },
      fontFamily: {
        sans: ${JSON.stringify(tokens.typography.fontFamily.base.split(", "))},
        mono: ${JSON.stringify(tokens.typography.fontFamily.mono.split(", "))},
      },
    },
  },
};
`;

// Generate TypeScript Exports
console.log("📝 Generating TypeScript exports...");
const tsExports = `/**
 * IPAI Design Tokens - TypeScript Exports
 * Auto-generated from tokens/source/tokens.json
 * DO NOT EDIT MANUALLY - Run 'pnpm generate:tokens' to regenerate
 */

export const tokens = ${JSON.stringify(tokens, null, 2)} as const;

export type Tokens = typeof tokens;

// Convenience type exports
export type ColorTokens = typeof tokens.color;
export type SpacingTokens = typeof tokens.spacing;
export type RadiusTokens = typeof tokens.radius;
export type ShadowTokens = typeof tokens.shadow;
export type TypographyTokens = typeof tokens.typography;

// Individual token access with type safety
export const color = tokens.color;
export const spacing = tokens.spacing;
export const radius = tokens.radius;
export const shadow = tokens.shadow;
export const typography = tokens.typography;

// Default export
export default tokens;
`;

// Write generated files
const cssPath = path.join(packageRoot, "css-vars.css");
const tailwindPath = path.join(packageRoot, "tailwind.preset.cjs");
const srcDir = path.join(packageRoot, "src");
const tsPath = path.join(srcDir, "index.ts");

// Ensure src directory exists
if (!fs.existsSync(srcDir)) {
  fs.mkdirSync(srcDir, { recursive: true });
}

console.log(`\n✍️  Writing files...`);
fs.writeFileSync(cssPath, cssVars);
console.log(`   ✅ ${cssPath}`);

fs.writeFileSync(tailwindPath, tailwindPreset);
console.log(`   ✅ ${tailwindPath}`);

fs.writeFileSync(tsPath, tsExports);
console.log(`   ✅ ${tsPath}`);

console.log(`\n✨ Token generation complete!`);
console.log(`\n📊 Summary:`);
console.log(`   - ${Object.keys(flat).length} total tokens`);
console.log(`   - ${Object.keys(tokens.color).length} color categories`);
console.log(`   - ${Object.keys(tokens.spacing).length} spacing tokens`);
console.log(`   - ${Object.keys(tokens.radius).length} radius tokens`);
console.log(`   - ${Object.keys(tokens.shadow).length} shadow tokens`);
console.log(`\n💡 Next steps:`);
console.log(`   1. Update package.json with "generate:tokens" script`);
console.log(`   2. Run 'pnpm generate:tokens' to test`);
console.log(`   3. Update apps to use generated tokens`);
console.log(`\n🎯 Files generated:`);
console.log(`   - css-vars.css (CSS custom properties)`);
console.log(`   - tailwind.preset.cjs (Tailwind config)`);
console.log(`   - src/index.ts (TypeScript exports)`);
