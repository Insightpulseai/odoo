# data-intelligence

Databricks-centered governed lakehouse, data products, and semantic analytics delivery plane.

## Purpose

This repository owns the governed analytics and data-engineering plane. It manages ingestion, transformation, semantic models, validation, and promotion of analytics-ready outputs.

## Owns

- Databricks jobs, bundles, and notebooks
- Data product schemas and contracts
- Curated transformations and semantic outputs
- Data quality and validation rules
- Analytics release evidence

## Does Not Own

- ERP transactional workflows
- General control-plane apps
- Agent definitions and prompt/skill content
- Azure landing-zone IaC
- Public website experiences

## Repository Structure

```text
data-intelligence/
├── .github/
├── bundles/
├── notebooks/
├── models/
├── schemas/
├── docs/
├── scripts/
├── spec/
├── ssot/
└── tests/
```

## Platform Doctrine

- Azure Databricks is the execution center
- Governed storage and semantic contracts must be explicit
- Notebook use is allowed, but notebook content is not the only authority surface
- Jobs, schemas, and contracts must be reproducible and reviewable

## Validation

Changes must:

- pass data-quality checks
- preserve schema compatibility or document breaks
- keep semantic definitions versioned
- produce promotion evidence where relevant
