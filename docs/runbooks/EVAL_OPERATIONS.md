# Eval Operations Runbook
- **Missing Evidence Failure**: If models omit evidence, provide explicitly structured evidence references in `system_prompt`.
- **Timeout Metrics Spike**: Scale model inference backends or relax `timeout_seconds` in `eval_engine.yaml`.
- **Quarantine resolution**: Ambiguous runs (where model hallucinates structural outputs) increment the `eval_fail_ambiguity_total` metric. Inspect judge prompt constraints.
