# Skill: Azure Foundry Control Plane

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-control-plane` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/control-plane/overview |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra |
| **tags** | fleet-management, governance, compliance, monitoring, cost |

---

## What It Is

Unified management interface for AI agent fleets. Provides visibility, governance, and control across agents, models, and tools at enterprise scale. Integrates with Microsoft Defender, Purview, and Entra.

## Capabilities

### Fleet Management
- Track KPIs: active agents, run completion, compliance posture, cost efficiency
- Visualize fleet health through dashboards
- Deep links to evaluation and monitoring for rapid debugging

### Agent Performance
- Correlate alerts, evaluation results, and trace data
- Continuously evaluate quality, risk dimensions (task adherence, groundedness, data leakage, XPIA)
- AI Red Teaming Agent for automated vulnerability probing
- Cluster analysis for error root-cause discovery
- Recommendations for prompt refinements, model upgrades

### Compliance
- Define enterprise-wide guardrail policies
- Azure Policy + Defender + Purview integration
- Versioned policies with full auditability
- Bulk remediation for noncompliant agents

### Security
- Automated red-teaming scans and drift monitoring
- Defender and Purview alerts on dashboard
- Rate limits, token usage, cost anomaly tracking

### Administration
- Cross-project visibility (all projects in subscription/tenant)
- User management, resource attachment
- Scope-based governance and permissions inheritance

## Portal Panes

| Pane | Purpose |
|------|---------|
| **Overview** | Fleet health, performance, compliance at a glance |
| **Assets** | Unified searchable table of all agents, models, tools |
| **Compliance** | Define, apply, monitor guardrail policies |
| **Quota** | Model deployments, quota usage, usage patterns |
| **Admin** | Projects, users, connected resources |

## Prerequisites

- Azure subscription
- Foundry project
- AI gateway configured (for advanced governance)
- Appropriate RBAC permissions

## IPAI Mapping

| Foundry Control Plane | IPAI Equivalent | Gap |
|----------------------|-----------------|-----|
| Fleet overview dashboard | None | **Gap — need agent fleet dashboard** |
| Asset inventory | AGENT_CAPABILITY_INVENTORY.yaml | Have it, not live/queryable |
| Compliance policies | Constitution + rules files | Static docs, not enforceable policies |
| Cost tracking | None | **Gap — need token/cost tracking** |
| Red teaming | None | **Gap — need automated security testing** |
| Cross-project admin | GitHub org + Supabase ops | Fragmented, not unified |

### What to Adopt

1. **Cost tracking** — Add token usage tracking to ops.run_events
2. **Compliance dashboard** — Surface constitution violations in Superset
3. **Red teaming** — Add adversarial test cases to eval datasets
4. **Fleet inventory** — Sync AGENT_CAPABILITY_INVENTORY.yaml to Supabase ops.skills
