# Pulser for Odoo — Microsoft Marketplace Research Brief

**Prepared for:** InsightPulseAI / Dataverse IT Consultancy
**Context:** ISV Success enrolled 6 Apr 2026 · EM: So Yeong Choi · Publish target Aug–Sep 2026 · Benefit window closes 6 Apr 2027
**Prepared:** 18 Apr 2026 (T-150 days to publish target)

---

## Executive summary

- **Publish ONE thing first: Pulser as a transactable SaaS offer.** Odoo/Databricks/Managed Services are either ineligible, dilutive, or better as Consulting Service listings. Do not package four offers at publish.
- **Offer type is SaaS, not Managed App or Container.** Microsoft's Mar 2026 AI publishing guidance lands multitenant AI agents on SaaS. Managed App / Container only fit when customer data must stay in customer tenant.
- **Pricing: flat per-seat primary plan + metered overage dimension (hybrid).** FY26 ERP-AI benchmark is $18–$30/user/mo. Pulser's wedge is thin-layer-over-Odoo-$24.90, so price the AI at $19–$29/user/mo as a **bundle inclusive of Odoo hosting**, with metered overage only on AI-workflow volume. Per-seat is mandatory for M365-aligned procurement and for IP Co-sell telemetry.
- **IP Co-sell Ready is the real goal, not just Co-sell Ready.** IP Co-sell unlocks MACC burn-down, quota credit for Microsoft sellers, and tier-2+ Marketplace Rewards. Requires transactable + $100K TTM billed sales — but FY26 **App Accelerate** (public preview mid-2026) adds a nomination-based early access pathway that bypasses the $100K threshold for partners with MACC pipeline traction. Push So Yeong Choi to nominate you the moment the offer goes live.
- **The 12-month clock is the risk, not certification.** Certification is 2–4 weeks. The lost weeks are Partner Center tax profile (48h), SaaS fulfillment API build (4–8 weeks for a novice team), Entra ID SSO wiring (1–2 weeks), and the **co-sell doc pack** (one-pager + reference architecture + pitch deck + geo-keyed sales contacts). Start these at T-150.

---

## 1. Recommended offer structure

| Decision | Call | Rationale |
|---|---|---|
| **Offer type** | **SaaS** (transactable, through Microsoft) | Microsoft's Mar-2026 AI publishing flowchart lands multitenant AI agents hosted in publisher tenant on SaaS. Managed App requires customer-tenant deployment (ARM/Bicep templates, not your model). Container requires customer AKS (not your model). |
| **Hosting** | Publisher tenant (your ACA, Databricks, Foundry) | Keeps Odoo+Pulser runtime, Unity Catalog, and eval harness in your control. SaaS exempts you from shipping deployment assets. |
| **Billing model** | **Hybrid**: flat per-seat primary plan + metered dimension for AI-action overage | Marketplace supports flat, per-user, flat+metered. Per-user is mandatory for IP Co-sell telemetry and M365 procurement alignment. Metered dimension future-proofs for the agentic pricing shift (IDC: 70% of vendors off pure seats by 2028). Note: metered does NOT apply to the per-user model, so the hybrid is built as "Flat per tier + metered overage dimension." |
| **Pricing tiers (v1)** | **Starter $19/user/mo** (Odoo + Pulser assistant, 5 AI actions/user/day), **Pro $29/user/mo** (+ Analytics overlay, 50 actions/day), **Enterprise — private offer** (unlimited + governance). Metered: `$0.10 per AI action above plan`. Annual + monthly. 14-day free trial. | Sits under D365 BC Premium ($110) and SuiteAI-inclusive NetSuite ($999 platform + $99/user). Beats Copilot4Odoo perpetual ($107/module) on AI capability. Anchors below M365 Copilot $30 so AI+ERP bundle reads no-brainer. |
| **Transactable** | Yes — transactable through Microsoft | Required for IP Co-sell, MACC burn-down, Marketplace Rewards tier escalation, and App Accelerate early access. BYOL/free listings ineligible after 11 Jul 2023. |
| **Geographic plan** | Publish to all Microsoft-managed countries at launch (incl. SEA). PH entity files tax profile as publisher-managed country. | Microsoft processes billing and remits tax in Microsoft-managed countries; you owe only on your publisher-managed geos. Tax profile validation ~48h. |
| **Channel** | Enable **CSP resale** + **Multiparty Private Offers (MPO)** at publish | MPO lets a local SI/reseller co-sign private offers with you, invoice through Microsoft, both parties paid. Currently US/UK/CA only for MPO customers — PH customers use single-party private offers until MPO expands. |
| **Co-sell path** | **Co-sell Ready at publish → IP Co-sell via App Accelerate nomination within 90 days → IP Co-sell via $100K TTM as fallback** | Co-sell Ready is automatic once docs uploaded. IP Co-sell historically gated on $100K TTM billed sales; App Accelerate (Ignite 2025) opens nomination path considering MACC traction, pipeline, partner readiness — this is your fast lane. |

