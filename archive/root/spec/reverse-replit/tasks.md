# Task Breakdown — Reverse Replit

## T1 — Task Bus Core
- [ ] jobs table
- [ ] job_runs table
- [ ] artifacts table
- [ ] claim/ack RPCs

## T2 — Workspace Layer
- [ ] work.pages
- [ ] work.blocks
- [ ] permissions model
- [ ] full-text search

## T3 — Indexing Worker
- [ ] queue-based indexer
- [ ] retry + backoff
- [ ] vector optional

## T4 — Ask-Docs (RAG)
- [ ] membership gate
- [ ] citation stability
- [ ] no silent fallback

## T5 — Agent Planner
- [ ] intent → plan
- [ ] plan schema
- [ ] approval gate

## T6 — Runtime Adapter
- [ ] runtime manifest
- [ ] execution shim
- [ ] logs + artifacts

## T7 — Deployment Adapter
- [ ] snapshot generator
- [ ] provider adapters
- [ ] rollback metadata

## T8 — CI Guards
- [ ] plan-before-exec
- [ ] SSOT-only config
- [ ] secret consumer validation
