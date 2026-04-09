# Go-Live Cutover Brief — Odoo 18 on Azure

> Single delivery lane. No architecture/harness/spec work until these gates close.
> Target: week of 2026-04-21 (earliest, contingent on P0+P1 closure without new blockers)

---

## Launch Gate

**Go-live only when ALL of the following are true:**

- [ ] PG private path is fully closed (ACA→PG via PE, public access disabled, no rollback)
- [ ] Entra OIDC is live on the production access path
- [ ] Production-path smoke test passes end-to-end
- [ ] Concurrent load test passes with evidence
- [ ] IaC baseline is measured and evidenced
- [ ] Composite assessment score is at least **3.0 / 5**

---

## Blocker Status (5 hard blockers)

| # | Blocker | Status | Evidence |
|---|---|---|---|
| 1 | Alert routing verification | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/alert-routing-verification.md` |
| 2 | PG PITR restore drill | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/pg-pitr-restore-test.md` |
| 3 | KV private endpoint | **CLOSED** | `docs/evidence/20260405-0048/blocker-closure/kv-private-endpoint.md` |
| 4 | IaC drift measurement | **MEASURED** (0% managed) | `docs/evidence/20260405-0200/blocker-closure/iac-drift-assessment.md` |
| 5 | Entra OIDC activation | **NOT STARTED** | — |

---

## Remaining Execution Waves

### Wave A — Network and Identity Closure

| Step | Gate | Board Item | Status |
|---|---|---|---|
| A1 | Finish ACA private-path cutover for PG connectivity | #266 (Doing) | Blocked — ACA apps need migration to `ipai-odoo-ha-env` |
| A2 | Re-disable PG public access, verify production path healthy | #266 | Depends on A1 |
| A3 | Activate Entra OIDC, complete identity control plane | #249 (Odoo Identity & Auth) | Not started |

### Wave B — Proof and Rebuildability

| Step | Gate | Board Item | Status |
|---|---|---|---|
| B1 | First real IaC managed deployment pass | #274 (Doing) | Drift measured at 0%; need first Bicep deploy |
| B2 | Record evidence for deployed baseline (not just intended state) | #261 (Assessment Evidence Refresh) | Not started |

### Wave C — Launch Validation

| Step | Gate | Board Item | Status |
|---|---|---|---|
| C1 | Run concurrent k6 load test (not just sequential) | #280 (sequential done) | k6 script ready, need full VU run |
| C2 | Execute full smoke suite against production path | #95 (under #247) | Script exists, not run in prod path |
| C3 | Define minimum SLI/SLO targets, connect alert thresholds | #271 | Not started |

---

## Active Board Lane

### Keep active (launch-critical only)

| Epic | State | Role |
|---|---|---|
| #63 Execute Odoo 18 Go-Live Critical Path | **Doing** | Primary delivery lane |
| #74 Execute Remaining Odoo 18 Go-Live Blockers | **Doing** | Blocker closure lane |

### Deferred until after launch

- Benchmark stack freeze
- Harness v3 policy freeze
- Spec-bundle generation (#238-244 canonical Epics)
- Portfolio normalization beyond go-live lane
- Assessment-harness improvements (#243)

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

## Decision Rules

1. **No architecture/spec work** until Wave C completes
2. **No board normalization** beyond go-live lane until launch
3. **No new Epics** until the OBJ-001-007 spine is validated post-launch
4. **Evidence-first** — every gate closure requires committed evidence, not just CLI output
5. **PG public access** stays in Doing until ACA private-path cutover is verified end-to-end

---

*Generated: 2026-04-05. Next review: after Wave A completion.*
