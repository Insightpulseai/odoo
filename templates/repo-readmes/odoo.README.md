# odoo

Transactional system of record built on Odoo Community Edition, OCA modules, and thin IPAI bridge modules.

## Purpose

This repository is the ERP runtime and application source of truth for transactional business workflows. It hosts the Odoo stack, OCA addons, thin IPAI integration bridges, runtime configuration, release scripts, and validation logic.

## Owns

- Odoo runtime configuration
- OCA addon inventory and ordering
- Thin IPAI bridge modules
- Local development and test runtime contract
- Odoo-specific CI, release validation, and evidence
- ERP-facing application behavior

## Does Not Own

- Cross-platform control-plane APIs
- General-purpose agent runtime services
- Enterprise website experiences
- Azure landing zone infrastructure
- Design system source of truth

## Repository Structure

```text
odoo/
├── .github/
├── addons/
│   ├── oca/
│   ├── ipai/
│   └── local/
├── config/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── docker/
├── docs/
├── evidence/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Canonical Rules

- `addons/oca` is the default parity lane
- `addons/ipai` is reserved for thin bridges and integration glue
- `addons/local` is minimal and non-canonical
- Odoo addon discovery must enumerate OCA repo roots correctly
- Runtime/database naming must remain canonical and deterministic

## Runtime Doctrine

- Local runtime contract is repo-defined and testable
- Production remains deployment-gated and evidence-backed
- Configuration must be generated or rendered from machine-readable SSOT where possible

## Validation

Changes must:

- preserve addon-path correctness
- pass contract/integration/smoke tests
- avoid hidden runtime drift
- include evidence for deploy-affecting changes
