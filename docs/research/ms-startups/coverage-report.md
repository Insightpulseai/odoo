# Coverage Report — MS for Startups Crawl

**Crawled 2026-04-15.**

## URLs fetched successfully (3)

| URL | Outcome |
|---|---|
| https://learn.microsoft.com/en-us/startups/ | ✓ 200 — hub index captured |
| https://www.microsoft.com/en-us/startups | ✓ 200 — $150K headline + PH geo confirmed |
| https://learn.microsoft.com/en-us/partner-center/marketplace-offers/create-new-saas-offer | ✓ 200 — full SaaS publishing flow |

## URLs attempted, failed or redirected (3)

| URL | Outcome | Workaround |
|---|---|---|
| https://foundershub.startups.microsoft.com/ | 301 → portal.startups.microsoft.com | Use portal URL; signup requires auth |
| https://learn.microsoft.com/en-us/partner-center/marketplace-offers/isv-success | 404 | Doc moved; check Partner Center dashboard directly |
| https://learn.microsoft.com/en-us/partner-center/marketplace-offers/co-sell-overview | 404 | Doc moved; engage MS PDM or Partner Center |

## URLs skipped (intentional)

- `portal.startups.microsoft.com` downstream pages — auth-walled; not public docs
- Per-country localization pages — PH is tagged; no special blocker expected
- Marketplace offer variants (VM, Container, Managed App) — SaaS is the target form for `ipai_odoo_on_aca`; other forms not on IPAI roadmap
- Pricing pages (Microsoft Marketplace fees) — commission rates change; check Partner Center for live rates

## Depth coverage
- Depth 0 (hub): ✓
- Depth 1 (marketing landing): ✓
- Depth 1 (partner-center offer creation): ✓
- Depth 2+ (Co-sell, ISV Success deep-dive, Founders Hub tier details): **blocked** on MS doc restructuring + auth-walled portal

## Signal completeness

| Section of knowledge-base.md | Signal source | Confidence |
|---|---|---|
| Program catalog | Fetched + IPAI memory | High |
| Lifecycle map | Fetched + doctrine | High |
| Dependency graph | Fetched + memory | High |
| Dollar-value inventory | Fetched ($150K) + UNKNOWN on sub-tiers | Medium |
| Obligation inventory | Partial — memory + 404s force gaps | Medium |
| PH-specific notes | Geo tag confirmed; BIR intersection flagged | Medium |
| Contradictions / gotchas | Fetched + session experience | High |
| Open questions | All enumerated | High |

## Top 5 most valuable programs surfaced

1. Microsoft for Startups Founders Hub (up to $150K Azure credits)
2. Azure Marketplace (SaaS offer publishing — strategic `ipai_odoo_on_aca` slot)
3. ISV Success (already enrolled for IPAI — MpnId 7097325)
4. Co-sell Ready (downstream of Marketplace — unlocks MS seller channel)
5. Entra Agent ID / Agent 365 catalog (deadline 2026-05-01)

## Recommended next refresh triggers

- Microsoft Learn re-indexes ISV Success + Co-sell docs (404 lifted)
- IPAI completes Founders Hub portal signup (state change)
- Marketplace publishing underway (Issue 29 in motion)
- 2026-05-01 passes (Agent 365 GA — re-verify benefit set)
