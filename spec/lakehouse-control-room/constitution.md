# Lakehouse Control Room - Constitution

## Overview

This document defines the non-negotiable rules, constraints, and success criteria for the Lakehouse Control Room system - an open-source alternative to Databricks capabilities built on Supabase (control plane) + containerized executors (data plane).

## Core Principles

### 1. Separation of Concerns

- **Control Plane (Supabase)**: Stores intent, state, events, artifacts, caps, routing decisions
- **Executor Plane (Containers/K8s)**: Stateless workers that claim work, execute phases, and report back
- **Data Plane (Object Storage)**: S3-compatible storage for artifacts, logs, datasets, Delta/Iceberg tables

### 2. Deterministic Operations

- Every run MUST be reproducible given the same input spec
- Runs are immutable once created; only status transitions allowed
- Events are append-only; never mutate historical records
- Artifacts are write-once with checksums for integrity verification

### 3. GitOps-First

- Pipeline specs live in Git as the source of truth
- CI validates specs before they can be executed
- Schema/contract drift blocks deployment
- Migrations are forward-only with explicit rollback migrations

## Non-Negotiables

### Security

1. No secrets in Git - use env/secret manager references only
2. Service role keys are server-only (never exposed to clients)
3. RLS enforced on all user-facing tables
4. Audit trail for all state transitions

### Reliability

1. Heartbeat-based liveness detection for all executors
2. Automatic requeue of stale/zombie runs
3. Caps enforcement at multiple layers (executor + orchestration + query engine)
4. Retry semantics with exponential backoff and max retry limits

### Observability

1. All runs emit structured events
2. Artifacts include metadata for lineage tracking
3. Routing matrix drives alert escalation
4. Multi-signal scoring for prioritization

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Run claim latency | < 1s | p95 time from queued to claimed |
| Event ingestion | < 100ms | p95 time to persist event |
| Heartbeat tolerance | 15 min | Max time before requeue |
| Artifact integrity | 100% | SHA-256 verification pass rate |
| Cap enforcement | 100% | No cap exceeded without termination |

## Constraints

### Technical

- PostgreSQL 15+ (Supabase)
- S3-compatible object storage
- Containerized executors (Docker/K8s)
- Node.js 20+ for Edge Functions
- Python 3.11+ for scripts

### Operational

- Forward-only migrations (no destructive changes)
- Evidence-first deployment (proofs before claims)
- CI gates block non-compliant changes

## Governance

- Changes to this constitution require explicit approval
- All significant features require a spec bundle
- Contract changes require migration + compatibility verification
