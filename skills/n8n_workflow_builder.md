# Skill: n8n_workflow_builder

> [!NOTE]
> This skill is governed by the [agentic-automation-specialist Spec Kit](file:///Users/tbwa/Documents/GitHub/Insightpulseai/odoo/spec/agentic-automation-specialist/prd.md).

## Purpose

Create **agent-invocable n8n workflows** that are deterministic, observable, idempotent, and safe for autonomous execution.

## Inputs

- Agent goal (what the AI is trying to achieve)
- Trigger type (queue / webhook / cron / RPC)
- Tool contract:
  - Input schema
  - Output schema
  - Error codes
- Systems touched (Supabase, Odoo, Slack, etc.)
- Success criteria (machine-verifiable)

## Outputs

- `infra/n8n/workflows/**/<name>.json`
- Invocation contract (documented in markdown or inline JSON comment)
- Verification plan (test run + expected ops.runs state)
- Evidence capture plan

## Guardrails

- No secrets in workflow JSON
- Prefer Supabase primitives first
- Must emit structured error codes (not free-text only)
- Must include rollback / disable path
- Must write execution state to `ops.*`

## Agent Compatibility

- Designed for tool-calling by AI agents
- Safe to retry automatically
- Explicitly documents failure modes for agent reasoning
