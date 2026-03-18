# Foundry SDK Decision

> Version: 1.0.0
> Canonical repo: `agent-platform`

## Context
The platform requires a centralized, secure, and performant AI runtime connecting Odoo, Databricks, and custom frontend applications. Microsoft Foundry provides both an SDK and an Agent Framework.

## Decision
- **Use the Foundry SDK** as the primary integration layer when building applications that require agents, evaluations, tracing, and Foundry-specific features.
- **Use the Project Endpoint** as the central runtime integration surface.
- **Prefer Entra ID / DefaultAzureCredential** for authentication across all services.
- **Language Support**: Python and .NET are first-class implementation lanes within the `agent-platform` repository.

## Consequences
- Odoo, data pipelines, and custom frontends will interface with AI capabilities exclusively through the Foundry Project Endpoint, maintaining strong isolation.
- Authentication relies strictly on Microsoft Entra ID rather than scattered API keys.
- .NET is supported immediately as an equivalent first-class runtime to Python.
