// jwt_issuer_test.ts
// Verifies JWT_ISSUER selection: client_id-first, app_id as fallback.
//
// Run: deno test --allow-env supabase/functions/github-app-auth/jwt_issuer_test.ts
//
// These are unit tests of pure selection logic — no network calls, no private key required.

import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";

// ── Reproduction of the issuer-selection logic ─────────────────────────────
// Mirrors the constant logic at the top of index.ts. Tests prove the invariants
// without importing the full function (which requires GITHUB_PRIVATE_KEY).

function selectIssuer(clientId: string | undefined, appId: string | undefined): string {
  // client_id preferred; fallback to app_id; both undefined → empty string (will fail at JWT sign time)
  return clientId || appId || "";
}

// ── Tests ──────────────────────────────────────────────────────────────────

Deno.test("selectIssuer: prefers client_id when both are set", () => {
  const iss = selectIssuer("Iv23liwGL7fnYySPPAjS", "2191216");
  assertEquals(iss, "Iv23liwGL7fnYySPPAjS");
});

Deno.test("selectIssuer: falls back to app_id when client_id is absent", () => {
  const iss = selectIssuer(undefined, "2191216");
  assertEquals(iss, "2191216");
});

Deno.test("selectIssuer: falls back to app_id when client_id is empty string", () => {
  const iss = selectIssuer("", "2191216");
  assertEquals(iss, "2191216");
});

Deno.test("selectIssuer: returns empty string when both are absent (will fail at sign time)", () => {
  const iss = selectIssuer(undefined, undefined);
  assertEquals(iss, "");
});

// ── Concrete pulser-hub values ─────────────────────────────────────────────

Deno.test("pulser-hub: client_id Iv23liwGL7fnYySPPAjS is selected over app_id 2191216", () => {
  const clientId = "Iv23liwGL7fnYySPPAjS";   // ssot/github/app-manifest.yaml
  const appId    = "2191216";                 // ssot/github/app-manifest.yaml
  assertEquals(selectIssuer(clientId, appId), clientId);
  assertEquals(selectIssuer(undefined, appId), appId);
});
