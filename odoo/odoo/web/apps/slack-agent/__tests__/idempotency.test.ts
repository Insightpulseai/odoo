// __tests__/idempotency.test.ts
// Tests for Slack idempotency key builders.
//
// Slack retries delivery on non-2xx or slow responses.
// The same Slack event must produce the same idempotency key so that
// taskbus.enqueue() deduplicates it (ops.runs.idempotency_key UNIQUE).

import { describe, it, expect } from 'vitest'
import {
  slackEventKey,
  slackInteractionKey,
  slackCommandKey,
} from '../server/lib/idempotency'

describe('slackEventKey', () => {
  it('produces deterministic key from event_id', () => {
    expect(slackEventKey('Ev012ABC')).toBe('slack:event:Ev012ABC')
    expect(slackEventKey('Ev012ABC')).toBe(slackEventKey('Ev012ABC'))
  })

  it('produces different keys for different event_ids', () => {
    expect(slackEventKey('Ev001')).not.toBe(slackEventKey('Ev002'))
  })
})

describe('slackInteractionKey', () => {
  it('produces deterministic key from trigger_id', () => {
    const tid = '12345.98765.abcd'
    expect(slackInteractionKey(tid)).toBe(`slack:interaction:${tid}`)
    expect(slackInteractionKey(tid)).toBe(slackInteractionKey(tid))
  })
})

describe('slackCommandKey', () => {
  it('normalizes leading slash in command name', () => {
    expect(slackCommandKey('/run', 'tid1')).toBe('slack:command:run:tid1')
    expect(slackCommandKey('run', 'tid1')).toBe('slack:command:run:tid1')
  })

  it('different trigger_ids produce different keys (no dedup across invocations)', () => {
    expect(slackCommandKey('/ask', 'tid1')).not.toBe(slackCommandKey('/ask', 'tid2'))
  })

  it('different commands produce different keys', () => {
    expect(slackCommandKey('/ask', 'tid1')).not.toBe(slackCommandKey('/run', 'tid1'))
  })
})
