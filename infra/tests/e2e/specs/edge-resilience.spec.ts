import { test, expect } from "@playwright/test";

/**
 * Edge + DB resilience verification specs.
 * Validates hostname preservation (Front Door) and basic connectivity resilience.
 *
 * Run via: BASE_URL=https://erp.insightpulseai.com npx playwright test specs/edge-resilience.spec.ts
 */

test.describe("Hostname Preservation", () => {
  test("response headers do not leak internal ACA FQDN", async ({
    request,
    baseURL,
  }) => {
    const response = await request.get(`${baseURL}/web/login`);
    const headers = response.headers();

    // No response header should contain the internal ACA domain
    const headerValues = Object.values(headers).join(" ");
    expect(headerValues).not.toContain(".azurecontainerapps.io");
    expect(headerValues).not.toContain("salmontree-b7d27e19");
  });

  test("redirects preserve public hostname", async ({ request, baseURL }) => {
    // Request root — Odoo typically redirects / to /web
    const response = await request.get(`${baseURL}/`, {
      maxRedirects: 0,
    });

    const status = response.status();
    if (status >= 300 && status < 400) {
      const location = response.headers()["location"] ?? "";
      // Redirect target must use the public hostname, not internal FQDN
      expect(location).not.toContain(".azurecontainerapps.io");
      if (location.startsWith("http")) {
        const url = new URL(location);
        expect(url.hostname).not.toContain("azurecontainerapps.io");
      }
    }
    // If no redirect, that's also fine (some Odoo configs serve / directly)
  });

  test("Set-Cookie domain does not expose internal hostname", async ({
    request,
    baseURL,
  }) => {
    const response = await request.get(`${baseURL}/web/login`);
    const setCookie = response.headers()["set-cookie"] ?? "";

    // Cookie domain must not be the internal ACA FQDN
    expect(setCookie).not.toContain(".azurecontainerapps.io");
    expect(setCookie).not.toContain("salmontree-b7d27e19");
  });
});

test.describe("Connection Resilience", () => {
  test("health endpoint responds within timeout", async ({
    request,
    baseURL,
  }) => {
    // /web/health is the Front Door health probe path
    const start = Date.now();
    const response = await request.get(`${baseURL}/web/health`, {
      timeout: 10_000,
    });
    const elapsed = Date.now() - start;

    expect(response.status()).toBeLessThan(500);
    // Health check should respond in under 5s (well within Front Door's 10s timeout)
    expect(elapsed).toBeLessThan(5_000);
  });

  test("consecutive requests succeed (no connection drops)", async ({
    request,
    baseURL,
  }) => {
    // Fire 5 sequential requests — all should succeed
    // This catches connection pool exhaustion or intermittent drops
    const results: number[] = [];
    for (let i = 0; i < 5; i++) {
      const response = await request.get(`${baseURL}/web/login`);
      results.push(response.status());
    }

    // All should be 200 (or redirect 3xx)
    for (const status of results) {
      expect(status).toBeLessThan(500);
    }
  });
});
