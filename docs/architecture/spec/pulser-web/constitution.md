# Pulser Web — Constitution

> Non-negotiable rules and constraints for the Pulser web experience layer.

---

## Invariants

1. **UI renders evidence, never generates it.** The web layer displays TaxEvidenceCardView, TaxNavigationCardView, etc. but never constructs citations or authority determinations.
2. **Authority badges must render.** Every tax response card must display TaxAuthorityBadge(s) showing the highest-tier source. Badges cannot be hidden or suppressed.
3. **Ambiguity banners are non-dismissible on first view.** TaxAmbiguityBannerView (conflicting_sources, missing_authority, unsupported_case, requires_review) must be shown prominently and cannot be auto-dismissed.
4. **Navigation cards separate official from internal.** TaxNavigationCardView must render `official_links` (BIR/government) and `internal_links` (Odoo) in visually distinct sections — never interleaved.
5. **Action proposals show risk.** TaxActionProposalCardView must always display `risk_level` and `approval_required` status. No action card without risk disclosure.
6. **Legal basis is always visible.** For action proposals, the `legal_basis` section (Tier 1-2 citations) must be visible without scrolling or expanding.
7. **No UI-only tax advice.** The web layer cannot add explanatory text that constitutes tax guidance beyond what the agent response contains.
8. **Pulser is the public brand.** Use "Pulser" and "Ask Pulser" in all user-facing surfaces. "Copilot" is internal only.
9. **Execution model citations are labeled.** When showing Tier 5 (Odoo localization) references, they must be labeled as "Implementation Reference" — not "Legal Authority."
10. **Responsive evidence cards.** All tax evidence cards must render correctly on mobile viewports (320px minimum).
