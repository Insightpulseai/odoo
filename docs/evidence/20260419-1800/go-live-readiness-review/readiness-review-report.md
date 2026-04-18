# Go-Live Readiness Review Report
**Assessment Date:** 2026-04-19
**Evidence Pack:** `docs/evidence/20260419-1800/go-live-readiness-review/`
**SSOT Authority:** `ssot/release/go-live-readiness.yaml` v1.0

---

## Executive Summary

The IPAI platform is **NOT GO-LIVE READY** for the first formal cutover gate. The mandatory ERP surface (`erp.insightpulseai.com`) has three first-gate blockers: SSO end-to-end verification is pending, no cutover plan exists, and no hypercare rota is defined. Identity governance presents a critical security blocker with 7 Global Administrators against a target of 3, 9 member accounts against a target of 4, and a Secure Score of 43.77% against a near-term target of 65%. No UAT, SIT, or performance testing has been signed off, and no production support plan exists.

**Recommendation: NO-GO.** A minimum viable remediation path is defined in Section 8.

---

## 1. Surface Readiness Table

| Surface | Domain | Go-Live Gate Scope | Gate Status | First-Gate Blockers |
|---|---|---|---|---|
| `erp` | erp.insightpulseai.com | MUST PASS | **BLOCKED** | SSO unverified, no cutover plan, no hypercare rota |
| `pulser_chat_on_erp` | embedded in ERP | DECIDE NOW | Decision pending | Eval gate undefined, user training pending |
| `databricks_control_tower` | — | DECIDE NOW | Decision pending | Executive entitlements pending, eval regression loop pending |
| `www.insightpulseai.com` | www.insightpulseai.com | Excluded | Out of scope | Scaffold exists, template adoption pending |
| `prismalab.insightpulseai.com` | prismalab.insightpulseai.com | Excluded | Out of scope | Evidence pipeline pending |
| `www.w9studio.net` | www.w9studio.net | Excluded | Out of scope | App scaffold not yet created |

Source: `ssot/release/go-live-scope-matrix.yaml`

---

## 2. Category-by-Category Assessment

### 2.1 Testing

| Item | Status | Evidence / Notes |
|---|---|---|
| System integration testing completed and signed off | **FAILED** | No SIT evidence found in any SSOT or evidence bundle |
| User acceptance testing completed and signed off | **FAILED** | No UAT evidence found |
| Performance testing completed and signed off | **FAILED** | No performance test results found |

**Category verdict: FAIL**
Source: `ssot/release/go-live-readiness.yaml#core_readiness_checklist.testing`

### 2.2 Deployable Artifacts

| Item | Status | Evidence / Notes |
|---|---|---|
| Code finished | **PARTIAL** | ERP Odoo CE 18 + ipai_odoo_copilot v18.0.4.0.0 shipped; MAF agent-platform still in phase-1 skeleton state; `business_dimensions.yaml` entity model is a stub |
| Deployable packages built | **PARTIAL** | Odoo container built and running on `ipai-odoo-dev` (ACA). Agent-platform `pyproject.toml` + `uv.lock` not yet created (migration phase 1 pending per `ssot/agent-platform/agent_framework_adoption.yaml#migration`) |

**Category verdict: PARTIAL**
Source: `ssot/agent-platform/agent_framework_adoption.yaml#migration.current_drift`; `ssot/odoo/business_dimensions.yaml#master_entity_model.status`

### 2.3 Data

| Item | Status | Evidence / Notes |
|---|---|---|
| Data migration plan documented | **NOT ASSESSED** | No data migration plan found in any SSOT; business_dimensions entity model is a stub with several TODO keys (`ssot/odoo/business_dimensions.yaml#master_entity_model`) |

**Category verdict: NOT ASSESSED (presumed FAIL)**

### 2.4 Cutover

| Item | Status | Evidence / Notes |
|---|---|---|
| Cutover plan signed off | **FAILED** | `ssot/release/go-live-scope-matrix.yaml#erp.readiness_status.cutover_plan: not_drafted` |
| Cutover window defined | **FAILED** | No window defined in any SSOT |
| Rollback window defined | **FAILED** | No rollback drill or tested rollback plan found; `ssot/release/go-live-scope-matrix.yaml` open decision #4 unresolved |

**Category verdict: FAIL**

### 2.5 People

