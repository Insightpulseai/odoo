# Prompt: SaaS Deployment Stamp Design

## Context

You are the SaaS Platform Architect designing deployment stamp patterns for a multi-tenant platform on Azure.

## Task

Given the tenant growth projection, geo requirements, and SLA targets, produce a deployment stamp design covering:

1. **Stamp composition**: Define the Azure resources that constitute one stamp — Container Apps Environment, PostgreSQL, Redis, Storage, networking. Include the Bicep/ARM template structure.
2. **Capacity model**: Calculate maximum tenants per stamp based on resource limits (connections, CPU, memory, storage). Define scaling triggers for new stamp creation.
3. **Tenant-to-stamp assignment**: Algorithm for placing tenants into stamps — round-robin, capacity-aware, affinity-based, or tier-based. Include rebalancing strategy.
4. **Stamp lifecycle**: Procedures for creating new stamps (IaC deployment), scaling within a stamp, draining a stamp (migrating tenants out), and decommissioning empty stamps.
5. **Geo-distribution**: How stamps map to Azure regions. Traffic routing via Azure Front Door with region-aware backend pools. Data residency compliance.
6. **Stamp health monitoring**: Per-stamp health metrics, capacity utilization dashboards, and alerting thresholds for proactive scaling.

## Constraints

- Each stamp must be deployable from a single parameterized IaC template
- Stamp failure must not cascade — each stamp is a blast radius boundary
- Tenant assignment must be stored in a central catalog (not hardcoded in routing)
- Stamp count must stay within subscription limits
- Cross-stamp communication must be minimized (stamps are independent units)

## Output Format

Produce a structured document with:
- Stamp architecture diagram
- Bicep module skeleton for one stamp
- Capacity calculation spreadsheet
- Assignment algorithm pseudocode
- Front Door routing configuration
