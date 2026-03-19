import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test("extension build verification - all required files present", async () => {
  const distDir = path.resolve(__dirname, "../../dist");

  // Verify dist directory exists
  expect(fs.existsSync(distDir), `dist/ not found at ${distDir}. Run pnpm build first.`).toBeTruthy();

  console.log(`✓ dist/ directory exists: ${distDir}`);

  // Verify manifest.json exists and is valid
  const manifestPath = path.join(distDir, 'manifest.json');
  expect(fs.existsSync(manifestPath), `manifest.json should exist at ${manifestPath}`).toBeTruthy();

  const manifestContent = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  expect(manifestContent.manifest_version).toBe(3);
  expect(manifestContent.name).toBe("Alpha Browser");
  expect(manifestContent.version).toBe("0.1.0");

  console.log(`✓ manifest.json is valid (Manifest V3)`);

  // Verify background service worker file exists
  const serviceWorkerPath = path.join(distDir, manifestContent.background.service_worker);
  expect(fs.existsSync(serviceWorkerPath), `Service worker should exist at ${serviceWorkerPath}`).toBeTruthy();
  const swSize = fs.statSync(serviceWorkerPath).size;
  expect(swSize).toBeGreaterThan(100); // Should have content

  console.log(`✓ service-worker.js exists (${swSize} bytes)`);

  // Verify content script exists
  const contentScript = manifestContent.content_scripts[0].js[0];
  const contentScriptPath = path.join(distDir, contentScript);
  expect(fs.existsSync(contentScriptPath), `Content script should exist at ${contentScriptPath}`).toBeTruthy();
  const csSize = fs.statSync(contentScriptPath).size;
  expect(csSize).toBeGreaterThan(100);

  console.log(`✓ ${contentScript} exists (${csSize} bytes)`);

  // Verify popup HTML exists
  const popupPath = path.join(distDir, manifestContent.action.default_popup);
  expect(fs.existsSync(popupPath), `Popup HTML should exist at ${popupPath}`).toBeTruthy();

  console.log(`✓ ${manifestContent.action.default_popup} exists`);

  // Verify icons directory exists
  const iconsDir = path.join(distDir, 'icons');
  expect(fs.existsSync(iconsDir), `Icons directory should exist`).toBeTruthy();

  console.log(`✓ icons/ directory exists`);

  // Verify key popup assets
  const popupHtml = fs.readFileSync(popupPath, 'utf-8');
  expect(popupHtml).toContain('<!DOCTYPE html>');

  console.log(`✓ Popup HTML is valid`);

  // Verify dependencies are bundled (check assets directory)
  const assetsDir = path.join(distDir, 'assets');
  if (fs.existsSync(assetsDir)) {
    const assetFiles = fs.readdirSync(assetsDir);
    expect(assetFiles.length).toBeGreaterThan(0);
    console.log(`✓ ${assetFiles.length} bundled assets in assets/`);
  }

  console.log('\n=== Phase 1 Extension Build Verification: PASS ===');
  console.log('All required files present and valid.');
  console.log('Extension is ready to be loaded in Chrome (chrome://extensions).');
});
