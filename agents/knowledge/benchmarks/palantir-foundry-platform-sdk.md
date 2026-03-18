# Palantir Foundry Platform SDK

> Source: github.com/palantir/foundry-platform-python

## What it is

The official Python SDK for the Palantir Foundry API. Provides programmatic access to Foundry platform capabilities — datasets, transforms, pipelines, and platform administration. This is an **external integration layer** — not part of the Microsoft/GitHub SDK stack, not an orchestration framework, not a channel delivery SDK.

## Critical Naming Disambiguation

| Name | Platform | Company | Relation to us |
|------|----------|---------|----------------|
| **Palantir Foundry** | Palantir's data/analytics platform | Palantir Technologies | External integration, out-of-scope by default |
| **Azure AI Foundry** | Microsoft's AI agent backend | Microsoft | Core platform component, used by M365 Agents SDK |

These are **completely unrelated platforms** from different companies that happen to share the word "Foundry" in their names. Never conflate them.

## Key Capabilities

| Capability | Description |
|-----------|-------------|
| Foundry Platform SDK | REST API access to Foundry datasets, transforms, pipelines, administration |
| Ontology SDK | Higher-level SDK for building applications on Palantir's ontology layer |
| Dataset operations | Read/write Foundry datasets programmatically |
| Transform management | Trigger and monitor Foundry transform pipelines |
| Platform administration | User management, project configuration, resource allocation |

## SDK Selection Guidance

Palantir explicitly distinguishes two SDKs and recommends different ones for different use cases:

| SDK | Use when |
|-----|----------|
| **Foundry Platform SDK** | You need REST API access to Foundry platform capabilities (datasets, transforms, admin) |
| **Ontology SDK** | You are building applications on top of Palantir's ontology layer (object types, actions, functions) |

**Palantir recommends the Ontology SDK** for ontology-based application development. Use the Platform SDK only when you need direct platform API access.

## Role in Our Stack

**External integration only, out-of-scope unless explicitly needed.**

Default status: **out-of-scope**. Only activate this integration path when:
1. A real Palantir Foundry workload exists in the organization
2. The integration requirement has been explicitly documented
3. The integration assessment gate has passed (see skill: `palantir-foundry-integration-assessment`)

## What it is NOT

| Misuse | Correct layer |
|--------|--------------|
| Core agent orchestration | Microsoft Agent Framework (`microsoft/agent-framework`) |
| Channel delivery (Teams, M365 Copilot) | Microsoft 365 Agents SDK (`microsoft/Agents`) |
| Developer coding assistant | GitHub Copilot SDK (`github/copilot-sdk`) |
| Azure AI Foundry (Microsoft) | Completely unrelated — different company, different platform |

## Architecture Position

```
Microsoft Agent Framework    (orchestration)
Microsoft 365 Agents SDK    (channel delivery)
GitHub Copilot SDK          (developer assistance)
Palantir Foundry SDK       <-- THIS (external integration, optional)
```

The Palantir Foundry SDK is optional and external. It does not participate in the core agent stack unless a real Palantir workload requires it.

## Cross-References

- Persona: `agents/personas/external-platform-integrator.md`
- Skill: `agents/skills/palantir-foundry-integration-assessment/`
- Skill map: `agent-platform/ssot/learning/agent_sdk_stack_map.yaml`
