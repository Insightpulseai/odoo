# web

Customer-facing and operator-facing web experiences, shared UI packages, and edge-delivered application surfaces.

## Purpose

This repository owns public and product-facing web applications, content-driven experiences, shared UI packages, and route/SEO/content contracts for browser-based experiences.

## Owns

- Marketing and product-facing web apps
- Shared web UI packages
- Route and content contracts
- Frontend testing and accessibility validation
- Edge-delivered web behavior

## Does Not Own

- ERP runtime
- Azure infrastructure provisioning
- Lakehouse and semantic analytics workloads
- Deployable agent runtime services
- Canonical design-token SSOT if kept in `design`

## Repository Structure

```text
web/
├── .github/
├── apps/
│   ├── marketing/
│   ├── product/
│   └── landing-redirect/
├── packages/
│   ├── ui/
│   ├── brand/
│   └── content/
├── edge/
├── docs/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Validation

Changes must:

- preserve route correctness
- pass accessibility and smoke coverage
- keep content and UI packages aligned
- maintain deterministic preview/release behavior
