# Skill: Azure Foundry Agent Identity

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-agent-identity` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra |
| **tags** | identity, entra, rbac, authentication, managed-identity |

---

## What It Is

Agent Identity is a specialized identity type in Microsoft Entra ID for AI agents. Provides standardized governance, authentication, and authorization. Foundry auto-provisions and manages identities throughout the agent lifecycle.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Agent Identity** | Entra service principal representing the agent at runtime |
| **Agent Identity Blueprint** | Template/class governing a category of agents (e.g., "Contoso Sales Agent") |
| **Shared Project Identity** | All unpublished agents in a project share one identity |
| **Distinct Agent Identity** | Published agents get their own identity + blueprint |

## Authentication Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Attended (OBO)** | Agent acts on behalf of a human user via delegated permissions | User-facing copilots |
| **Unattended** | Agent acts under its own authority via app-assigned roles | Background automation, SRE agents |

## Lifecycle

1. Create first agent in project → auto-provisions shared identity
2. Develop + test → all agents use shared project identity
3. Publish → auto-creates distinct identity + blueprint
4. Reassign RBAC roles to new distinct identity
5. Manage via Entra admin center → Conditional Access, governance

## Tool Authentication

| Tool | Auth Method |
|------|-------------|
| MCP servers | Agent identity (Entra), key-based, OAuth passthrough |
| OpenAPI tools | Anonymous, API key, managed identity |
| A2A | Agent identity |
| Built-in (Code Interpreter, File Search) | Auto — no config needed |

## IPAI Relevance

| Foundry Pattern | IPAI Current | Gap |
|-----------------|-------------|-----|
| Entra agent identity | Keycloak (transitional) → Entra (target) | Identity migration not yet started |
| Auto-provisioned identity | Manual service principal creation | **Gap — need auto-provisioning** |
| OBO flow | Not implemented | **Gap — needed for user-facing copilot** |
| Blueprint governance | No equivalent | **Gap — need agent class management** |
| Shared project identity | N/A | Useful for dev, distinct for prod |

### Migration Path

1. Complete Keycloak → Entra migration (prerequisite)
2. Register ipai-odoo-copilot-azure as Entra agent identity blueprint
3. Configure OBO flow for Odoo Discuss copilot channel
4. Set up Conditional Access policies for agent identities
5. Assign least-privilege RBAC per tool per agent
