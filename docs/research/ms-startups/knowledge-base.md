# Microsoft for Startups — IPAI Knowledge Base

> Program catalog + lifecycle map + dependency graph + $ inventory + PH notes.
> Sources: raw captures in `docs/research/ms-startups/raw/` + IPAI session memory
> (`project_partner_center_verification`, `reference_isv_success_program`,
> `project_marketplace_distribution`, `project_m365_e7_agent365`).
> Compiled 2026-04-15.

---

## 0. Program catalog

| Program | What it is | Max $ value | Eligibility (key) | Obligations | IPAI status |
|---|---|---|---|---|---|
| **Microsoft for Startups Founders Hub** | Entry-level benefits for early-stage founders | Up to **$150,000 Azure credits** (tier-gated); plus OpenAI credits, GitHub, M365 seats | Must be building a software product; private company; pre-IPO; VC-backed preferred but not required | Report Azure consumption; maintain active portal; complete tier-advancement milestones | ENROLL — not yet (portal signup needed) |
| **ISV Success** | Accelerator for publishing SaaS to Azure Marketplace | Azure credits + engineering assistance + GTM benefits (specific $ UNKNOWN — MS moved docs) | Must be publishing to Microsoft Marketplace OR Business Applications platform | Publish offer within program term; engage with MS engineering reviews | **ENROLLED** (per memory) — MpnId 7097325 |
| **Co-sell Ready / Co-sell Prioritized** | Access to Microsoft seller channel for co-selling | Revenue share with Microsoft sellers; MACC (Microsoft Azure Consumption Commit) eligibility | Transactable Marketplace offer; solution claim submitted; Microsoft seller enablement complete | Engagement templates maintained; Microsoft seller enablement delivered; minimum deal size targets | Pending (post-Marketplace listing) |
| **Azure Marketplace** | Transactable commerce surface | N/A (revenue channel) | Partner Center enrolled; SaaS / VM / Container / Managed App / Private Offer | Microsoft commission on transactable offers (standard ~3-20% depending on offer type); certification per offer | Eligible; not yet publishing (Issue 29) |
| **M365 Agents / Agent 365** | M365 Copilot agent catalog | N/A (distribution surface) | Entra Agent ID registered per agent; M365 E7 context | Register via Entra; reassign permissions post-publish | Agent IDs visible on IPAI tenant today (per memory); 3 agents to register by 2026-05-01 (Issue 13) |
| **Partner Center** | Umbrella workspace for all above | N/A (platform) | Legal entity verified; MPN ID; identity verification | Keep profile current; meet program-specific requirements | **ENROLLED** (MpnId 7097325) |
| **AppSource / Dynamics 365 Marketplace** | D365-specific extension catalog | N/A | D365-compatible extension | Similar to Azure Marketplace | Not IPAI target (Odoo, not D365) |

---

## 1. Lifecycle map — which programs apply when

```
IDEA           Founders Hub signup (portal) — no revenue required
  ↓
MVP            Founders Hub benefits active (Azure credits)
               + start Azure Marketplace listing prep
  ↓
TRACTION       ISV Success ENROLL (already done for IPAI)
               + publish transactable Marketplace offer
               + pursue Co-sell Ready (requires transactable)
  ↓
SCALE          Co-sell Prioritized (higher MACC engagement)
               + AppSource/Dynamics marketplace if applicable
               + Agent 365 catalog listing (post-E7 GA)
  ↓
EXIT           M&A channel through Microsoft partnerships (not program-gated)
```

**IPAI current position:** TRACTION — ISV Success enrolled, Marketplace publishing pending (Issue 29), Co-sell Ready downstream.

---

## 2. Dependency graph — what blocks what

```
Partner Center account
  └── ISV Success enrollment
        └── Marketplace publishing (listing-only OR transactable)
              └── Co-sell Ready (requires transactable offer)
                    └── Co-sell Prioritized (requires Co-sell Ready)
                          └── MACC deals (requires Co-sell Prioritized)

Azure subscription (paid, billing method)
  └── Founders Hub benefits usage (Azure credits)

M365 tenant
  └── Entra Agent ID registration
        └── Agent 365 catalog publish (post-E7 GA 2026-05-01)
```

**IPAI dependency state (verified 2026-04-15):**
- Partner Center: ✓ enrolled
- ISV Success: ✓ enrolled
- Marketplace publishing: ✗ not yet (Issue 29)
- Co-sell Ready: ✗ blocked on Marketplace publishing
- Founders Hub: ✗ portal signup not completed (UNKNOWN why — check `project_partner_center_verification`)
- Entra Agent ID: ⚡ visible on tenant; 3 agents not yet registered (Issue 13)

---

## 3. Dollar-value inventory (stackable benefits a founder can capture)

| Benefit | Ceiling (USD) | Conditions | IPAI capture path |
|---|---|---|---|
| Azure credits (Founders Hub) | **$150,000** | Tier-gated; typically earned across 12-24 months | Sign up Founders Hub portal |
| OpenAI API credits (via Founders Hub) | UNKNOWN (previously ~$2,500) | Active portal + AI use case | Same |
| GitHub Enterprise | UNKNOWN (previously ~$6,600) | Portal enrollment | Same |
| M365 E5 seats | UNKNOWN (typically 5 seats, time-limited) | Portal enrollment | Already on IPAI tenant |
| LinkedIn Sales Navigator (previously included) | UNKNOWN | Portal enrollment | Not currently used |
| Perplexity Pro (previously included) | UNKNOWN | Portal enrollment | Not currently used |
| ISV Success cloud credits | UNKNOWN | Program active | ENROLLED — UNKNOWN credit redemption status |
| ISV Success engineering assistance | N/A (non-monetary) | Program active | ENROLLED |

