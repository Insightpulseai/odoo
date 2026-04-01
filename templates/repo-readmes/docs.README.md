# docs

Cross-repo architecture, governance, runbooks, evidence, strategy, and operating model documentation.

## Purpose

This repository is the cross-repo documentation authority surface. It captures architecture, decisions, governance, runbooks, evidence models, and strategic operating context that should not live in only one workload repo.

## Owns

- Cross-repo architecture documentation
- ADRs and governance docs
- Evidence model and runbook templates
- Strategic operating-model docs
- Cross-cutting documentation indexes and freshness policy

## Does Not Own

- Application runtime code
- Infra provisioning logic
- ERP addon implementation
- Agent runtime services
- Shared UI packages

## Repository Structure

```text
docs/
├── .github/
├── architecture/
├── governance/
├── runbooks/
├── strategy/
├── templates/
├── spec/
└── ssot/
```

## Validation

Changes must:

- preserve authority clarity
- avoid duplicating repo-local truths unnecessarily
- keep freshness and ownership explicit
- maintain stable cross-references to SSOT and spec surfaces
