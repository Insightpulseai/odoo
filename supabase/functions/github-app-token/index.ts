// Supabase Edge Function: GitHub App Token Broker
// Contract: C-19 (docs/contracts/GITHUB_APP_CONTRACT.md)
//
// Generates GitHub App JWT and exchanges it for installation access tokens.
// - RS256 JWT signing using Web Crypto API (no external JWT library)
// - In-memory token cache with 5-minute safety margin
// - Returns 503 with ssot_ref when secrets are missing

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// JWT helper — RS256 signing using Web Crypto API
async function createJWT(appId: string, privateKeyPem: string): Promise<string> {
  // Decode PEM to binary
  const pemContent = privateKeyPem
    .replace("-----BEGIN RSA PRIVATE KEY-----", "")
    .replace("-----END RSA PRIVATE KEY-----", "")
    .replace(/\n/g, "");
  const binaryKey = Uint8Array.from(atob(pemContent), (c) => c.charCodeAt(0));

  const key = await crypto.subtle.importKey(
    "pkcs8",
    binaryKey,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );

  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT" };
  const payload = {
    iss: appId,
    iat: now - 60,
    exp: now + 600, // 10 minutes
  };

  const encode = (obj: unknown) => {
    const json = JSON.stringify(obj);
    return btoa(json).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
  };

  const headerB64 = encode(header);
  const payloadB64 = encode(payload);
  const signingInput = `${headerB64}.${payloadB64}`;

  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    new TextEncoder().encode(signingInput),
  );

  const signatureB64 = btoa(String.fromCharCode(...new Uint8Array(signature)))
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");

  return `${headerB64}.${payloadB64}.${signatureB64}`;
}

// In-memory token cache
const tokenCache = new Map<number, { token: string; expiresAt: number }>();

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const { installation_id } = await req.json();
  if (!installation_id) {
    return new Response(
      JSON.stringify({ error: "installation_id required" }),
      { status: 400 },
    );
  }

  // Check cache
  const cached = tokenCache.get(installation_id);
  const now = Math.floor(Date.now() / 1000);
  if (cached && cached.expiresAt > now + 300) {
    // Return cached token if > 5 min remaining
    return new Response(
      JSON.stringify({ token: cached.token, expires_at: cached.expiresAt, cached: true }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }

  // Load secrets
  const appId = Deno.env.get("GITHUB_APP_ID");
  const privateKey = Deno.env.get("GITHUB_APP_PRIVATE_KEY_PEM");

  if (!appId || !privateKey) {
    return new Response(
      JSON.stringify({
        error: "KEY_MISSING",
        ssot_ref: "ssot/secrets/registry.yaml",
        missing: !appId ? "GITHUB_APP_ID" : "GITHUB_APP_PRIVATE_KEY_PEM",
      }),
      { status: 503 },
    );
  }

  // Generate JWT
  const jwt = await createJWT(appId, privateKey);

  // Exchange for installation token
  const resp = await fetch(
    `https://api.github.com/app/installations/${installation_id}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );

  if (!resp.ok) {
    const errBody = await resp.text();
    console.error(`GitHub token exchange failed: ${resp.status} ${errBody}`);
    return new Response(
      JSON.stringify({ error: "Token exchange failed", status: resp.status, detail: errBody }),
      { status: 502 },
    );
  }

  const tokenData = await resp.json();
  const expiresAt = Math.floor(new Date(tokenData.expires_at).getTime() / 1000);

  // Cache
  tokenCache.set(installation_id, {
    token: tokenData.token,
    expiresAt: expiresAt,
  });

  return new Response(
    JSON.stringify({
      token: tokenData.token,
      expires_at: expiresAt,
      permissions: tokenData.permissions,
      cached: false,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } },
  );
});