| Item | Status | Evidence / Notes |
|---|---|---|
| User training completed | **FAILED** | `ssot/release/go-live-scope-matrix.yaml#pulser_chat_on_erp.readiness_status.user_training: pending` |
| Security role assignments correct | **FAILED** | Drift report: 7 GAs (target 3), 9 members (target 4), 0 guests (target 11), 378 SPs with 0 canonically named. Source: `docs/evidence/20260419/entra-identity-audit/drift-report.md` |
| License allocation sufficient | **NOT ASSESSED** | Entra ID P2 licensed; Odoo CE (no seat licensing). No documented license sufficiency check. |

**Category verdict: FAIL**
Source: `docs/evidence/20260419/entra-identity-audit/drift-report.md`

### 2.6 Support

| Item | Status | Evidence / Notes |
|---|---|---|
| Production support plan signed off | **FAILED** | `ssot/release/go-live-scope-matrix.yaml#erp.readiness_status.runtime_support_plan: pending` |
| On-call coverage confirmed for cutover window | **FAILED** | No cutover window defined; no on-call rota found |
| Escalation contacts documented | **NOT ASSESSED** | No escalation contact list found in any SSOT |

**Category verdict: FAIL**

### 2.7 Risk

| Item | Status | Evidence / Notes |
|---|---|---|
| Critical open issues from prior reviews mitigated | **FAILED** | Identity drift is unmitigated (7 GAs, AADSTS500117 Odoo SSO hotfix still in place), MAF migration phase 2 pending, 5 deprecated MCP connectors still active in claude.ai UI, Databricks Genie MCP stale |

**Category verdict: FAIL**
Source: `ssot/odoo/odoo-sso-runtime-state.yaml#odoo_sso_https_hotfix`; `ssot/tooling/mcp-runtime-state.yaml#cloud_remote_servers.deprecated_requires_user_action_in_claude_ai_ui`

---

## 3. Go / No-Go Matrix Evaluation

### 3.1 GO Conditions (all required)

| Condition | Status | Evidence |
|---|---|---|
| Core readiness checklist complete | **NOT MET** | 5 of 7 categories fail |
| Readiness review report published | **MET** | This document |
| No unmitigated critical blockers | **NOT MET** | Identity drift (7 GAs), SSO unverified, no cutover plan |
| Cutover plan signed off by stakeholders | **NOT MET** | `go-live-scope-matrix.yaml#erp.cutover_plan: not_drafted` |
| Production support on-call confirmed | **NOT MET** | Support plan status: pending |
| Rollback plan tested in preprod | **NOT MET** | No rollback drill recorded |

**GO conditions met: 1 of 6**

### 3.2 NO-GO Triggers (any one triggers NO-GO)

| Trigger | Fired? | Evidence |
|---|---|---|
| Unmitigated critical blocker | **YES** | SSO unverified (AADSTS500117 hotfix in place), 7 GAs active |
| Cutover plan unsigned | **YES** | Not drafted |
| Support coverage gap during cutover window | **YES** | Cutover window not defined; support plan pending |
| Rollback plan untested | **YES** | No rollback plan or drill recorded |
| Environment drift between preprod and prod | **PARTIAL** | No prod environment exists yet; dev/prod parity not assessed |
| Licensing gap for active users | **NOT ASSESSED** | No license sufficiency check documented |

**NO-GO triggers fired: 4 of 6 (confirmed); 1 partial; 1 not assessed**

**Decision: NO-GO**

---

## 4. Blocker Inventory

See `blocker-register.yaml` for full structured register.

### First-Gate Blockers (must clear before cutover)

| ID | Severity | Category | Description | Surface |
|---|---|---|---|---|
| BLOCKER-01 | Critical | Testing | No SIT, UAT, or performance testing signed off | erp |
| BLOCKER-02 | Critical | Cutover | Cutover plan not drafted | erp |
| BLOCKER-03 | Critical | Identity | 7 Global Administrators active (target: 3); Secure Score 43.77% | platform |
| BLOCKER-04 | Critical | Identity | Odoo SSO end-to-end test pending; AADSTS500117 hotfix in place | erp |
| BLOCKER-05 | Critical | Support | Production support plan pending; no on-call rota | erp |
| BLOCKER-06 | Critical | Cutover | Rollback plan not documented or tested | erp |
| BLOCKER-07 | High | Identity | 9 member accounts (target 4); 5 surplus users to remove/reclassify | platform |
| BLOCKER-08 | High | Identity | 0 of 11 TBWA\SMP guests invited (target: 11) | platform |
| BLOCKER-09 | High | Agent Platform | MAF migration phase 1 skeleton not complete; no `pyproject.toml` or `uv.lock` | agent-platform |
| BLOCKER-10 | High | Data | `business_dimensions.yaml` entity model is a stub; 6 of 8 entity keys are TODO | erp + analytics |

