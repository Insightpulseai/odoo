export class RouterMetrics {
  counts = {
    tasks_enqueued: 0,
    tasks_claimed: 0,
    claim_conflicts: 0,
    retries_scheduled: 0,
    retry_exhaustion_count: 0,
    dead_letter_count: 0,
    malformed_envelope_rejects: 0,
    duplicate_suppression_count: 0,
    lease_expiries: 0,
  };
  gauges = {
    queue_depth_gauge: 0,
    task_age_gauge: 0
  };

  recordCount(name: keyof RouterMetrics['counts'], val = 1) { this.counts[name] += val; }
  setGauge(name: keyof RouterMetrics['gauges'], val: number) { this.gauges[name] = val; }
}
