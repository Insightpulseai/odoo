# Marketplace Control Plane

## Structure

```
marketplace/
  offers/
    <offer-slug>/
      offer.yaml                    # Canonical offer metadata
      plans/
        <plan-slug>/
          plan.yaml                 # Plan metadata + pricing
      listing/
        summary.md                  # Short description
        description.md              # Long description
        search-keywords.yaml        # Marketplace search terms
        media/                      # Screenshots, logos
      technical/
        saas/
          landing-page.md           # SaaS fulfillment config
          apis.yaml                 # API contracts
          webhook-contracts.md      # Webhook specs
        azure/                      # Azure-specific config
          managed-app/
          vm/
          container/
      co-sell/
        solution.yaml               # Co-sell metadata
        value-prop.md               # Value proposition
        industries.yaml             # Target industries
      legal/
        terms.md                    # Terms of service
        privacy.md                  # Privacy policy
        support.md                  # Support policy
      evidence/
        certification/              # Marketplace certification proofs
        security/                   # Security review outputs
        deployment/                 # Architecture + deployment proofs
      release/
        changelog.md                # Offer revision history
        publish-history.yaml        # Machine-readable publish log
  schemas/
    offer.schema.yaml               # Offer validation schema
    plan.schema.yaml                # Plan validation schema
  policies/
    MARKETPLACE_GOVERNANCE.md       # Publishing governance
  scripts/
    validate-offer.sh               # Schema validation
    generate-ingestion-payload.sh   # Partner Center API payload
  docs/
    MARKETPLACE_CONTROL_PLANE.md    # This file
```

## Object model

Mirrors Microsoft Partner Center:

```
Offer (1)
  └── Plan (1..N)
       ├── Pricing
       ├── Availability
       └── Technical Config
  └── Listing (1)
       ├── Summary
       ├── Description
       └── Media
  └── Co-sell (0..1)
  └── Legal (1)
  └── Evidence (1)
  └── Release (1)
```

## CI/CD workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate-offer-schema.yml` | PR | Validate offer.yaml against schema |
| `validate-plan-pricing.yml` | PR | Validate plan pricing consistency |
| `validate-listing-policy.yml` | PR | Check listing completeness |
| `generate-ingestion-payload.yml` | Merge | Generate Partner Center API payload |
| `publish-marketplace-offer.yml` | Manual | Publish to marketplace |
| `sync-co-sell-metadata.yml` | Merge | Sync co-sell data to Partner Center |

## References

- [Microsoft Marketplace Overview](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/overview)
- [SaaS Offer Creation](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/create-new-saas-offer)
- [Plans and Pricing](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/plans-pricing)
- [Product Ingestion API](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/product-ingestion-api)
- [Co-sell Requirements](https://learn.microsoft.com/en-us/partner-center/referrals/co-sell-requirements)
- [Listing Policies](https://learn.microsoft.com/en-us/legal/marketplace/certification-policies)
