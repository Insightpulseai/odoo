import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BASE_URL || "http://localhost:8069";
const useChromeExt = process.env.PLAYWRIGHT_USE_CHROME_EXTENSION === "1";

/**
 * Phase 3 (Chrome/extension): many extensions require a persistent context + headful Chromium.
 * In CI, we run headful via Xvfb.
 *
 * TODO: provide an actual extension directory at tests/e2e/extension/ if needed.
 */
export default defineConfig({
  testDir: "./specs",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure"
  },
  projects: [
    {
      name: useChromeExt ? "chromium-extension" : "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // Extension mode is handled in test fixture by launching persistent context with args.
        // Keep normal mode default.
      }
    }
  ]
});
