# Azure Samples Usage Policy

> Version: 1.0.0
> Canonical repo: `templates`

## Context
Microsoft publishes significant reference material inside the `Azure-Samples` organization containing quickstarts and starter templates. 

## Decision
- Treat `Azure-Samples` strictly as a reference library and implementation cookbook, **not** as the primary architectural doctrine.
- Repositories from `Azure-Samples` **do not** override the core Platform Cloud Adoption Framework (CAF) model, Azure Landing Zone (ALZ) structure, or repository taxonomy defined in this organization.

## Consequences
- The platform borrows concrete AI capabilities (e.g., Azure AI Search or Azure OpenAI ingestion patterns) from `Azure-Samples`.
- Top-level repository structures and environment bootstrapping will be based on local Azure DevOps pipelines and Enterprise Scale blueprints, preventing sample logic from dictating networking or identity constraints.
