import { describe, it, expect } from 'vitest'
import { verifyPaddleWebhookSignature, PRICING_PLANS } from '../paddle'
import crypto from 'crypto'

describe('Paddle Webhook Signature Verification', () => {
  const secret = 'pdl_ntfset_test_secret_key'

  function generateValidSignature(payload: string, timestamp: string): string {
    const signedPayload = `${timestamp}:${payload}`
    const hmac = crypto.createHmac('sha256', secret)
    hmac.update(signedPayload)
    const signature = hmac.digest('hex')
    return `ts=${timestamp};h1=${signature}`
  }

  it('should verify a valid signature', () => {
    const timestamp = Math.floor(Date.now() / 1000).toString()
    const payload = JSON.stringify({ event_type: 'subscription.created', event_id: 'evt_123' })
    const signature = generateValidSignature(payload, timestamp)

    const result = verifyPaddleWebhookSignature(payload, signature, secret)
    expect(result).toBe(true)
  })

  it('should reject an invalid signature', () => {
    const payload = JSON.stringify({ event_type: 'subscription.created', event_id: 'evt_123' })
    const invalidSignature = 'ts=12345;h1=invalidsignature'

    const result = verifyPaddleWebhookSignature(payload, invalidSignature, secret)
    expect(result).toBe(false)
  })

  it('should reject a tampered payload', () => {
    const timestamp = Math.floor(Date.now() / 1000).toString()
    const originalPayload = JSON.stringify({ event_type: 'subscription.created', event_id: 'evt_123' })
    const tamperedPayload = JSON.stringify({ event_type: 'subscription.canceled', event_id: 'evt_123' })
    const signature = generateValidSignature(originalPayload, timestamp)

    const result = verifyPaddleWebhookSignature(tamperedPayload, signature, secret)
    expect(result).toBe(false)
  })

  it('should reject missing signature parts', () => {
    const payload = JSON.stringify({ event_type: 'test' })

    expect(verifyPaddleWebhookSignature(payload, 'ts=12345', secret)).toBe(false)
    expect(verifyPaddleWebhookSignature(payload, 'h1=abc123', secret)).toBe(false)
    expect(verifyPaddleWebhookSignature(payload, '', secret)).toBe(false)
  })

  it('should reject empty secret', () => {
    const payload = JSON.stringify({ event_type: 'test' })
    const signature = 'ts=12345;h1=abc123'

    expect(verifyPaddleWebhookSignature(payload, signature, '')).toBe(false)
  })
})

describe('Pricing Plans', () => {
  it('should have three pricing tiers', () => {
    expect(Object.keys(PRICING_PLANS)).toHaveLength(3)
    expect(PRICING_PLANS).toHaveProperty('starter')
    expect(PRICING_PLANS).toHaveProperty('pro')
    expect(PRICING_PLANS).toHaveProperty('enterprise')
  })

  it('should have annual prices lower than monthly', () => {
    const { starter, pro } = PRICING_PLANS

    expect(starter.annual.price).toBeLessThan(starter.monthly.price!)
    expect(pro.annual.price).toBeLessThan(pro.monthly.price!)
  })

  it('should have enterprise with custom pricing (null)', () => {
    expect(PRICING_PLANS.enterprise.monthly.price).toBeNull()
    expect(PRICING_PLANS.enterprise.annual.price).toBeNull()
    expect(PRICING_PLANS.enterprise.monthly.priceId).toBeNull()
  })

  it('should mark pro as popular', () => {
    expect(PRICING_PLANS.pro.popular).toBe(true)
  })

  it('should have features for each tier', () => {
    expect(PRICING_PLANS.starter.features.length).toBeGreaterThan(0)
    expect(PRICING_PLANS.pro.features.length).toBeGreaterThan(PRICING_PLANS.starter.features.length)
    expect(PRICING_PLANS.enterprise.features.length).toBeGreaterThan(PRICING_PLANS.pro.features.length)
  })
})
