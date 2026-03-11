# Constitution — Reverse RORK × Reverse Replit

## 1. Objective
Replace opaque AI workbenches (RORK, Replit) with a deterministic,
agent-orchestrated Workspace OS.

## 2. Core Principles
- Intent must become a plan
- Plans must be reviewable
- Execution must be replayable
- State must be inspectable
- No UI-only configuration

## 3. System Boundaries
- SoR: PostgreSQL
- SSOT: spec/, ssot/, migrations
- SoW: Workspace + task execution
- UI: Non-authoritative

## 4. Agent Rules
Agents:
- MUST emit plans before execution
- MUST write artifacts to SSOT
- MUST execute via task bus

Agents MUST NOT:
- Execute directly from prompts
- Hide intermediate state
- Mutate infra without a task record

## 5. Runtime Rule
If execution cannot be reproduced from:
- Git
- DB migrations
- Task logs
it is invalid.

Status: ENFORCED
