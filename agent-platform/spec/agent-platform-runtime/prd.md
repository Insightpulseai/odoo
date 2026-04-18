# Agent Platform Runtime — PRD Stub

> References: `ssot/agent-platform/agent_framework_adoption.yaml#minimal_skeleton`
> Full PRD: `docs/architecture/agent-framework-adoption.md`

## Problem
IPAI needs a policy-gated, multi-agent runtime that orchestrates specialist workers across
Odoo, Foundry, and Azure services without exposing credentials to agents.

## Success Criteria
- `/health` returns 200 within 500 ms in ACA.
- Supervisor routes tasks to correct specialist worker.
- All mutating tool calls produce an audit trace.
- Eval gate passes before any production release.
