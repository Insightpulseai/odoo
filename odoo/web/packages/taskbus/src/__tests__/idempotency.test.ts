// packages/taskbus/src/__tests__/idempotency.test.ts
import { scheduleBucketKey, runEventKey, adHocJobKey } from '../idempotency'

describe('scheduleBucketKey', () => {
  it('rounds down to the nearest 5-minute boundary', () => {
    const d = new Date('2026-03-01T08:07:00.000Z') // mm=7 → bucket=5
    expect(scheduleBucketKey('sched-1', d)).toBe('schedule:sched-1:bucket:2026-03-01-08-05')
  })

  it('produces the same key for two dates in the same 5-min window', () => {
    const d1 = new Date('2026-03-01T08:10:00.000Z')
    const d2 = new Date('2026-03-01T08:14:59.999Z')
    expect(scheduleBucketKey('s', d1)).toBe(scheduleBucketKey('s', d2))
  })

  it('produces different keys for different 5-min windows', () => {
    const d1 = new Date('2026-03-01T08:10:00.000Z')
    const d2 = new Date('2026-03-01T08:15:00.000Z')
    expect(scheduleBucketKey('s', d1)).not.toBe(scheduleBucketKey('s', d2))
  })

  it('includes the schedule id in the key', () => {
    const d = new Date('2026-03-01T00:00:00.000Z')
    const key = scheduleBucketKey('my-schedule-id', d)
    expect(key).toContain('my-schedule-id')
  })
})

describe('runEventKey', () => {
  it('produces a stable key for the same run and step', () => {
    expect(runEventKey('run-abc', 'ping.pong:0')).toBe('run:run-abc:step:ping.pong:0')
  })
})

describe('adHocJobKey', () => {
  it('includes jobType and clientKey', () => {
    const key = adHocJobKey('ping', 'my-client-key')
    expect(key).toBe('adhoc:ping:my-client-key')
  })
})
