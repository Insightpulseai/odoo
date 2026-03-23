export class EvalMetricsAggregator {
  counts = {
    eval_requests_total: 0,
    eval_success_total: 0,
    eval_fail_explicit_total: 0,
    eval_fail_ambiguity_total: 0,
    eval_fail_timeout_total: 0,
    eval_fail_malformed_total: 0
  };

  record(name: keyof EvalMetricsAggregator['counts']) {
    this.counts[name]++;
  }
}