---

## 2. Packaging decision matrix

**Do not bundle all four layers into one marketplace listing.**

| Layer | Marketplace disposition | Publish sequence | Rationale |
|---|---|---|---|
| **1. Odoo on Cloud (managed ERP)** | **Do NOT list as standalone** | — | Odoo CE is GPL/LGPL — reselling hosted Odoo as a standalone marketplace product invites brand friction with Odoo SA. Bundle as runtime underneath Pulser SaaS. |
| **2. Pulser (AI workflow copilot on Odoo)** | **Transactable SaaS offer — PRIMARY listing** | **Wave 1: Aug–Sep 2026** | IP differentiator. All Co-sell motion attaches here. Listing sells "Pulser for Odoo — AI-assisted business operations" and silently bundles Odoo hosting. |
| **3. Analytics & Dashboards on Databricks** | **Add-on plan within Pulser offer** (Pro/Enterprise tiers), NOT separate offer | **Wave 1 (as tier)**; separate Power BI App listing **Wave 2: Q1 2027** | Separate offer splits billed-sales across SKUs, slowing Marketplace Rewards tier progression. Keep revenue concentrated. Spin out Analytics as Power BI App once Pulser is IP Co-sell eligible. |
| **4. Cloud Operations / Managed Services** | **Consulting Service offer** (free, non-transactable) | **Wave 1 companion listing: Aug 2026** | Lists services for Assessment, Briefing, Implementation, POC, Workshop. Free, fast approval, generates co-sell leads. Does NOT contribute to IP Co-sell revenue threshold but does generate Microsoft-seller-visible pipeline. |

**Why concentrate**: Marketplace Rewards and IP Co-sell eligibility tier on **company-level Marketplace Billed Sales TTM**. Splitting a $200K first-year pipeline across four offers yields four sub-$50K offers and no tier escalation. One $200K Pulser SaaS offer with a Consulting companion gets you to IP Co-sell ($100K TTM) inside year one.

---

## 3. Competitive positioning (FY26)

| Competitor | Core play | AI pricing | Where Pulser wins | Where Pulser loses |
|---|---|---|---|---|
| **Odoo Enterprise native AI** (Odoo 18.3+ AI App) | Built-in lead scoring, OCR, email draft, agent builder | Bundled in $24.90/user/mo | Multi-agent orchestration, maker-checker governance, policy-gated approvals, Unity Catalog lineage. Odoo native is single-agent DIY. | Distribution: Odoo.com funnel is huge. Pulser earns every meeting. |
| **D365 Business Central + Copilot** | First-party ERP + AI | Copilot bundled free from Oct 2025; BC $80–$110/user/mo | PH SMB TCO: Pulser @ $19–$29 bundled includes ERP; BC @ $80+ needs Copilot Studio add-ons. Odoo CE 18 module depth outpaces BC on several SMB verticals. | In-tenant-data story + Microsoft-native motion. BC wins any deal where "Microsoft-native" is the criterion. |
| **SAP B1 + Joule** | Enterprise ERP + usage-priced AI | Seat + usage-based AI; non-transparent | Price, implementation speed (Odoo 2–4 mo vs SAP 12–24), SMB fit. | Enterprise brand trust in regulated verticals. |
| **NetSuite + SuiteAI** | Cloud ERP + bundled AI | ~$999/mo platform + $99/user; AI bundled | PH SMB list pricing (NetSuite minimum ~$1.2K/mo), agentic + governed workflow story. | Oracle's enterprise reach in PH BPO/finance. |
| **Copilot4Odoo / Bistasolutions / OCA copilots** | Third-party AI modules on Odoo | $107/module perpetual or $1,399 Complete Pack | Azure-native runtime, policy-gated governance, multi-agent orchestration, Microsoft Marketplace distribution, Entra SSO. Community copilots are single-model chat wrappers. | Odoo-marketplace discoverability. |

