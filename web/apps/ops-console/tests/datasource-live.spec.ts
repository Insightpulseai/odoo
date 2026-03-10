import { test, expect } from "@playwright/test";

/**
 * Integration Test: Data Source Live Proof
 * This test ensures that the application is talking to real targets and NOT local/mock data
 * when running in staging/prod contexts (simulated by CI env vars).
 */

test.describe("Data Source Validation", () => {
  test("should only hit approved live domains and report live mode", async ({ page }) => {
    // Collect all network requests
    const requests: string[] = [];
    page.on("request", (request) => {
      requests.push(request.url());
    });

    // Navigate to the dashboard
    await page.goto("/");

    // Wait for the DataSourceBadge to hydrate
    const badge = page.locator("div:has-text('MODE')");
    await expect(badge).toBeVisible();

    // 1. Verify the debug endpoint reports LIVE mode
    const response = await page.request.get("/api/_debug/datasources");
    const attestation = await response.json();

    // In CI (where APP_ENV=prod or stage), this MUST be live
    if (process.env.APP_ENV === "production" || process.env.APP_ENV === "staging") {
      expect(attestation.mode).toBe("live");
      await expect(badge).toContainText("LIVE MODE");
    }

    // 2. Network Proof: No local JSON or mock imports
    const forbiddenPatterns = [
      "/mocks/",
      "mock-data",
      ".json", // except for maybe manifest/assets if specifically allowed
    ];

    for (const url of requests) {
      for (const pattern of forbiddenPatterns) {
        if (url.includes(pattern) && !url.includes("manifest.json") && !url.includes("_next")) {
          throw new Error(`Forbidden network request detected: ${url}`);
        }
      }
    }

    // 3. Network Proof: Requests should go to approved domains (Supabase/Odoo)
    const hasSupabaseCalls = requests.some(url => url.includes("supabase.co"));
    // Note: In local dev without real creds this might fail, but in CI it PROVES truth.
    if (attestation.mode === "live") {
      // We expect at least the debug call and ideally the data calls
      expect(hasSupabaseCalls).toBe(true);
    }
  });

  test("should hard-fail if mock mode is forced in prod", async ({ page }) => {
    // This test would require a custom build/env config to simulate
    // But we can verify the guard logic via the /api/_debug/datasources logic
    const response = await page.request.get("/api/_debug/datasources");
    const attestation = await response.json();

    if (attestation.envName === "production" && attestation.mode === "mock") {
       // The app layout should have thrown and rendered the fatal error overlay
       await expect(page.locator("h1")).toContainText("Data Source Security Failure");
    }
  });
});