### Post-Gate Items (not first-gate blocking)

| ID | Severity | Category | Description | Surface |
|---|---|---|---|---|
| BLOCKER-11 | Medium | Tooling | 5 deprecated MCP connectors still active in claude.ai UI (Supabase, Vercel, Cloudflare×2, n8n) | platform |
| BLOCKER-12 | Medium | Tooling | Databricks Genie MCP stale (wrong warehouse ID); adopt workspace-native Genie-as-MCP | databricks |
| BLOCKER-13 | Medium | Agent Platform | MAF phase 2 migration (move existing src/ to packaged layout) pending | agent-platform |
| BLOCKER-14 | Medium | Scope Decision | `pulser_chat_on_erp` gate scope undecided (in first gate vs. follow-on) | pulser_chat_on_erp |
| BLOCKER-15 | Medium | Scope Decision | `databricks_control_tower` gate scope undecided | databricks_control_tower |
| BLOCKER-16 | Low | Identity | 378 service principals with 0 canonically named (`sp-*`/`mi-*`/`agent-*`) | platform |
| BLOCKER-17 | Low | Identity | 1 unmanaged agent identity (no sponsor, no canonical name) | agent-platform |

---

## 5. Open Decisions (from go-live-scope-matrix.yaml)

| # | Question | Recommended Default | Implication |
|---|---|---|---|
| 1 | Is `pulser_chat_on_erp` in first go-live gate? | **No — follow-on release** | ERP goes live without AI copilot; copilot enabled post-cutover. Avoids eval gate, training, and Foundry SLA from blocking ERP cutover. |
| 2 | Is `databricks_control_tower` in first go-live gate? | **No — parallel release track** | ERP goes live without Databricks dashboards. Control Tower releases on its own cadence after executive entitlements and eval regression loop are resolved. |
| 3 | Hypercare window length for ERP cutover | **72 hours** | Aligned with Microsoft Dynamics go-live guidance as baseline for first go-live. |
| 4 | Rollback criteria and tested rollback drill date | **Define criteria before cutover plan sign-off** | Rollback triggers must be explicit (e.g., P1 incident unresolved within 4h of cutover). Drill must be run in preprod before the cutover window is approved. |

Source: `ssot/release/go-live-scope-matrix.yaml#open_decisions`

---

## 6. Hypercare and Rollback Plan Gap

### Hypercare

- **Current state:** Not defined. `ssot/release/go-live-scope-matrix.yaml#erp.readiness_status.hypercare_plan: not_drafted`
- **Required:** `ssot/release/go-live-readiness.yaml#cutover_discipline.post_cutover` mandates hypercare window definition, daily go-live status reports, incident escalation readiness, and rollback criteria monitoring.
- **Gap:** No hypercare window length agreed, no daily status report template, no escalation contacts documented.

### Rollback

- **Current state:** No rollback plan documented. No rollback drill run.
- **Required:** `ssot/release/go-live-readiness.yaml#cutover_discipline.rollback_discipline` mandates documented + signed-off rollback plan, rollback execution criteria (critical Sev1 unresolvable within hypercare), and evidence capture.
- **Gap:** Both the plan document (`rollback_plan_tested.md`) and the preprod drill are missing.

---

## 7. Recommended Remediation Sequence (Dependency-Ordered)

The following sequence is dependency-safe and addresses first-gate blockers before post-gate items.

