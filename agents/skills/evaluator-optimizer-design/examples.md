# Evaluator-Optimizer Design — Examples

## Example 1: Marketing Copy Refinement

```
Generator: Write marketing copy for product launch
Evaluator: Score on brand voice (1-10), clarity (1-10), CTA strength (1-10)
Stopping: All scores ≥ 8 OR iterations ≥ 3
Feedback: Specific improvement suggestions per dimension
Expected iterations: 2
```

## Example 2: SQL Query Optimization

```
Generator: Write SQL query for analytics report
Evaluator: EXPLAIN ANALYZE (deterministic) — check cost, scan type, join strategy
Stopping: Cost < threshold OR iterations ≥ 4
Feedback: Execution plan with bottleneck identification
Expected iterations: 2-3
```

Note: Example 2 uses a deterministic evaluator (EXPLAIN ANALYZE), which is preferred over LLM-based evaluation when available.
