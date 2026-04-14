# Wave-01 Acceleration Plan — 2026-04-14 (REVISED)

## Status
Active (locked 2026-04-14, **revised same-day to L2+L3 only**)

## Target
**Execution acceleration without scope cuts.** External committed dates UNCHANGED:

| Milestone | Date |
|---|---|
| First customer-usable Wave-01 slice | **2026-07-14** (R2) |
| PH BIR + production hardening | **2026-10-14** (R3) |
| GA / partner-shippable | **2026-12-15** (R4) |

L1 (drop PO) and L4 (IPAI-tenant-only at GA) are NOT applied. They are decision-gated levers that trigger only on miss.

---

## Active levers (2)

| Lever | Mechanism | Status |
|---|---|---|
| **L2 — Multi-agent parallel build per Issue** | 3-5 subagents per Wave-01 Issue (model/view/test split), proven pattern (3 agents → 16 files for `ipai_finance_gl` <30min) | ✅ active |
| **L3 — Aggressive D365 reference repo harvest** | Use FastTrack-Implementation-Assets + MB-310 labs + dynamics-365-unified-operations-public as direct parity-record templates instead of writing from scratch | ✅ active |

## Deferred levers (2 — only on gate failure)

| Lever | Trigger condition |
|---|---|
| **L1 — Drop D365 PO from Wave-01** | If 2026-04-27 pace gate fails (no `ipai_finance_ap` shipped) |
| **L4 — IPAI-tenant-only at GA** | If 2026-06-15 first-customer-slice gate fails |

---

## 3 explicit decision gates

| Date | Gate | Action if MET | Action if MISSED |
|---|---|---|---|
| **2026-04-27** | Pace gate: did `ipai_finance_ap` (#528) ship? | Continue with full Wave-01 scope | Trigger **L1** (drop PO Epic #525 + 4 Issues to Wave-02) OR slip GA |
| **2026-06-15** | First customer-usable slice live on IPAI tenant? | Continue with full customer onboarding scope | Trigger **L4** (W9 sandbox-only at GA; defer OMC + TBWA\SMP) |
| **2026-08-11** | All BIR forms (eBIRForms / eFPS / ePAY / eAFS) working? | Continue with full BIR pack | Defer eAFS to post-GA |

---

## R1 sequencing (current iteration: 2026-04-14 → 2026-05-14)

All 9 active Wave-01 Issues now in `ipai-platform\R1-Foundation-30d` iteration.

### Active Wave-01 — Epic #523 D365 Finance Parity (5 Issues)
| Issue | Title | State | Status |
|---|---|---|---|
| #527 | General Ledger and Financial Foundation | Doing | ✅ DONE — scaffold + parity model in PR #742 |
| #528 | Accounts Payable and Accounts Receivable | To Do | 🔜 R1-NEXT (next executable, target Apr 21-27) |
| #526 | Finance Core Capabilities and Use Cases | To Do | R1-backlog |
| #529 | Expense, Cash, Fixed Assets, and Budgeting | To Do | R1-backlog |
| #530 | Finance and Operations Common Capabilities | To Do | R2-backlog |

### Active Wave-01 — Epic #524 Finance Agents Parity (4 Issues)
| Issue | Title | State | Status |
|---|---|---|---|
| #532 | Financial Reconciliation Agent | Doing | ✅ DONE — productized v0 in PR #742 |
| #531 | Finance Agents Operating Model | To Do | 🔜 R1-NEXT |
| #533 | Collections in Outlook Equivalent | To Do | 🔜 R1-NEXT |
| #534 | Finance Agent Surfaces and Governance | To Do | 🔜 R1-NEXT |

### Wave-01 retained but deferred-execution — Epic #525 D365 Project Operations (4 Issues)
| Issue | Title | State |
|---|---|---|
| #535 | Project Operations Core Guidance | To Do |
| #536 | Project Operations Core Functional Parity | To Do |
| #537 | Project Operations Integrated with ERP Guidance | To Do |
| #538 | Project Operations Integrated with ERP Functional Parity | To Do |

PO Epic stays in Wave-01 scope. Execution begins after R1' Finance pace is proven.

---

## What this plan KEEPS

- ✅ External committed dates unchanged (R2/R3/R4 GA)
- ✅ All 13 Wave-01 Issues remain in scope
- ✅ Doctrine alignment (CE → property fields → OCA → adjacent → compose → `ipai_*` last)
- ✅ MODULE_INTROSPECTION + TECHNICAL_GUIDE for every `ipai_*` module
- ✅ CI gates (test-before-commit; spec-bundle validation)
- ✅ HITL approval on mutating agent tools
- ✅ Engineering execution doctrine (reuse first, build the delta only)

## What this plan does NOT change

- No new top-level org repos
- No deferral of W9 / OMC / TBWA\SMP onboarding
- No GA date compression
- No Project Operations scope cut

---

## Pace gate math

**Min 1 Wave-01 Issue per developer-week.** 13 Wave-01 Issues / R1 (4 weeks) + R2 (8 weeks) + R3 (12 weeks) = ample buffer at full scope.

R1 close target: 5 of 9 active Issues moving (#527 + #532 done; #528 + #531 + #533 + #534 in flight or shipped; #526 + #529 + #530 in backlog).

---

## Status statement (use externally — UNCHANGED)

```text
Azure substrate:                  YES
Functional F&O-equivalent OS:     NOT YET — first usable slice in 91 days (Jul 14 2026)
Go-live-ready:                    NOT YET — GA in 245 days (Dec 15 2026)
```

---

## Anchors

- ADO Epics: #523 (D365 Finance), #524 (Finance Agents), #525 (D365 Project Operations) — ALL Wave-01
- ADO Issues in R1: #527 (Doing), #528, #531, #532 (Doing), #533, #534
- ADO Issues backlog: #526, #529, #530
- Memory: `project_delivery_position_20260414.md` (canonical dates) + `project_acceleration_plan_20260414.md` (this plan)
- `docs/backlog/wave-01-finance-agents-project-ops.md`
- `CLAUDE.md` § Engineering Execution Doctrine

## Revision history

- **2026-04-14 morning** — Original plan: L1+L2+L3+L4, GA compressed to 2026-09-15
- **2026-04-14 afternoon** — REVISED: L2+L3 only, GA stays 2026-12-15, 3 explicit decision gates added; L1+L4 deferred to gate-failure triggers
