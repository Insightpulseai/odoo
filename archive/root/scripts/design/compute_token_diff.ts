#!/usr/bin/env -S npx tsx
/**
 * Token Diff Computation Script
 *
 * Computes the difference between Figma-exported tokens and the SSOT tokens.json.
 * Generates both JSON and Markdown outputs for CI gates and PR comments.
 *
 * Usage:
 *   ./scripts/design/compute_token_diff.ts --figma <contract.json> --baseline <tokens.json>
 *
 * Outputs:
 *   - ops/design/token_diff.json (machine-readable)
 *   - ops/design/token_diff.md (PR comment ready)
 */

import * as fs from "fs";
import * as path from "path";

// ============================================================================
// TYPES
// ============================================================================

interface FigmaContract {
  tokens_touched: {
    colors?: string[];
    spacing?: string[];
    typography?: string[];
    shadows?: string[];
    radii?: string[];
    other?: string[];
  };
}

interface TokensJson {
  colors?: Record<string, unknown>;
  spacing?: Record<string, unknown>;
  typography?: Record<string, unknown>;
  shadows?: Record<string, unknown>;
  radii?: Record<string, unknown>;
  [key: string]: unknown;
}

interface TokenDiff {
  computed_at: string;
  figma_contract_path: string;
  baseline_path: string;
  summary: {
    total_figma_tokens: number;
    total_baseline_tokens: number;
    added: number;
    removed: number;
    unchanged: number;
  };
  by_category: {
    [category: string]: {
      added: string[];
      removed: string[];
      unchanged: string[];
    };
  };
  has_breaking_changes: boolean;
  breaking_changes: string[];
}

// ============================================================================
// CLI ARGS
// ============================================================================

function getArg(name: string, defaultValue = ""): string {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : defaultValue;
}

const figmaPath = getArg("--figma", "ops/design/figma_contract.json");
const baselinePath = getArg("--baseline", "tokens.json");
const outJson = getArg("--out-json", "ops/design/token_diff.json");
const outMd = getArg("--out-md", "ops/design/token_diff.md");

// ============================================================================
// DIFF LOGIC
// ============================================================================

function normalizeTokenName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
}

function getBaselineTokens(baseline: TokensJson, category: string): Set<string> {
  const tokens = new Set<string>();

  // Try direct category access
  const categoryData = baseline[category];
  if (categoryData && typeof categoryData === "object") {
    for (const key of Object.keys(categoryData)) {
      tokens.add(normalizeTokenName(key));
    }
  }

  return tokens;
}

function computeDiff(figma: FigmaContract, baseline: TokensJson): TokenDiff {
  const categories = ["colors", "spacing", "typography", "shadows", "radii", "other"];
  const byCategory: TokenDiff["by_category"] = {};
  let totalFigma = 0;
  let totalBaseline = 0;
  let totalAdded = 0;
  let totalRemoved = 0;
  let totalUnchanged = 0;
  const breakingChanges: string[] = [];

  for (const category of categories) {
    const figmaTokens = new Set(
      (figma.tokens_touched[category as keyof typeof figma.tokens_touched] || []).map(normalizeTokenName)
    );
    const baselineTokens = getBaselineTokens(baseline, category);

    totalFigma += figmaTokens.size;
    totalBaseline += baselineTokens.size;

    const added: string[] = [];
    const removed: string[] = [];
    const unchanged: string[] = [];

    // Tokens in Figma but not in baseline = added
    for (const token of figmaTokens) {
      if (!baselineTokens.has(token)) {
        added.push(token);
      } else {
        unchanged.push(token);
      }
    }

    // Tokens in baseline but not in Figma = removed (potential breaking change)
    for (const token of baselineTokens) {
      if (!figmaTokens.has(token)) {
        removed.push(token);
        breakingChanges.push(`${category}.${token} removed`);
      }
    }

    byCategory[category] = { added, removed, unchanged };
    totalAdded += added.length;
    totalRemoved += removed.length;
    totalUnchanged += unchanged.length;
  }

  return {
    computed_at: new Date().toISOString(),
    figma_contract_path: figmaPath,
    baseline_path: baselinePath,
    summary: {
      total_figma_tokens: totalFigma,
      total_baseline_tokens: totalBaseline,
      added: totalAdded,
      removed: totalRemoved,
      unchanged: totalUnchanged,
    },
    by_category: byCategory,
    has_breaking_changes: breakingChanges.length > 0,
    breaking_changes: breakingChanges,
  };
}

