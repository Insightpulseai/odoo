# Azure Assessment Results — 2026-04-05

> Internal harness run. 6 agents (3 harvesters + drafter/judge + gap challenger + calibration).
> This does NOT replace the official Microsoft Assessments portal.

---

## Assessment Run Info

| Field | Value |
|---|---|
| Date | 2026-04-05 |
| Harness version | 1.0 (structured v1 rewrite) |
| Platform analysis revision | R3 |
| Evidence freshness | 0 days (live repo scan + Azure Resource Graph) |
| Assessor | Agent swarm (3 harvesters, 1 drafter/judge, 1 gap challenger, 1 calibration judge) |
| Weight model | 0.60 WAF core + 0.20 workload overlays + 0.20 transformation readiness |
| Prior baseline | 2.7/5.0 (self-assessed R3), 2.4/5.0 WAF lens |

---

## Core WAF Scores (Layer A)

| Pillar | Judged Score | Challenged Score | Confidence | Evidence Class | Answer Safety |
|---|---|---|---|---|---|
| Reliability | 1.5/5 | 1.5 | Low | Present (probes, backup doctrine) | RISKY |
| Security | 2.5/5 | 2.2 | Medium | Mixed (WAF+PG PE proven, identity not operational) | RISKY |
| Cost Optimization | 1.5/5 | 1.0 | Low | Weak (inventory only, zero cost visibility) | UNSUPPORTED |
| Operational Excellence | 2.8/5 | 2.4 | Medium | Mixed (IaC governed, 20+ resources drifted) | RISKY |
| Performance Efficiency | 2.5/5 | 2.4 | Medium | Mixed (sizing governed, no load testing) | RISKY |
| **WAF Core Average** | **2.16/5** | **1.90/5** | | | |

---

## Workload Overlay Scores (Layer B)

| Overlay | Fit Score | Key Finding | Confidence |
|---|---|---|---|
| SaaS | 2.0/5 | Tenancy governed, boundaries trivially satisfied (single-tenant). Multitenancy deferred, billing absent. | Medium |
| AI | 2.5/5 | Build-vs-buy proven (Foundry). Scoped tools governed. Safety not implemented, eval framework absent. | Medium |
| SAP (workload-ops) | 2.5/5 | Monitoring goals present, tool authority proven. SLO enforcement absent, DR manual. | Medium-High |
| Mission-critical | 1.0/5 | Explicitly deferred. HA configured but untested. | Low |
| **Overlay Average** | **2.00/5** | | |

---

## Transformation Readiness Scores (Layer C)

| Phase | Score | Visibility | Alignment | Governance | Exec Readiness | Continuous Feedback |
|---|---|---|---|---|---|---|
| Discover | 2.8/5 | 4.0 | 2.5 | 2.5 | 2.5 | 2.0 |
| Analyze | 2.5/5 | 3.5 | 3.5 | 2.5 | 2.5 | 2.0 |
| Design | 3.0/5 | 4.0 | 3.0 | 4.0 | 2.5 | 2.5 |
| Implement | 1.8/5 | 2.5 | 2.0 | 2.0 | 2.0 | 1.5 |
| Operate | 1.2/5 | 2.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| **Transformation Average** | **2.26/5** | **3.2** | **2.4** | **2.4** | **2.1** | **1.8** |

---

## Final Weighted Score

| Component | Weight | Score | Weighted |
|---|---|---|---|
| WAF Core (Layer A) | 0.60 | 2.16/5 | 1.296 |
| Workload Overlays (Layer B) | 0.20 | 2.00/5 | 0.400 |
| Transformation Readiness (Layer C) | 0.20 | 2.26/5 | 0.452 |
| **Total** | **1.00** | | **2.15/5** |

**Result band: WEAK (1.5-2.4)**

**Calibrated likely official range: 1.8-2.2/5.0**

**Prior self-assessed baseline: 2.7/5.0 (R3)**

**Delta: -0.55 (harness is stricter than self-assessment by applying present/governed/proven decision rules)**

---

## Hard Blockers

| # | Blocker | Status | Effort | Impact on Score |
|---|---|---|---|---|
| 1 | IaC drift -- 20+ portal resources not in Bicep | OPEN (25+ days) | 2h (measure), 1-2d (reconcile) | OpEx +0.5 |
| 2 | Backup restore unproven -- zero restore tests ever | OPEN (25+ days) | 30 min | Reliability +0.5 |
| 3 | KV private endpoint missing -- public network enabled | OPEN (25+ days) | 1h (Bicep change) | Security +0.3 |
| 4 | Alert routing unverified -- 4 rules, targets unknown | OPEN (25+ days) | 30 min | Reliability +0.3, OpEx +0.2 |
| 5 | Identity gaps -- Entra OIDC not activated, MFA not enforced | OPEN (25+ days) | Half day | Security +0.5 |

**Blocker override**: With any hard blocker open, verdict cannot exceed CONDITIONALLY_READY.

---

## Gap Challenger Findings

