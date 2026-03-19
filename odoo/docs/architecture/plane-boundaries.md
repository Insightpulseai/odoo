# Plane Boundaries

## Purpose

Define what each plane owns, what it can read, and what it must not replace.

## Governance / control plane

### Owns
- Azure Boards work hierarchy
- GitHub code and PR history
- Azure Pipelines build/release history
- Resource Graph live inventory/drift queries
- repo SSOT and contracts
- runtime evidence documents

### Must not replace
- transactional records
- analytical data products
- agent runtime state

## Identity / network / security plane

### Owns
- authentication
- workload identity
- secrets/certificates
- ingress and network isolation
- shared security controls

### Must not replace
- workload-specific authorization logic
- tenant business data
- application business workflows

## Business systems plane

### Owns
- operational transactions
- business process execution
- ERP master and transactional data
- finance/project/operations workflows

### Must not replace
- medallion/lakehouse engineering
- model training/runtime governance
- portfolio/governance planning

## Data intelligence plane

### Owns
- ingestion pipelines
- analytical storage
- data transformation
- ML engineering
- semantic/reporting outputs

### Must not replace
- ERP transaction truth
- release truth
- tenant control-plane workflows

## Agent / AI runtime plane

### Owns
- model selection/routing
- tool selection/governance
- agent orchestration
- eval/tracing/runtime promotion

### Must not replace
- portfolio planning
- code truth
- transactional ERP truth
- lakehouse engineering truth

## Experience / domain application plane

### Owns
- user-facing applications
- workbenches
- workflow UI surfaces
- domain APIs

### Must not replace
- shared security plane
- release/governance plane
- foundational data/agent platforms

## Cross-plane integration rules

- all cross-plane integrations must be explicit
- no plane may silently become a second system of record
- tenant context must propagate across business, data, and agent planes
- all production-bound cross-plane changes must have release evidence

## Truth-plane map

- planned truth = Azure Boards
- code truth = GitHub
- release truth = Azure Pipelines
- live Azure inventory truth = Resource Graph
- intended-state truth = repo SSOT
- agent/runtime/eval truth = Foundry
- transactional truth = Odoo
- analytical truth = Databricks/Fabric outputs where designated

---

*Last updated: 2026-03-17*
