# Agent Orchestrator

This service is the control-plane sidecar for agent orchestration.

## Responsibilities

- Call Foundry/model backends
- Call Odoo through bounded service methods or External API
- Aggregate MCP-assisted inspection/grounding results
- Return structured outputs and proposal objects

## Non-responsibilities

- Direct accounting mutation
- Direct tax posting
- Bypassing Odoo approval and audit flows
