import { test, expect, chromium } from "@playwright/test";
import path from "path";

const useChromeExt = process.env.PLAYWRIGHT_USE_CHROME_EXTENSION === "1";

test("smoke: web responds", async ({ page, baseURL }) => {
  await page.goto(baseURL!);
  // Odoo typically redirects; just assert content exists.
  await expect(page).toHaveTitle(/Odoo|Login|Database/i);
});

test("phase3: can launch chromium with extension (optional)", async ({ baseURL }) => {
  test.skip(!useChromeExt, "Set PLAYWRIGHT_USE_CHROME_EXTENSION=1 to enable extension mode");

  const extensionPath = process.env.CHROME_EXTENSION_DIR
    || path.resolve(process.cwd(), "extension"); // tests/e2e/extension (placeholder)
  // NOTE: extensionPath must exist and contain a valid manifest.json for real runs.
  // This test is intentionally a harness check; it will fail fast if extension not present.
  const context = await chromium.launchPersistentContext("", {
    headless: false,
    args: [
      `--disable-extensions-except=${extensionPath}`,
      `--load-extension=${extensionPath}`
    ]
  });

  const page = await context.newPage();
  await page.goto(baseURL!);
  await expect(page).toHaveTitle(/Odoo|Login|Database/i);
  await context.close();
});
