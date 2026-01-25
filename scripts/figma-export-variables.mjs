/**
 * Exports Figma Variables (local) for a given file key.
 * Requires FIGMA_ACCESS_TOKEN and FIGMA_FILE_KEY.
 *
 * Uses: GET /v1/files/:file_key/variables/local  (see Figma Variables API)
 * @see https://developers.figma.com/docs/rest-api/variables-endpoints/
 */
import fs from "node:fs";
import path from "node:path";

const token = process.env.FIGMA_ACCESS_TOKEN;
const fileKey = process.env.FIGMA_FILE_KEY;

if (!token) throw new Error("Missing FIGMA_ACCESS_TOKEN");
if (!fileKey) throw new Error("Missing FIGMA_FILE_KEY");

const outDir = path.resolve("figma/tokens");
fs.mkdirSync(outDir, { recursive: true });

const url = `https://api.figma.com/v1/files/${encodeURIComponent(fileKey)}/variables/local`;

const res = await fetch(url, {
  headers: { "X-Figma-Token": token },
});

if (!res.ok) {
  const body = await res.text();
  throw new Error(`Figma Variables API failed: ${res.status} ${res.statusText}\n${body}`);
}

const json = await res.json();

// Raw export
fs.writeFileSync(path.join(outDir, "variables.local.json"), JSON.stringify(json, null, 2));

// Minimal "tokens.json" derivation (keeps this deterministic and CI-friendly):
// - Emits a flattened map of variable name -> resolved value (if present), else metadata stub.
// NOTE: adjust mapping to your design-token schema SSOT if you already have one.
const tokens = {};
const varsObj = json?.meta?.variables ?? {};
for (const [varId, v] of Object.entries(varsObj)) {
  const name = v?.name ?? varId;
  // Prefer modeValues if available; otherwise keep type + id.
  const modeValues = v?.valuesByMode ?? null;
  tokens[name] = modeValues ?? { id: varId, resolvedType: v?.resolvedType ?? v?.variableType ?? "unknown" };
}

fs.writeFileSync(path.join(outDir, "tokens.json"), JSON.stringify({ tokens }, null, 2));

console.log(`OK: wrote figma/tokens/variables.local.json + tokens.json (${Object.keys(tokens).length} tokens)`);
