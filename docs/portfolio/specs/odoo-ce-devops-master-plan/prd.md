# PRD: Odoo CE DevOps Master Plan

## Executive Summary

Deploy a self-hosted Odoo CE 19 stack achieving ≥80% Enterprise Edition feature parity through systematic phase execution with GO/NO-GO gates at each milestone.

## Goals

1. **Platform Readiness** (Phase 0): Establish spec kit, CI gates, and documentation governance
2. **Infrastructure Baseline** (Phase 1): Lock Docker topology and runtime SSOT
3. **Database Foundation** (Phase 2): Initialize production-ready database with role separation
4. **Functional Parity** (Phase 3): Achieve CE+OCA feature coverage
5. **Operational Parity** (Phase 4): Match Odoo.sh operational capabilities
6. **Enterprise Extras** (Phase 5): Add BI, AI agents, advanced monitoring
7. **Production Launch** (Phase 6): Cutover and go-live
8. **Continuous Improvement** (Phase 7): Operate, learn, iterate

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Parity Score | ≥95% | `scripts/check_odoosh_parity.py` |
| Gate Pass Rate | 100% | `scripts/go_no_go_check.sh` |
| EE Feature Parity | ≥80% | `scripts/test_ee_parity.py` |
| Test Coverage | ≥80% | CI pytest coverage |
| SSIM Visual Parity | ≥0.97/0.98 | Mobile/Desktop screenshots |

## Milestones

| ID | Milestone | Dependencies | Deliverables |
|----|-----------|--------------|--------------|
| M0 | Platform Lock | None | Spec kit, CI gates, parity check |
| M1 | Infra Lock | M0 | Docker topology, backup scripts, DR runbook |
| M2 | DB Lock | M1 | Schema baseline, role separation, snapshot |
| M3 | OCA Lock | M2 | Curated modules, oca.lock.json |
| M4 | Ops Lock | M3 | Branch promotion, runbot, web shell |
| M5 | BI Lock | M4 | Superset dashboards, monitoring |
| M6 | GO LIVE | M5 | Production cutover, SLA commitment |

## Phase Breakdown

### Phase 0: Platform Readiness
- Spec kit structure (`spec/`)
- LLM context files (`llms.txt`, `llms-full.txt`)
- CI gates (llms-txt-check, ci-runbot, docs-drift-gate)
- Parity validation script
- CLAUDE.md documentation

### Phase 1: Infrastructure Baseline
- Root `docker-compose.yml`
- Production `deploy/docker-compose.prod.yml`
- Dockerfile (`docker/Dockerfile.ce19`)
- Backup scripts (`scripts/backup/`)
- Security configs (`security/`)
- DR runbook (`docs/DR_RUNBOOK.md`)

### Phase 2: Database Initialization
- DB init runbook (`docs/DB_INIT_RUNBOOK.md`)
- Environment templates (`.env.example`)
- Role creation (odoo_app RW, odoo_reporting RO)
- Schema baseline snapshot
- Rollback procedure

### Phase 3: CE + OCA Parity
- OCA module management (`oca.lock.json`)
- IPAI custom modules (`addons/ipai/`)
- Module testing CI
- EE parity mapping (`docs/ee_parity_mapping.yml`)

### Phase 4: Odoo.sh Operational Parity
- GAP 1: Branch promotion workflow
- GAP 2: Runbot dashboard
- GAP 3: Multi-DC backups
- GAP 4: Browser web shell

### Phase 5: Enterprise Extras
- BI integration (Apache Superset)
- AI agents (MCP servers)
- Advanced monitoring
- DR drill schedule

### Phase 6: Production Launch
- Final parity validation
- Cutover checklist
- SLA commitment
- Rollback procedure

### Phase 7: Operate & Learn
- Performance monitoring
- Incident response
- Continuous improvement
- Quarterly reviews

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Phase gate failure | High | Automated checks, clear criteria |
| Data loss during init | Critical | Backup before any DB operation |
| Module compatibility | Medium | Pinned OCA commits, CI testing |
| Performance regression | Medium | Benchmarking, visual parity |
| Security vulnerability | High | Threat modeling, scanning |

## Stakeholders

- **Finance SSC Manager**: Primary user, BIR compliance owner
- **DevOps Engineer**: Infrastructure, deployment, monitoring
- **Odoo Developer**: Module development, OCA integration
- **BI Architect**: Analytics, dashboards, reporting
