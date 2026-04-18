# Agent Platform Runtime — Constitution

> Stub. Canonical authority: `ssot/agent-platform/agent_framework_adoption.yaml` and
> `docs/architecture/agent-framework-adoption.md`.

## Core Principles

1. Supervisor-mediated orchestration only — workers never invoke workers directly.
2. Mutating actions require explicit approval (read-only tools may run approval-free).
3. Session state stored externally; agents are stateless containers.
4. DefaultAzureCredential + Managed Identity — zero secrets in agent code.
5. MCP-first for all reusable tools.
