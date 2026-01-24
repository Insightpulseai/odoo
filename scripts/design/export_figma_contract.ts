#!/usr/bin/env -S npx tsx
/**
 * Figma Contract Export Script
 *
 * Exports a machine-readable contract from Figma for AI-first SDLC enforcement.
 * Uses the Figma REST API to extract file metadata, variables, styles, and nodes.
 *
 * Usage:
 *   FIGMA_TOKEN=xxx ./scripts/design/export_figma_contract.ts --file-key <KEY> [--node-id <ID>]
 *
 * Environment:
 *   FIGMA_TOKEN - Figma personal access token (required)
 *
 * References:
 *   - Figma REST API: https://www.figma.com/developers/api
 *   - Variables API (Enterprise): https://developers.figma.com/docs/rest-api/variables-endpoints/
 */

import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";

// ============================================================================
// TYPES
// ============================================================================

interface FigmaContract {
  version: string;
  feature_slug: string;
  phase: number;
  phase_label: string;
  owners: {
    design: string[];
    engineering: string[];
    data?: string[];
    ops?: string[];
    product?: string[];
  };
  figma_meta: {
    file_key: string;
    file_name: string;
    node_id?: string;
    exported_at: string;
    exporter_version: string;
    figma_last_modified: string;
  };
  routes: Array<{
    path: string;
    name: string;
    component?: string;
    roles?: string[];
    figma_frame_id?: string;
  }>;
  components: Array<{
    name: string;
    status: "existing" | "new" | "modified";
    figma_component_id?: string;
    props?: string[];
    variants?: string[];
  }>;
  tokens_touched: {
    colors?: string[];
    spacing?: string[];
    typography?: string[];
    shadows?: string[];
    radii?: string[];
    other?: string[];
  };
  schemas_touched: {
    tables?: string[];
    functions?: string[];
    rls_policies?: string[];
    edge_functions?: string[];
  };
  roles?: Array<{
    name: string;
    permissions: Array<"view" | "create" | "edit" | "delete" | "admin">;
  }>;
  success_metrics?: Array<{
    name: string;
    target: string;
    measurement?: string;
  }>;
  dependencies?: {
    spec_bundles?: string[];
    migrations?: string[];
    packages?: string[];
  };
  contract_hash?: string;
}

interface FigmaFile {
  name: string;
  lastModified: string;
  version: string;
  document: FigmaNode;
  components: Record<string, FigmaComponent>;
  styles: Record<string, FigmaStyle>;
}

interface FigmaNode {
  id: string;
  name: string;
  type: string;
  children?: FigmaNode[];
}

interface FigmaComponent {
  key: string;
  name: string;
  description: string;
}

interface FigmaStyle {
  key: string;
  name: string;
  styleType: string;
}

interface FigmaVariables {
  meta: {
    variableCollections: Record<string, unknown>;
    variables: Record<string, unknown>;
  };
}

// ============================================================================
// CLI ARGS
// ============================================================================

function getArg(name: string, defaultValue = ""): string {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : defaultValue;
}

function hasFlag(name: string): boolean {
  return process.argv.includes(name);
}

const fileKey = getArg("--file-key");
const nodeId = getArg("--node-id");
const outPath = getArg("--out", "ops/design/figma_contract.json");
const featureSlug = getArg("--slug", "");
const phase = parseInt(getArg("--phase", "3"), 10);

const FIGMA_TOKEN = process.env.FIGMA_TOKEN;
const EXPORTER_VERSION = "1.0.0";

// ============================================================================
// FIGMA API
// ============================================================================

const FIGMA_BASE = "https://api.figma.com/v1";

async function figmaGet<T>(endpoint: string): Promise<T> {
  if (!FIGMA_TOKEN) {
    throw new Error("FIGMA_TOKEN environment variable is required");
  }

  const url = `${FIGMA_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      "X-Figma-Token": FIGMA_TOKEN,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Figma API error: ${res.status} ${res.statusText} - ${text}`);
  }

  return res.json() as Promise<T>;
}

