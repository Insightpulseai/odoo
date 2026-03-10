/**
 * Fluent 2 Design Tokens Build Script
 *
 * Generates CSS variables from Microsoft Fluent 2 design tokens.
 * Output files:
 *   - dist/fluent.css     (CSS custom properties for light/dark themes)
 *   - dist/tokens.json    (Raw tokens for tooling)
 *   - dist/tailwind-preset.cjs (Tailwind CSS preset bridging tokens)
 *
 * @see https://fluent2.microsoft.design/design-tokens
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import fluentTokens from "@fluentui/tokens";

const { tokens, webLightTheme, webDarkTheme } = fluentTokens;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Convert a Fluent theme object to CSS custom properties
 */
function toCssVars(
  theme: Record<string, unknown>,
  selector: string
): string {
  const lines = Object.entries(theme)
    .filter(([, v]) => typeof v === "string" || typeof v === "number")
    .map(([k, v]) => `  --${k}: ${v};`);
  return `${selector} {\n${lines.join("\n")}\n}\n`;
}

/**
 * Generate Tailwind preset that references CSS variables
 */
function generateTailwindPreset(theme: Record<string, unknown>): string {
  // Extract color tokens (those containing 'color' in name or starting with specific prefixes)
  const colorTokens = Object.entries(theme)
    .filter(
      ([k, v]) =>
        typeof v === "string" &&
        (k.toLowerCase().includes("color") ||
          k.startsWith("colorNeutral") ||
          k.startsWith("colorBrand") ||
          k.startsWith("colorPalette") ||
          k.startsWith("colorStatus") ||
          k.startsWith("colorCompound"))
    )
    .reduce(
      (acc, [k]) => {
        // Convert camelCase to kebab-case for Tailwind
        const kebabKey = k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
        acc[kebabKey] = `var(--${k})`;
        return acc;
      },
      {} as Record<string, string>
    );

  // Extract spacing tokens
  const spacingTokens = Object.entries(theme)
    .filter(
      ([k, v]) =>
        (typeof v === "string" || typeof v === "number") &&
        (k.startsWith("spacing") || k.startsWith("stroke"))
    )
    .reduce(
      (acc, [k]) => {
        const kebabKey = k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
        acc[kebabKey] = `var(--${k})`;
        return acc;
      },
      {} as Record<string, string>
    );

  // Extract border radius tokens
  const radiusTokens = Object.entries(theme)
    .filter(([k]) => k.startsWith("borderRadius"))
    .reduce(
      (acc, [k]) => {
        const kebabKey = k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
        acc[kebabKey] = `var(--${k})`;
        return acc;
      },
      {} as Record<string, string>
    );

  // Extract shadow tokens
  const shadowTokens = Object.entries(theme)
    .filter(([k]) => k.startsWith("shadow"))
    .reduce(
      (acc, [k]) => {
        const kebabKey = k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
        acc[kebabKey] = `var(--${k})`;
        return acc;
      },
      {} as Record<string, string>
    );

  // Extract font tokens
  const fontTokens = Object.entries(theme)
    .filter(([k]) => k.startsWith("fontFamily"))
    .reduce(
      (acc, [k]) => {
        const kebabKey = k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
        acc[kebabKey] = `var(--${k})`;
        return acc;
      },
      {} as Record<string, string>
    );

  return `/**
 * Fluent 2 Design Tokens - Tailwind CSS Preset
 *
 * Auto-generated from @fluentui/tokens
 * Usage in tailwind.config.js:
 *   const preset = require("@ipai/design-tokens/dist/tailwind-preset.cjs");
 *   module.exports = { presets: [preset], ... }
 *
 * @see https://fluent2.microsoft.design/design-tokens
 */

module.exports = {
  theme: {
    extend: {
      colors: {
        fluent: ${JSON.stringify(colorTokens, null, 8).replace(/^/gm, "        ").trim()}
      },
      spacing: ${JSON.stringify(spacingTokens, null, 8).replace(/^/gm, "      ").trim()},
      borderRadius: ${JSON.stringify(radiusTokens, null, 8).replace(/^/gm, "      ").trim()},
      boxShadow: ${JSON.stringify(shadowTokens, null, 8).replace(/^/gm, "      ").trim()},
      fontFamily: ${JSON.stringify(fontTokens, null, 8).replace(/^/gm, "      ").trim()}
    }
  }
};
`;
}

/**
 * Main build function
 */
function build(): void {
  const outDir = path.resolve(__dirname, "../dist");
  fs.mkdirSync(outDir, { recursive: true });

  console.log("Building Fluent 2 design tokens...");

  // Generate CSS with light and dark themes
  const cssContent = `/**
 * Fluent 2 Design Tokens (CSS Custom Properties)
 *
 * Auto-generated from @fluentui/tokens
 * Source: https://fluent2.microsoft.design/design-tokens
 *
 * Usage:
 *   <html data-theme="light"> or <html data-theme="dark">
 *   Then reference tokens as: var(--colorBrandBackground)
 */

/* Light theme (default) */
${toCssVars(webLightTheme as unknown as Record<string, unknown>, ':root, :root[data-theme="light"]')}
/* Dark theme */
${toCssVars(webDarkTheme as unknown as Record<string, unknown>, ':root[data-theme="dark"]')}
/* System preference detection */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
${Object.entries(webDarkTheme as unknown as Record<string, unknown>)
  .filter(([, v]) => typeof v === "string" || typeof v === "number")
  .map(([k, v]) => `    --${k}: ${v};`)
  .join("\n")}
  }
}
`;

  fs.writeFileSync(path.join(outDir, "fluent.css"), cssContent, "utf8");
  console.log("  ✓ dist/fluent.css");

  // Generate tokens JSON
  fs.writeFileSync(
    path.join(outDir, "tokens.json"),
    JSON.stringify(
      {
        meta: {
          source: "@fluentui/tokens",
          generatedAt: new Date().toISOString(),
          documentation: "https://fluent2.microsoft.design/design-tokens",
        },
        tokens,
        themes: {
          light: webLightTheme,
          dark: webDarkTheme,
        },
      },
      null,
      2
    ),
    "utf8"
  );
  console.log("  ✓ dist/tokens.json");

  // Generate Tailwind preset
  const tailwindPreset = generateTailwindPreset(
    webLightTheme as unknown as Record<string, unknown>
  );
  fs.writeFileSync(
    path.join(outDir, "tailwind-preset.cjs"),
    tailwindPreset,
    "utf8"
  );
  console.log("  ✓ dist/tailwind-preset.cjs");

  console.log("\nBuild complete!");
}

build();