**Hero line for listing page**: *"Pulser is the only AI operating copilot for Odoo with policy-gated, auditable, multi-agent workflows — purpose-built for marketing ops, media ops, retail ops, and finance ops, delivered through Microsoft Marketplace with MACC burn-down."*

**2x2 positioning**: X = ERP breadth (Odoo-specific → multi-ERP) · Y = AI depth (chat assistant → governed agentic workflow). Pulser occupies *Odoo-specific × governed-agentic* — nobody else is there. Moveworks = multi-ERP × agentic; D365 Copilot = D365-specific × agentic; Copilot4Odoo = Odoo-specific × chat-assistant.

---

## 4. 60-day action plan (18 Apr 2026 → 17 Jun 2026)

**Week 1–2 (18 Apr – 1 May): Foundation**
- File Partner Center tax profile (PH entity). 48h validation. Day-1 action — blocks everything.
- Book **Marketplace Publish Consult** technical enablement for Week 4 — come with offer type/pricing decided.
- Book **D&P (Design & Practice)** for Week 3 — SaaS fulfillment API architecture review.
- Draft SaaS offer spec bundle: offer type, plans, metered dimension schema, Entra SSO flow, landing URL.
- Stand up separate dev subscription (Sponsorship `eba824fb`) for marketplace dev: landing page, webhook listener, stage fulfillment impl.

**Week 3–4 (2 May – 15 May): Build**
- Implement SaaS fulfillment API flows on ACA: landing, activation, update, suspend/reinstate, webhook. Compress with Microsoft sample SDK (`Ercenk/Microsoft-commercial-marketplace-transactable-SaaS-offer-SDK`).
- Entra ID SSO on landing (MSA + Entra both required).
- D&P session: validate architecture + code review on fulfillment.
- Start pre-publish content: one blog every 2 weeks until publish (6 posts).

**Week 5–6 (16 May – 29 May): Co-sell doc pack**
- One-pager (A4, value prop + use cases + pricing + support + MACC-eligible callout).
- Reference architecture diagram (ACA + Databricks + Foundry + Odoo + Entra + Key Vault + managed identity).
- Pitch deck (10–12 slides, Microsoft-seller-facing, battlecard format).
- Geo sales contacts per region.
- **Marketplace Publish Consult** — come with draft listing + pricing + offer structure for review.

**Week 7–8 (30 May – 12 Jun): Preview publish + cert**
- Submit in Preview to exercise full certification (~2–4 weeks). Catches issues before Aug go-live.
- **Architecture Design Review** Week 8 — scale/multitenant isolation, Unity Catalog row-level security per customer tenant, Foundry prompt injection mitigations, Content Safety.
- Demo video v1 (90–120s: Odoo workflow → Pulser agent → maker-checker approval → outcome). Captions mandatory.

**Week 9 (13 – 17 Jun): GTM prep**
- Finalize listing (outcome-led hero, 3 use-case bullets, MACC-eligible + Azure-native badges, integrations list).
- LinkedIn teaser campaign: founder + 2 team members, 1 post/week on Odoo + AI + governance.
- Line up 3 design-partner LOIs for case-study generation at publish.
- Book **Architecture Review** (4th enablement slot) for July, post-preview cert — security/compliance/go-live readiness.

