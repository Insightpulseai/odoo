---
name: azure-pg-ha-dr
description: PostgreSQL HA/DR posture validation for Azure Database for PostgreSQL Flexible Server
microsoft_capability_family: "Azure / Database / PostgreSQL"
---

# azure-pg-ha-dr

## Microsoft Capability Family

**Azure / Database / PostgreSQL**

## Purpose

Validate that the Odoo PostgreSQL server (pg-ipai-odoo) meets HA/DR requirements: zone-redundant HA, backup retention >= 7 days, PITR, geo-redundancy.

## Required Repo Evidence

- `infra/ssot/azure/resources.yaml`
- `infra/ssot/azure/service-matrix.yaml`
- `docs/evidence/<stamp>/azure-pg-ha-dr/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure PostgreSQL Flexible Server high availability zone redundant"
2. `microsoft_docs_search` — "Azure PostgreSQL backup geo-redundant PITR"
3. `microsoft_docs_search` — "Azure PostgreSQL Flexible Server disaster recovery failover"

## Workflow

1. Classify under Azure / Database / PostgreSQL
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

resources.yaml declares zone-redundant HA, backup >= 7 days, DR drill evidence with failover time.