async function getFile(key: string): Promise<FigmaFile> {
  return figmaGet<FigmaFile>(`/files/${key}`);
}

async function getVariables(key: string): Promise<FigmaVariables | null> {
  try {
    // Variables API may be restricted to Enterprise plans
    return await figmaGet<FigmaVariables>(`/files/${key}/variables/local`);
  } catch (err) {
    console.warn("Variables API unavailable (may require Enterprise plan):", err);
    return null;
  }
}

async function getStyles(key: string): Promise<{ styles: FigmaStyle[] } | null> {
  try {
    return await figmaGet<{ styles: FigmaStyle[] }>(`/files/${key}/styles`);
  } catch (err) {
    console.warn("Styles API unavailable:", err);
    return null;
  }
}

// ============================================================================
// EXTRACTORS
// ============================================================================

function extractRoutesFromNodes(node: FigmaNode, routes: FigmaContract["routes"] = []): FigmaContract["routes"] {
  // Look for frames with names matching route patterns (e.g., "/dashboard", "Page: Dashboard")
  const routePatterns = [
    /^\/[a-z0-9-/]+$/i, // URL paths
    /^Page:\s*(.+)$/i, // "Page: Name" format
    /^Screen:\s*(.+)$/i, // "Screen: Name" format
  ];

  if (node.type === "FRAME" || node.type === "COMPONENT" || node.type === "COMPONENT_SET") {
    for (const pattern of routePatterns) {
      const match = node.name.match(pattern);
      if (match) {
        const routePath = match[1] ? `/${match[1].toLowerCase().replace(/\s+/g, "-")}` : node.name;
        routes.push({
          path: routePath.startsWith("/") ? routePath : `/${routePath}`,
          name: node.name,
          figma_frame_id: node.id,
        });
        break;
      }
    }
  }

  if (node.children) {
    for (const child of node.children) {
      extractRoutesFromNodes(child, routes);
    }
  }

  return routes;
}

function extractComponentsFromFile(file: FigmaFile): FigmaContract["components"] {
  const components: FigmaContract["components"] = [];

  for (const [key, comp] of Object.entries(file.components || {})) {
    components.push({
      name: comp.name,
      status: "existing", // Default; would need baseline comparison for accurate status
      figma_component_id: comp.key,
    });
  }

  return components;
}

function extractTokensFromStyles(styles: FigmaStyle[] | null): FigmaContract["tokens_touched"] {
  const tokens: FigmaContract["tokens_touched"] = {
    colors: [],
    spacing: [],
    typography: [],
    shadows: [],
    radii: [],
    other: [],
  };

  if (!styles) return tokens;

  for (const style of styles) {
    switch (style.styleType) {
      case "FILL":
        tokens.colors!.push(style.name);
        break;
      case "TEXT":
        tokens.typography!.push(style.name);
        break;
      case "EFFECT":
        tokens.shadows!.push(style.name);
        break;
      default:
        tokens.other!.push(style.name);
    }
  }

  return tokens;
}

function extractTokensFromVariables(variables: FigmaVariables | null): FigmaContract["tokens_touched"] {
  const tokens: FigmaContract["tokens_touched"] = {
    colors: [],
    spacing: [],
    typography: [],
    shadows: [],
    radii: [],
    other: [],
  };

  if (!variables?.meta?.variables) return tokens;

  // Variables have resolvedType: "COLOR", "FLOAT", "STRING", "BOOLEAN"
  for (const [_id, variable] of Object.entries(variables.meta.variables)) {
    const v = variable as { name: string; resolvedType: string };
    const name = v.name;
    const type = v.resolvedType;

    switch (type) {
      case "COLOR":
        tokens.colors!.push(name);
        break;
      case "FLOAT":
        // Could be spacing, radius, etc. - categorize by naming convention
        if (name.toLowerCase().includes("spacing") || name.toLowerCase().includes("gap")) {
          tokens.spacing!.push(name);
        } else if (name.toLowerCase().includes("radius")) {
          tokens.radii!.push(name);
        } else {
          tokens.other!.push(name);
        }
        break;
      default:
        tokens.other!.push(name);
    }
  }

  return tokens;
}