| Step | Action | Owner | Dependency | Blocker Cleared |
|---|---|---|---|---|
| 1 | Resolve open decisions 1–4 (scope, hypercare length, rollback criteria) | platform-architecture | None | Unblocks cutover plan drafting |
| 2 | Entra remediation: create `jake.admin@`, verify PIM eligibility on break-glass accounts | platform-architecture | None | BLOCKER-03 partial |
| 3 | Odoo SSO end-to-end test: verify Microsoft sign-in at `erp.insightpulseai.com` | platform-architecture | ACA running | BLOCKER-04 |
| 4 | Remove duplicate break-glass and mailbox-UPN Entra members; reduce GAs to 3 | platform-architecture | Step 2 complete | BLOCKER-03, BLOCKER-07 |
| 5 | Bulk-invite 11 TBWA\SMP guests per `ssot/identity/guest-invite-registry.yaml` | platform-architecture | Step 4 safe to proceed | BLOCKER-08 |
| 6 | Implement CA-001 through CA-006 Conditional Access policies | platform-architecture | Steps 2–4 complete | BLOCKER-03 (Secure Score) |
| 7 | Draft and sign off cutover plan (window, runbook, roles) | platform-architecture | Steps 1–3 complete | BLOCKER-02 |
| 8 | Document rollback criteria; run preprod rollback drill | platform-architecture | Step 7 complete | BLOCKER-06 |
| 9 | Draft and sign off production support plan + on-call rota | platform-architecture | Step 7 complete | BLOCKER-05 |
| 10 | Complete MAF phase 1 skeleton (`pyproject.toml`, `uv.lock`, `src/agent_platform/`) | agent-platform | None (parallel) | BLOCKER-09 |
| 11 | Complete `business_dimensions.yaml` entity model stub | platform-architecture | None (parallel) | BLOCKER-10 |
| 12 | Plan and execute SIT, UAT, performance testing; obtain sign-offs | platform-architecture + QA | Steps 7–9 complete (env stable) | BLOCKER-01 |
| 13 (post-gate) | Remove 5 deprecated MCP connectors from claude.ai UI | platform-architecture | None | BLOCKER-11 |
| 14 (post-gate) | Adopt Databricks workspace-native Genie-as-MCP | platform-architecture | None | BLOCKER-12 |
| 15 (post-gate) | MAF phase 2 migration (move existing src/ to packaged layout) | agent-platform | Step 10 complete | BLOCKER-13 |

---

## 8. Minimum Viable Path to GO

For a GO decision, the following must be resolved before cutover:

1. BLOCKER-01 resolved: SIT + UAT signed off (performance testing evidence or explicit waiver with documented risk acceptance).
2. BLOCKER-02 resolved: Cutover plan drafted and signed by decision authority.
3. BLOCKER-03 resolved to sufficient level: GAs reduced to target 3; CA-001 (all-users MFA) and CA-003 (block legacy auth) at minimum implemented.
4. BLOCKER-04 resolved: Odoo SSO verified end-to-end with Microsoft sign-in flow; AADSTS500117 hotfix removed or confirmed stable.
5. BLOCKER-05 resolved: Support plan and on-call rota signed off.
6. BLOCKER-06 resolved: Rollback plan documented and preprod drill run.

Items BLOCKER-07 through BLOCKER-17 are NOT first-gate blocking and can proceed post-cutover on a tracked remediation schedule.

---

## 9. Evidence Anchors

| Source SSOT | Path |
|---|---|
| Go-live readiness doctrine | `ssot/release/go-live-readiness.yaml` |
| Surface scope matrix | `ssot/release/go-live-scope-matrix.yaml` |
| Entra target state v2.0 | `ssot/identity/entra_target_state.yaml` |
| Entra identity matrix | `ssot/identity/entra-identity-matrix.yaml` |
| Directory authority matrix | `platform/ssot/identity/directory-authority-matrix.yaml` |
| Odoo SSO runtime state | `ssot/odoo/odoo-sso-runtime-state.yaml` |
| Entra identity drift report | `docs/evidence/20260419/entra-identity-audit/drift-report.md` |
| MAF adoption SSOT | `ssot/agent-platform/agent_framework_adoption.yaml` |
| MCP runtime state | `ssot/tooling/mcp-runtime-state.yaml` |
| OCA must-have scaffolds | `infra/ssot/oca/must_have_*.yaml` |
| Business dimensions | `ssot/odoo/business_dimensions.yaml` |
| Azure resource inventory | `ssot/architecture/azure-resource-inventory.yaml` |
| Azure resource inventory (dev) | `platform/ssot/azure/resource-inventory.dev.yaml` |
| Pulser pack matrix | `platform/ssot/agents/pulser-pack-matrix.yaml` |
