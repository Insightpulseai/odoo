#!/usr/bin/env node
import { copyFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = join(__dirname, '..');
const dist = join(root, 'dist');

// Copy manifest.json
copyFileSync(join(root, 'public/manifest.json'), join(dist, 'manifest.json'));
console.log('✓ Copied manifest.json');

// Copy icons (create placeholder if needed)
const iconsDir = join(dist, 'icons');
if (!existsSync(iconsDir)) {
  mkdirSync(iconsDir, { recursive: true });
}

// For now, create empty icon files (replace with actual icons later)
const iconSizes = [16, 32, 48, 128];
for (const size of iconSizes) {
  const srcPath = join(root, `public/icons/icon-${size}.png`);
  const destPath = join(iconsDir, `icon-${size}.png`);

  if (existsSync(srcPath)) {
    copyFileSync(srcPath, destPath);
  } else {
    // Create placeholder file
    copyFileSync(srcPath, destPath);
  }
}
console.log('✓ Copied icons');

console.log('✓ Post-build complete');
