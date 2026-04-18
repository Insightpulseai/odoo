# Tasks: Microsoft Marketplace GTM (Wave 1)

> Source of truth for actual execution status. Reconciled against Partner Center
> reality as of 2026-04-18. Aspirational checkmarks removed.
> Full research brief: `docs/gtm/marketplace_research_brief.md`.

Legend: `[ ]` = not done · `[~]` = in progress · `[x]` = done + verified

---

## EPIC 1 — ISV Success Enrollment and Benefit Activation

### 1.1 Program onboarding
- [x] Enrolled in ISV Success (2026-04-06, confirmed via Partner Center)
- [x] Orientation call held with EM So Yeong Choi (2026-04-13)
- [x] Business summary + application info replied (2026-04-17)
- [ ] Support ticket **2604130030000838** resolved (Azure Sponsorship mobile-number block)

### 1.2 Benefit redemption
- [x] GitHub Enterprise coupon `ISV-Success-Program-12months-570064f` redeemed (20 seats)
- [x] Azure bulk credit active ($5,000 to admin@insightpulseai.com, expires 2027-04-30)
- [x] Visual Studio Enterprise × 25 assigned (1/25 — Jake only; 24 unassigned)
- [ ] Assign remaining 24 VS Enterprise seats to team before benefit lapses
- [ ] **Redeem M365 E5 Developer × 25** — status "Unknown"; needs activation on fresh sandbox tenant
- [ ] **Redeem D365 Partner Sandbox × 25** (Sales/Field/CS) — status "Not Redeemed"
- [ ] **Redeem D365 discounted/free × 25** — status "Unknown"

### 1.3 Technical enablement sessions (one-shot, expire 2027-04-30)
- [ ] **Application Architecture Design Session (ADS)** — book for Week 3 (w/c 2 May)
- [ ] **Application Publishing Consultation** — book for Week 6 (w/c 23 May)
- [ ] **Application Design Review (ADR)** — book for Week 8 (post-Preview cert)
- [x] Azure Standard Support Plan active (unlimited incidents)

### 1.4 Partner Center hygiene
- [ ] **Add marketing contacts (up to 3)** — blocks all marketing benefit activation
- [x] Partner Center verified account, MpnId 7097325
- [ ] Tax profile validated for PH publisher entity
- [ ] Decision: PSCB ($925/yr) purchase — value-captures on Power BI Premium × 15

---

## EPIC 2 — Transactable SaaS Offer Engineering

### 2.1 Offer structure decisions (per research brief)
- [x] Offer type locked: **SaaS** (transactable through Microsoft)
- [x] Pricing model locked: **Hybrid** (flat per-seat + metered overage)
- [x] Tiers defined: Starter $19, Pro $29, Enterprise private · $0.10/AI-action overage
- [x] Packaging call: single primary Pulser SaaS offer + Consulting Service companion
- [ ] Scope out of Wave 1: Teams integration (deferred to Wave 2 M365 agent)
- [ ] Scope out of Wave 1: Analytics separate listing (deferred to Wave 3 Power BI App)

### 2.2 SaaS fulfillment API implementation
- [ ] Scaffold fulfillment API on ACA (subscribe/activate/update/suspend/reinstate/webhook)
- [ ] Entra ID SSO on landing page (MSA + Entra, both required)
- [ ] Webhook listener (marketplace event → Odoo tenant provisioning)
- [ ] Metered billing client (emit usage event per AI-action overage)
- [ ] Use `Ercenk/Microsoft-commercial-marketplace-transactable-SaaS-offer-SDK` as scaffolding reference
- [ ] Stand up dev/stage on Sub B `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` (separate from production `eba824fb`)

### 2.3 Odoo tenant provisioning
- [ ] Multi-tenant Odoo provisioning stamp (per-customer `odoo_<tenant_id>` DB)
- [ ] Entra ID SSO passthrough to Odoo (native Odoo OIDC)
- [ ] Row-level security in Unity Catalog per customer tenant
- [ ] Content Safety integration for Pulser agent I/O per customer

