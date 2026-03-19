# Execution Plan — Reverse Replit

## Phase 1 — Foundations
- Task bus schema (jobs, runs, artifacts)
- Workspace schema (pages, blocks)
- Search + indexing pipeline

## Phase 2 — Agent Decomposition
- Planner agent
- Scaffold agent
- Runtime agent
- Deploy agent

(All communicate via task bus)

## Phase 3 — Runtime Adapters
- Node runtime
- Python runtime
- Web app runtime
- Job/cron runtime

## Phase 4 — UI
- Workspace UI (Notion-like)
- Plan review UI
- Run inspection UI

## Phase 5 — Governance
- SSOT enforcement
- Secrets registry enforcement
- CI guards for plan-first execution
