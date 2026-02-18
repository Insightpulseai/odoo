/**
 * Copy built assets to Odoo static directory
 *
 * This script runs after Vite build to copy the IIFE bundle
 * and CSS to the Odoo addon's static/lib directory.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const distDir = path.resolve(__dirname, "../dist");
const targetDir = path.resolve(__dirname, "../../static/lib");

// Ensure target directory exists
fs.mkdirSync(targetDir, { recursive: true });

// Files to copy with their source and target names
const files = [
  { src: "ipai_ai_ui.iife.js", dest: "ipai_ai_ui.iife.js" },
  { src: "style.css", dest: "ipai_ai_ui.css" },
];

let success = true;

for (const file of files) {
  const srcPath = path.join(distDir, file.src);
  const destPath = path.join(targetDir, file.dest);

  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    const stats = fs.statSync(destPath);
    console.log(`✓ Copied ${file.src} → ${file.dest} (${(stats.size / 1024).toFixed(1)} KB)`);
  } else {
    console.error(`✗ Source file not found: ${srcPath}`);
    success = false;
  }
}

if (success) {
  console.log(`\n✓ Build artifacts copied to ${targetDir}`);
} else {
  console.error("\n✗ Some files could not be copied");
  process.exit(1);
}
