// server/lib/verify.ts
// Slack request signature verification.
//
// Slack signs every inbound request with:
//   X-Slack-Signature:        v0=<hex-HMAC-SHA256>
//   X-Slack-Request-Timestamp: <unix-seconds>
//
// The signature is HMAC-SHA256 of "v0:<timestamp>:<rawBody>" using
// SLACK_SIGNING_SECRET as the key.
//
// References:
//   https://api.slack.com/authentication/verifying-requests-from-slack
//   https://docs.slack.dev/authentication/verifying-requests-from-slack

const REPLAY_WINDOW_SECONDS = 5 * 60 // 5 minutes

/**
 * Verify a Slack request signature.
 * Returns null on success; returns an error string on failure.
 *
 * @param signingSecret  SLACK_SIGNING_SECRET value
 * @param rawBody        Raw request body bytes (Buffer or Uint8Array)
 * @param timestamp      Value of X-Slack-Request-Timestamp header
 * @param signature      Value of X-Slack-Signature header (e.g. "v0=abc123")
 */
export async function verifySlackSignature(
  signingSecret: string,
  rawBody: Uint8Array | string,
  timestamp: string | null,
  signature: string | null,
): Promise<string | null> {
  if (!timestamp || !signature) {
    return 'Missing X-Slack-Signature or X-Slack-Request-Timestamp'
  }

  // Replay-attack guard: reject requests older than 5 minutes
  const ts = parseInt(timestamp, 10)
  const nowSec = Math.floor(Date.now() / 1000)
  if (Math.abs(nowSec - ts) > REPLAY_WINDOW_SECONDS) {
    return `Request timestamp too old (${Math.abs(nowSec - ts)}s). Possible replay attack.`
  }

  const bodyStr =
    typeof rawBody === 'string'
      ? rawBody
      : new TextDecoder().decode(rawBody)

  const baseString = `v0:${timestamp}:${bodyStr}`

  // Use Web Crypto API (available in Node.js 18+, Vercel Edge, Deno)
  const enc = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(signingSecret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  )

  const sigBytes = await crypto.subtle.sign('HMAC', key, enc.encode(baseString))
  const computedHex = Array.from(new Uint8Array(sigBytes))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
  const computed = `v0=${computedHex}`

  // Constant-time comparison to prevent timing attacks
  if (!timingSafeEqual(computed, signature)) {
    return 'Slack signature mismatch'
  }

  return null // success
}

/** Constant-time string comparison (prevents timing side-channels). */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false
  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return result === 0
}
