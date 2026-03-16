# DevUI Local Developer Experience

> Version: 1.0.0
> Canonical repo: `agent-platform`

## Context
A consistent, reproducible local testing environment is necessary to iterate on multi-agent workflows without depending exclusively on deployed capability hosts.

## Decision
- Mirror the **Agent Framework DevUI** directory ergonomics for local agent/workflow structure (`devui .`).
- Organize agents, workflows, and tools into standard discoverable directories.
- Require an explicit `.env.example` in each sample/template to document required context variables.

## Consequences
- The local developer cycle aligns natively with the framework's integrated tooling.
- Agents built in this repository are pre-structured to operate cleanly inside the expected UI testing harness.
