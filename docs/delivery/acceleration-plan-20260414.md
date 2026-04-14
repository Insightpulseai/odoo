# Wave-01 Acceleration Plan — 2026-04-14

## Status
Active (locked 2026-04-14)

## Target
Move GA from **2026-12-15 → 2026-09-15** (~90 days saved). First customer-usable slice from **2026-07-14 → 2026-06-15**.

---

## 4 stacked levers (each reversible)

| Lever | Mechanism | Days saved | Status |
|---|---|---|---|
| **L1** | Drop D365 Project Operations (Epic #525) from Wave-01 → defer to Wave-02 | 30 | ✅ active |
| **L2** | Multi-agent parallel build per Issue (proven pattern: 3 agents → 16 files <30min) | 25 | ✅ active |
| **L3** | Aggressive harvest from D365 reference repos (FastTrack assets + MB-310 labs as parity templates) | 20 | ✅ active |
| **L4** | Customer-scope cut: IPAI tenant only at GA; defer W9 production + OMC + TBWA\SMP to post-GA | 15 | ✅ active |
| **TOTAL** | | **~90 days** | |

---

## Compressed R-band schedule

### R1' — Apr 14 → May 7 (23 days, was 30)
**Theme: definition + scaffold.**

| Week | Wave-01 Issue | ADO ID | Status |
|---|---|---|---|
| W1 (Apr 14-20) | GL Foundation | #527 | ✅ DONE (scaffold) |
| W1 (Apr 14-20) | Reconciliation Agent v0 | #532 | ✅ DONE (productized) |
| W2 (Apr 21-27) | Accounts Payable + Accounts Receivable scaffold | #528 | Scheduled |
| W3 (Apr 28-May 4) | Collections in Outlook scaffold | #533 | Scheduled |
| W3 (Apr 28-May 4) | Finance Agents Operating Model | #531 | Scheduled |
| W4 (May 5-7) | Expense + Cash + Fixed Assets + Budgeting scaffold | #529 | Scheduled |
| W4 (May 5-7) | Finance Agent Surfaces + Governance | #534 | Scheduled |
| W4 (May 5-7) | Finance Core Capabilities + Use Cases | #526 | Scheduled |

### R2' — May 8 → Jun 15 (38 days, was 60) — **first customer-usable**
**Theme: working slice on IPAI tenant.**

| Week | Deliverable |
|---|---|
| W5-6 (May 8-21) | `ipai_finance_gl` + `ipai_finance_ap` wired to Odoo CE; UAT vs MB-310 lab scenarios |
| W7-8 (May 22-Jun 4) | `ipai_finance_ar` + Recon Agent v1 (real bank feed) + Collections in Outlook v1 |
| W9-10 (Jun 5-15) | Power BI semantic + Financial Reports Intelligence + ACA blue/green wired |
| **Jun 15** | **First customer slice GA on IPAI tenant** |
| | Closes: #530 Finance + Operations Common Capabilities |

### R3' — Jun 16 → Aug 15 (60 days, was 90) — PH BIR + production hardening
**Theme: PH ops production-grade.**

| Week | Deliverable |
|---|---|
| W11-14 (Jun 16-Jul 13) | BIR pack: eBIRForms + eFPS + ePAY + eAFS + 2307 automation |
| W15-18 (Jul 14-Aug 11) | Production Agent Runtime Hardening (#341) + Partner Center Phase 1 + Solution Kit (#480) |
| W19 (Aug 12-15) | Resource-level Azure Policy enforcement + audit pass |

### R4' — Aug 16 → Sep 15 (30 days, was 60) — GA
**Theme: GA polish + marketplace listing.**

| Week | Deliverable |
|---|---|
| W20-21 (Aug 16-29) | Marketplace listing submission + ISV Success readiness review |
| W22 (Aug 30-Sep 5) | All Wave-01 epics → Closed; 80% parity demonstration on IPAI tenant |
| W23 (Sep 6-15) | **GA on Sep 15.** Marketplace listing live. IPAI tenant in production. |

---

## What this plan defers (per L1 + L4)

### Wave-02 (post-GA)
- **D365 Project Operations Parity** (Epic #525) — all 4 child Issues:
  - #535 Project Operations Core Guidance
  - #536 Project Operations Core Functional Parity
  - #537 Project Operations Integrated with ERP Guidance
  - #538 Project Operations Integrated with ERP Functional Parity
- **W9 Studio production cutover** (W9 stays sandbox/staging)
- **OMC tenant onboarding**
- **TBWA\SMP tenant onboarding**
- **AVM Bicep migration of 21 hand-written modules** (background cleanup, not gating)
- **Reference-adaptations harvest beyond Wave-01 critical** (defer Workspace, Partner Center storefront, awesome-list research)

---

## What this plan KEEPS (no compromise)

- ✅ Doctrine alignment (CE → property fields → OCA → adjacent → compose → `ipai_*` last)
- ✅ MODULE_INTROSPECTION + TECHNICAL_GUIDE for every `ipai_*` module
- ✅ CI gates (test-before-commit; spec-bundle validation)
- ✅ HITL approval on mutating agent tools
- ✅ Tag policy enforcement (resource-level rolls into R3 hardening)
- ✅ Engineering execution doctrine (reuse first, build the delta only)

---

## Decision points

| When | Decision |
|---|---|
| **Now (2026-04-14)** | ✅ Plan approved — all 4 levers active |
| **End of W2 (Apr 27)** | If `ipai_finance_ap` not shipped → drop another scope item OR slip Sep 15 |
| **End of R2' (Jun 15)** | First customer slice live on IPAI? If no → cancel L4 (re-scope to W9 sandbox-only) |
| **End of W18 (Aug 11)** | All BIR forms working? If no → defer eAFS to post-GA |

---

## Pace gate

**Minimum 1 Wave-01 Issue per developer-week.**
- Active Wave-01 scope: 9 Issues (5 under #523 + 4 under #524, post-L1 cut)
- R1' weeks: 4 weeks → 9 Issues / 4 weeks = **2.25 Issues/week needed in R1'**
- R2' weeks: 6 weeks → mostly Issue completion + UAT
- Math works. No buffer in R1'.

---

## Status statement (use externally)

```text
Azure substrate:                  YES
Functional F&O-equivalent OS:     NOT YET — first usable slice in 62 days (Jun 15)
Go-live-ready:                    NOT YET — GA in 154 days (Sep 15)
```

---

## Anchors

- ADO Epics: #523 (D365 Finance), #524 (Finance Agents); #525 deferred to Wave-02
- ADO Active Issues (R1'): #526, #527, #528, #529, #531, #532, #533, #534 (in R1'); #530 (R2')
- Memory: `project_delivery_position_20260414.md` (predecessor — supersede with this entry for compressed dates)
- `ssot/benchmarks/parity_matrix.yaml`
- `docs/backlog/wave-01-finance-agents-project-ops.md`
- `CLAUDE.md` § Engineering Execution Doctrine
