// packages/taskbus/src/idempotency.ts
// Idempotency-key helpers for runs and events.

/**
 * Build a deterministic bucket key for a schedule run.
 * Dedupes within a 5-minute window (same cron tick resolution).
 *
 * Format: schedule:<schedule_id>:bucket:<YYYY-MM-DD-HH-mm-5min>
 */
export function scheduleBucketKey(scheduleId: string, now: Date = new Date()): string {
  // Round down to nearest 5-minute boundary
  const mm = now.getUTCMinutes()
  const bucket5 = Math.floor(mm / 5) * 5
  const ts = [
    now.getUTCFullYear(),
    String(now.getUTCMonth() + 1).padStart(2, '0'),
    String(now.getUTCDate()).padStart(2, '0'),
    String(now.getUTCHours()).padStart(2, '0'),
    String(bucket5).padStart(2, '0'),
  ].join('-')
  return `schedule:${scheduleId}:bucket:${ts}`
}

/**
 * Build a deterministic idempotency key for a run event.
 * Format: run:<run_id>:step:<step_key>
 */
export function runEventKey(runId: string, stepKey: string): string {
  return `run:${runId}:step:${stepKey}`
}

/**
 * Build a idempotency key for ad-hoc job submissions.
 * Callers should make `clientKey` stable for the logical operation.
 */
export function adHocJobKey(jobType: string, clientKey: string): string {
  return `adhoc:${jobType}:${clientKey}`
}