**Stackable ceiling (conservative estimate, PH-eligible):** ~$150K Azure + ancillary ~$15-20K (GitHub + OpenAI + tools) over 24 months = **~$165K-170K USD**. Exact amounts require live Founders Hub tier verification.

---

## 4. Obligation inventory

| Obligation | Trigger | IPAI action |
|---|---|---|
| Partner Center profile current | Ongoing | Keep tenant + legal entity info updated |
| MFA / security requirements | 2026-04-01 onwards (per memory) | Already compliant per `reference_partner_center_auth` |
| Marketplace certification pass | Per-offer | Plan for Issue 29 |
| Co-sell engagement templates | Post-Co-sell Ready | Future |
| Microsoft seller enablement | Post-Co-sell Ready | Future |
| Annual ISV Success milestone reviews | Yearly | UNKNOWN — check enrollment anniversary |
| Entra Agent ID reassignment post-publish | Per registered agent | Plan for Issue 13 |

---

## 5. Philippines / SEA specifics

| Item | Status |
|---|---|
| PH is a tagged geo on microsoft.com/startups | ✓ (no country exclusion) |
| Founders Hub open to PH-registered companies | ✓ (standard commercial geos) |
| ISV Success open to PH | ✓ (IPAI is enrolled) |
| Azure credits redeemable on PH-billed subscriptions | ✓ (via PAYG sub) |
| BIR invoicing requirements for Microsoft-issued credits | UNKNOWN — check with PH legal (`ipai_bir_tax_compliance` relevant) |
| Co-sell to PH customers via local Microsoft PH seller team | ✓ (standard) |
| MACC eligibility for PH enterprise customers (TBWA\SMP) | ✓ (standard MACC applies) |
| PH-specific Marketplace offer currency | USD preferred; PHP UNKNOWN |

---

## 6. Contradictions / gotchas

1. **`foundershub.startups.microsoft.com` redirects to `portal.startups.microsoft.com`** — URL drift; canonical portal is portal.startups.microsoft.com as of 2026-04-15. Update any documented links.
2. **ISV Success + Co-sell docs returning 404 on Microsoft Learn** — Microsoft moved/restructured docs; refresh the canonical URLs via Partner Center dashboard, not search.
3. **$150K headline number is a ceiling, not a guaranteed grant** — tier-gated; most startups capture $1K-$25K initially, then advance.
4. **Transactable → listing-only is irreversible** — create listing-only first if pricing uncertain; promote to transactable later (Issue 29 path).
5. **Partner Center MFA enforcement (2026-04-01)** — already handled per IPAI memory, but worth verifying before any Marketplace operation.
6. **Sponsorship subs excluded from Claude deployments** — does NOT affect Founders Hub or Marketplace publishing, only Anthropic model deployment (per `project_foundry_anthropic_sponsorship_blocker`).

---

## 7. Open questions (see `open-questions.md` for full list)

Top 5:
1. What tier level is IPAI currently in Founders Hub (if enrolled)?
2. Exact ISV Success benefit redemption status for IPAI's enrollment?
3. Does `ipai-copilot-resource` count toward Founders Hub Azure-credit consumption?
4. Is `ipai_odoo_on_aca` Marketplace offer best published by IPAI legal entity or W9 / TBWA joint-venture entity?
5. PH-specific co-sell seller mapping — which Microsoft PH rep covers TBWA\SMP finance ops account?

---

## 8. Top 5 highest-leverage programs for IPAI (ranked)

1. **Microsoft for Startups Founders Hub** — $150K Azure credit capture to fund `ipai-copilot-resource` + ACA runtime + Foundry inference. Action: complete portal signup if not done.
2. **Azure Marketplace — `ipai_odoo_on_aca` listing** (Issue 29) — unique market position (no Odoo-on-ACA competitor). Private offer first, transactable later.
3. **ISV Success benefits** — already enrolled; ensure credits + engineering hours are being drawn down.
4. **Entra Agent ID / Agent 365 registration** (Issue 13, deadline 2026-05-01) — catalog visibility for 3 published agents before M365 E7 GA.
5. **Co-sell Ready** — downstream of #2; unlocks Microsoft PH seller team engagement for TBWA\SMP, W9, PrismaLab deals.

---

## 9. Related

- Raw captures: `docs/research/ms-startups/raw/*.md`
- Coverage report: `docs/research/ms-startups/coverage-report.md`
- Open questions: `docs/research/ms-startups/open-questions.md`
- Skill: `.claude/skills/ms-startups-navigator/SKILL.md`
- Persona: `agents/personas/growth-officer-persona.md`
- Judge: `agents/judges/growth-decision-judge.md`
- IPAI memory: `project_partner_center_verification`, `reference_isv_success_program`, `project_marketplace_distribution`, `project_m365_e7_agent365`

---

*Compiled 2026-04-15. Next refresh when Microsoft Learn ISV Success / Co-sell docs are re-indexed, or when IPAI's Founders Hub portal status changes.*
