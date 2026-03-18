# Skill: Azure Foundry Hosted Agents

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-hosted-agents` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra, foundry |
| **tags** | hosted-agents, containers, deployment, scaling, frameworks |

---

## What It Is

Containerized agent applications deployed on Foundry Agent Service. You write the code (any framework), Foundry manages the runtime, scaling, and infrastructure. Currently in public preview.

## Supported Frameworks

- Microsoft Agent Framework
- LangGraph
- Custom code (any HTTP-compatible framework)

## Lifecycle

`create → start → update → stop → delete`

Each phase has specific capabilities and status transitions.

## Region Availability

Supported in **Southeast Asia** — compatible with IPAI's Azure region (`rg-ipai-dev`).

Also: East US, East US 2, West US, West US 3, Canada East/Central, France Central, Germany West Central, Sweden Central, UK South, Japan East, Australia East, and more.

## Security

- Don't put secrets in container images or env vars — use managed identities + Key Vault
- Review data sharing policies for any non-Microsoft service connected
- No private networking support during preview

## IPAI Relevance

| Hosted Agent Concept | IPAI Equivalent |
|---------------------|-----------------|
| Container deployment | Azure Container Apps (`ipai-odoo-dev-*`) |
| Managed scaling | ACA auto-scaling (already configured) |
| Framework flexibility | Claude Agent SDK / custom Python |
| Lifecycle management | ACA revision management |

### Key Difference

Foundry hosted agents add: managed observability, auto-identity provisioning, one-click Teams/M365 publishing, and integrated eval. ACA gives more infrastructure control but requires manual setup of these features.

### Decision: When to use Foundry Hosted vs ACA Direct

| Use Case | Choose |
|----------|--------|
| User-facing copilot with Teams/M365 distribution | Foundry Hosted |
| Background Odoo automation (cron, worker) | ACA Direct |
| Multi-agent reasoning with eval | Foundry Hosted |
| Simple webhook/integration routing | ACA Direct (or n8n) |
