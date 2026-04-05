# Odoo 18 Go-Live Cutover Brief

> Authoritative cutover policy. Single execution lane until all launch gates close.
> Target: week of 2026-04-21 (earliest, contingent on P0+P1 closure without new blockers)

---

## Scope

Odoo CE 18.0 on Azure Container Apps, backed by Azure PostgreSQL Flexible Server (`pg-ipai-odoo`), fronted by Azure Front Door, with Entra ID as the identity provider.

---

## Active Launch Lane

### Epic #63 — Execute Odoo 18 Go-Live Critical Path

Primary execution lane. All cutover-critical work lives here.

- **Issue #247** — Go-Live Critical Path
  - Task #279 — DONE: KV private endpoint deployed, DNS linked, public access disabled
  - Task #281 — Wave A1: Migrate ACA apps to ipai-odoo-ha-env
  - Task #282 — Wave A1: Verify private-path PG connectivity from ACA
  - Task #283 — Wave A2: Re-disable PG public access after private-path verified
  - Task #284 — Wave C1: Run concurrent k6 load test against production path
  - Task #285 — Wave C2: Execute full production-path smoke suite
  - Task #286 — Wave C3: Go-live readiness signoff — all gates green

### Epic #106 — Schema Governance — Declare Canonical Authority and Eliminate Drift

Supporting governance/evidence lane.

- **Issue #258** — Security Posture Closure
  - Task #266 — P0: Disable PG public network access and create private endpoint (**Doing**)
  - Task #287 — P0: Verify KV private endpoint remains enforced
  - Task #288 — P0: Complete Entra OIDC activation
  - Task #289 — P0: Validate Conditional Access enforcement
  - Task #290 — P0: Confirm legacy/public fallback paths are closed

- **Issue #259** — Reliability & DR Evidence
  - Task #273 — DONE: PITR restore drill — 3 databases restored successfully
  - Task #293 — DONE: Alert routing verification — test notification succeeded
  - Task #291 — P1: Record RTO/RPO from restore rehearsal
  - Task #292 — P1: Publish DR evidence summary

- **Issue #260** — IaC & Drift Remediation
  - Task #274 — P0: Measure IaC drift (**Doing** — measured at 0% managed)
  - Task #294 — P0: Execute first real managed deployment pass
  - Task #295 — P0: Inventory unmanaged resources
  - Task #296 — P0: Classify resources as managed / exception / drift
  - Task #297 — P1: Publish deployment reproducibility baseline

- **Issue #261** — Assessment Evidence Refresh
  - Task #298 — P1: Attach launch evidence packet
  - Task #299 — P1: Recompute composite readiness score
  - Task #300 — P1: Record launch decision against 3.0+ threshold

---

## Blocker Register

| # | Blocker | Status | Evidence |
|---|---|---|---|
| 1 | Alert routing verification | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/alert-routing-verification.md` |
| 2 | PG PITR restore drill | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/pg-pitr-restore-test.md` |
| 3 | KV private endpoint | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/kv-private-endpoint.md` |
| 4 | IaC drift measurement | **MEASURED** (0% managed) | `docs/evidence/20260405-0200/blocker-closure/iac-drift-assessment.md` |
| 5 | Entra OIDC activation | **NOT STARTED** | — |

---

## Wave Order

### Wave A — Network and Identity Closure

1. Finish ACA private-path cutover for PostgreSQL connectivity
2. Re-disable PG public access after migration verified
3. Activate Entra OIDC and complete identity control plane

### Wave B — Proof and Rebuildability

4. Execute first real managed IaC deployment pass
5. Record evidence for deployed baseline (not just intended state)

### Wave C — Launch Validation

6. Run concurrent k6 load test against production path
7. Execute full smoke suite against actual production route
8. Define minimum SLI/SLO targets and connect alert thresholds

---

## Launch Gate

**Go-live only when ALL of the following are true:**

- [ ] PG private path is fully closed (ACA→PG via PE, public disabled, no rollback)
- [ ] Entra OIDC is live on the production access path
- [ ] Production-path smoke test passes end-to-end
- [ ] Concurrent load test passes with evidence
- [ ] IaC baseline is measured and evidenced (first real deployment)
- [ ] Composite assessment score is at least **3.0 / 5**

---

## Acceptance Criteria

### P0 — ACA private-path cutover for PostgreSQL

Done only when:
- ACA workload is validated on the intended private path
- DB traffic is proven over private connectivity
- Temporary public fallback is disabled again
- Health path remains green after closure

### P0 — Execute first real managed deployment pass

Done only when:
- IaC is applied to the live environment at least once
- Managed vs unmanaged vs exception inventory exists
- Drift is explicitly measured, not inferred

### P1 — Entra OIDC activation

Done only when:
- Production auth path uses Entra OIDC
- Conditional Access is active
- Policy enforcement is evidenced
- Legacy fallback auth assumptions are removed or documented as exceptions

### P1 — Concurrent load validation

Done only when:
- Concurrent k6 run completes against production path
- Results are attached as evidence
- No blocker-level regression in latency/error rate

### P1 — End-to-end production smoke execution

Done only when:
- Smoke suite runs against actual production route
- Login / health / core transactional path pass
- Evidence is attached to the launch packet

### P1 — SLI/SLO definition

Done only when:
- Minimum availability / latency / recovery targets are declared
- Alert thresholds are mapped to those targets
- Targets are linked to the cutover signoff packet

### Launch decision review

Done only when:
- All preceding launch gates are closed
- Composite assessment is >= 3.0
- Go-live is explicitly approved or deferred with reason

---

## Score Trajectory

| Milestone | Composite | Trigger |
|---|---|---|
| R4.2 (current) | 2.3 / 5 | Provisional — stale inputs |
| After Wave A | ~2.8 | PG private + Entra OIDC |
| After Wave B | ~3.0 | IaC baseline + evidence refresh |
| After Wave C | ~3.2 | Load + smoke + SLO |
| **Go-live minimum** | **3.0+** | All gates green |

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-05 | NOT READY — launch deferred | 3 of 5 hard blockers closed; ACA private-path, OIDC, IaC deployment, concurrent load, smoke, SLO still open |

---

## Non-Launch Work (Deferred)

These are frozen until launch gates close:
- Benchmark stack freeze
- Harness v3 policy freeze
- Spec-bundle generation
- Portfolio normalization beyond go-live lane
- Assessment-harness refinements

---

*Generated: 2026-04-05. Next review: after Wave A completion.*
