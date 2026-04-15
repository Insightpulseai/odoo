# Program OKR + PPM Template (PMBOK + Clarity PPM-aligned)

> **Status:** canonical template for IPAI programs
> **Locked:** 2026-04-15
> **Authority:** this file (reusable OKR + PPM pattern)
> **References:**
> - [Clarity PPM — Objectives and Key Results (OKRs)](https://techdocs.broadcom.com/us/en/ca-enterprise-software/business-management/clarity-project-and-portfolio-management-ppm-on-premise/16-1-1/introducing-clarity-cookbooks/clarity-cookbook--objectives-and-key-results--okrs-.html)
> - PMBOK 7th ed — Schedule Control, WBS, Risk Response
> - OKR methodology (Google / John Doerr origin)

---

## When to use this template

Any new **program** (multi-project engagement with one accountable sponsor). Instantiate a copy as `docs/programs/<program-slug>.md` and fill in.

One program = one file. Do not use this template for single-project work.

---

## The 5 non-negotiable gates

Every program OKR set must pass these 5 gates before going live:

### Gate 1 — SMART criteria on every Key Result

Each KR is:
- **S**pecific — names the thing being changed
- **M**easurable — has a metric + measurement method
- **A**chievable — stretch but credible given capacity
- **R**elevant — laddered to the Objective
- **T**ime-bound — absolute date, not "by Q3"

Reject any KR that fails one of the five.

### Gate 2 — 3–5 Key Results per Objective

Hard limit. More than 5 means the Objective is too broad — split it. Fewer than 3 means the Objective is under-specified.

### Gate 3 — OKR scoring cadence (0.0–1.0 Google-style)

Score every KR on a 0.0–1.0 scale at regular cadence:

| Score | Meaning |
|---|---|
| 0.0 | No progress |
| 0.3 | Real effort, low outcome |
| 0.7 | **Target** — aspirational shipped; "good" |
| 1.0 | Over-delivered |

**Aspirational default: 0.7.** A program scoring 1.0 consistently means the OKRs were not stretched; 0.0–0.3 means sandbag.

Scoring cadence:
- Per KR: every sprint close
- Per Objective: monthly review (Exec OKR dashboard)
- Per Program: quarterly rollup

### Gate 4 — Risk linkage (low confidence KR = escalated risk)

Each KR carries a **confidence score** 0.0–1.0 set at kickoff and reviewed monthly.

Rule:
- `confidence >= 0.7` — on track, normal cadence
- `0.4 <= confidence < 0.7` — amber; Monthly review + mitigation plan
- `confidence < 0.4` — red; escalate to program sponsor; risk register gets a new entry or upgrade

Every KR with confidence < 0.7 **must have** a corresponding row in the risk register with mitigation + owner.

### Gate 5 — WBS / Milestone alignment (PMBOK schedule control)

Every KR maps to a WBS node (deliverable) and a milestone (date). Format:

```
KR-X.Y.Z → WBS <code> → Milestone <id> → Target <ISO date>
```

This lets PMBOK schedule control (forward pass, critical path) measure OKR slippage in the same variance framework as the rest of the project.

No KR without a WBS row. No WBS row without a named milestone (even if "rolling" — then the milestone is the next checkpoint).

---

## Template structure (copy this)

```
# <Program Name> — OKR + PPM Plan

> Status:       TEMPLATE | ACTIVE | CLOSED
> Locked:       YYYY-MM-DD
> Sponsor:      <name>, <role>
> Program ID:   <short slug>
> Tenant:       <tenant code if client-facing>

## 1. Program charter
## 2. Stakeholder register (RACI)
## 3. OKRs
## 4. WBS + milestone alignment
## 5. Risk register (with KR-confidence linkage)
## 6. Scoring log
## 7. Schedule control (PMBOK)
## 8. Dashboards
## 9. References
```

---

## Section-by-section contract

### 1. Program charter (PMBOK Initiating)

Required fields (no others in this section):

```yaml
purpose:        <one sentence>
objective:      <single program-level Objective>
success:        <4 criteria that let the sponsor say "done">
duration:       <ISO start> → <ISO end>
budget:         <amount + currency> OR "TBD on contract"
approach:       <2–3 sentences>
non_goals:      <what this program explicitly does NOT do>
```

### 2. Stakeholder register (PMBOK Stakeholder Management)

Required table columns:

| Role | Name | Responsibility | RACI |
|---|---|---|---|
| Sponsor | … | Accountable | A |
| Program owner | … | Responsible — Delivery | R |
| Finance SME (client) | … | Responsible — Domain | R |
| Technical lead | … | Responsible — Architecture | R |
| Consulted | … | Audit / CPA / counsel | C |
| Informed | … | Leadership | I |

RACI = Responsible / Accountable / Consulted / Informed. **Exactly one `A` per row of responsibility.**

### 3. OKRs (PPM / Clarity pattern)

Structure per Objective:

```
Objective O.n — <clear action statement>

  KR-n.1 — <verb> <measured output> by <date>
    WBS:        <code>
    Milestone:  <id>
    Measure:    <how measured, where>
    Confidence: 0.0–1.0 (initial)
    Owner:      <single name>

  KR-n.2 — ...
  KR-n.3 — ...
  (max 5, min 3)
```

**Objectives per program: 2–4.** More than 4 = program too broad.
**KRs per Objective: 3–5.** Hard limit.
**Total KRs per program: 6–20.** Anything larger fragments attention.

### 4. WBS + milestone alignment (PMBOK)

One table. Row = WBS deliverable. Columns include the KR that this WBS node delivers on.

| WBS code | Deliverable | Parent | Milestone | Target date | KR link | Owner |
|---|---|---|---|---|---|---|
| 1.0 | … | root | M1 | YYYY-MM-DD | KR-1.1 | … |
| 1.1 | … | 1.0 | M2 | YYYY-MM-DD | KR-1.1 | … |
| 2.0 | … | root | M3 | YYYY-MM-DD | KR-2.1 | … |

WBS numbering = PMBOK hierarchical decimal. Max 3 levels before it becomes pseudo-hierarchy.

### 5. Risk register (with KR-confidence linkage)

| Risk ID | Description | Probability | Impact | KR impacted | Confidence at KR | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| R1 | … | Low/Med/High | Low/Med/High | KR-1.2 | 0.5 | … | … | Open |

**Rule:** every risk with Impact ≥ Med must link to ≥ 1 KR. Every KR with confidence < 0.7 must appear in ≥ 1 risk row.

### 6. Scoring log (Clarity PPM pattern)

Append-only log.

```yaml
- date: 2026-MM-DD
  review_type: sprint_close | monthly | quarterly
  scores:
    - kr: KR-1.1
      score: 0.7
      confidence: 0.8
      comment: "…"
    - kr: KR-1.2
      score: 0.3
      confidence: 0.5
      comment: "blocked on …"
  program_objective_rollup:
    - objective: O.1
      rollup_score: 0.5   # avg of its KR scores
      status: amber
```

At monthly review, the **program dashboard reads the most-recent entry**.

### 7. Schedule control (PMBOK)

Required elements:

```yaml
baseline_schedule:     <reference to project.project plan + milestones>
baseline_locked_at:    <YYYY-MM-DD>
variance_threshold:
  green:  |variance_days| <= 5
  amber:  5 < |variance_days| <= 14
  red:    |variance_days| > 14 → schedule change request required
change_control:
  trigger: red variance
  authority: program sponsor + technical lead
  artifact: PR with updated milestone dates + justification
earned_value_tracking: optional (turn on for >USD 100k engagements)
```

### 8. Dashboards (Boards + Power BI)

Follow [`docs/programs/tbwa-smp-okr-milestones-dashboard.md`](./tbwa-smp-okr-milestones-dashboard.md) structure:

- Dashboard 1 — Executive OKR (monthly review)
- Dashboard 2 — Milestone Timeline (weekly review)
- Dashboard 3 — Operations Health (daily standup)

Plus: **OKR Scoring Widget** required on Dashboard 1 (renders latest scoring log entry, color-coded).

### 9. References

Internal:
- Link to program charter / SOW (if signed)
- Link to related programs
- Link to tenant identity file (if client-facing)
- Link to backlog pack (if recurring work applies)

External:
- Clarity PPM OKR cookbook
- PMBOK 7th edition references used

---

## OKR authoring checklist (run before publishing)

- [ ] Every Objective has 3–5 KRs (not 2, not 6+)
- [ ] Every KR has all 5 SMART elements (S/M/A/R/T explicit)
- [ ] Every KR has a WBS code + Milestone + Owner
- [ ] Every KR has an initial confidence score 0.0–1.0
- [ ] Every KR with confidence < 0.7 has a risk-register row
- [ ] Every milestone has an absolute ISO date (no "Q3-ish")
- [ ] Every risk with Impact ≥ Med links to ≥ 1 KR
- [ ] Scoring log initialized with kickoff entry
- [ ] Baseline schedule locked before first sprint starts

---

## Anti-patterns (reject at review)

- "By Q3" or "Late 2026" — not a date
- KR that counts an activity, not an outcome ("hold 5 workshops" ≠ "adopt X")
- Objective with 8 KRs — split the Objective, don't tolerate
- 1.0 scores every review — OKRs not stretched; re-baseline
- Risk register that doesn't reference KRs — the two are meant to fuse
- Schedule baseline that moves without a change request (PR) — undermines PMBOK control
- WBS that doesn't tie to an Odoo `project.project` + `project.task` when the program is delivery-heavy — loses system-of-action trail

---

## Instantiation command

```
cp docs/programs/_PROGRAM_OKR_TEMPLATE.md docs/programs/<slug>.md
# Then fill every <...> placeholder.
# Every instantiation is reviewed via PR against the 5 gates above.
```

---

*Last updated: 2026-04-15*
