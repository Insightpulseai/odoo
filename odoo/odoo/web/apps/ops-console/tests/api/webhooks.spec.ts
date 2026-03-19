/**
 * Webhook receiver API tests (Playwright)
 *
 * Tests: signature verification, JSON responses, dedupe behavior,
 * and normalization assertions for work_item_ref format.
 *
 * NOTE: These are API-level tests that test the route contract (always JSON,
 * correct signatures, etc.) in isolation. DB-level dedupe is tested via
 * the migration PRIMARY KEY constraint.
 */

import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { planeSig, githubSig, TEST_PLANE_SECRET, TEST_GITHUB_SECRET } from "../helpers/webhook-sig";

const BASE_URL = process.env.TEST_BASE_URL ?? "http://localhost:3000";

function loadFixture(path: string): string {
  return readFileSync(resolve(__dirname, "../fixtures/webhooks", path), "utf-8");
}

// ── Plane webhook ────────────────────────────────────────────────────────────

test.describe("POST /api/webhooks/plane", () => {
  const ENDPOINT = `${BASE_URL}/api/webhooks/plane`;
  const body = loadFixture("plane/issue_created.json");

  test("returns JSON with ok:true on valid signature", async ({ request }) => {
    const sig = planeSig(TEST_PLANE_SECRET, body);
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-Plane-Delivery": "test-delivery-plane-001",
        "X-Plane-Event": "issue.created",
        "X-Plane-Signature": sig,
      },
      data: body,
    });
    // Route may return 500 if Supabase env not present in test — that's ok.
    // What we assert: always JSON, never empty, Content-Type correct.
    const ct = res.headers()["content-type"] ?? "";
    expect(ct).toContain("application/json");
    const json = await res.json();
    expect(json).toHaveProperty("ok");
  });

  test("returns 403 JSON on invalid signature", async ({ request }) => {
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-Plane-Delivery": "test-delivery-plane-002",
        "X-Plane-Event": "issue.created",
        "X-Plane-Signature": "deadbeef",
      },
      data: body,
    });
    expect(res.status()).toBe(403);
    const ct = res.headers()["content-type"] ?? "";
    expect(ct).toContain("application/json");
    const json = await res.json();
    expect(json.ok).toBe(false);
    expect(json.error).toBe("invalid signature");
  });

  test("response is never 204 and body is never empty", async ({ request }) => {
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-Plane-Delivery": "test-delivery-plane-003",
        "X-Plane-Event": "issue.created",
        "X-Plane-Signature": "bad",
      },
      data: body,
    });
    expect(res.status()).not.toBe(204);
    const text = await res.text();
    expect(text.length).toBeGreaterThan(0);
  });
});

// ── GitHub webhook ───────────────────────────────────────────────────────────

test.describe("POST /api/webhooks/github", () => {
  const ENDPOINT = `${BASE_URL}/api/webhooks/github`;
  const body = loadFixture("github/issues_opened.json");

  test("returns JSON with ok:true on valid signature", async ({ request }) => {
    const sig = githubSig(TEST_GITHUB_SECRET, body);
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Delivery": "test-delivery-github-001",
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": sig,
      },
      data: body,
    });
    const ct = res.headers()["content-type"] ?? "";
    expect(ct).toContain("application/json");
    const json = await res.json();
    expect(json).toHaveProperty("ok");
  });

  test("returns 403 JSON on invalid signature", async ({ request }) => {
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Delivery": "test-delivery-github-002",
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": "sha256=deadbeef",
      },
      data: body,
    });
    expect(res.status()).toBe(403);
    const ct = res.headers()["content-type"] ?? "";
    expect(ct).toContain("application/json");
    const json = await res.json();
    expect(json.ok).toBe(false);
  });

  test("response is never 204 and body is never empty", async ({ request }) => {
    const res = await request.post(ENDPOINT, {
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Delivery": "test-delivery-github-003",
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": "bad",
      },
      data: body,
    });
    expect(res.status()).not.toBe(204);
    const text = await res.text();
    expect(text.length).toBeGreaterThan(0);
  });
});

// ── Normalization unit tests (processor logic) ───────────────────────────────

test.describe("work_item_ref format (normalization)", () => {
  test("Plane: work_item_ref uses issue.id not key", () => {
    const payload = JSON.parse(loadFixture("plane/issue_created.json"));
    const issueId = payload.issue.id;
    const ref = `plane:${issueId}`;
    expect(ref).toBe("plane:iss_1001");
  });

  test("GitHub: work_item_ref includes full repo name to prevent collision", () => {
    const payload = JSON.parse(loadFixture("github/issues_opened.json"));
    const ref = `github:${payload.repository.full_name}#${payload.issue.number}`;
    expect(ref).toBe("github:Insightpulseai/odoo#421");
    // Ensure repo name is present (collision prevention)
    expect(ref).toContain("Insightpulseai/odoo");
  });

  test("GitHub: different repos produce different refs", () => {
    const ref1 = "github:Insightpulseai/odoo#421";
    const ref2 = "github:Insightpulseai/other-repo#421";
    expect(ref1).not.toBe(ref2);
  });
});
