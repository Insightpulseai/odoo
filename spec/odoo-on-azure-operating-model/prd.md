# PRD — Odoo on Azure Operating Model

## Objective

Publish the canonical Odoo-on-Azure workload operating model for InsightPulseAI.

## Why this matters

The platform already has a live Azure estate, multiple repos with distinct authority surfaces, and a growing set of workload, control-plane, and documentation artifacts. This target establishes a unified, benchmarked documentation and governance model so the Odoo workload can be planned, operated, and evolved with enterprise-grade rigor.

## Benchmark model

- SAP on Azure → workload operating model
- Microsoft Foundry → AI platform benchmark where AI intersects the workload
- Azure + GitHub AI-led SDLC → engineering delivery benchmark
- Databricks + Fabric → data-intelligence benchmark for adjacent analytics lanes

## In scope

- workload overview and support matrix
- workload-center and OSI model
- monitoring and operational insights
- deployment automation framework
- runtime reference architecture
- planning/reference family
- integration playbooks

## Out of scope

- Odoo Enterprise feature parity expansion
- non-Azure primary runtime patterns
- broad custom Odoo module programs
- marketing-site content unrelated to operator guidance

## Success metrics

- all core workload documentation families are published
- repo authority is explicit for all workload doc families
- drift/evidence gaps are documented and tracked
- Azure Boards can roll up progress by workstream and repo team

## Affected repos

- docs
- platform
- infra
- odoo
- agents
- data-intelligence

## Owning teams

- ipai-docs
- ipai-platform-control
- ipai-infra
- ipai-odoo-runtime
- ipai-agents
- ipai-data-intelligence

## Workstream model

1. Overview Family
2. Workload Center Family
3. Monitoring Family
4. Deployment Automation Family
5. Runtime Family
6. Planning and Reference Family
7. Integrations Family

## Acceptance conditions

- all workstreams have source-of-truth repo ownership
- cross-repo navigation exists
- major runtime/control-plane claims have evidence backing
- Azure Boards Epic and Features are created and linked
- completion is visible through Feature rollups and evidence-backed Stories

## UAT Scenario Authority

Detailed business acceptance scenarios, execution templates, and sign-off records are maintained in:
- `spec/odoo-on-azure-operating-model/uat-scenarios.md`

## Azure Boards projection

Epic title:
`[TARGET] Odoo on Azure Operating Model Published`

Feature naming pattern:
`[FEATURE] <Workstream Name>`
