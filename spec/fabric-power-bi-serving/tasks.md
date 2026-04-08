# Tasks — Fabric + Power BI Serving Layer

> Task breakdown for the canonical analytics workload-allocation policy.

---

## Phase 1 — Architecture Codification

- [x] **T1.1** Create `docs/architecture/ANALYTICS_TARGET_STATE.md` with workload allocation table
- [x] **T1.2** Define decision rules DR-1 through DR-6 in `ANALYTICS_TARGET_STATE.md`
- [x] **T1.3** Define non-goals / prohibited-patterns table in `ANALYTICS_TARGET_STATE.md`
- [x] **T1.4** Document current-state resource inventory in `ANALYTICS_TARGET_STATE.md`
- [x] **T1.5** Verify no contradictions with `MEDALLION_ARCH.md` mandatory pillars

## Phase 2 — Spec Formalization

- [x] **T2.1** Create spec bundle `spec/fabric-power-bi-serving/`
- [x] **T2.2** Write `prd.md` with problem statement, goals, non-goals, FR-1 through FR-6, acceptance criteria
- [x] **T2.3** Write `plan.md` with workstreams WS-1 through WS-5, risks, dependencies
- [x] **T2.4** Write `tasks.md` (this file)
- [ ] **T2.5** Cross-reference spec bundle in `MEDALLION_ARCH.md` references section

## Phase 3 — Review Gates

- [ ] **T3.1** Architecture review: confirm workload table covers all known workload classes
- [ ] **T3.2** Confirm Fabric Data Warehouse vs Lakehouse endpoint boundary is unambiguous
- [ ] **T3.3** Confirm Power BI connection policy prohibits direct Odoo PG access
- [ ] **T3.4** Confirm semantic model governance (one per domain, `.pbip` source control) is actionable
- [ ] **T3.5** Stakeholder sign-off on workload-allocation policy

## Phase 4 — Fabric Workspace Provisioning (future)

- [ ] **T4.1** Provision Fabric dev workspace with appropriate capacity SKU
- [ ] **T4.2** Activate Fabric Mirroring for `pg-ipai-odoo` (staging DB first)
- [ ] **T4.3** Create first Fabric Data Warehouse mart (finance domain)
- [ ] **T4.4** Validate Lakehouse SQL analytics endpoint access to mirrored Delta tables
- [ ] **T4.5** Configure workspace RBAC (viewer, contributor, admin roles)

## Phase 5 — Power BI Semantic Layer (future)

- [ ] **T5.1** Create `data-intelligence/powerbi/` directory structure
- [ ] **T5.2** Author finance domain semantic model in Power BI Desktop (`.pbip`)
- [ ] **T5.3** Connect semantic model to Databricks SQL Warehouse
- [ ] **T5.4** Define RLS roles in semantic model
- [ ] **T5.5** Publish to Power BI Service dev workspace
- [ ] **T5.6** Configure scheduled refresh or Direct Lake mode
- [ ] **T5.7** Create Power BI app for governed distribution
- [ ] **T5.8** Upgrade Power BI license from Free to Pro (required for RLS + apps)

## Phase 6 — Governance Enforcement (future)

- [ ] **T6.1** Configure Power BI gateway connection allow-list (Databricks SQL, Fabric Warehouse, Lakehouse endpoint only)
- [ ] **T6.2** Add CI check for `.pbip` connection strings (reject Odoo PG direct connections)
- [ ] **T6.3** Add Fabric Warehouse provisioning gate (requires architecture review)
- [ ] **T6.4** Monitor Fabric Mirroring latency and set alerting threshold (15 min)
- [ ] **T6.5** Document exception process for non-standard data source connections

---

*Last updated: 2026-03-21*
