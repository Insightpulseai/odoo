# Go / No-Go Decision Draft
**Date:** 2026-04-19
**Solution:** IPAI Platform — First Production Cutover Gate
**Primary Surface:** erp.insightpulseai.com (Odoo CE 18 + OCA + ipai_*)
**Evidence Pack:** `docs/evidence/20260419-1800/go-live-readiness-review/`
**Authority:** `ssot/release/go-live-readiness.yaml#go_no_go_matrix`

---

## Current Recommendation: NO-GO

**Rationale:** 4 of 6 NO-GO triggers are confirmed fired. 0 of 6 GO conditions are fully met (1 is met: readiness review report published). Six critical first-gate blockers remain unmitigated.

---

## NO-GO Triggers Fired

| Trigger | Status | Evidence Anchor |
|---|---|---|
| Unmitigated critical blocker | FIRED | BLOCKER-03 (7 GAs), BLOCKER-04 (SSO unverified + hotfix in place) |
| Cutover plan unsigned | FIRED | `ssot/release/go-live-scope-matrix.yaml#erp.readiness_status.cutover_plan: not_drafted` |
| Support coverage gap during cutover window | FIRED | Support plan pending; cutover window undefined |
| Rollback plan untested | FIRED | No rollback plan or drill exists |
| Environment drift between preprod and prod | PARTIAL | No production environment distinct from dev yet |
| Licensing gap for active users | NOT ASSESSED | No license sufficiency check documented |

---

## What Moves This to GO (Minimum Viable Set)

All six items below must be resolved and evidenced before a GO decision can be made:

1. **BLOCKER-01 cleared:** SIT + UAT sign-off documents in `docs/evidence/<date>/testing/`. Performance test evidence or explicit waiver with documented risk acceptance.

2. **BLOCKER-02 cleared:** Cutover plan document drafted, cutover window defined, roles assigned, stakeholder sign-off obtained and recorded.

3. **BLOCKER-03 cleared (minimum viable level):** GAs reduced to 3. CA-001 (require MFA for all users) and CA-003 (block legacy auth) implemented. Secure Score evidence captured. Full CA-002/004/005/006 implementation is preferred but CA-001 and CA-003 are the minimum for cutover.

4. **BLOCKER-04 cleared:** Odoo SSO verified end-to-end (Microsoft sign-in button → Entra login → Odoo session). AADSTS500117 hotfix either removed (preferred: AFD X-Forwarded-Proto canonicalization resolved) or confirmed stable under load with explicit risk acceptance.

5. **BLOCKER-05 cleared:** Production support plan and hypercare runbook drafted and signed off. On-call contacts named. Hypercare window (recommended: 72h) agreed.

6. **BLOCKER-06 cleared:** Rollback plan documented. Rollback trigger criteria explicit (e.g., P1 unresolved within 4h). Preprod rollback drill run and evidence captured.

BLOCKER-07 through BLOCKER-17 do not block the GO decision but must be tracked on a post-cutover remediation schedule.

---

## Decision Authority Required

| Role | Name | Required For |
|---|---|---|
| Platform Architecture Lead | Jake Tolentino (Admin) | Technical sign-off on all six minimum viable items |
| Cutover Lead | TBD — to be named in cutover plan | Cutover plan sign-off |
| Support Lead | TBD — to be named in support plan | Support plan and on-call rota sign-off |
| Go/No-Go Decision Owner | Jake Tolentino | Final GO authorization |

---

## Signoff Lines

All named decision holders must sign before the GO decision is recorded.

**Readiness Review Report reviewed and accepted:**

| Stakeholder | Role | Signature | Date |
|---|---|---|---|
| | Platform Architecture Lead | | |
| | Cutover Lead | | |
| | Support Lead | | |
| | Go/No-Go Decision Owner | | |

**Final GO decision (complete only after all six minimum viable items are evidenced):**

| Field | Value |
|---|---|
| Decision | [ ] GO / [ ] NO-GO / [ ] DELAY |
| Decision date | |
| Decision owner | |
| Evidence pack | |
| Notes | |

---

## Next Review

A follow-up readiness review should be scheduled when BLOCKER-02 (cutover plan), BLOCKER-04 (SSO verified), and BLOCKER-06 (rollback drill) are complete. At that point, a revised GO/NO-GO assessment will be materially different from this one.

---

*This document is a draft recommendation only. It is not a signed go-live authorization.*
*Authority: `ssot/release/go-live-readiness.yaml#readiness_review.decision_authority: named_stakeholder_set_per_release`*
