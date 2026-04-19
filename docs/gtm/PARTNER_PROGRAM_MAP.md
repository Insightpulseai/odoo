# Partner Program Map

Canonical source: [`ssot/governance/partner-program-authority.yaml`](../../ssot/governance/partner-program-authority.yaml)

## Purpose

Clarify the three distinct Microsoft + GitHub partner tracks IPAI interacts with, and prevent conflation of benefits, client provisioning, and extension productization.

## The three tracks

| Track | Authority for | Use for | IPAI state |
|---|---|---|---|
| Microsoft Partner Center (AI Cloud Partner Program) | benefits, Azure credits, GitHub entitlements, marketplace motion | IPAI's own benefits, co-sell, marketplace publish | ISV Success enrolled (2026-04-06) |
| GitHub Enterprise partner surfaces (billing / CSP) | client enterprise provisioning, CSP partner path | provisioning GitHub for customers | out of scope until CSP motion activates |
| GitHub Copilot Partner Program | Copilot Chat extension productization | building Copilot extensions | reference only until Pulser GA |

## When to use which

- **Consuming benefits for IPAI** → Partner Center.
- **Provisioning GitHub for a customer** → GitHub billing / CSP docs.
- **Building Copilot extensions** → Copilot Partner Program.

## Clean policy statement

```
Partner Center        = benefits + Microsoft commercial motion
GitHub partner/billing = client GitHub Enterprise provisioning
Copilot Partner Program = build Copilot extensions/integrations
```

## Near-term priorities

1. **Partner Center benefits** — confirm FY26 GitHub entitlement, redeem seats into the `ipai` enterprise, track in [`partner_center_checklist.md`](partner_center_checklist.md).
2. **Marketplace publish** — Aug–Sep 2026 target per ISV Success engagement. See [`MARKETPLACE_OFFER.md`](MARKETPLACE_OFFER.md) and [`marketplace_research_brief.md`](marketplace_research_brief.md).
3. **CSP motion** — gated on first paying enterprise customer requesting managed GitHub.
4. **Copilot Partner Program** — gated on Pulser GA + Safe Outputs coverage.

## Non-goals

- Not conflating Partner Center benefits with GitHub customer provisioning.
- Not pursuing Copilot Partner Program before Pulser GA + safety coverage.
- Not treating marketplace listing content as architecture truth.

## Related

- [Partner program authority SSOT](../../ssot/governance/partner-program-authority.yaml)
- [Partner Center checklist](partner_center_checklist.md)
- [Marketplace research brief](marketplace_research_brief.md)
- [Microsoft co-sell one-pager](microsoft_cosell_one_pager.md)
- [GitHub Enterprise migration SSOT](../../ssot/governance/github-enterprise-migration.yaml)
- [GitHub operating layers](../../ssot/governance/github-operating-layers.yaml)
