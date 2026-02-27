/**
 * auth_guard.ts — Supabase Edge Function auth middleware
 *
 * Supports three verification modes:
 *
 *   JWT (user token)
 *     Authorization: Bearer <supabase-jwt>
 *     Verifies against SUPABASE_JWT_SECRET env var.
 *     Populates req.user with decoded claims.
 *
 *   Service Role
 *     Authorization: Bearer <service_role_key>
 *     Allows full bypass for server-to-server calls.
 *
 *   HMAC-SHA256 (webhook callbacks from Odoo / external systems)
 *     x-signature: <hex>
 *     x-timestamp: <unix_epoch>
 *     Verifies HMAC-SHA256(body + timestamp, WEBHOOK_HMAC_SECRET).
 *     Rejects requests with timestamp outside ±300s window.
 *
 * Usage
 * -----
 *   import { requireAuth, requireHmac } from "../_shared/auth_guard.ts";
 *
 *   // Require any valid JWT or service-role:
 *   const user = await requireAuth(req);
 *
 *   // Require HMAC signature (webhook route):
 *   const body = await requireHmac(req);
 *
 * Env vars (set in Supabase Vault / project secrets — never hardcoded):
 *   SUPABASE_JWT_SECRET       — project JWT secret
 *   SUPABASE_SERVICE_ROLE_KEY — service role key
 *   WEBHOOK_HMAC_SECRET       — HMAC secret shared with Odoo
 */

import { create, verify } from "https://deno.land/x/djwt@v3.0.2/mod.ts";

const TIMESTAMP_WINDOW_SEC = 300;

// ── Types ──────────────────────────────────────────────────────────────────

export interface AuthUser {
  sub: string;
  email?: string;
  role?: string;
  isServiceRole: boolean;
}

export class AuthError extends Error {
  constructor(
    message: string,
    public readonly status: number = 401,
  ) {
    super(message);
    this.name = "AuthError";
  }
}

// ── JWT / Service-Role auth ────────────────────────────────────────────────

/**
 * Require a valid Supabase JWT or service-role key.
 * Throws AuthError on failure.
 */
export async function requireAuth(req: Request): Promise<AuthUser> {
  const authHeader = req.headers.get("Authorization") ?? "";
  if (!authHeader.startsWith("Bearer ")) {
    throw new AuthError("Missing Authorization header", 401);
  }
  const token = authHeader.slice(7);

  // Service-role shortcut (full bypass)
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  if (serviceRoleKey && token === serviceRoleKey) {
    return { sub: "service_role", role: "service_role", isServiceRole: true };
  }

  // Verify as JWT
  const jwtSecret = Deno.env.get("SUPABASE_JWT_SECRET") ?? "";
  if (!jwtSecret) {
    throw new AuthError("SUPABASE_JWT_SECRET not configured", 500);
  }

  try {
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(jwtSecret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"],
    );
    const payload = await verify(token, key) as Record<string, unknown>;
    const sub = payload["sub"] as string | undefined;
    if (!sub) {
      throw new AuthError("Invalid JWT: missing sub claim", 401);
    }
    return {
      sub,
      email: payload["email"] as string | undefined,
      role: payload["role"] as string | undefined,
      isServiceRole: false,
    };
  } catch (err) {
    if (err instanceof AuthError) throw err;
    throw new AuthError(`JWT verification failed: ${err.message}`, 401);
  }
}

// ── HMAC webhook auth ──────────────────────────────────────────────────────

/**
 * Require a valid HMAC-SHA256 signature for webhook requests.
 * Returns the raw body bytes on success.
 * Throws AuthError on failure.
 */
export async function requireHmac(req: Request): Promise<Uint8Array> {
  const signature = req.headers.get("x-signature") ?? "";
  const timestampStr = req.headers.get("x-timestamp") ?? "";

  if (!signature || !timestampStr) {
    throw new AuthError("Missing x-signature or x-timestamp header", 401);
  }

  const timestamp = parseInt(timestampStr, 10);
  if (isNaN(timestamp)) {
    throw new AuthError("Invalid x-timestamp", 401);
  }
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - timestamp) > TIMESTAMP_WINDOW_SEC) {
    throw new AuthError(
      `Timestamp outside ±${TIMESTAMP_WINDOW_SEC}s window`,
      401,
    );
  }

  const hmacSecret = Deno.env.get("WEBHOOK_HMAC_SECRET") ?? "";
  if (!hmacSecret) {
    throw new AuthError("WEBHOOK_HMAC_SECRET not configured", 500);
  }

  const body = new Uint8Array(await req.arrayBuffer());
  const message = new Uint8Array([
    ...body,
    ...new TextEncoder().encode(timestampStr),
  ]);

  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(hmacSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );

  const signatureBytes = hexToBytes(signature);
  const valid = await crypto.subtle.verify("HMAC", key, signatureBytes, message);
  if (!valid) {
    throw new AuthError("HMAC signature verification failed", 401);
  }

  return body;
}

// ── Helpers ────────────────────────────────────────────────────────────────

function hexToBytes(hex: string): Uint8Array {
  const result = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    result[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return result;
}

/**
 * Convenience wrapper: returns a 401 JSON Response on AuthError.
 * Usage:
 *   const user = await guardAuth(req);
 *   if (user instanceof Response) return user;
 */
export async function guardAuth(
  req: Request,
): Promise<AuthUser | Response> {
  try {
    return await requireAuth(req);
  } catch (err) {
    if (err instanceof AuthError) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: err.status,
        headers: { "Content-Type": "application/json" },
      });
    }
    throw err;
  }
}

export async function guardHmac(
  req: Request,
): Promise<Uint8Array | Response> {
  try {
    return await requireHmac(req);
  } catch (err) {
    if (err instanceof AuthError) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: err.status,
        headers: { "Content-Type": "application/json" },
      });
    }
    throw err;
  }
}
