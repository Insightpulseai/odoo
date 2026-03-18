# Domain Workbench Map

## Purpose

Define the major domain-facing workbenches that sit on top of the platform planes.

## Marketing / retail media workbench

### Uses
- Odoo for operational entities/workflows
- Databricks for audience, campaign, and performance intelligence
- Fabric / BI for reporting surfaces
- Foundry agents for planning, analysis, QA, and recommendations

### Benchmark references
- activation and creative-media operating systems
- cultural / consumer intelligence systems
- creative effectiveness benchmarks
- regional data hub / measurement benchmarks
- generative media creation benchmarks

## Entertainment / creator workbench

### Uses
- content and campaign operational records
- creative-generation and metadata pipelines
- cultural/consumer intelligence
- domain agents for ideation, packaging, and reporting

## Financial services / compliance workbench

### Uses
- Odoo operational records
- document intelligence subsystem
- Databricks/Fabric reporting and governed analytics
- Foundry agents with stricter safety/eval gates

### Additional rules
- higher isolation and audit posture
- stronger approval/human-in-the-loop requirements

## Data engineering + agent factory workbench

### Uses
- Databricks
- Foundry
- Azure DevOps
- Resource Graph
- repo SSOT

### Users
- platform engineers
- data engineers
- agent engineers
- operators and judges

## Shared workbench requirements

- each workbench must consume explicit APIs/contracts
- each workbench must declare its truth dependencies
- no workbench may create a shadow control plane
- each workbench must preserve tenant context if multitenant

---

*Last updated: 2026-03-17*
