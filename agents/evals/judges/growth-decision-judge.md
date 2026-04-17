# Growth Decision Judge

**Purpose:** Score any proposed IPAI growth action against the MS for Startups knowledge base + Kira (CGO persona) + IPAI doctrine. Returns a structured JSON verdict with per-dimension scores + rationale + blocking flag.

**Inputs:** A proposed growth action (natural language, e.g., "publish `ipai_odoo_on_aca` as private Marketplace offer for TBWA\SMP").

**Grounding:** `docs/research/ms-startups/knowledge-base.md`, `docs/strategy/pulser-product-packaging.md`, `docs/competitive/d365-marketplace-coverage.md`, `CLAUDE.md` cross-repo invariants, `feedback_stick_to_gpt41`, `feedback_no_billing_nagging`, `feedback_foundry_reuse_doctrine`, `project_ms_agent_competitive_map`.

**Locked 2026-04-15.**

---

## 1. Scoring dimensions (0-5, each)

| # | Dimension | Criterion text | 0 (fail) | 5 (clear pass) |
|---|---|---|---|---|
| 1 | **Program fit** | Is there a Microsoft / partner program already funding this? | No program; pure personal P&L bet | Funded by Founders Hub + ISV Success + Co-sell, all named |
| 2 | **Evidence** | Is there customer or market data supporting the bet? | Pure hypothesis | Named customer + LOI + data point from `docs/competitive/d365-marketplace-coverage.md` or AppSource |
| 3 | **Reversibility** | Can we roll back within 30 days? | Multi-year contract; engineering rework >3 FTE-months | Pilot / private offer / listing-only / opt-out built in |
| 4 | **Unit economics** | Does CAC / LTV / payback math work? | Payback >18 months OR LTV unknown | Payback <9 months; LTV/CAC ≥3x with named assumptions |
| 5 | **Sequencing** | Do prerequisites exist in IPAI state today? | Requires unprovisioned infra, unshipped `ipai_*` modules, or unenrolled programs | Every prerequisite verified live (runbooks, infra, enrollments) |
| 6 | **Regulatory / compliance fit** | PH BIR, data residency, Entra Agent 365, Partner Center policy | Conflicts with CLAUDE.md Cross-Repo Invariants OR PH regulatory rules | Doctrine-aligned AND PH-compliant |
| 7 | **Strategic coherence** | Does it ladder to the 12-month roadmap? | Random; distracts from Finance Ops / PH Compliance wedge | Directly advances Pack 1/4 first, then Pack 3, then Pack 2 (per packaging doc) |

**Composite score:** sum (max 35). Scores of 28+ clear-pass; 20-27 proceed with caveats; 13-19 borderline; <13 clear-fail.

**Blocking flag (auto-block regardless of composite):**
- Regulatory fit < 3 (compliance BLOCK)
- Program fit = 0 AND unit economics < 3 (unfunded + unviable)
- Sequencing = 0 (prerequisite blocker — fix the blocker first)

---

## 2. Output format (JSON schema)

```json
{
  "action": "<the proposed growth action>",
  "timestamp": "<ISO 8601>",
  "scores": {
    "program_fit": {"score": 0-5, "rationale": "..."},
    "evidence": {"score": 0-5, "rationale": "..."},
    "reversibility": {"score": 0-5, "rationale": "..."},
    "unit_economics": {"score": 0-5, "rationale": "..."},
    "sequencing": {"score": 0-5, "rationale": "..."},
    "regulatory_fit": {"score": 0-5, "rationale": "..."},
    "strategic_coherence": {"score": 0-5, "rationale": "..."}
  },
  "composite": 0-35,
  "verdict": "clear_pass | proceed_with_caveats | borderline | clear_fail",
  "blocking_flags": ["..."],
  "caveats": ["..."],
  "recommendation": "proceed | defer | reframe | reject"
}
```

---

## 3. Worked examples

### Example 1 — CLEAR PASS

**Action:** "Ship `ipai_bir_tax_compliance` Phase 1 (2307 + SAWT DAT + PDF via Foundry Code Interpreter) in Q2 2026, bundled with Pack 4 PH Compliance for the TBWA\SMP pilot."

