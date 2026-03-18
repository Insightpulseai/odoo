# Marketplace Governance Policy

## Purpose

This policy governs how Microsoft Marketplace offers are managed within the InsightPulseAI organization.

## Ownership model

| Domain | Owner | Artifacts |
|--------|-------|-----------|
| Product | Product lead | offer.yaml, plan.yaml, pricing, roadmap |
| Marketing | Marketing lead | listing/summary, listing/description, media |
| Legal/Compliance | Legal | legal/terms, legal/privacy, legal/support |
| Engineering/Platform | Platform lead | technical/*, evidence/* |
| Partner/Sales | Sales lead | co-sell/*, private offers |

## Publish workflow

1. All offer/plan changes committed to `marketplace/offers/<offer-slug>/`
2. CI validates schema compliance (`validate-offer-schema.yml`)
3. CI validates listing policy (`validate-listing-policy.yml`)
4. PR review required from at least one domain owner
5. Merge to main triggers ingestion payload generation
6. Manual publish approval required for production marketplace updates

## Schema enforcement

- All `offer.yaml` files must validate against `schemas/offer.schema.yaml`
- All `plan.yaml` files must validate against `schemas/plan.schema.yaml`
- CI gates reject non-compliant changes

## Naming conventions

- Offer slugs: lowercase, hyphenated (e.g., `odooops-control-plane`)
- Plan slugs: lowercase, hyphenated (e.g., `professional`, `enterprise`)
- No spaces, no underscores, no uppercase in slugs

## Evidence requirements

Before any marketplace publish:
- [ ] Listing content complete (summary, description, keywords, media)
- [ ] Legal docs reviewed (terms, privacy, support)
- [ ] Technical config validated (APIs, webhooks, SSO)
- [ ] Plan pricing confirmed
- [ ] Screenshots/media present
- [ ] Support/privacy URLs accessible and returning 200
- [ ] Architecture evidence in `evidence/deployment/`
