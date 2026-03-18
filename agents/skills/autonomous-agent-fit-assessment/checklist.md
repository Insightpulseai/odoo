# Autonomous Agent Fit Assessment — Checklist

## Criteria (ALL must be true for agent recommendation)
- [ ] Open-ended: steps cannot be predicted
- [ ] Feedback-dependent: environmental feedback drives next actions
- [ ] Adaptive: strategy must change based on discoveries
- [ ] Cost-justified: quality gain outweighs latency/cost increase

## If Agent Justified
- [ ] Sandbox environment defined
- [ ] Resource limits set (tokens, tool calls, time)
- [ ] Monitoring/observability configured
- [ ] Human review checkpoints specified

## If Not Justified
- [ ] Simpler alternative identified (single call, sequential, parallel, eval-optimizer)
- [ ] Documented why the simpler pattern suffices
