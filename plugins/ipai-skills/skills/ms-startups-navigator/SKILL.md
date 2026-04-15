---
name: ms-startups-navigator
description: Given founder context (stage, revenue, tenant, product category), return the exact next 3 Microsoft for Startups actions with links, dollar value, and obligations. Use when the user asks about MS for Startups, Founders Hub, ISV Success, Co-sell, Azure Marketplace publishing, or M365 Agent 365 registration.
type: flexible
---

# MS for Startups Navigator

Reusable skill for routing founder questions into concrete Microsoft program actions, grounded in `docs/research/ms-startups/knowledge-base.md` + IPAI session memory.

---

## Decision tree — founder stage to applicable programs

```
Stage: IDEA (no revenue, no MVP)
  → Action 1: Sign up for Founders Hub at https://portal.startups.microsoft.com/signup
  → Action 2: Provision Azure subscription with billing (required to draw credits)
  → Action 3: Start Partner Center account (takes days; do early)

Stage: MVP (product built, pre-revenue or small revenue)
  → Action 1: Draw Founders Hub Azure credits; consume on build
  → Action 2: Apply for ISV Success (requires SaaS-product plan)
  → Action 3: Design Marketplace offer shape (listing-only vs transactable)

Stage: TRACTION (paying customers, >$10K ARR)
  → Action 1: Publish Marketplace offer (start listing-only or private)
  → Action 2: Pursue Co-sell Ready (requires transactable)
  → Action 3: Register Entra Agent ID for published agents (pre-2026-05-01)

Stage: SCALE ($500K+ ARR)
  → Action 1: Negotiate MACC with Microsoft via Co-sell Prioritized
  → Action 2: Expand Marketplace offer portfolio (private offers for specific enterprise deals)
  → Action 3: Consider Dynamics/AppSource if the product extends D365 (IPAI: no, Odoo)
```

---

## IPAI-specific routing (applied)

IPAI's current state (per `docs/research/ms-startups/knowledge-base.md §1`):
- Stage: TRACTION
- Partner Center: ENROLLED (MpnId 7097325)
- ISV Success: ENROLLED
- Founders Hub: UNCONFIRMED (portal signup status in Open Question 1)
- Marketplace: not yet publishing
- Entra Agent ID: 3 agents pending (Issue 13, deadline 2026-05-01)

**Next 3 actions for IPAI today:**
1. **Verify / complete Founders Hub portal signup** (Open Question 1). If already in, confirm tier + audit credit drawdown against `ipai-copilot-resource` + ACA consumption.
2. **Publish `ipai_odoo_on_aca` as private Marketplace offer** (Issue 29, P2). Start with private offer for TBWA\SMP; convert to public transactable later.
3. **Register Entra Agent ID** for pulser-finance, pulser-ops, pulser-research before 2026-05-01 (Issue 13, P1, deadline-driven).

---

## Copy-pasteable application templates

### Founders Hub portal signup (template message to MS)
```
Company: InsightPulse AI (IPAI)
Founders: [name + contact]
Country: Philippines
Product: Agentic operating copilot for Odoo-centered workflows
  (Pulser — custom-engine multi-agent, policy-gated enterprise copilot)
Stage: TRACTION — paying pilot customers (TBWA\SMP, W9 Studio, PrismaLab)
Azure footprint: ipai-copilot-resource (Foundry), pg-ipai-odoo (PG Flex),
  acae-ipai-dev-sea (ACA), docai-ipai-dev (Document Intelligence),
  srch-ipai-dev-sea (AI Search)
Partner Center: MpnId 7097325, ISV Success enrolled
Use case: $150K Azure credit capture to fund Pulser agent inference + Odoo runtime + Fabric mirror
```