function mergeTokens(
  a: FigmaContract["tokens_touched"],
  b: FigmaContract["tokens_touched"]
): FigmaContract["tokens_touched"] {
  return {
    colors: [...new Set([...(a.colors || []), ...(b.colors || [])])],
    spacing: [...new Set([...(a.spacing || []), ...(b.spacing || [])])],
    typography: [...new Set([...(a.typography || []), ...(b.typography || [])])],
    shadows: [...new Set([...(a.shadows || []), ...(b.shadows || [])])],
    radii: [...new Set([...(a.radii || []), ...(b.radii || [])])],
    other: [...new Set([...(a.other || []), ...(b.other || [])])],
  };
}

function computeContractHash(contract: Omit<FigmaContract, "contract_hash">): string {
  const json = JSON.stringify(contract, Object.keys(contract).sort());
  return crypto.createHash("sha256").update(json).digest("hex");
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  if (!fileKey) {
    console.error("Usage: export_figma_contract.ts --file-key <KEY> [--node-id <ID>] [--slug <SLUG>] [--phase <0-6>]");
    console.error("");
    console.error("Environment:");
    console.error("  FIGMA_TOKEN - Figma personal access token (required)");
    process.exit(2);
  }

  if (!FIGMA_TOKEN) {
    console.error("Error: FIGMA_TOKEN environment variable is required");
    process.exit(2);
  }

  console.log(`Exporting Figma contract for file: ${fileKey}`);
  if (nodeId) {
    console.log(`Targeting node: ${nodeId}`);
  }

  // Fetch file and metadata
  const file = await getFile(fileKey);
  console.log(`File name: ${file.name}`);
  console.log(`Last modified: ${file.lastModified}`);

  // Fetch variables (Enterprise-only, may fail)
  const variables = await getVariables(fileKey);

  // Fetch styles
  const stylesResponse = await getStyles(fileKey);
  const styles = stylesResponse?.styles || null;

  // Extract data
  const routes = extractRoutesFromNodes(file.document);
  const components = extractComponentsFromFile(file);
  const tokensFromStyles = extractTokensFromStyles(styles);
  const tokensFromVariables = extractTokensFromVariables(variables);
  const tokens_touched = mergeTokens(tokensFromStyles, tokensFromVariables);

  // Derive feature slug from file name if not provided
  const derivedSlug =
    featureSlug ||
    file.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

  // Build contract
  const phaseLabels = ["Portfolio", "Discovery", "System Design", "Design", "Build", "Test", "Launch"];

  const contract: Omit<FigmaContract, "contract_hash"> = {
    version: "1.0",
    feature_slug: derivedSlug,
    phase: phase,
    phase_label: phaseLabels[phase] || "Unknown",
    owners: {
      design: ["@design-team"], // TODO: Extract from Figma file metadata or require as input
      engineering: ["@eng-team"],
    },
    figma_meta: {
      file_key: fileKey,
      file_name: file.name,
      node_id: nodeId || undefined,
      exported_at: new Date().toISOString(),
      exporter_version: EXPORTER_VERSION,
      figma_last_modified: file.lastModified,
    },
    routes,
    components,
    tokens_touched,
    schemas_touched: {
      // TODO: Could be extracted from frame annotations or linked issues
      tables: [],
      functions: [],
      rls_policies: [],
      edge_functions: [],
    },
  };

  // Compute hash
  const contractWithHash: FigmaContract = {
    ...contract,
    contract_hash: computeContractHash(contract),
  };

  // Write output
  const outDir = path.dirname(outPath);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  fs.writeFileSync(outPath, JSON.stringify(contractWithHash, null, 2));
  console.log(`\nWrote contract to: ${outPath}`);
  console.log(`Contract hash: ${contractWithHash.contract_hash}`);
  console.log(`\nSummary:`);
  console.log(`  Routes: ${routes.length}`);
  console.log(`  Components: ${components.length}`);
  console.log(`  Tokens: ${Object.values(tokens_touched).flat().length}`);
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
