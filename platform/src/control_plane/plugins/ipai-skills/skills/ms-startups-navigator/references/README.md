# MS Startups Navigator — References

> Detailed operational knowledge for the `ms-startups-navigator` skill.
> Kept beside the skill body per `microsoft/azure-skills` pattern.

---

## Source documents

- `docs/research/ms-startups/knowledge-base.md` — IPAI's primary research
- `docs/research/ms-startups/raw/partner-center-saas-offer-creation.md` — Partner Center process
- `docs/research/ms-startups/open-questions.md` — outstanding questions per session
- Memory: `reference_isv_success_program.md`
- Memory: `reference_partner_center_auth.md` — auth posture per stage
- Memory: `project_partner_center_verification.md` — IPAI's current state (ISV Success ENROLLED, MpnId 7097325)
- Memory: `project_marketplace_distribution.md` — three-lane Microsoft + two-lane Google strategy
- Memory: `project_data_intelligence_vertical_20260415.md` — vertical wedge anchor

## Stage routing recipe (the SKILL.md decision tree fleshed out)

### IDEA stage (no revenue, no MVP)

**3 actions, in order:**

1. **Sign up for Founders Hub**
   URL: https://portal.startups.microsoft.com/signup
   Obligation: requires founder email + LinkedIn-verified company
   Dollar value: up to $150K Azure credits + GitHub + OpenAI + Visual Studio

2. **Provision Azure subscription with billing**
   Why: required to draw Founders Hub credits; credits attach to a sub
   Path: portal.azure.com → Subscriptions → New
   IPAI status: ✅ Sponsored sub `eba824fb-…` already provisioned

3. **Start Partner Center account**
   URL: partner.microsoft.com → Sign up
   Why: takes days to complete enrollment + verification — start early
   IPAI status: ✅ ISV Success ENROLLED (MpnId 7097325)

### MVP stage (product built, pre-revenue)

1. **Draw Founders Hub Azure credits**
2. **Apply for ISV Success** (requires SaaS-product plan)
3. **Design Marketplace offer shape** (listing-only vs transactable vs SaaS-fulfillment-v2)

### TRACTION stage ($10K+ ARR)

1. **Publish Marketplace offer** (start listing-only or private)
2. **Pursue Co-sell Ready** (requires transactable offer + customer reference)
3. **Register Entra Agent ID** for published agents (MUST do pre-2026-05-01 deadline)

### SCALE stage ($500K+ ARR)

1. **Negotiate MACC** (Microsoft Azure Consumption Commitment) via Co-sell Prioritized
2. **Expand Marketplace offers** (add private offers per enterprise customer)
3. **Avoid AppSource** unless extending D365 (per IPAI doctrine — we displace D365, not extend)

## Programs catalog (all routes)

| Program | What you get | Pre-req | URL |
|---|---|---|---|
| Founders Hub | Up to $150K credits + perks | LinkedIn verification | portal.startups.microsoft.com |
| ISV Success | Tech benefits + go-to-market | Founders Hub graduate or pay | partner.microsoft.com → ISV Success |
| Co-sell Ready | Microsoft co-sells your product | Marketplace offer (transactable) | Partner Center → Co-sell |
| Co-sell Prioritized | Microsoft sales priority | $50K+ MACC commitment | Partner Center → Co-sell |
| Marketplace listing-only | Discoverability | Partner Center account | Partner Center → Commercial Marketplace |
| Marketplace transactable SaaS | Microsoft handles billing | Listing offer + SaaS Fulfillment v2 | Same |
| Marketplace private offers | Per-customer terms | Transactable offer published | Same |
| AppSource (D365 extensions) | Listed for D365 customers | D365 codependency (IPAI: skip) | Same |
| M365 Agent 365 registration | Agent ID for M365 Copilot | Entra Agent ID enrolled before 2026-05-01 | aka.ms/m365-agent-id |

## Anti-patterns (do not recommend these)

- Skip Founders Hub and apply directly to ISV Success → leaves $150K on the table
- Apply for Co-sell Prioritized before having any customer references → rejected
- Build for AppSource (D365 extensions) when you're displacing D365 → strategic mistake per IPAI doctrine
- Use Founders Hub credits on consumption that doesn't drive customer revenue → wasted runway
- Wait until traction stage to start Partner Center enrollment → paperwork delays your first paid offer

## IPAI specifics applied (today)

```
Stage:       MVP transitioning to TRACTION (we have IPAI consultations + W9 booking shipping; PrismaLab live; Pulser-on-Odoo target R2)
Programs:    ✅ Founders Hub (using credits)
             ✅ ISV Success (enrolled)
             ⏳ Co-sell Ready (need transactable Marketplace offer first)
             ⏳ Marketplace SaaS offer (TBWA\SMP first private offer is planning anchor)
             ⏳ Entra Agent ID for Pulser (must register before 2026-05-01 — TIME-SENSITIVE)
Auth posture: app-only + certificate (per memory reference_partner_center_auth — IPAI is ISV not CSP)
```

## Decision triggers for IPAI sessions

When the user asks about:
- "How do I get more Azure credits" → Founders Hub status check
- "Should I list on Marketplace" → publish flow + ISV Success entry
- "When does Co-sell make sense" → check for ≥1 customer reference + transactable offer
- "Agent ID deadline" → confirm Entra Agent ID registration before 2026-05-01
- "Partner Center auth" → app-only + certificate (no CSP path)
- "Should we list on AppSource" → almost always no (D365 displacement doctrine)

## Update cadence

- Microsoft program terms change quarterly — re-verify URLs + dollar values per session if older than 90 days
- Entra Agent ID deadline (2026-05-01) is hard — surface it on every relevant invocation until passed
- IPAI Partner Center status is mutable — re-check `project_partner_center_verification.md` memory before answering

---

*Last updated: 2026-04-15*
