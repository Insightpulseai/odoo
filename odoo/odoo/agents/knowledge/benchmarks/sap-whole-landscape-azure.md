# SAP Whole-Landscape on Azure — Benchmark

## Source

https://learn.microsoft.com/en-us/azure/architecture/guide/sap/sap-whole-landscape

## Weight

1.0

## Why it matters

Microsoft's canonical guidance for designing a complete SAP estate on Azure: hub/shared services, production, non-production, DR. Covers network design, security, performance, resilience across the full landscape — not just a single workload deployment.

This is the structural benchmark for our Odoo Whole-Landscape architecture.

## Key patterns to adapt

- Hub/spoke network topology with shared services
- Environment separation (prod/nonprod/DR) via subscriptions or resource groups
- NSG + WAF + private endpoints for network security
- Availability zones for zonal resilience
- PostgreSQL Flexible Server replaces HANA
- Container Apps replaces SAP app servers (ASCS, dialog, web dispatcher)
- Azure Front Door replaces SAP Web Dispatcher for public ingress
- Databricks replaces SAP BW for analytics
- Foundry replaces SAP BTP for agent/AI capabilities

## What maps directly

- Hub/shared services model
- Prod/nonprod separation
- DR region design
- Identity and RBAC patterns
- Network segmentation
- Backup and PITR strategy
- Observability stack

## What needs custom discipline for Odoo

- Odoo has no native HA clustering (SAP has ASCS/ERS failover)
- Odoo has no built-in enterprise audit trail (must add via ipai_* or OCA modules)
- Odoo multi-company is simpler than SAP client separation but less governed
- Module lifecycle management in Odoo is manual (no SAP Transport Management System equivalent)
- No SAP SolMan equivalent — must build observability/ops console

## Must not influence

- Odoo module boundaries (OCA-first doctrine stands)
- Repo topology (already decided)
- Agent runtime design (Foundry, not SAP BTP)
