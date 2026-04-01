# templates

Reusable starter kits and scaffolds for repositories, specs, docs, automations, and design artifacts.

## Purpose

This repository provides reusable templates that accelerate consistent repo creation and document generation across the organization.

## Owns

- Repo starter templates
- Spec templates
- Runbook and ADR templates
- Automation and workflow templates
- Design and document starter artifacts
- Template catalog and validation rules

## Does Not Own

- Live application code
- Production infrastructure
- ERP runtime logic
- Runtime agent orchestration
- Cross-repo governance outside template definitions

## Repository Structure

```text
templates/
├── repo/
│   ├── service/
│   ├── library/
│   └── docs-site/
├── spec/
│   ├── prd/
│   ├── plan/
│   └── tasks/
├── automation/
│   ├── workflow/
│   └── adr/
├── design/
├── docs/
├── ssot/
└── tests/
```

## Validation

Changes must:

- keep templates renderable and current
- preserve compatibility with org standards
- document versioning and intended use
- avoid silently drifting from canonical repo policies