```json
{
  "action": "Ship ipai_bir_tax_compliance Phase 1 bundled with Pack 4 for TBWA\\SMP pilot",
  "timestamp": "2026-04-15T12:00:00+08:00",
  "scores": {
    "program_fit": {"score": 3, "rationale": "Not directly funded by a specific MS program, but the Marketplace surface (via Issue 29) and Co-sell Ready downstream will monetize. Azure consumption (Code Interpreter + Foundry) draws Founders Hub credits. Partial credit: MS doesn't fund PH BIR specifically."},
    "evidence": {"score": 5, "rationale": "TBWA\\SMP Finance is a named pilot customer with concrete BIR filing needs. Avalara gap confirmed in docs/competitive/d365-marketplace-coverage.md §13 — zero PH BIR competitors on Azure Marketplace."},
    "reversibility": {"score": 4, "rationale": "Phase 1 is DAT + PDF generation only (not eBIRForms submission). Fully within-Odoo-module; can be unshipped via module uninstall. Reversibility limited only by reputational cost with TBWA\\SMP if pilot fails."},
    "unit_economics": {"score": 4, "rationale": "Zero incremental license cost (OCA + ipai_*); engineering cost already in P0 backlog (Issue 9). vs. D365 Finance + Project Operations $45,540/yr for 11 users — payback is immediate on first pilot close."},
    "sequencing": {"score": 5, "rationale": "All prerequisites live: ipai-copilot-resource + Code Interpreter built-in + docai-ipai-dev + pg-ipai-odoo + Tax Guru MI. Module stub exists in repo."},
    "regulatory_fit": {"score": 5, "rationale": "PH BIR 2307 / SAWT are regulatory mandates. Shipping this IS the compliance fit. Doctrine-aligned per CLAUDE.md (Azure-native, OCA-first, thin ipai_*)."},
    "strategic_coherence": {"score": 5, "rationale": "Directly advances Pack 4 (PH Compliance) + Pack 1 (Finance Ops via integrated AP + CWT flow). Ranked P0 in docs/strategy/pulser-product-packaging.md §2."}
  },
  "composite": 31,
  "verdict": "clear_pass",
  "blocking_flags": [],
  "caveats": ["Program fit only partial — pursue Founders Hub credit drawdown in parallel to amortize Azure consumption"],
  "recommendation": "proceed"
}
```

---

### Example 2 — CLEAR PASS (bigger bet)

**Action:** "Publish `ipai_odoo_on_aca` to Azure Marketplace as a private offer for TBWA\\SMP, starting 2026-05 with a 90-day conversion window to public transactable."

```json
{
  "action": "Publish ipai_odoo_on_aca as private Marketplace offer for TBWA\\SMP; 90-day window to public transactable",
  "scores": {
    "program_fit": {"score": 5, "rationale": "Direct Microsoft programs: Partner Center Marketplace + ISV Success (both enrolled) + eligible for Co-sell Ready after publishing. Not just Founders-Hub-adjacent — this IS the GTM channel Microsoft wants partners on."},
    "evidence": {"score": 4, "rationale": "Named customer (TBWA\\SMP) in active pilot. Market evidence: docs/competitive/d365-marketplace-coverage.md §11 — zero Odoo-on-ACA competitors in 39 Odoo-search results. No prior transactable offers to benchmark conversion rate; hence 4 not 5."},
    "reversibility": {"score": 4, "rationale": "Private offer → listing-only → transactable is the doctrine-recommended sequence. Private offer can be withdrawn in <7 days. Transactable is harder to reverse (MS Learn: transactable → listing-only is IRREVERSIBLE); mitigated by staying listing-only during pilot."},
    "unit_economics": {"score": 4, "rationale": "Zero new engineering (infra exists). Marketplace certification cost = engineering hours only. TBWA pilot revenue covers first-year CAC by ~10x. Public transactable unit economics TBD — hence 4 not 5."},
    "sequencing": {"score": 5, "rationale": "All prerequisites live: Partner Center enrolled, ipai-odoo-mcp deployed, Odoo on ACA live, Entra ID auth canonical. Issue 29 already in backlog."},
    "regulatory_fit": {"score": 5, "rationale": "Private offer to TBWA (single tenant) minimizes data-residency and compliance surface. Marketplace publishing itself is doctrine-compliant."},
    "strategic_coherence": {"score": 5, "rationale": "Unlocks Co-sell Ready (next rung up the program ladder). Positions IPAI as the 'enterprise-grade managed Odoo on Azure' — the exact thin-delta-not-platform-clone thesis in docs/strategy/pulser-product-packaging.md."}
  },
  "composite": 32,
  "verdict": "clear_pass",
  "blocking_flags": [],
  "caveats": [
    "Do NOT convert to public transactable before pricing decision (Open Question 7) is resolved",
    "Legal entity for publishing (Open Question 5) must be confirmed before Create Offer"
  ],
  "recommendation": "proceed"
}
```