**Benefit activation sequence** (the critical sequencing question):
1. **D&P** early (Week 3) — architectural decisions
2. **Marketplace Publish Consult** mid (Week 6) — listing + pricing + offer structure sign-off
3. **Architecture Design Review** before Preview submit (Week 8) — production readiness
4. **Architecture Review** after Preview cert (July) — security/compliance/scale/go-live

Do NOT save any session for "after publish" — they're sharpest with decisions to make, not retrospectives.

**Azure credit deployment** (Sponsorship sub): dev/stage marketplace tenant (fulfillment API, landing, webhook) · reference demo environment for sales + CIX walkthroughs · eval harness for agent safety/accuracy telemetry. Keep production customer subs separate.

---

## 5. Publish-to-revenue plan (Aug 2026 → end-CY26)

| Phase | Focus | Targets |
|---|---|---|
| **T+0 (Aug–Sep): Publish** | Go live. Auto Co-sell Ready once docs uploaded. Consulting companion listing same week. Announce: LinkedIn, blog, PH tech press (BusinessWorld, Philstar Tech), Microsoft community hub partner digest. Kickoff 3 design-partner private offers at discount for case studies. | Listing live · 3 private offers signed |
| **T+30 (Sep–Oct): Co-sell activation** | Submit App Accelerate early-access nomination via So Yeong Choi. Surface any MACC-pipeline traction. First "Pulser for Odoo" webinar co-marketed with MS Philippines. First customer case study published. | App Accelerate nomination submitted · 1 webinar · 1 case study |
| **T+60 (Oct–Nov): Pipeline build** | 15 qualified leads, 5 in active eval, 2 signed. At $19–29/seat × 30 seats × 3 = ~$2K MRR floor. Upload sales contacts to Partner Center; attend MSAPAC ISV briefings. Second webinar, second case study. MPO with first PH channel partner (if MPO expands to APAC, else single-party private offers). | 2 signed customers · Microsoft-seller-visible |
| **T+90 (Nov–Dec): First reference** | Formalize one customer as Microsoft-published case study — single strongest accelerant to co-sell seller adoption. $15–25K TTM run rate (on track to $100K by Apr 2027). Submit Marketplace Rewards tier progression check at $10K TTM. | 1 MS-published case · 1st Rewards tier unlocked |
| **T+120 (Dec 2026): Year-end close** | CY26 goal: 5 customers, $50–75K TTM billed, 1 published case, App Accelerate accepted or clear path to $100K. Begin Analytics Power BI App Wave 2 prep (Q1 2027). | 5 customers · IP Co-sell pathway confirmed |

**Microsoft "sales-ready" assets** (produce all by T+30):
- One-pager (required for co-sell doc pack)
- Pitch deck (required)
- Battlecard vs D365 BC, NetSuite, SAP B1, Odoo Enterprise native AI
- ROI calculator (inputs: seats, AI-actions/mo, ERP baseline cost → savings from agentic automation + MACC burn-down)
- CIX-style demo environment (pre-loaded Odoo tenant, invitable by Microsoft sellers). *Kitameraki's 200% trial growth came from making themselves trivially easy for Microsoft sellers to showcase.*

---

## 6. Top 5 risks with mitigations

