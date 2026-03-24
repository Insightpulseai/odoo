---
name: azure-observability-baseline
description: Azure Monitor, App Insights, and Log Analytics baseline for platform observability
microsoft_capability_family: "Azure / Monitor / App Insights"
---

# azure-observability-baseline

## Microsoft Capability Family

**Azure / Monitor / App Insights**

## Purpose

Validate diagnostic settings, Application Insights, alerting rules, and Log Analytics workspace covering all platform services.

## Required Repo Evidence

- `infra/ssot/azure/service-matrix.yaml`
- `infra/azure/monitor/`
- `docs/evidence/<stamp>/azure-observability/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure Container Apps diagnostic settings Log Analytics"
2. `microsoft_docs_search` — "Azure Monitor alert rules Container Apps"
3. `microsoft_docs_search` — "Application Insights Azure PostgreSQL Flexible Server"

## Workflow

1. Classify under Azure / Monitor / App Insights
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

All ACA apps have diagnostics, App Insights connected, >= 3 alert rules, data flowing to Log Analytics.
