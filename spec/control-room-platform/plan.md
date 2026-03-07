# Control Room Platform -- Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-07
> **Current Phase**: Phase 0 (Repo-Only)
> **Spec Bundle**: `spec/control-room-platform/`

---

## Phased Rollout

The Control Room Platform follows the constitutional promotion state machine:
`repo-only --> configured --> deployed --> live`

Each phase corresponds to a promotion state. All 7 bounded contexts are currently at `repo-only`.

---

## Phase 0: Repo-Only (Current)

**Objective**: Specs, contracts, CI validators, and governance artifacts exist in the repository. No runtime services.

**Duration**: Weeks 1-3 (started 2026-03-07)

**Deliverables**:
1. Constitution, PRD, plan, and task files (this spec bundle)
2. KPI contracts YAML (`platform/data/contracts/control_room_kpis.yaml`)
3. Event contracts YAML (`platform/data/contracts/control_room_events.yaml`)
4. Runtime state document (`docs/architecture/CONTROL_ROOM_RUNTIME_STATE.md`)
5. Repository taxonomy (`docs/governance/repository_taxonomy.yaml`)
6. Taxonomy JSON Schema (`docs/governance/repository_taxonomy.schema.json`)
7. CI validators for contract YAML and state document
8. Governance lint rules in pre-commit and GitHub Actions

**Exit Criteria**:
- All 9 files written and committed
- CI validators pass on main branch
- No overclaiming in any document
- All 7 bounded contexts accurately represented at `repo-only`

**Workstreams**: W1 (Spec & Governance), W2 (KPI Contracts), W3 (Event Contracts), W4 (CI Validators)

---

## Phase 1: Environment Configuration

**Objective**: Secrets, connections, and staging environments provisioned for each bounded context.

**Duration**: Weeks 4-8

**Deliverables**:
1. Environment variable manifest per bounded context
2. Connection verification scripts per system
3. Secrets provisioned in GitHub Actions, `.env` files, and n8n credentials
4. Staging database schemas created (Supabase `ctrl.*`, Odoo `odoo_dev`)
5. Databricks workspace configured with Unity Catalog
6. Azure/Foundry project created with tool registrations
7. Plane workspace configured with Control Room project

**Exit Criteria**:
- Connection test scripts pass for all 7 contexts
- Secrets are provisioned (verified by name, never value)
- Staging schemas are created and migrated
- All contexts promoted to `configured` with evidence

**Workstreams**: W5 (Environment Setup)

---

## Phase 2: Deployment

**Objective**: Runtime services deployed to staging, health checks passing.

**Duration**: Weeks 9-14

**Deliverables**:
1. Supabase `ctrl.*` schema deployed with RLS policies
2. Odoo KPI extraction cron job deployed
3. n8n workflows deployed for event routing
4. Databricks DLT pipelines deployed for KPI ingestion
5. Azure/Foundry copilot tools deployed
6. GitHub Actions CI validators running on all PRs
7. Control Room API deployed (references `spec/control-room-api/`)
8. Health check endpoints active for all deployed services

**Exit Criteria**:
- Health check endpoints return 200 for all deployed services
- Container logs show no startup errors
- Database migrations applied successfully
- All contexts promoted to `deployed` with evidence

**Workstreams**: W6 (Odoo Integration), W7 (Supabase Integration), W8 (Databricks Integration), W9 (Dashboard & Observability)

---

## Phase 3: Live

**Objective**: Production traffic flowing, monitoring active, alerting configured.

**Duration**: Weeks 15-20

**Deliverables**:
1. Production Odoo syncing KPI data on schedule
2. Supabase `ctrl.integration_events` receiving real events
3. Databricks gold tables populated with KPI history
4. Alerting configured for KPI threshold breaches
5. Dashboard showing real-time platform state
6. Weekly governance report auto-generated
7. Runbook for each bounded context incident response

**Exit Criteria**:
- Real data flowing through all pipelines for 7 consecutive days
- At least one KPI threshold breach detected and alerted
- Governance report generated without manual intervention
- All contexts promoted to `live` with evidence

**Workstreams**: W9 (Dashboard & Observability), plus ongoing W6-W8

---

## Workstream Summary

| ID | Workstream | Phase | Tasks | Owner |
|----|-----------|-------|-------|-------|
| W1 | Spec & Governance | 0 | 6 | Platform team |
| W2 | KPI Contracts | 0 | 5 | Platform team |
| W3 | Event Contracts | 0 | 5 | Platform team |
| W4 | CI Validators | 0 | 6 | Platform team |
| W5 | Environment Setup | 1 | 7 | DevOps |
| W6 | Odoo Integration | 2 | 5 | Odoo team |
| W7 | Supabase Integration | 2 | 5 | Platform team |
| W8 | Databricks Integration | 2 | 4 | Data team |
| W9 | Dashboard & Observability | 2-3 | 5 | Platform team |
| | **Total** | | **48** | |

---

## Dependency Graph

```
W1 (Spec & Governance) ----+
                            |
W2 (KPI Contracts) --------+--> W4 (CI Validators)
                            |         |
W3 (Event Contracts) ------+         |
                                      v
                              W5 (Environment Setup)
                                      |
                        +-------------+-------------+
                        |             |             |
                        v             v             v
                  W6 (Odoo)    W7 (Supabase)  W8 (Databricks)
                        |             |             |
                        +-------------+-------------+
                                      |
                                      v
                            W9 (Dashboard & Observability)
```

**Critical Path**: W1 --> W4 --> W5 --> W6+W7 --> W9

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Databricks workspace not provisioned | W8 blocked | Medium | Proceed with Supabase+Odoo first; Databricks is Phase 2 |
| Azure/Foundry access not available | Copilot tools delayed | Medium | Agent tools can be added post-live as enhancement |
| Plane API changes | Sync breaks | Low | Plane sync is unidirectional; can buffer in Supabase |
| KPI data not available from Odoo | Dashboard incomplete | Medium | Use mock data in staging; real data in production only |
| Overclaiming in legacy docs | Governance violations | High | CI lint catches overclaiming; systematic cleanup in W1 |

---

## Phase 0 Detailed Schedule

Since Phase 0 is the current phase, here is a detailed breakdown:

| Week | Tasks | Deliverable |
|------|-------|-------------|
| Week 1 | W1.1-W1.6, W2.1-W2.3 | Spec bundle written, KPI YAML drafted |
| Week 2 | W2.4-W2.5, W3.1-W3.5 | KPI YAML finalized, event YAML written |
| Week 3 | W4.1-W4.6 | CI validators implemented and passing |

---

## Cross-References

- `spec/control-room-platform/constitution.md` -- Non-negotiable rules
- `spec/control-room-platform/prd.md` -- Product requirements
- `spec/control-room-platform/tasks.md` -- 48 tasks with status
- `spec/control-room-api/plan.md` -- Control Room API implementation plan
- `spec/integration-control-plane/plan.md` -- Supabase control plane plan
- `spec/databricks-apps-control-room/plan.md` -- Databricks control room plan
