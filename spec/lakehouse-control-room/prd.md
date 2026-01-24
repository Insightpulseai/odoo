# Lakehouse Control Room - Product Requirements Document

## Problem Alignment

### Problem Statement

Organizations need Databricks-like lakehouse capabilities (Delta tables, job orchestration, SQL warehouses, governance) but face significant licensing costs and vendor lock-in. Existing open-source alternatives require substantial integration effort and lack a unified control plane.

### Target Users

1. **Data Engineers**: Need to author, schedule, and monitor data pipelines
2. **Data Platform Teams**: Require governance, cost controls, and operational visibility
3. **Analytics Engineers**: Want SQL access to lakehouse tables with proper security
4. **MLOps Engineers**: Need experiment tracking and model serving infrastructure

### Current Pain Points

- Databricks licensing costs for full-featured usage
- Vendor lock-in with proprietary formats and APIs
- Fragmented tooling across orchestration, compute, and governance
- Lack of unified observability across data pipelines

## Solution Alignment

### Core Solution

A Supabase-backed control plane that orchestrates lakehouse operations across containerized executors, providing:

1. **Unified Control Room UI**: Single pane for runs, events, artifacts, routing
2. **Executor Registry**: Manage Spark/Trino/dbt workers with capability flags
3. **Job Templates**: Repeatable jobs with promotion gates
4. **Runtime Caps**: Cost control with enforcement at multiple layers

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Control Room UI (Next.js)                       │
├─────────────────────────────────────────────────────────────────────┤
│                    Supabase Control Plane (SSOT)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ops.runs │  │ops.events│  │artifacts│  │routing │  │  caps   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                      Executor Contract (OpenAPI)                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  Spark  │  │  Trino  │  │   dbt   │  │ Python  │  │Notebook │   │
│  │Executor │  │Executor │  │Executor │  │Executor │  │Executor │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    Data Plane (Object Storage)                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  S3/MinIO  │  Delta Tables  │  Artifacts  │  Logs  │  Lineage │ │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Capability Parity with Databricks

| Databricks Feature | Our Implementation | Parity Level |
|--------------------|-------------------|--------------|
| Delta Lake tables | Delta Lake OSS + Spark | Strong |
| Workflows/Jobs | Control Room + Executors | Strong |
| SQL Warehouse | Trino/Spark Thrift | Strong |
| Unity Catalog | OpenMetadata + Policy | Strong |
| Dashboards | Superset/Metabase | Strong |
| DLT Pipelines | dbt + streaming + gates | Partial |
| Genie (NL→SQL) | WrenAI + RAG | Strong |
| Photon | N/A (proprietary) | Hard |

### Key Differentiators

1. **No License Cost**: All core components are open source
2. **Portable**: Standard APIs, no vendor lock-in
3. **Supabase-Native**: Leverage existing Supabase infrastructure
4. **GitOps-First**: Everything as code, CI-enforced

## Launch Readiness

### Phase 1: Foundation (Current)

- [x] OpenAPI contract for executor communication
- [x] Supabase ops schema (runs, events, artifacts, routing, caps)
- [x] Spec bundle with governance rules
- [ ] PR gate workflow for contract validation
- [ ] Basic executor implementation (claim/execute/report)

### Phase 2: Core Capabilities

- [ ] Job templates with scheduling
- [ ] Spark executor integration
- [ ] Trino SQL warehouse setup
- [ ] Artifact storage with checksums
- [ ] Routing matrix with escalation

### Phase 3: Governance & UX

- [ ] Control Room UI (Next.js + Supabase UI)
- [ ] Multi-signal scoring
- [ ] Caps enforcement at all layers
- [ ] OpenMetadata integration
- [ ] Lineage capture

### Phase 4: Advanced

- [ ] Streaming pipelines
- [ ] ML experiment tracking (MLflow)
- [ ] Delta Sharing protocol
- [ ] NL→SQL (WrenAI integration)

## Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Executor types supported | 5+ | Phase 2 |
| Run throughput | 1000/day | Phase 2 |
| UI page load | < 2s | Phase 3 |
| Feature parity score | 80%+ | Phase 3 |
| Zero-license cost | Yes | Always |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance vs Databricks | Medium | Tuning + Trino + AQE |
| Governance complexity | High | Policy-as-code + CI gates |
| Executor reliability | High | Heartbeat + requeue + retry |
| Schema drift | Medium | Contract validation in PR gate |
