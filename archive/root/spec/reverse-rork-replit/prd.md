# Product Requirements — Reverse RORK × Reverse Replit

## Problem
RORK and Replit:
- Collapse planning, execution, and deployment
- Hide agent decisions
- Prevent replay and audit
- Bind users to platform runtimes

## Solution
A Workspace Execution OS that separates:
- Thinking (planning)
- Doing (task execution)
- Knowing (workspace memory)
- Shipping (deployment)

## 3. Core Capabilities

### 3.1 Intent → Plan
- Natural language input
- Structured plan output
- Mandatory human approval

### 3.2 Task Bus
- Queue-based execution
- Idempotent jobs
- Retry + backoff
- Cron + event triggers

### 3.3 Workspace (SoW)
- Pages, blocks, code cells
- Searchable memory
- RAG-capable knowledge layer

### 3.4 Runtime Abstraction
- Declarative runtime manifests
- No platform-owned compute
- Adapter-based execution

### 3.5 Deployment
- Explicit deploy tasks
- Provider adapters
- Rollback metadata

## 4. Non-Goals
- Browser IDE parity
- Hidden "one-click" magic
- Proprietary agent runtime

## 5. Success Criteria
- 100% plan-first execution
- Zero UI-only state
- Deterministic replay of runs
