# WorkbenchX — Product Requirements Document

## Product

**WorkbenchX** — a governed AI development and deployment platform built on Supabase control-plane primitives.

## Why now

Enterprise AI teams want a unified environment to build and deploy AI on governed data, with collaboration, compliance, and controlled infrastructure. Cloudera AI Workbench highlights this exact need: governed enterprise data access (SDX), unified workspace, and secure deployment of AI applications and agents across hybrid/multi-cloud.

## Goals

1. Provide **governed, collaborative AI development** (projects, notebooks/sessions, code + dataset versioning).
2. Provide **containerized compute sessions** (CPU/GPU) and **reproducible experiments** with tracked results.
3. Provide **deployment surfaces**:
   - "Analytical Apps" (long-running UIs like Streamlit/Flask equivalents)
   - "Models as endpoints" (REST inference service with HA semantics)
4. Provide **agentic workflows** (multi-agent runs, RAG pipelines, fine-tune pipelines) as first-class job types.
5. Preserve **auditability and compliance**: lineage, artifacts, access logs, and deterministic evidence.

## Non-goals

* Replacing Cloudera SDX, Ranger, or full data lakehouse governance stack.
* Becoming a general Kubernetes management platform.
* Providing a proprietary notebook UI if a stable OSS UI can be embedded.

## Users

* **Data Scientist**: explore datasets, run sessions, train models, publish results.
* **ML Engineer**: productionize pipelines, manage model deployments, monitoring.
* **Platform Admin**: enforce policies, manage runtimes, quotas, approvals.
* **Compliance / Security**: review lineage, access trails, and artifacts.

## Problem statement

Teams struggle to ship AI in regulated environments because:

* compute is fragmented (ad-hoc notebooks, local, random servers)
* data access is uncontrolled
* experiments are not reproducible
* deployments lack traceability

## Key product capabilities

### P0 — Projects & governance

* Create projects with:
  * repo linkage (Git SHA)
  * dataset refs
  * approved runtimes (container images)
* RBAC + RLS-backed access:
  * project membership
  * dataset permissions
  * run permissions

### P0 — Sessions (interactive compute)

* Launch session with: runtime image, CPU/mem/GPU profile, expiration/idle timeout
* Attach: notebook UI (embedded), terminal, logs
* Store: session events, output artifacts (notebooks, charts, exports)

### P0 — Experiments (tracked training runs)

* Create experiment from project
* Track: params, metrics, artifacts, dataset + code refs
* Compare runs
* Promote run → model candidate

### P0 — Models (REST endpoints)

* Deploy model from a selected run
* Provide: endpoint URL, versioning, access policy (API key/JWT), metrics (latency, error rate, usage)
* Record lineage: run → model → endpoint → usage events

### P0 — Analytical Apps (long-running apps)

* Deploy app from project: app type (streamlit/flask/nextjs), runtime, route + auth
* Support: versioned releases, health checks, logs + alerts

### P1 — AI Studios equivalents (RAG / fine-tune / synthetic / multi-agent)

* Provide templated pipelines:
  * RAG: ingest → chunk → embed → retrieve → answer
  * Fine-tune: dataset → train → evaluate → deploy
  * Multi-agent: planner/executor/evaluator loops

### P1 — Accelerators ("AMPs"-like templates)

* Provide "project templates":
  * notebook starter
  * RAG starter
  * model serving starter
  * app starter

## Success metrics

* Time-to-first-governed-run: < 30 minutes
* % runs with complete lineage (dataset+code+runtime): > 95%
* Mean time to reproduce a result: < 10 minutes
* Deployment failure rate: < 2%
* Audit retrieval time (who ran what on which data): < 60 seconds

## Risks & mitigations

* **Runner drift**: solve via pinned container images + execution attestation.
* **Secret sprawl**: solve via Vault + SSOT registry + short-lived tokens.
* **Cost blowups**: solve via quotas, per-project compute budgets, idle timeouts.
* **Vendor lock-in**: maintain "provider adapters" for sandbox + inference.
