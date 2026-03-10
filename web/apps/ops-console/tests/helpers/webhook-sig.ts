/**
 * Webhook signature helpers for test use.
 * Computes HMAC-SHA256 signatures matching production receivers.
 */
import { createHmac } from "node:crypto";

/**
 * Compute Plane webhook signature: hex(HMAC-SHA256(secret, body))
 */
export function planeSig(secret: string, body: string): string {
  return createHmac("sha256", secret).update(body).digest("hex");
}

/**
 * Compute GitHub webhook signature: "sha256=" + hex(HMAC-SHA256(secret, body))
 */
export function githubSig(secret: string, body: string): string {
  return "sha256=" + createHmac("sha256", secret).update(body).digest("hex");
}

/**
 * Deterministic test secrets (never use in production)
 */
export const TEST_PLANE_SECRET  = "plane-test-secret-do-not-use-in-prod";
export const TEST_GITHUB_SECRET = "github-test-secret-do-not-use-in-prod";
