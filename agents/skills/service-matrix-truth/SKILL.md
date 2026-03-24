---
name: service-matrix-truth
description: Validate service-matrix.yaml against live Azure resource state
microsoft_capability_family: "Azure / Architecture / Operations"
---

# service-matrix-truth

## Microsoft Capability Family

**Azure / Architecture / Operations**

## Purpose

Validate service-matrix.yaml matches live Azure state via Resource Graph. All declared services exist, config matches, no undeclared resources.

## Required Repo Evidence

- `infra/ssot/azure/service-matrix.yaml`
- `infra/ssot/azure/resources.yaml`
- `docs/evidence/<stamp>/service-matrix/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Resource Graph query container apps inventory"
2. `microsoft_docs_search` — "Azure Resource Graph Kusto query examples"
3. `microsoft_docs_search` — "Azure architecture documentation best practices"

## Workflow

1. Classify under Azure / Architecture / Operations
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Zero drift declared vs live, no undeclared resources, validation script runs in CI.