### 2.4 Certification prep
- [ ] Defender for Cloud enabled on Sub A (posture gate for cert)
- [ ] Defender for Cloud enabled on Sub B
- [ ] Azure AD policy review pass (conditional access on admin endpoints)
- [ ] Secret scanning clean (current blocker: commit `9b6b09c35` pending scrub)

---

## EPIC 3 — Co-sell Readiness

### 3.1 Doc pack (required for automatic Co-sell Ready badge at publish)
- [ ] One-pager (A4, value prop + use cases + MACC-eligible callout)
- [ ] Reference architecture diagram (ACA + Databricks + Foundry + Odoo + Entra + KV)
- [ ] Pitch deck (10-12 slides, seller-facing, battlecard format)
- [ ] Geo sales contacts per region (APAC lead = founder)
- [ ] ROI calculator (seats × AI-actions × baseline cost → savings + MACC burn-down)

### 3.2 Design partner LOIs (for case studies at T+60 post-publish)
- [ ] Identify 3 design-partner candidates
- [ ] Draft discounted private offer template
- [ ] Secure 3 LOIs before publish (to accelerate case-study generation)

### 3.3 IP Co-sell path
- [ ] Apply for **App Accelerate** early-access nomination at T+30 post-publish
- [ ] Fallback: track toward $100K TTM billed sales by 2027-04-06 for revenue-path qualification

---

## EPIC 4 — Marketplace Listing Content

### 4.1 Listing copy
- [ ] Hero statement (outcome-led, not tech-led)
- [ ] 3 use-case bullets (finance ops / media ops / retail ops)
- [ ] Integrations list (Azure AI Foundry, Databricks, Power BI, Odoo, Entra, Key Vault)
- [ ] Badges: MACC-eligible, Azure-native, Data & AI solution area
- [ ] Listing page hero line: "Pulser is the only AI operating copilot for Odoo with policy-gated, auditable, multi-agent workflows"

### 4.2 Demo video (v1)
- [ ] Record 90-120s demo (Odoo workflow → Pulser agent → maker-checker approval → outcome)
- [ ] Captions mandatory (accessibility + listing SEO)
- [ ] Upload to marketplace offer preview

### 4.3 Screenshots
- [ ] Odoo AP workflow with Pulser overlay
- [ ] Databricks Analytics dashboard
- [ ] Power BI embedded report
- [ ] Foundry agent eval dashboard
- [ ] Content Safety policy board

### 4.4 CIX-style demo environment
- [ ] Preloaded Odoo tenant with PH scenarios
- [ ] Pulser agents activated with safe-mode policies
- [ ] Invitable by Microsoft sellers (AAD guest access)
- [ ] 2-minute startup time (cache warm)

---

## EPIC 5 — Publish and Post-Launch

### 5.1 Preview submission (T-60 — mid-Jun 2026)
- [ ] Submit offer in Preview (not live) to exercise certification cycle
- [ ] Cert expected 2-4 weeks

### 5.2 Go-live (T-0 — Aug-Sep 2026)
- [ ] Flip offer to public
- [ ] Announce: LinkedIn, blog, PH tech press (BusinessWorld, Philstar Tech)
- [ ] Submit to Microsoft community hub April partner digest
- [ ] Kickoff 3 design-partner private offers

### 5.3 T+30 (Sep-Oct)
- [ ] App Accelerate nomination submitted to So Yeong Choi
- [ ] First webinar with Microsoft PH
- [ ] First customer case study published

### 5.4 T+90 target
- [ ] 5 customers signed
- [ ] $15K+ TTM run rate
- [ ] Microsoft-published case study
- [ ] First Marketplace Rewards tier unlocked

---

## Dependencies

- `spec/m365-declarative-agent/` (Wave 2) — surface-layer companion, Q4 2026
- `spec/finops-hub/` (infra) — Phase 0 tag governance unblocks per-tenant cost allocation on demo environments
- `.claude/agents/upstream/` — `azure-saas-architect` + `azure-principal-architect` for SaaS architecture review
- `docs/gtm/marketplace_research_brief.md` — decision rationale

---

*Last reconciled: 2026-04-18 against Partner Center state. Future updates must be evidence-backed (Partner Center screenshot, CLI output, or committed artifact).*
