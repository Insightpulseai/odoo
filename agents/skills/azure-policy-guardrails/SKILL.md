---
name: azure-policy-guardrails
description: Azure Policy assignments and guardrails for subscription governance
microsoft_capability_family: "Azure / Governance / Security"
---

# azure-policy-guardrails

## Microsoft Capability Family

**Azure / Governance / Security**

## Purpose

Ensure Azure Policy enforces: allowed regions, required tags, denied SKUs, encryption, network baselines. Compliance >= 90%.

## Required Repo Evidence

- `infra/azure/policy/`
- `infra/ssot/azure/resources.yaml`
- `docs/evidence/<stamp>/azure-policy/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Policy built-in definitions Container Apps"
2. `microsoft_docs_search` — "Azure Policy deny effect allowed locations"
3. `microsoft_docs_search` — "Azure Policy compliance evaluation remediation"

## Workflow

1. Classify under Azure / Governance / Security
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Policy initiative assigned, allowed locations restricted, required tags enforced, compliance >= 90%.
