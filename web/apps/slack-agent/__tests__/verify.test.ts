// __tests__/verify.test.ts
// Unit tests for Slack signature verification.
//
// Tests cover:
//   - Valid signatures pass
//   - Invalid signatures reject
//   - Replay attacks reject (old timestamp)
//   - Missing headers reject

import { describe, it, expect } from 'vitest'
import { verifySlackSignature } from '../server/lib/verify'

const SECRET = 'test_signing_secret_abc123'

/** Build a valid Slack-signed request for testing. */
async function buildValidRequest(
  body: string,
  secret = SECRET,
  nowSec = Math.floor(Date.now() / 1000),
): Promise<{ timestamp: string; signature: string }> {
  const timestamp = String(nowSec)
  const baseString = `v0:${timestamp}:${body}`

  const enc = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  )
  const sigBytes = await crypto.subtle.sign('HMAC', key, enc.encode(baseString))
  const hex = Array.from(new Uint8Array(sigBytes))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')

  return { timestamp, signature: `v0=${hex}` }
}

describe('verifySlackSignature', () => {
  it('returns null for a valid signature', async () => {
    const body = '{"type":"event_callback","event_id":"Ev123"}'
    const { timestamp, signature } = await buildValidRequest(body)
    const err = await verifySlackSignature(SECRET, body, timestamp, signature)
    expect(err).toBeNull()
  })

  it('rejects a tampered body', async () => {
    const body = '{"type":"event_callback","event_id":"Ev123"}'
    const { timestamp, signature } = await buildValidRequest(body)
    const tamperedBody = '{"type":"event_callback","event_id":"EVIL"}'
    const err = await verifySlackSignature(SECRET, tamperedBody, timestamp, signature)
    expect(err).toContain('Slack signature mismatch')
  })

  it('rejects a wrong signing secret', async () => {
    const body = '{"type":"event_callback"}'
    const { timestamp, signature } = await buildValidRequest(body, 'wrong_secret')
    const err = await verifySlackSignature(SECRET, body, timestamp, signature)
    expect(err).toContain('Slack signature mismatch')
  })

  it('rejects missing timestamp header', async () => {
    const body = '{"type":"event_callback"}'
    const { signature } = await buildValidRequest(body)
    const err = await verifySlackSignature(SECRET, body, null, signature)
    expect(err).toContain('Missing')
  })

  it('rejects missing signature header', async () => {
    const body = '{"type":"event_callback"}'
    const { timestamp } = await buildValidRequest(body)
    const err = await verifySlackSignature(SECRET, body, timestamp, null)
    expect(err).toContain('Missing')
  })

  it('rejects replay attack (timestamp too old)', async () => {
    const body = '{"type":"event_callback"}'
    const oldTimestamp = Math.floor(Date.now() / 1000) - 6 * 60 // 6 minutes ago
    const { timestamp, signature } = await buildValidRequest(body, SECRET, oldTimestamp)
    const err = await verifySlackSignature(SECRET, body, timestamp, signature)
    expect(err).toContain('timestamp too old')
  })

  it('accepts Uint8Array body', async () => {
    const body = 'payload=hello+world'
    const { timestamp, signature } = await buildValidRequest(body)
    const bodyBytes = new TextEncoder().encode(body)
    const err = await verifySlackSignature(SECRET, bodyBytes, timestamp, signature)
    expect(err).toBeNull()
  })
})
