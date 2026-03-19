/**
 * Evaluation contract — defines eval dataset, result, and threshold shapes.
 * Mirrors: agents/evals/odoo-copilot/thresholds.yaml + rubric.md
 */

/** A single eval test case */
export interface EvalCase {
  id: string;
  category: 'quality' | 'safety' | 'product' | 'rbac' | 'context' | 'actions';
  subcategory: string;
  prompt: string;
  expected_behavior: string;
  context?: Record<string, unknown>;
}

/** Result of evaluating a single case */
export interface EvalCaseResult {
  id: string;
  category: string;
  subcategory: string;
  prompt: string;
  response_excerpt: string;
  pass: boolean;
  notes: string;
  manual_review: boolean;
  latency_ms?: number;
}

/** Threshold configuration */
export interface EvalThresholds {
  // Quality
  relevance_min: number;
  task_adherence_min: number;
  accuracy_min: number;
  context_awareness_min: number;

  // Safety
  refusal_correctness_min: number;
  hallucination_rate_max: number;
  pii_leakage_max: number;
  critical_policy_violations_max: number;
  prompt_injection_resistance_min: number;
  data_exfiltration_resistance_min: number;
  privilege_escalation_resistance_min: number;

  // Runtime
  latency_p95_seconds_max: number;
  error_rate_max: number;
}

/** Complete eval run result */
export interface EvalRunResult {
  eval_run_id: string;
  date: string;
  agent_id: string;
  system_prompt_version: string;
  model: string;
  dataset_size: number;
  results: EvalCaseResult[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    pass_rate: number;
    by_category: Record<string, { total: number; passed: number }>;
  };
  threshold_check: Record<string, { threshold: number; actual: number; pass: boolean }>;
  release_decision: string;
  blocking_issues: string[];
}

/** Blocking conditions that prevent release */
export const BLOCKING_CONDITIONS = [
  'no_evaluation_results',
  'any_critical_policy_violation',
  'any_pii_leak',
  'any_action_confirmation_bypass',
  'any_prompt_injection_success',
  'any_privilege_escalation_success',
  'any_data_exfiltration_success',
  'any_rbac_bypass',
] as const;

export type BlockingCondition = (typeof BLOCKING_CONDITIONS)[number];
