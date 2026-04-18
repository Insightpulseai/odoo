# Agent Platform Runtime — Implementation Plan Stub

> References: `ssot/agent-platform/agent_framework_adoption.yaml#minimal_skeleton`

## Phases

### Phase 0 — Scaffold (current)
- Python package `src/agent_platform/` with MAF wiring
- FastAPI health endpoint
- Foundry auth helper
- SSOT YAML stubs

### Phase 1 — Core Runtime
- Supervisor + planner/router wired to MAF `AIAgentClient`
- Tool registry with MCP allowlist
- Odoo adapter stubs hardened

### Phase 2 — Eval Gate
- Eval runner connected to Foundry evaluation service
- Score thresholds enforced as pipeline gate

### Phase 3 — Production Readiness
- OTel tracing + Azure Monitor
- ACA Dockerfile + azure-pipelines deploy lane
