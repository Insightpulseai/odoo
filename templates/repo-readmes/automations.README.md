# automations

Scheduled and event-driven automation jobs with explicit connectors, contracts, retry behavior, and runbooks.

## Purpose

This repository owns automation jobs and workflows that operate across platform surfaces, including scheduled jobs, maintenance tasks, and event-driven handlers.

## Owns

- Scheduled jobs
- Event-driven automation flows
- Connector-specific automation wrappers
- Retry/idempotency rules
- Automation runbooks and validation

## Does Not Own

- Core app business logic
- General-purpose control-plane UI
- Deployable agent runtime services
- Azure landing-zone infrastructure
- Canonical persona/skill/judge definitions

## Repository Structure

```text
automations/
├── .github/
├── jobs/
├── connectors/
├── runbooks/
├── docs/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Validation

Changes must:

- be idempotent where possible
- declare triggers and retry expectations
- preserve connector contract correctness
- include validation for failure handling and observability
