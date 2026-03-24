---
name: aca-private-networking
description: Azure Container Apps private networking, VNet integration, and NSG configuration
microsoft_capability_family: "Azure / Networking / Container Apps"
---

# aca-private-networking

## Microsoft Capability Family

**Azure / Networking / Container Apps**

## Purpose

Validate internal services not publicly exposed, VNet integration configured, NSG rules restrict to Front Door only.

## Required Repo Evidence

- `infra/ssot/azure/service-matrix.yaml`
- `infra/azure/networking/`
- `docs/evidence/<stamp>/aca-networking/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Container Apps VNet integration internal environment"
2. `microsoft_docs_search` — "Azure Container Apps NSG rules Front Door origin"
3. `microsoft_docs_search` — "Azure Container Apps private DNS zone configuration"

## Workflow

1. Classify under Azure / Networking / Container Apps
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Internal apps have internal ingress, public apps Front Door only, VNet integration enabled.