### Marketplace offer draft (Issue 29 — `ipai_odoo_on_aca`)
```
Offer ID: ipai-odoo-on-aca
Offer alias: IPAI Odoo on ACA (private)
Publisher: InsightPulse AI (MpnId 7097325)
Offer type: Software as a Service (SaaS)
Listing type: Listing-only → Contact me (private offer first)
  [Convert to transactable after TBWA\SMP pilot closes]
Authentication: Microsoft Entra ID (one-click) — already canonical per CLAUDE.md Cross-Repo Invariant #2
Lead management: HTTPS endpoint → ipai-odoo-connector → crm.lead
```

### Entra Agent ID registration (Issue 13)
```
Agents to register by 2026-05-01:
  1. pulser-finance → id-ipai-agent-finance-close-dev + peers (ap-invoice, bank-recon, tax-guru, doc-intel)
  2. pulser-ops → id-ipai-agent-pulser-dev
  3. pulser-research → (new MI required OR reuse pulser-dev with separate SP)
Per-agent artifacts:
  spec/pulser-agent-365-registration/manifest-<agent>.json
Target catalog: IPAI tenant + TBWA tenant (dual registration for co-sell to TBWA users)
```

---

## Gotcha list (things MS docs don't say loudly)

1. **`foundershub.startups.microsoft.com` is gone** — canonical portal is `portal.startups.microsoft.com`. Don't document the old URL.
2. **$150K is a ceiling, not a grant** — tier-gated drawdown, most startups capture $1-25K initially.
3. **Transactable → listing-only is IRREVERSIBLE** — always start listing-only if pricing uncertain.
4. **ISV Success + Co-sell docs currently 404 on MS Learn** — get canonical URLs from Partner Center dashboard directly, not public search.
5. **Sponsored subscription blocks Claude on Foundry but NOT Founders Hub benefits** — don't conflate (per `project_foundry_anthropic_sponsorship_blocker`).
6. **Partner Center MFA mandatory since 2026-04-01** — routine access must use MFA-enabled session.
7. **Private offer speed >> public offer speed** — for TBWA-specific or strategic first customers, private offers avoid certification backlog.
8. **Agent 365 catalog requires distinct SP per agent** — not a shared-identity trick; each agent gets its own Entra service principal.
9. **PH is tagged geo, not excluded** — Microsoft for Startups accepts PH-registered companies; BIR treatment of credits is the open item.
10. **Co-sell Ready ≠ MACC eligibility immediately** — Co-sell Ready gates Microsoft seller engagement; MACC is a separate commercial track that typically requires minimum deal size + Co-sell Prioritized.

---

## Link-out map (canonical sources of truth)

| Topic | Canonical URL | Fallback |
|---|---|---|
| Microsoft for Startups program | https://www.microsoft.com/en-us/startups | Founders Hub portal |
| Founders Hub signup | https://portal.startups.microsoft.com/signup | Direct Azure enrollment |
| Partner Center | https://partner.microsoft.com/dashboard | — |
| Marketplace publisher guide | https://learn.microsoft.com/en-us/partner-center/marketplace-offers | Partner Center dashboard |
| ISV Success | UNKNOWN — doc moved; use Partner Center dashboard | MS PDM |
| Co-sell Ready | UNKNOWN — doc moved; use Partner Center dashboard | MS PDM |
| SaaS offer creation | https://learn.microsoft.com/en-us/partner-center/marketplace-offers/create-new-saas-offer | — |
| M365 Agent 365 / Entra Agent ID | Per `project_m365_e7_agent365` memory + MS DevBlogs | — |

---

## Trigger phrases for this skill

Invoke when the user says / asks about:
- "MS for Startups", "Microsoft for Startups", "Founders Hub"
- "ISV Success", "Co-sell", "Co-sell Ready", "MACC"
- "Azure Marketplace publish", "AppSource", "private offer"
- "Agent 365", "Entra Agent ID", "M365 E7"
- "Partner Center", "MpnId"
- "Azure credits", "$150K", "startup credits"

---

*Skill compiled 2026-04-15. Refresh when MS moves docs or IPAI enrollment state changes.*
