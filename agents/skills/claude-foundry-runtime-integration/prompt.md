# Claude Foundry Runtime Integration — Prompt

You are integrating Claude into Azure AI Foundry as a model provider.

## Decision: Foundry vs. Direct API

Choose Foundry when:
- Model governance (routing, version control, cost tracking) is needed
- Multiple models coexist and Foundry manages selection
- Enterprise audit trail required

Choose Direct API when:
- Simple single-model integration
- Minimal governance overhead acceptable
- Lowest latency is priority

## Deployment Steps

1. **Model catalog**: Deploy Claude from Foundry model catalog
2. **Configuration**: Set runtime parameters (temperature, max tokens, etc.)
3. **Rate limits**: Configure per-project rate limits
4. **Cost controls**: Set budget alerts and spending limits
5. **Tool integration**: Connect MCP servers if tools are needed
6. **Validation**: End-to-end test

## Output

```
Integration path: [foundry_hosted | direct_api]
Justification: [why this path]
Deployment: [Foundry project, model version]
Runtime: [parameters, limits]
Tools: [MCP servers connected, if any]
Validation: [test results]
```
