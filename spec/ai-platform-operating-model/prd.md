# PRD — AI Platform Operating Model

## Objective

Publish the canonical AI platform operating model for InsightPulseAI around the Odoo-on-Azure estate.

## Why this matters

AI capabilities now span model access, orchestration, retrieval, safety, evaluation, governance, and production operations. This target defines the AI platform as a distinct control-plane and runtime family rather than letting AI concerns leak into Odoo addons or ad hoc app patterns.

## Benchmark model

- Microsoft Foundry → end-to-end AI platform benchmark
- Azure AI Search → retrieval and grounding benchmark
- Agent runtime patterns → external orchestration/runtime benchmark

## In scope

- AI platform index and taxonomy
- Foundry control plane
- retrieval and grounding
- model governance and evals
- AI safety and operations
- Odoo boundary rules for thin connector surfaces only

## Out of scope

- fat Odoo AI modules
- undocumented per-app AI patterns
- replacing Odoo business logic with AI runtime logic

## Success metrics

- AI platform docs exist as a distinct family
- external-runtime-only boundary is explicit
- Foundry, retrieval, and safety responsibilities are documented
- work item and repo ownership are clear across platform and agents repos

## Affected repos

- docs
- platform
- agents
- odoo

## Owning teams

- ipai-docs
- ipai-platform-control
- ipai-agents
- ipai-odoo-runtime

## Workstream model

1. AI Platform Index
2. Foundry Control Plane
3. Retrieval and Grounding
4. Agent Runtime Boundaries
5. AI Safety and Operations

## Acceptance conditions

- the AI platform family exists and is linked from the central docs index
- runtime/orchestration concerns are documented outside Odoo
- connector-only Odoo boundary is documented
- current bridge and gap status is explicit

## Azure Boards projection

Epic title:
`[TARGET] AI Platform Operating Model Published`
