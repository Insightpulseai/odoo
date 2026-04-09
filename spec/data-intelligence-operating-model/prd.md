# PRD — Data Intelligence Operating Model

## Objective

Publish the canonical data-intelligence operating model for InsightPulseAI around the Odoo-on-Azure ecosystem.

## Why this matters

Odoo is the transactional system of record, but it should not become the enterprise lakehouse, semantic BI layer, or cross-domain analytics platform. This target defines the governed analytical layer and the integration of ERP data into a broader data-intelligence architecture.

## Benchmark model

- Databricks + Fabric → lakehouse, governance, BI, and AI-ready data benchmark

## In scope

- data-intelligence index
- lakehouse and governance model
- batch and real-time ingestion patterns
- semantic consumption and BI
- data/AI integration boundaries

## Out of scope

- replacing Odoo operational reporting entirely
- pushing data-platform logic into Odoo runtime
- ad hoc analytics with no governance model

## Success metrics

- a separate data-intelligence doc family exists
- Odoo vs data-platform responsibilities are explicit
- ingestion and governance patterns are documented
- BI and AI-ready consumption boundaries are documented

## Affected repos

- docs
- data-intelligence
- platform
- odoo

## Owning teams

- ipai-docs
- ipai-data-intelligence
- ipai-platform-control
- ipai-odoo-runtime

## Workstream model

1. Data Intelligence Index
2. Lakehouse and Governance
3. Ingestion Patterns
4. Consumption and BI
5. Data/AI Integration

## Acceptance conditions

- the data-intelligence family exists and is linked from the central docs index
- Odoo vs lakehouse/BI responsibilities are explicit
- ingestion and governance assumptions are documented
- AI-readiness boundaries are documented

## Azure Boards projection

Epic title:
`[TARGET] Data Intelligence Operating Model Published`
