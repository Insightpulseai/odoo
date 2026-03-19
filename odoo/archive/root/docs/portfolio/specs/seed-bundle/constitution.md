# Constitution — Seed Bundle

## Purpose

The seed bundle provides deterministic, version-controlled seed data for AFC (Advanced Financial Closing) and STC (SAP Tax Compliance) workstreams using SAP canonical taxonomy.

## Non-Negotiable Rules

### 1. SAP Naming is Canonical

- All task and check names MUST use SAP terminology
- SAP naming provides SOP/manual consistency
- Never rename SAP canonical items to Odoo terms in seed files

### 2. Odoo Mapping is Separate

- Translation to Odoo models MUST be in `90_odoo_mapping.yaml` files
- Mapping files define model targets, field transforms, OCA dependencies
- Seed files remain Odoo-agnostic

### 3. Localization is Overlay

- Country-specific customizations MUST be in overlay files (`60_localization_*.yaml`)
- Overlays patch the SAP baseline without polluting it
- PH-specific items: BIR forms, ATC codes, deadlines, thresholds

### 4. Schema Enforcement

- All seed YAML files MUST validate against their schemas
- CI MUST block PRs with invalid seeds
- Schemas are defined in `seeds/schema/` directory

### 5. Immutable Structure

Core seed structure MUST NOT change without spec update:

```
seeds/
├── workstreams/
│   ├── afc_financial_close/
│   └── stc_tax_compliance/
├── shared/
├── schema/
└── scripts/
```

## Allowed Changes

- Adding new tasks/checks to existing workstreams
- Adding new overlays for localization
- Updating schema versions with backward compatibility
- Adding new shared configurations

## Prohibited Changes

- Renaming SAP canonical codes
- Moving localization into SAP baseline files
- Removing existing tasks/checks without deprecation period
- Breaking schema changes without migration plan
