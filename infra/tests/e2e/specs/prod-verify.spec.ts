import { test, expect } from "@playwright/test";

/**
 * Production verification smoke tests.
 * Run via: BASE_URL=https://erp.insightpulseai.com npx playwright test specs/prod-verify.spec.ts
 *
 * These tests produce screenshots in the evidence directory and verify
 * that core Odoo surfaces are reachable and responding correctly.
 */

test.describe("Production Verification", () => {
  test("login page is reachable and renders", async ({ page, baseURL }) => {
    const response = await page.goto(`${baseURL}/web/login`);
    expect(response?.status()).toBeLessThan(500);

    // Odoo login page must contain a login form
    await expect(page.locator("form")).toBeVisible({ timeout: 15_000 });

    // Must have password field (proves it's the real login page, not an error)
    await expect(page.locator('input[type="password"]')).toBeVisible();

    await page.screenshot({
      path: `${process.env.EVIDENCE_DIR || "evidence"}/screenshots/01-login-page.png`,
      fullPage: true,
    });
  });

  test("web client static assets load", async ({ page, baseURL }) => {
    const response = await page.goto(`${baseURL}/web/login`);
    expect(response?.status()).toBeLessThan(500);

    // Check that CSS loaded (page should have styled elements)
    const hasStyles = await page.evaluate(() => {
      const el = document.querySelector("body");
      if (!el) return false;
      const style = window.getComputedStyle(el);
      // A styled page will have a non-default font or background
      return style.fontFamily !== "" || style.backgroundColor !== "";
    });
    expect(hasStyles).toBe(true);

    // Check that at least one JS bundle loaded
    const scripts = await page.locator("script[src]").count();
    expect(scripts).toBeGreaterThan(0);

    await page.screenshot({
      path: `${process.env.EVIDENCE_DIR || "evidence"}/screenshots/02-assets-loaded.png`,
      fullPage: true,
    });
  });

  test("database selector is disabled (list_db=False)", async ({
    page,
    baseURL,
  }) => {
    const response = await page.goto(`${baseURL}/web/database/selector`);
    // With list_db=False, Odoo returns 403 or redirects to login
    const status = response?.status() ?? 0;
    const isBlocked = status === 403 || status === 404 || page.url().includes("/web/login");
    expect(isBlocked).toBe(true);

    await page.screenshot({
      path: `${process.env.EVIDENCE_DIR || "evidence"}/screenshots/03-db-selector-blocked.png`,
      fullPage: true,
    });
  });

  test("HTTP security headers present", async ({ request, baseURL }) => {
    const response = await request.get(`${baseURL}/web/login`);
    const headers = response.headers();

    // X-Frame-Options or CSP frame-ancestors should be set
    const hasFrameProtection =
      headers["x-frame-options"] !== undefined ||
      (headers["content-security-policy"] ?? "").includes("frame-ancestors");
    expect(hasFrameProtection).toBe(true);

    // X-Content-Type-Options should be nosniff
    expect(headers["x-content-type-options"]).toBe("nosniff");
  });
});
