# Claude MCP Integration — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Tool description quality | 30% | Clear, capability-focused, tested |
| Auth selection | 20% | Hierarchy followed correctly |
| Response design | 20% | High-signal, no noise |
| Error handling | 15% | Actionable, educational |
| Discovery config | 15% | Appropriate for tool count |

## Test Cases

### TC-1: Small tool set (<10)
- Input: "Integrate 5 Odoo tools"
- Expected: All loaded, no discovery needed
- Fail if: Unnecessary discovery configured

### TC-2: Large tool set (>10)
- Input: "Integrate 20 Azure tools"
- Expected: 3-5 always loaded, rest deferred, discovery enabled
- Fail if: All 20 loaded simultaneously

### TC-3: Auth selection
- Input: "Azure-hosted service with managed identity available"
- Expected: Managed identity selected
- Fail if: API key recommended

## Pass threshold: 3/3 correct designs
