# Azure Connector

Wrapper for Azure service interactions used by automation jobs.

## Scope

- Azure Key Vault (secret retrieval)
- Azure Container Apps (deployment status, scaling)
- Azure Resource Graph (resource inventory queries)
- Azure DevOps (pipeline trigger, work item sync)

## Auth

Uses Managed Identity or `DefaultAzureCredential` chain.
Never hardcode service principal secrets. Secrets resolved from Key Vault.

<!-- TODO: Implement base connector with DefaultAzureCredential and retry -->
