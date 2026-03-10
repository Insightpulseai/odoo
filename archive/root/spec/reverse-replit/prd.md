# Product Requirements — Reverse Replit

## Problem
Replit collapses ideation, execution, and deployment into a single opaque agent
that is:
- Non-reproducible
- Non-auditable
- Non-enterprise-safe

## Solution
A modular Workspace OS that:
- Converts intent → plan → tasks → execution
- Uses a task bus instead of a monolithic agent
- Separates authoring, execution, and deployment
- Supports Notion-like docs + Replit-like runtimes

## 3. Core Capabilities

### 3.1 Intent → Plan
- Natural language input
- Deterministic plan output (YAML/JSON)
- User approval required

### 3.2 Task Bus
- DAG-based execution
- Retryable, idempotent jobs
- Cron + event triggers

### 3.3 Workspace (SoW)
- Pages, blocks, code cells
- Search (FTS + vector)
- RAG over workspace content

### 3.4 Runtime Abstraction
- Container spec (not container control)
- Local / DO / Fly / k8s compatible
- No platform-owned compute lock-in

### 3.5 Deployment
- Git snapshot
- Infra adapters (Vercel, DO, Fly)
- Explicit deploy step

## 4. Explicit Non-Goals
- Browser IDE replacement
- One-click "magic" deploys
- Proprietary agent runtime

## 5. Success Metrics
- 100% reproducible builds
- Zero UI-only steps
- Deterministic replay of any run
