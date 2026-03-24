---
name: odoo-release-promotion
description: Odoo release promotion workflow from dev to staging to production
microsoft_capability_family: "GitHub / DevOps / Azure Deployment"
---

# odoo-release-promotion

## Microsoft Capability Family

**GitHub / DevOps / Azure Deployment**

## Purpose

Define and validate promotion workflow with stage gates. Container Apps revision management for zero-downtime deployments.

## Required Repo Evidence

- `infra/ssot/azure/service-matrix.yaml`
- `scripts/deploy-odoo-modules.sh`
- `docs/evidence/<stamp>/release-promotion/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Container Apps revision management traffic splitting"
2. `microsoft_docs_search` — "Azure DevOps pipeline stage gates approval"
3. `microsoft_docs_search` — "Azure Container Apps blue green deployment"

## Workflow

1. Classify under GitHub / DevOps / Azure Deployment
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Pipeline has dev/staging/prod stages, staging requires test pass, prod requires manual approval, revision traffic splitting.
