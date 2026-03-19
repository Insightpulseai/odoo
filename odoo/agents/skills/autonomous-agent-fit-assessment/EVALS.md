# Autonomous Agent Fit Assessment — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Criteria assessment accuracy | 35% | Correct on all 4 criteria |
| Pattern recommendation | 25% | Agent only when justified, simpler otherwise |
| Guardrail completeness | 20% | All 4 guardrails present when agent recommended |
| Alternative quality | 10% | Good simpler pattern when agent rejected |
| Cost awareness | 10% | Tradeoff explicitly acknowledged |

## Test Cases

### TC-1: Clear agent task
- Input: "Debug unknown production error"
- Expected: agent_justified with all 4 guardrails
- Fail if: Workflow recommended

### TC-2: Clear workflow task
- Input: "Generate monthly sales report from known data"
- Expected: workflow_sufficient (sequential)
- Fail if: Agent recommended

### TC-3: Borderline case
- Input: "Write a blog post on a given topic"
- Expected: Reasoned assessment (likely evaluator-optimizer, not agent)
- Fail if: Defaulted to agent without analyzing criteria

## Pass threshold: 3/3 correct assessments with complete guardrails
