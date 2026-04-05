# Odoo 18 Launch Evidence Index

> Tracks all evidence artifacts required for go-live gate closure.
> Each gate must have committed evidence before launch decision.

---

## Closed Evidence

| Gate | Evidence Path | Board Task | Status |
|---|---|---|---|
| Alert routing | `docs/evidence/20260405-0048/blocker-closure/alert-routing-verification.md` | #293 | **CLOSED** |
| PITR restore drill | `docs/evidence/20260405-0048/blocker-closure/pg-pitr-restore-test.md` | #273 | **CLOSED** |
| KV private endpoint | `docs/evidence/20260405-0048/blocker-closure/kv-private-endpoint.md` | #279 | **CLOSED** |
| Performance baseline (sequential) | `docs/evidence/20260405-0200/blocker-closure/perf-baseline.md` | #280 | **CLOSED** |
| IaC drift measurement | `docs/evidence/20260405-0200/blocker-closure/iac-drift-assessment.md` | #274 | **MEASURED** (0% managed) |

## Open Evidence (Required for Launch)

| Gate | Expected Evidence Path | Board Task | Status |
|---|---|---|---|
| ACA private-path cutover | `docs/evidence/<stamp>/go-live/aca-private-path.md` | #281, #282, #283 | **NOT STARTED** |
| PG public access closure (post-migration) | `docs/evidence/<stamp>/go-live/pg-public-disabled-final.md` | #266 | **DOING** |
| Entra OIDC activation | `docs/evidence/<stamp>/go-live/entra-oidc-activation.md` | #288 | **NOT STARTED** |
| Conditional Access enforcement | `docs/evidence/<stamp>/go-live/conditional-access.md` | #289 | **NOT STARTED** |
| First managed IaC deployment | `docs/evidence/<stamp>/go-live/iac-first-deployment.md` | #294 | **NOT STARTED** |
| Concurrent k6 load test | `docs/evidence/<stamp>/go-live/k6-concurrent-results.md` | #284 | **NOT STARTED** |
| Production smoke suite | `docs/evidence/<stamp>/go-live/production-smoke.md` | #285 | **NOT STARTED** |
| SLI/SLO definition | `docs/evidence/<stamp>/go-live/sli-slo-targets.md` | — | **NOT STARTED** |
| RTO/RPO benchmark | `docs/evidence/<stamp>/go-live/rto-rpo-benchmark.md` | #291 | **NOT STARTED** |
| Composite readiness score (>= 3.0) | `docs/evidence/<stamp>/go-live/readiness-score.md` | #299 | **NOT STARTED** |

## Launch Decision

| Field | Value |
|---|---|
| Current recommendation | **NOT READY** |
| Closed gates | 5 of 11 |
| Open gates | 6 of 11 |
| Composite score | 2.3 / 5 (provisional) |
| Required composite | >= 3.0 |
| Earliest target | Week of 2026-04-21 |

---

*Updated: 2026-04-05*
