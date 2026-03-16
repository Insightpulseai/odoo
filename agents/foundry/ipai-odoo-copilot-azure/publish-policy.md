# IPAI Odoo Copilot — Publish Policy

> Version: 1.0.0
> Last updated: 2026-03-14
> Parent: runtime-contract.md (C-30)

## Publish Levels

| Level | Requirements | Default Mode |
|-------|-------------|-------------|
| Internal Prototype | Runtime contract exists, health probe passes | read_only |
| Advisory Release | Quality + safety evals pass thresholds, guardrails active | read_only |
| Guided Actions Beta | Tool/action evals pass, draft_only mode validated | draft_only |
| GA | Full eval suite, hardened auth, SLA defined, security review | configurable |

## Current State

**Internal Prototype** — allowed.

All other levels blocked until evaluation evidence exists.

## Promotion Rules

1. No level can be skipped
2. Each promotion requires a passing evaluation run at the target level's thresholds
3. Evaluation results must be committed to `agents/evals/odoo-copilot/results/`
4. Safety failures (PII leakage, unauthorized actions) block any promotion
5. Promotion decisions are recorded in this file's changelog

## Rollback Rules

1. Any critical safety failure triggers immediate rollback to Internal Prototype
2. Rollback does not require a new evaluation — it restores the last known-safe level
3. Rollback must be documented with incident reference

## Advisory Mode Default

Until GA, the copilot defaults to `read_only` mode:
- No Odoo write operations
- No draft creation
- Responses are informational only
- Users are informed that the copilot is in advisory mode

## Changelog

| Date | From | To | Evidence |
|------|------|----|----------|
| 2026-03-14 | — | Internal Prototype | Runtime contract C-30 v1.3.0, health probe passing |