---

### Example 3 — CLEAR FAIL

**Action:** "Launch a paid LinkedIn advertising campaign ($15K/month) to drive cold outbound to D365 Finance users in SEA, pitching migration to Odoo + Pulser."

```json
{
  "action": "Launch $15K/mo LinkedIn paid ads to cold D365 Finance users in SEA",
  "scores": {
    "program_fit": {"score": 0, "rationale": "Zero Microsoft program funds this. $15K/mo comes straight from IPAI P&L."},
    "evidence": {"score": 1, "rationale": "No named customer asking for D365→Odoo migration. No pipeline evidence. Assumes a segment wants to migrate, which is contradicted by D365's high switching cost."},
    "reversibility": {"score": 3, "rationale": "Ads can be paused. But attribution + list-building leakage cannot be recovered. 30-day opt-out is standard."},
    "unit_economics": {"score": 1, "rationale": "LinkedIn cold outbound CPL in SEA for enterprise finance: $150-400. At 2% MQL→opportunity→close, CAC lands at $15K-40K per customer. IPAI Pack 1 ACV assumption unvalidated — if ACV is $12K/yr, LTV/CAC < 1x."},
    "sequencing": {"score": 2, "rationale": "IPAI doesn't have sales infrastructure to handle cold inbound (no AE team, no SDR). Creates qualification work without throughput capacity."},
    "regulatory_fit": {"score": 3, "rationale": "GDPR/DPA compliance OK on LinkedIn. Doctrine-neutral."},
    "strategic_coherence": {"score": 1, "rationale": "Violates Kira's 'only warm channels' principle. Contradicts docs/strategy/pulser-product-packaging.md §3 (no D365 displacement marketing; compete on thin deltas + PH moat instead)."}
  },
  "composite": 11,
  "verdict": "clear_fail",
  "blocking_flags": ["Program fit = 0 AND unit economics < 3 — unfunded AND unviable"],
  "caveats": [],
  "recommendation": "reject"
}
```

---

### Example 4 — BORDERLINE

**Action:** "Sponsor the Philippines Chamber of Commerce and Industry (PCCI) Finance Summit for $8,000 in Q3 2026, with IPAI founder keynote on BIR automation."

```json
{
  "action": "Sponsor PCCI Finance Summit Q3 2026 at $8K + founder keynote",
  "scores": {
    "program_fit": {"score": 1, "rationale": "Not funded by Microsoft programs directly. Not typical Microsoft co-sell motion. Could be positioned as part of Co-sell Ready activation if MS PH PDM is engaged."},
    "evidence": {"score": 3, "rationale": "PCCI membership overlaps with IPAI's target segment (PH CFO / Finance Controller). Conference evidence: historical 200-400 attendees from target companies. No specific named prospect, but concentration is real."},
    "reversibility": {"score": 4, "rationale": "$8K is a fixed cost; keynote prep is reusable content. Can decline next year cleanly."},
    "unit_economics": {"score": 3, "rationale": "Break-even needs ~0.7 Pack 1+4 closes ($12K each = $8.4K margin after direct costs). Historical keynote→pilot conversion is ~2-3 per 300 attendees = feasible. Moderate confidence."},
    "sequencing": {"score": 4, "rationale": "Prerequisites: one case study (TBWA\\SMP in progress), one working demo (Pulser Finance agent live). Both achievable by Q3. Some risk if TBWA pilot slips."},
    "regulatory_fit": {"score": 4, "rationale": "PH industry event; doctrine-neutral. Note: tax treatment of sponsorship expense is standard."},
    "strategic_coherence": {"score": 4, "rationale": "Warm channel, PH-native, validates Pack 4 (PH Compliance) thesis. Aligns with 'Finance Ops lead + Compliance moat' positioning."}
  },
  "composite": 23,
  "verdict": "borderline",
  "blocking_flags": [],
  "caveats": [
    "Contingent on TBWA\\SMP pilot closing a case study by Q3",
    "Engage MS PH PDM first — may co-fund 50% via Co-sell activation budget"
  ],
  "recommendation": "defer — reframe as co-funded with MS PH PDM; if MS co-funds 50%, upgrades to clear_pass"
}
```

