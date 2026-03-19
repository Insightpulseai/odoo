# Evaluator-Optimizer Design — Checklist

## Prerequisites
- [ ] Quality criteria are measurable (not subjective)
- [ ] First attempt consistently insufficient
- [ ] Iteration demonstrably improves quality
- [ ] No deterministic tool available
- [ ] Latency budget allows multiple iterations

## Design
- [ ] Generator spec defined
- [ ] Evaluator rubric with scoring method
- [ ] Stopping criteria: quality threshold defined
- [ ] Stopping criteria: max iteration limit set
- [ ] Feedback format specified (how eval reaches generator)
- [ ] Typical iteration count estimated
