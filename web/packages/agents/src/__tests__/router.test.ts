// packages/agents/src/__tests__/router.test.ts
// Tests router dispatch + ping handler writes expected events.

import type { SupabaseClient } from '@supabase/supabase-js'
import type { JobMessage } from '@ipai/taskbus'
import { dispatch } from '../router'

function makeMsg(overrides: Partial<JobMessage> = {}): JobMessage {
  return {
    run_id:          'test-run-id',
    job_type:        'ping',
    agent:           'ping-agent',
    input:           { message: 'hello' },
    idempotency_key: 'adhoc:ping:test-1',
    ...overrides,
  }
}

// Minimal Supabase mock — router/handlers don't call it directly for ping
const mockSupabase = {} as SupabaseClient

describe('dispatch — ping-agent', () => {
  it('returns completed status for a valid ping message', async () => {
    const result = await dispatch(makeMsg(), mockSupabase)
    expect(result.status).toBe('completed')
  })

  it('emits a ping.pong event with the echoed message', async () => {
    const result = await dispatch(makeMsg({ input: { message: 'test-ping' } }), mockSupabase)
    expect(result.events).toHaveLength(1)
    expect(result.events![0].event_type).toBe('ping.pong')
    expect(result.events![0].payload.message).toBe('test-ping')
  })

  it('includes run_id in the output', async () => {
    const result = await dispatch(makeMsg(), mockSupabase)
    expect(result.output?.run_id).toBe('test-run-id')
  })
})

describe('dispatch — unknown job_type', () => {
  it('returns failed status for unregistered job type', async () => {
    // sync-odoo-agent allows sync_odoo, but we pass an unknown job
    const result = await dispatch(
      makeMsg({ job_type: 'unknown_job', agent: 'ping-agent' }),
      mockSupabase,
    ).catch(() => ({ status: 'failed' as const, error: 'policy' }))
    expect(result.status).toBe('failed')
  })
})

describe('dispatch — policy violation', () => {
  it('throws PolicyViolation if agent is not registered', async () => {
    await expect(
      dispatch(makeMsg({ agent: 'unknown-agent' }), mockSupabase),
    ).rejects.toThrow('PolicyViolation')
  })
})