---

### Example 5 — CLEAR FAIL (subtle — doctrine collision)

**Action:** "Add GitHub Actions CI for the `ipai_bir_tax_compliance` repo to run nightly BIR form regression tests before production deploys."

```json
{
  "action": "Add GitHub Actions CI for ipai_bir_tax_compliance nightly tests",
  "scores": {
    "program_fit": {"score": 2, "rationale": "GitHub Actions is part of the M365 ecosystem; indirectly aligned with GitHub MCP usage. But this isn't a GROWTH action."},
    "evidence": {"score": 3, "rationale": "CI/CD is good practice. But the evidence doesn't support GitHub Actions specifically vs Azure Pipelines."},
    "reversibility": {"score": 5, "rationale": "CI workflows can be deleted immediately."},
    "unit_economics": {"score": 3, "rationale": "Engineering hours; not a revenue / growth lever."},
    "sequencing": {"score": 3, "rationale": "IPAI already has .github/workflows for some CI; adding more is additive. But doctrine direction is opposite."},
    "regulatory_fit": {"score": 5, "rationale": "No regulatory issue."},
    "strategic_coherence": {"score": 0, "rationale": "CLAUDE.md §Engineering & Delivery Authority (REVISED 2026-04-14): 'Azure Pipelines is the sole CI/CD authority. GitHub Actions and Vercel are FORBIDDEN.' This proposal directly violates locked doctrine. Also: CI is an engineering decision, not a CGO decision — wrong persona owns this."}
  },
  "composite": 21,
  "verdict": "clear_fail",
  "blocking_flags": ["Regulatory_fit passed but strategic_coherence = 0 indicates doctrine violation — auto-block"],
  "caveats": ["This isn't a CGO decision; route to Rafi (Principal Engineer persona). Additionally, Azure Pipelines is canonical — use that, not GitHub Actions."],
  "recommendation": "reject + route to Principal Engineer; reframe as Azure Pipelines"
}
```

---

## 4. Usage pattern

```python
# Pseudocode — wire via Pulser agent or agents/skills/
from pulser.judge import GrowthDecisionJudge

judge = GrowthDecisionJudge.load("agents/judges/growth-decision-judge.md")
result = judge.score(
    action="Sponsor PCCI Finance Summit Q3 2026 at $8K + founder keynote",
    context={
        "stage": "traction",
        "active_packs": ["finance_ops", "ph_compliance"],
        "open_questions": ["MS PH PDM engaged?"]
    }
)
# result.composite → 23
# result.verdict → "borderline"
# result.recommendation → "defer — reframe as co-funded with MS PH PDM"
```

Kira (`agents/personas/growth-officer-persona.md`) runs every significant bet through this judge BEFORE committing. Judgments are logged to `ops.agent_run` (per `docs/architecture/data-model-erd.md`) for audit.

---

## 5. Related

- `agents/personas/growth-officer-persona.md` — Kira, who uses this judge
- `docs/research/ms-startups/knowledge-base.md` — primary grounding
- `docs/strategy/pulser-product-packaging.md` — the strategic frame
- `docs/competitive/d365-marketplace-coverage.md` — the market evidence source
- `CLAUDE.md` — doctrine the judge checks strategic_coherence against

---

*Judge locked 2026-04-15. 5 worked examples cover 2 clear-pass, 2 clear-fail (one subtle doctrine-violation), 1 borderline. Refresh when packaging strategy shifts or Microsoft program terms change.*