| # | Risk | Prob | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **SaaS fulfillment API build overruns** the 12-month benefit clock | High | High | Use `Ercenk/Microsoft-commercial-marketplace-transactable-SaaS-offer-SDK` as scaffolding. v1 = 2 plans (Starter+Pro) + 1 metered dim. Defer private offers, MPO, CSP config to v1.1. Book D&P session on fulfillment impl specifically. |
| 2 | **Odoo GPL/AGPL licensing friction** with reselling Odoo through Marketplace | Med | High | Publish Pulser as the marketplace product (not "Odoo hosting"). Bundle Odoo as included runtime, not itemized. OCA modules stay LGPL-3/AGPL-3 per their terms; your `ipai_*` delta is your IP. PH legal counsel review before publish. |
| 3 | **Geographic/tax profile constraint** limits transact in PH or target APAC | Med | Med | PH files as Publisher-managed (you handle PH tax); MS-managed (US/EU/SG/AU/JP) handled for you. Confirm Singapore and Australia are MS-managed before go-live — primary APAC targets. |
| 4 | **Pricing mismatch** — metered too aggressive scares SMBs; flat too generous starves revenue | Med | Med | Launch Starter $19 / Pro $29 / Ent private. Metered overage $0.10/AI-action is safety valve, not primary revenue. Review monthly for first 6 months; adjust in v1.1 after 10+ signed customers. Do NOT bundle AI-actions unlimited — that's how margin dies when an agentic workload loops. |
| 5 | **Microsoft seller attention is finite**; without App Accelerate or customer reference, you're invisible | High | High | (a) Push So Yeong Choi for App Accelerate nomination at T+30. (b) Pre-commit 3 design-partner LOIs before publish so case study #1 lands T+60. (c) Attend MSAPAC ISV Success enablement monthly — name-level APAC seller relationships is the differentiator vs 10,000 other listings. |

---

## 7. Sources (selected — full list in research transcript)

**Microsoft official**
- [Plan a SaaS offer for Microsoft Marketplace](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/plan-saas-offer)
- [Publishing guidance for AI apps and agents on Microsoft Marketplace (11 Mar 2026)](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/artificial-intelligence-app-agent-publishing-guidance)
- [ISV Success program](https://www.microsoft.com/en-us/software-development-companies/offers-benefits/isv-success)
- [Co-sell requirements — Partner Center](https://learn.microsoft.com/en-us/partner-center/referrals/co-sell-requirements)
- [Azure IP Co-Sell Acceleration](https://learn.microsoft.com/en-us/microsoft-for-startups/benefits/azure-ipcs)
- [Marketplace Rewards](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/marketplace-rewards)
- [MACC FAQ](https://learn.microsoft.com/en-us/marketplace/macc-frequently-asked-questions)
- [Multiparty private offers for ISVs](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/multiparty-private-offers-for-isvs)
- [Ignite 2025: Drive the next era of software innovation with AI](https://techcommunity.microsoft.com/blog/Marketplace-Blog/ignite-2025-drive-the-next-era-of-software-innovation-with-ai/4470130)

**Case study reference**
- [Kitameraki case study — Microsoft Partner](https://partner.microsoft.com/en-us/case-studies/kitameraki-rewards)
- [How we increased trials 200% with Marketplace Rewards](https://techcommunity.microsoft.com/discussions/marketplace-forum/how-we-increased-trials-200-with-marketplace-rewards/4373476)

**Pricing / competitive (FY26)**
- [Microsoft 365 Copilot pricing](https://www.microsoft.com/en-us/microsoft-365-copilot/pricing)
- [Dynamics 365 Business Central pricing 2026](https://costbench.com/software/erp/microsoft-dynamics-365-business-central/)
- [Odoo AI Modules: Full Feature List and Pricing 2026](https://www.braincuber.com/blog/odoo-ai-modules-full-feature-list-and-pricing)
- [The 2026 Guide to SaaS, AI, and Agentic Pricing Models — Monetizely](https://www.getmonetizely.com/blogs/the-2026-guide-to-saas-ai-and-agentic-pricing-models)

**Regional**
- [Odoo Official Partner for Philippines](https://www.odoo.com/partners/country/philippines-171)
- [The State of Odoo ERP Adoption 2026](https://resident.com/resource-guide/2026/03/24/the-state-of-odoo-erp-adoption-2026-trends-roi-benchmarks-and-sector-specific-results)

---

## Cross-references (IPAI repo)

- `docs/architecture/` — existing reference architecture assets → co-sell diagram
- `ssot/` — platform authority matrix, integration adoption rules → listing disclosures
- `spec/` — location for the SaaS offer spec bundle (create `spec/marketplace-saas-offer/`)
- `docs/gtm/marketplace_offer_draft.json` — existing draft, reconcile with this brief
