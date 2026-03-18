# Claude Foundry Runtime Integration — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Path selection | 30% | Correct Foundry vs. Direct API choice |
| Configuration quality | 25% | Appropriate parameters, limits, controls |
| Cost governance | 20% | Budget and rate limits configured |
| Tool integration | 15% | MCP connected if needed |
| Validation | 10% | End-to-end test performed |

## Test Cases

### TC-1: Multi-model governance scenario
- Input: "3 models, enterprise audit required"
- Expected: Foundry-hosted with full governance
- Fail if: Direct API recommended

### TC-2: Simple single-model scenario
- Input: "One Claude call for a script, no governance needed"
- Expected: Direct API
- Fail if: Foundry recommended for trivial case

## Pass threshold: 2/2 correct path selections
