---
name: odoo-image-supply-chain
description: Container image build, scan, sign, and registry governance for Odoo images
microsoft_capability_family: "GitHub / DevOps / Azure Container Registry"
---

# odoo-image-supply-chain

## Microsoft Capability Family

**GitHub / DevOps / Azure Container Registry**

## Purpose

Ensure Odoo images built via CI, scanned for vulnerabilities, stored in canonical ACR (acripaiodoo), tagged with immutable digests.

## Required Repo Evidence

- `docker/odoo/Dockerfile`
- `infra/ssot/azure/resources.yaml`
- `docs/evidence/<stamp>/image-supply-chain/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Container Registry image scanning Defender for Containers"
2. `microsoft_docs_search` — "ACR tasks automated container build GitHub"
3. `microsoft_docs_search` — "Container image signing content trust Azure"

## Workflow

1. Classify under GitHub / DevOps / Azure Container Registry
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Images built via CI, scan runs before deploy, production uses immutable digest, ACR is only push target.
