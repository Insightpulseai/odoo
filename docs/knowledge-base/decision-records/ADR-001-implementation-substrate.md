# ADR-001: Implementation Substrate Selection

## Status
Accepted

## Context
Building an enterprise platform that must meet SAP-grade expectations for business process depth, compliance, and operational rigor. Need to choose the ERP implementation substrate.

## Decision
Use **Odoo 18 CE + OCA** as the ERP substrate, with **Azure** as the cloud platform and **thin ipai_* bridges** for custom gaps.

## Rationale

### Why Odoo CE
- Open source, no license cost, full code access
- Strong native modules (accounting, inventory/MRP, CRM, sales, purchase, project)
- Large OCA ecosystem for enterprise extensions
- Python-based (accessible for AI/automation integration)
- Modern web framework (Owl components)
- Active community with regular releases

### Why not SAP
- License cost prohibitive for the current scale
- Complexity exceeds current team capacity
- Vendor lock-in on infrastructure
- Over-engineered for current business scope

### Why not other ERPs
- ERPNext: smaller ecosystem, less mature accounting
- NetSuite: SaaS-only, vendor lock-in
- Microsoft Dynamics: license cost, Microsoft ecosystem dependency (partially mitigated by Azure alignment)

### Why Azure
- Existing organizational investment
- Strong identity (Entra ID), AI (Foundry), and data (Databricks) services
- Container Apps suitable for Odoo deployment model
- Mature governance tooling

## Consequences

### Positive
- Zero license cost for ERP
- Full control over customization and deployment
- Can benchmark against SAP patterns without SAP dependency
- Azure services fill platform gaps (identity, AI, data, BI)

### Negative
- Must build PH tax compliance from scratch (no SAP localization)
- CE lacks some enterprise features (Studio, advanced reporting, barcode)
- OCA module quality varies; must evaluate each module
- Single-vendor support not available (community-driven)
- Upgrade responsibility falls on us (no vendor-managed upgrades)

### Risks
- OCA modules may not have 18.0 branches for all needed functionality
- Custom ipai_* modules create maintenance burden
- Team must develop deep Odoo expertise (learning curve)

## Mitigation
- Config → OCA → Delta hierarchy minimizes custom code
- Knowledge base (this repo) accelerates learning
- Evaluation framework ensures quality gates before deployment
- Azure platform services offset Odoo CE limitations
