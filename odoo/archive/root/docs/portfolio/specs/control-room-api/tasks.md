# Control Room API — Task Checklist

> **Version**: 1.0.0
> **Status**: In Progress
> **Last Updated**: 2024-12-21

---

## Phase 1: Foundation

### 1.1 Spec Bundle
- [x] Create constitution.md
- [x] Create prd.md
- [x] Create plan.md
- [x] Create tasks.md

### 1.2 Database Schema
- [ ] Create Supabase migration for cr_jobs
- [ ] Create Supabase migration for cr_runs
- [ ] Create Supabase migration for cr_artifacts
- [ ] Create Supabase migration for cr_lineage_edges
- [ ] Add indexes for performance
- [ ] Add RLS policies

### 1.3 API Skeleton
- [ ] Initialize FastAPI project
- [ ] Create Pydantic models
- [ ] Implement health check
- [ ] Configure CORS and auth

---

## Phase 2: Core Endpoints

### 2.1 Jobs Router
- [ ] POST /api/v1/jobs/run
- [ ] POST /api/v1/jobs/validate
- [ ] GET /api/v1/jobs

### 2.2 Runs Router
- [ ] GET /api/v1/runs/{run_id}
- [ ] POST /api/v1/runs/{run_id}/cancel
- [ ] POST /api/v1/runs/{run_id}/events
- [ ] GET /api/v1/runs

### 2.3 Artifacts Router
- [ ] POST /api/v1/artifacts
- [ ] GET /api/v1/artifacts/{artifact_id}
- [ ] DELETE /api/v1/artifacts/{artifact_id}

### 2.4 Lineage Router
- [ ] GET /api/v1/lineage/graph
- [ ] POST /api/v1/lineage/edges

### 2.5 Webhooks Router
- [ ] POST /api/v1/webhooks/continue

---

## Phase 3: Execution Layer

### 3.1 Dispatcher
- [ ] Abstract dispatcher interface
- [ ] K8s Job implementation
- [ ] DO runner implementation
- [ ] Local executor (dev mode)

### 3.2 Callbacks
- [ ] Webhook delivery service
- [ ] Retry logic with backoff
- [ ] Dead letter queue

---

## Phase 4: Visio-DrawIO Skill

### 4.1 Skill Definition
- [ ] Create skill.yaml
- [ ] Document MCP integration
- [ ] Add to agent registry

### 4.2 Implementation
- [ ] Visio parser (vsdx)
- [ ] DrawIO XML generator
- [ ] PNG/SVG exporter
- [ ] Validation logic

### 4.3 Visual Regression
- [ ] Baseline comparison
- [ ] Diff threshold logic
- [ ] Report generation

### 4.4 Docker Image
- [ ] Headless drawio setup
- [ ] CLI entrypoint
- [ ] Multi-arch build

### 4.5 GitHub Actions
- [ ] diagrams-qa.yml workflow
- [ ] PR path filtering
- [ ] Artifact upload

---

## Phase 5: Integration

### 5.1 Continue CLI
- [ ] Test cn -p integration
- [ ] Document workflow
- [ ] Create examples

### 5.2 Documentation
- [ ] API reference (OpenAPI)
- [ ] Developer guide
- [ ] Runbook

### 5.3 Monitoring
- [ ] Health endpoints
- [ ] Metrics export
- [ ] Alerting rules

---

## Completion Criteria

- [ ] All API endpoints functional
- [ ] Supabase migrations applied
- [ ] Docker image builds
- [ ] CI/CD pipeline passes
- [ ] Documentation complete