function generateMarkdown(diff: TokenDiff): string {
  let md = `## Token Diff Report\n\n`;
  md += `**Computed:** ${diff.computed_at}\n\n`;

  md += `### Summary\n\n`;
  md += `| Metric | Count |\n`;
  md += `|--------|------:|\n`;
  md += `| Figma tokens | ${diff.summary.total_figma_tokens} |\n`;
  md += `| Baseline tokens | ${diff.summary.total_baseline_tokens} |\n`;
  md += `| Added | ${diff.summary.added} |\n`;
  md += `| Removed | ${diff.summary.removed} |\n`;
  md += `| Unchanged | ${diff.summary.unchanged} |\n`;
  md += `\n`;

  if (diff.has_breaking_changes) {
    md += `### ⚠️ Breaking Changes\n\n`;
    md += `The following tokens were removed from the baseline:\n\n`;
    for (const change of diff.breaking_changes) {
      md += `- \`${change}\`\n`;
    }
    md += `\n`;
  } else {
    md += `### ✅ No Breaking Changes\n\n`;
  }

  md += `### By Category\n\n`;
  for (const [category, changes] of Object.entries(diff.by_category)) {
    if (changes.added.length === 0 && changes.removed.length === 0) {
      continue;
    }

    md += `#### ${category.charAt(0).toUpperCase() + category.slice(1)}\n\n`;

    if (changes.added.length > 0) {
      md += `**Added (${changes.added.length}):**\n`;
      for (const token of changes.added.slice(0, 10)) {
        md += `- \`${token}\`\n`;
      }
      if (changes.added.length > 10) {
        md += `- ... and ${changes.added.length - 10} more\n`;
      }
      md += `\n`;
    }

    if (changes.removed.length > 0) {
      md += `**Removed (${changes.removed.length}):**\n`;
      for (const token of changes.removed.slice(0, 10)) {
        md += `- \`${token}\`\n`;
      }
      if (changes.removed.length > 10) {
        md += `- ... and ${changes.removed.length - 10} more\n`;
      }
      md += `\n`;
    }
  }

  return md;
}

// ============================================================================
// MAIN
// ============================================================================

function main() {
  // Check inputs exist
  if (!fs.existsSync(figmaPath)) {
    console.error(`Error: Figma contract not found: ${figmaPath}`);
    console.error("Run export_figma_contract.ts first.");
    process.exit(2);
  }

  if (!fs.existsSync(baselinePath)) {
    console.warn(`Warning: Baseline tokens not found: ${baselinePath}`);
    console.warn("Creating empty baseline for comparison.");
  }

  // Load files
  const figma: FigmaContract = JSON.parse(fs.readFileSync(figmaPath, "utf8"));
  const baseline: TokensJson = fs.existsSync(baselinePath)
    ? JSON.parse(fs.readFileSync(baselinePath, "utf8"))
    : {};

  // Compute diff
  const diff = computeDiff(figma, baseline);

  // Write outputs
  const outJsonDir = path.dirname(outJson);
  if (!fs.existsSync(outJsonDir)) {
    fs.mkdirSync(outJsonDir, { recursive: true });
  }

  fs.writeFileSync(outJson, JSON.stringify(diff, null, 2));
  console.log(`Wrote: ${outJson}`);

  const md = generateMarkdown(diff);
  fs.writeFileSync(outMd, md);
  console.log(`Wrote: ${outMd}`);

  // Report summary
  console.log(`\nSummary:`);
  console.log(`  Added: ${diff.summary.added}`);
  console.log(`  Removed: ${diff.summary.removed}`);
  console.log(`  Unchanged: ${diff.summary.unchanged}`);

  if (diff.has_breaking_changes) {
    console.log(`\n⚠️  Breaking changes detected!`);
    process.exit(1);
  }
}

main();
