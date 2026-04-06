# Enterprise Knowledge Base

> SAP-grade enterprise capability framework for Odoo 18 CE + OCA + IPAI on Azure.

## Status

| Field | Value |
|-------|-------|
| **Artifact status** | Generated seed corpus |
| **Authority** | Reference / draft — not SSOT |
| **Generated** | 2026-04-07 |
| **Promotion rule** | Individual files may be promoted to `ssot/` only after human review per `REVIEW_QUEUE.md` |
| **Review tracker** | [`REVIEW_QUEUE.md`](REVIEW_QUEUE.md) |

## Purpose

This knowledge base encodes the domain knowledge, architecture patterns, implementation playbooks, and evaluation criteria needed to build an enterprise platform that meets SAP-class expectations using Odoo CE + OCA as the implementation substrate and Azure as the cloud governance model.

## Structure

```
knowledge-base/
├── capability-map/          # Hierarchical capability taxonomy + maturity rubric
├── benchmark/               # SAP-to-Odoo equivalence matrix + gap analysis
├── learning/                # Phased learning architecture + 30/60/90 plan
├── ontology/                # Entity model, glossary, term mappings
├── skill-packs/             # Domain-specific skill packs (11 domains)
├── patterns/                # Architecture, integration, and anti-patterns
├── evaluation/              # Scenario tests, scoring rubrics, eval prompts
├── domain-primers/          # One-page primers per business domain
├── decision-records/        # Architecture decision records (ADRs)
├── checklists/              # Implementation and review checklists
└── process-maps/            # Canonical business process flows
```

## Design Principles

1. **Repo-first**: All knowledge lives in version-controlled files
2. **Machine-readable**: YAML for structured data, Markdown for prose
3. **Agent-consumable**: Skill packs are designed for both humans and coding agents
4. **Incremental**: Extend, don't rebuild — each artifact can grow independently
5. **Evidence-gated**: Maturity claims require observable proof

## Implementation Substrate

| Layer | Technology |
|-------|-----------|
| ERP | Odoo 18 CE + OCA modules |
| Custom | `ipai_*` bridges (last resort) |
| Cloud | Azure (ACA, Front Door, Key Vault, Entra ID) |
| Data | Databricks (Unity Catalog, DLT) + Power BI |
| AI | Azure AI Foundry |
| Identity | Entra ID + Odoo RBAC |

## Benchmark Model

SAP is the capability benchmark — not the implementation target. We extract:
- Business process depth and edge-case coverage
- Enterprise architecture discipline (separation of concerns, audit trails)
- Compliance and controls rigor (SoD, approval flows, document management)
- Integration maturity (idempotent APIs, event-driven, master data governance)
- Reporting depth (multi-dimensional, real-time, regulatory)

Then implement using Odoo/OCA/Azure primitives.

## Usage

- **Humans**: Read domain primers → study skill packs → run evaluation scenarios
- **Agents**: Load relevant skill pack + ontology → apply patterns → verify against checklists
- **Reviews**: Use evaluation framework for architecture reviews and capability audits
