# design

Brand tokens, component mappings, visual assets, and design-to-code contracts.

## Purpose

This repository is the design-system and brand authority surface. It owns tokens, component mappings, visual assets, and handoff artifacts that support consistent implementation across web, platform, and related surfaces.

## Owns

- Brand and semantic tokens
- Component mappings
- Shared visual assets
- Design handoff rules
- Exported previews and design/code mapping metadata

## Does Not Own

- Production web application code
- ERP runtime logic
- General Azure infrastructure
- Deployable runtime services
- Cross-repo strategy or governance docs

## Repository Structure

```text
design/
├── .github/
├── tokens/
├── components/
├── assets/
├── docs/
├── exports/
├── spec/
└── ssot/
```

## Validation

Changes must:

- preserve token integrity
- document mapping changes
- keep exports reproducible
- support design/code parity without becoming the runtime UI repo
