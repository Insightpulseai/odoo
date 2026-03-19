# Autonomous Agent Fit Assessment — Prompt

You are assessing whether a task requires an **autonomous agent** — the most complex and expensive pattern.

## Assessment Criteria

An autonomous agent is justified ONLY when ALL of these are true:

1. **Open-ended**: Steps cannot be predicted or enumerated in advance
2. **Feedback-dependent**: Progress depends on environmental feedback (tool results, execution outputs)
3. **Adaptive**: Strategy must change based on what's discovered during execution
4. **Justified cost**: Quality improvement outweighs latency and token cost increase

If ANY criterion fails, recommend a simpler pattern.

## Guardrail Requirements (Mandatory for Agent Recommendations)

Every autonomous agent must have:
- **Sandbox**: Isolated execution environment
- **Resource limits**: Max tokens, max tool calls, max time
- **Monitoring**: Observable execution trace
- **Human review**: Defined checkpoints where human can inspect/redirect

## Output Format

```
Assessment: [agent_justified | workflow_sufficient | single_call_sufficient]
Open-ended: [yes/no — reasoning]
Feedback-dependent: [yes/no — reasoning]
Adaptive: [yes/no — reasoning]
Cost-justified: [yes/no — reasoning]
Guardrails: [if agent justified, list all four]
Alternative: [if not justified, which simpler pattern]
```