| Domain | Claimed | Challenged | Delta | Strongest Overclaim | Smallest Repair |
|---|---|---|---|---|---|
| Reliability | 1.8 | 1.5 | -0.3 | "Backup governed" without any restore test | Run one PG PITR restore (30 min) |
| Security | 2.6 | 2.2 | -0.4 | "KV RBAC governed" while KV has public network | Deploy KV PE + disable public access (1h) |
| Cost | 1.5 | 1.0 | -0.5 | "Inventory governed" implies cost discipline | Create one budget alert (5 min) |
| OpEx | 3.0 | 2.4 | -0.6 | "3.0" while 20+ resources drifted from IaC | Measure drift: `az resource list` vs Bicep (2h) |
| Performance | 2.8 | 2.4 | -0.4 | "Autoscaling governed" without load testing | Run one `hey` load test against healthcheck (5 min) |
| Design | 3.2 | 2.8 | -0.4 | "40+ spec bundles" with zero rollback procedures | Add rollback section to one spec (10 min) |
| Implement | 2.0 | 1.5 | -0.5 | "In progress" while 5/5 blockers open 25+ days | Sequence 3 sub-1h blockers, execute this week |
| Operate | 1.2 | 0.8 | -0.4 | "Monitoring deployed" but routing unverified | Verify one alert reaches one human (30 min) |

**Gap challenger verdict**: Systematically optimistic by 0.4 points across all domains. Root cause: "governed" (documented intent) scored equivalently to "proven" (demonstrated capability).

---

## Answer Safety Summary

| Flag | Count | Domains |
|---|---|---|
| SAFE | 4 | AFD WAF active, PG Private Endpoint, IaC pipeline exists, Foundry deployed |
| RISKY | 8 | Reliability, Security, OpEx, Performance, SaaS, AI, SAP ops, Implement |
| UNSUPPORTED | 3 | Cost Optimization, Mission-Critical (deferred), Operate |

---

## Missing Proof (Prioritized by Effort)

| Priority | Domain | What is Missing | Effort | Impact |
|---|---|---|---|---|
| 1 | OpEx | Verify alert routing reaches a human | 30 min | Unblocks Operate scoring |
| 2 | Reliability | One PG PITR restore test with timing | 30 min | Unblocks Reliability +0.5 |
| 3 | Security | KV private endpoint deployed via Bicep | 1h | Unblocks Security +0.3 |
| 4 | OpEx | Measure IaC drift (resource list vs Bicep) | 2h | Unblocks OpEx +0.5 |
| 5 | Performance | One load test against healthcheck endpoint | 5 min | Unblocks Performance confidence |
| 6 | Cost | One budget alert on any resource group | 5 min | Unblocks Cost from 1.0 to 1.5 |
| 7 | Security | Entra OIDC token exchange proof | Half day | Unblocks Security +0.5, Identity |
| 8 | AI | One end-to-end Foundry agent invocation logged | 1h | Proves AI boundary separation |
| 9 | Design | Rollback section in one spec bundle | 10 min | Closes design gap |
| 10 | Operate | One SLO definition for Odoo web | 15 min | Establishes SLO practice |

**Critical finding from gap challenger**: Items 1-3 are sub-1-hour fixes that have been open for 25+ days. Closing them removes 3 of 5 hard blockers.

---

## Recommended Portal Answer Posture

| Pillar | Recommended Posture | Rationale |
|---|---|---|
| Reliability | Conservative | No restore test, no DR rehearsal, single env. Do not claim DR capability. |
| Security | Moderate | WAF and PG PE are proven (claim confidently). Identity is non-functional (acknowledge gap). |
| Cost Optimization | Conservative | Zero cost visibility. Do not claim any cost maturity. |
| Operational Excellence | Moderate | IaC and pipeline exist (claim). Caveat drift and alert routing gaps. |
| Performance Efficiency | Conservative | No load test, no APM. Do not claim performance maturity. |

---

## Calibration vs Likely Official Score

| Pillar | Internal (judged) | Calibrated Official Range | Delta Risk |
|---|---|---|---|
| Reliability | 1.5 | 1.2-1.5 | Low (already conservative) |
| Security | 2.5 | 2.0-2.3 | Medium (identity gap will hurt) |
| Cost | 1.5 | 0.8-1.2 | High (zero cost tooling) |
| OpEx | 2.8 | 2.2-2.6 | Medium (drift is main penalty) |
| Performance | 2.5 | 1.8-2.2 | High (no load testing) |
| **Aggregate** | **2.15** | **1.8-2.2** | |

---

## Post-Official Comparison (fill after official portal run)

| Pillar | Internal | Official | Delta | Classification |
|---|---|---|---|---|
| Reliability | 1.5 | | | |
| Security | 2.5 | | | |
| Cost Optimization | 1.5 | | | |
| Operational Excellence | 2.8 | | | |
| Performance Efficiency | 2.5 | | | |

---

## Executive Summary

**Score: 2.15/5.0 (WEAK band)**

The IPAI platform is a **governance execution problem, not an architecture problem**. Design intent is strong (3.0/5 Design phase, 40+ spec bundles, 37 platform contracts, 16 Bicep modules). Operational proof is nearly absent (1.2/5 Operate phase, 0 safe domains in operations).

**The single most important finding**: 3 of 5 hard blockers are sub-1-hour fixes (alert routing, backup restore test, KV PE). They have been open 25+ days. Closing them this week would remove 3 blockers and unlock score improvements across Reliability, Security, and OpEx.

**Recommended immediate sequence** (total: under 1 working day for items 1-4):
1. Verify alert routing (30 min) -- unblocks Operate
2. Test backup restore (30 min) -- unblocks Reliability
3. Deploy KV private endpoint (1h) -- unblocks Security
4. Measure IaC drift (2h) -- unblocks OpEx
5. Activate Entra OIDC (half day) -- unblocks Identity

**Expected score after blocker closure**: WAF core 2.16 -> ~3.0-3.3, crossing the EMERGING threshold.

---

*Assessment version: 1.0 | Harness: structured v1 | Date: 2026-04-05 | Agents: 6 (3 harvesters + judge + challenger + calibration)*
