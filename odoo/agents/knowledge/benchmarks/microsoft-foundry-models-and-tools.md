# Microsoft Foundry — Models, Tools, and Runtime Benchmark Reference

## Source

Microsoft Learn Foundry documentation (Azure AI Foundry platform).

## Three Control Planes

### 1. Model Selection and Routing

The Foundry model leaderboard compares models across four dimensions:

| Dimension | What it measures |
|-----------|-----------------|
| Quality | Task-specific accuracy, coherence, groundedness |
| Safety | Content safety, jailbreak resistance, harmful content filtering |
| Cost | Token pricing, total cost of ownership per workload |
| Throughput | Tokens per second, latency percentiles, concurrent request handling |

**Model router** enables real-time quality/cost/latency trade-offs by routing requests to different models based on workload characteristics. It is a conditional optimization surface, not a default-on feature.

### 2. Tool Catalog and MCP

Foundry Agent Service supports MCP (Model Context Protocol) tools with a clear local/remote distinction:

| Tool type | Description | Auth model |
|-----------|-------------|------------|
| Local MCP | Tools running in-process or same-host | Process-level isolation |
| Remote MCP | Tools accessed over network (Azure Functions, ACA, external) | Managed identity, Entra OAuth2, OAuth2, API key |
| Native Foundry tools | Built-in tools (code interpreter, file search, Bing grounding) | Platform-managed |

**Auth mode preference order**: managed identity > Entra OAuth2 > OAuth2 > key-based (last resort).

Custom remote MCP servers can be implemented via Azure Functions with managed identity and RBAC, registered in API Center for catalog governance.

### 3. Agent Build, Eval, and Runtime

The agent lifecycle follows: model + tools + auth configuration in builder, then validate via eval, then promote to hosted runtime.

| Stage | What happens |
|-------|-------------|
| Build | Select model, attach tools, configure auth, define system prompt |
| Eval | Run evaluation suite against quality/safety/policy thresholds |
| Promote | Move validated configuration to hosted runtime with evidence package |
| Runtime | Hosted agent serving requests with monitoring, tracing, rollback |

## Guardrails

1. **Foundry leaderboard = benchmark input, not automatic approval.** Leaderboard data informs model selection but does not replace workload-specific evaluation.

2. **Model router = conditional optimization surface, not default everywhere.** Use pinned models when workload is uniform; use router when workload variability justifies the complexity.

3. **Remote MCP = allowed only when auth, trust boundary, and evidence are defined.** No unregistered remote tools in production.

4. **Managed identity / Entra = preferred for Azure-native internal tool access.** Key-based auth is last resort and requires Key Vault storage.

5. **Preview features = not automatic canonical baseline.** GA models and tools are the default. Preview adoption requires explicit justification and eval evidence.

## Cross-References

- `docs/contracts/foundry-vscode-auth-contract.md` (C-35)
- `ssot/agents/mcp-baseline.yaml`
- `ssot/runtime/live-builder-surfaces.yaml`
- `agents/personas/foundry-model-governor.md`
- `agents/personas/foundry-tool-governor.md`
- `agents/personas/foundry-runtime-builder.md`
- `agents/personas/foundry-eval-judge.md`
