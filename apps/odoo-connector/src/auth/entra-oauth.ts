/**
 * entra-oauth.ts — PATCHED
 *
 * Changes from original lines 130-165:
 *   BEFORE: base64-decoded token claims directly (unstable data contract)
 *   AFTER:  jose JWKS verification + Microsoft Graph /me for user metadata
 *
 * Per ADO blog Mar 18 2026: "Authentication Tokens Are Not a Data Contract"
 * Token claims (name, email, upn, tid format) can change without notice.
 * Only oid, sub, tid, aud, iss are stable enough to read from token.
 * Everything else → Microsoft Graph /me.
 *
 * Dependencies: npm install jose @azure/identity
 */

import { createRemoteJWKSet, jwtVerify, JWTPayload } from "jose";
import { fetch } from "undici"; // or node-fetch

// ---------------------------------------------------------------------------
// Config — read from env, never hardcoded
// ---------------------------------------------------------------------------
const TENANT_ID = process.env.ENTRA_TENANT_ID!;           // 402de71a-...
const CLIENT_ID = process.env.ENTRA_CLIENT_ID!;           // Odoo app registration
const REDIRECT_URI = process.env.ENTRA_REDIRECT_URI!;
const CLIENT_SECRET = process.env.ENTRA_CLIENT_SECRET_KV!; // from kv-ipai-dev, not hardcoded

// Stable Entra v2 endpoints
const AUTHORITY       = `https://login.microsoftonline.com/${TENANT_ID}`;
const JWKS_URI        = `${AUTHORITY}/discovery/v2.0/keys`;
const TOKEN_ENDPOINT  = `${AUTHORITY}/oauth2/v2.0/token`;
const ISSUER          = `${AUTHORITY}/v2.0`;
const GRAPH_ME        = "https://graph.microsoft.com/v1.0/me";

// ---------------------------------------------------------------------------
// JWKS key set — cached in module scope, jose handles key rotation
// ---------------------------------------------------------------------------
const jwks = createRemoteJWKSet(new URL(JWKS_URI));

// ---------------------------------------------------------------------------
// Stable claims interface — only what the token guarantees
// DO NOT add name/email/upn here — use GraphUser for those
// ---------------------------------------------------------------------------
interface StableTokenClaims {
  oid: string;    // object ID — stable user identifier across sessions
  sub: string;    // pairwise subject — stable per client_id
  tid: string;    // tenant ID — validate === TENANT_ID
  aud: string;    // audience — validate === CLIENT_ID
}

// ---------------------------------------------------------------------------
// Microsoft Graph user profile — stable, always current
// ---------------------------------------------------------------------------
interface GraphUser {
  id: string;                // same as oid
  displayName: string;       // use this, NOT token.name
  mail: string | null;       // use this, NOT token.email
  userPrincipalName: string; // use this, NOT token.upn
  jobTitle: string | null;
}

// ---------------------------------------------------------------------------
// verifyEntraToken (replaces lines 130-165 of original)
//
// BEFORE (lines 130-165, original pattern):
//   const decoded = JSON.parse(atob(token.split('.')[1]));
//   const userId = decoded.oid;
//   const tenantId = decoded.tid;
//   const displayName = decoded.name;    ← UNSTABLE
//   const email = decoded.email;         ← UNSTABLE
//   const upn = decoded.upn;             ← UNSTABLE
//
// AFTER: cryptographic verification + Graph for user metadata
// ---------------------------------------------------------------------------
export async function verifyEntraToken(accessToken: string): Promise<{
  claims: StableTokenClaims;
  user: GraphUser;
}> {
  // Step 1: Verify signature and standard claims using JWKS
  // jose fetches and caches the JWKS automatically, handles key rotation
  const { payload } = await jwtVerify(accessToken, jwks, {
    issuer: ISSUER,
    audience: CLIENT_ID,
    algorithms: ["RS256"],
    clockTolerance: 60, // 1 minute clock skew tolerance
  });

  // Step 2: Extract only stable claims from verified token
  const claims = extractStableClaims(payload);

  // Step 3: Validate tenant — IPAI tenant only
  if (claims.tid !== TENANT_ID) {
    throw new Error(`Tenant mismatch: expected ${TENANT_ID}, got ${claims.tid}`);
  }

  // Step 4: Get user metadata from Graph, NOT from token
  // This is always current even if the user renamed or changed email
  const user = await getGraphUser(accessToken);

  return { claims, user };
}

function extractStableClaims(payload: JWTPayload): StableTokenClaims {
  const oid = payload["oid"] as string | undefined;
  const sub = payload["sub"] as string | undefined;
  const tid = payload["tid"] as string | undefined;
  const aud = Array.isArray(payload.aud) ? payload.aud[0] : payload.aud;

  if (!oid) throw new Error("Token missing oid claim");
  if (!tid) throw new Error("Token missing tid claim");
  if (!sub) throw new Error("Token missing sub claim");
  if (!aud) throw new Error("Token missing aud claim");

  return { oid, sub, tid, aud };
}

async function getGraphUser(accessToken: string): Promise<GraphUser> {
  const resp = await fetch(GRAPH_ME, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Graph /me failed: ${resp.status} ${body}`);
  }

  const data = await resp.json() as GraphUser;
  return data;
}

// ---------------------------------------------------------------------------
// exchangeCodeForToken — unchanged from original, included for context
// ---------------------------------------------------------------------------
export async function exchangeCodeForToken(code: string): Promise<{
  access_token: string;
  refresh_token: string;
  id_token: string;
  expires_in: number;
}> {
  const params = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    code,
    redirect_uri: REDIRECT_URI,
    scope: "openid profile email User.Read offline_access",
  });

  const resp = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString(),
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed: ${resp.status} ${body}`);
  }

  return resp.json() as Promise<{
    access_token: string;
    refresh_token: string;
    id_token: string;
    expires_in: number;
  }>;
}

// ---------------------------------------------------------------------------
// Odoo session creation — uses Graph user, not token claims
// ---------------------------------------------------------------------------
export async function createOdooSession(
  accessToken: string,
  db: string = "odoo"
): Promise<{ uid: number; sessionId: string }> {
  const { claims, user } = await verifyEntraToken(accessToken);

  // Use oid as the stable Odoo external identity key
  // user.mail / user.userPrincipalName for display — from Graph, not token
  const odooLogin = user.mail ?? user.userPrincipalName;

  const resp = await fetch(`${process.env.ODOO_URL}/web/session/authenticate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      params: {
        db,
        login: odooLogin,
        password: claims.oid, // Odoo OIDC addon: oid is the stable credential
      },
    }),
  });

  const data = await (resp.json() as Promise<{
    result?: { uid: number; session_id: string };
    error?: { message: string };
  }>);

  if (data.error) throw new Error(`Odoo auth failed: ${data.error.message}`);
  if (!data.result) throw new Error("Odoo auth returned no result");

  return {
    uid: data.result.uid,
    sessionId: data.result.session_id,
  };
}
