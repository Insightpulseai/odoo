# Databricks Production Readiness — Benchmark Reference

> Source: Databricks documentation and product pages
> Status: Active benchmark reference
> Last updated: 2026-03-17

## Canonical Rule

Databricks "production ready" is a benchmark for production discipline, not a blanket trust label.
A Databricks capability is production-grade in our doctrine only when:
- release maturity is acceptable (GA or Public Preview with stable interface/SLA/support)
- deployment path is codified
- observability/evaluation exists
- rollback/recovery expectations are defined

Beta, Private Preview, and Experimental features must NOT be treated as canonical production baseline.

## Release Maturity Classification

| Level | Production Use | Criteria |
|-------|---------------|----------|
| **GA (General Availability)** | Yes — fully supported, production-ready | Stable API, SLA, full documentation, support channel |
| **Public Preview** | Conditional — allowed with stable interface/SLA/support | Must verify: interface stability, SLA coverage, support availability |
| **Beta** | No — not acceptable as canonical production baseline | Unstable API, no SLA guarantee, limited support |
| **Private Preview** | No — not acceptable as canonical production baseline | Invite-only, breaking changes expected |
| **Experimental** | No — not acceptable as canonical production baseline | Research-stage, may be discontinued |

## Four Production-Readiness Lanes

### 1. Data Pipelines (Spark Declarative Pipelines)

Production-ready data pipeline surface. Covers batch, streaming, and CDC ingestion patterns.

Key criteria:
- Pipeline defined as code (DLT/SDP YAML or SQL, not ad-hoc notebooks)
- Data quality expectations defined (constraints, expectations framework)
- Orchestration through Jobs/Workflows (not manual triggers)
- Observability: event log, metrics, alerting
- Environment separation (dev/staging/prod)
- Rollback via checkpoints and versioned tables

### 2. Internal Data/AI Apps (Databricks Apps)

Production-ready serverless app hosting for internal tools and dashboards.

Key criteria:
- App packaged as Databricks App bundle
- Serverless compute with scaling configuration
- SSO/OAuth authentication (no hardcoded credentials)
- Minimal data access scope (least privilege)
- Codified deployment (CI/CD, not manual)
- Health checks and monitoring

### 3. Agents (Agent Framework)

Production-ready agent architecture with eval/monitoring.

Key criteria:
- Agent follows Databricks Agent Framework template
- Tool definitions registered and scoped
- Evaluation suite with measurable thresholds
- MLflow tracing and monitoring enabled
- Deployed on Databricks Apps (not notebook-served)
- Safety guardrails: content filtering, tool boundaries, escalation
- User feedback loop exists

### 4. Model Serving

Production-grade serving for custom and foundation models.

Key criteria:
- Model registered in Unity Catalog with lineage
- Staging-to-production promotion gate
- Serving endpoint configured with SLA (throughput, latency)
- A/B serving or traffic splitting capability
- Endpoint security: auth, rate limiting, network isolation
- Monitoring: inference latency, error rate, data drift
- Model governance: approval workflow, audit trail

## Cross-References

- `docs/architecture/reference-benchmarks.md` — cross-vendor benchmark registry
- `docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md` — platform data architecture
- `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml` — machine-readable skill map
