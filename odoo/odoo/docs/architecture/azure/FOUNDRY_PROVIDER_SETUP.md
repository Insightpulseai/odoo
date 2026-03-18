# Azure AI Foundry Provider Setup for Claude Code

> Configuration reference for routing Claude Code through Azure AI Foundry.
> Covers environment variables, auth options, RBAC requirements, and Key Vault integration.
>
> Last updated: 2026-03-14

---

## Environment Variables

### Minimal Configuration

```bash
CLAUDE_CODE_USE_FOUNDRY=1
ANTHROPIC_FOUNDRY_RESOURCE=data-intel-ph-resource
```

### Alternative: Explicit Base URL

```bash
CLAUDE_CODE_USE_FOUNDRY=1
ANTHROPIC_FOUNDRY_BASE_URL=https://data-intel-ph-resource.services.ai.azure.com/anthropic
```

The `ANTHROPIC_FOUNDRY_RESOURCE` shorthand is preferred. Use `ANTHROPIC_FOUNDRY_BASE_URL` only when the resource name alone is insufficient (e.g., custom endpoints or proxy configurations).

---

## Auth Options

### Option 1: API Key

```bash
ANTHROPIC_FOUNDRY_API_KEY=<key-from-key-vault>
```

Retrieve from Azure Key Vault:

```bash
az keyvault secret show --vault-name kv-ipai-dev --name azure-ai-foundry-api-key --query value -o tsv
```

Use this option for: local development, CI/CD pipelines, environments without Azure AD integration.

### Option 2: Azure Credential Chain

No API key variable needed. Claude Code uses the Azure credential chain automatically when `CLAUDE_CODE_USE_FOUNDRY=1` is set and no API key is provided.

Supported credential sources (in order):

1. **`az login`** -- interactive login for local development
2. **`DefaultAzureCredential`** -- automatic chain (environment, managed identity, CLI, etc.)
3. **Managed identity** -- for Azure-hosted compute (Container Apps, VMs, Functions)

```bash
# Local: ensure you are logged in
az login

# Then just set the Foundry flag and resource
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=data-intel-ph-resource
```

Use this option for: Azure-hosted workloads, devcontainers with `az login`, environments where managed identity is available.

---

## Required RBAC

Both roles must be assigned on the Foundry resource for the identity (user, service principal, or managed identity) invoking Claude Code.

| Role | Resource | Purpose |
|------|----------|---------|
| **Azure AI User** | `data-intel-ph-resource` | Permits model invocation via the Foundry API |
| **Cognitive Services User** | `data-intel-ph-resource` | Permits API access to cognitive services endpoints |

### Assigning Roles

```bash
# Get the resource ID
RESOURCE_ID=$(az cognitiveservices account show \
  --name data-intel-ph-resource \
  --resource-group rg-data-intel-ph \
  --query id -o tsv)

# Assign Azure AI User
az role assignment create \
  --assignee <principal-id> \
  --role "Azure AI User" \
  --scope "$RESOURCE_ID"

# Assign Cognitive Services User
az role assignment create \
  --assignee <principal-id> \
  --role "Cognitive Services User" \
  --scope "$RESOURCE_ID"
```

---

## Current Foundry Resources

| Resource | Resource Group | Type | Purpose |
|----------|---------------|------|---------|
| `data-intel-ph-resource` | `rg-data-intel-ph` | Cognitive Services account | Main AI services account (Claude, other models) |
| `aifoundry-ipai-dev` | `rg-ipai-ai-dev` | AI Foundry workspace | AI Foundry workspace for model management |
| `proj-ipai-claude` | `rg-ipai-ai-dev` | AI Foundry project | Claude-specific project within the workspace |
| `oai-ipai-dev` | `rg-ipai-ai-dev` | OpenAI account | OpenAI models (GPT-4o, embeddings) |

### Resource Relationships

```
rg-data-intel-ph
  └── data-intel-ph-resource (Cognitive Services — Claude endpoint)

rg-ipai-ai-dev
  ├── aifoundry-ipai-dev (AI Foundry workspace)
  │   └── proj-ipai-claude (Claude project)
  └── oai-ipai-dev (OpenAI account)
```

---

## Key Vault Integration

All Foundry-related secrets are stored in `kv-ipai-dev` (resource group `rg-ipai-devops`).

| Secret Name | Purpose |
|-------------|---------|
| `azure-ai-foundry-api-key` | API key for `data-intel-ph-resource` |
| `azure-ai-foundry-endpoint` | Foundry endpoint URL |
| `azure-ai-foundry-openai-endpoint` | OpenAI-compatible endpoint URL |
| `azure-ai-foundry-agent-id` | Agent ID for Foundry agent runtime |

### Retrieving Secrets

```bash
# API key
az keyvault secret show --vault-name kv-ipai-dev --name azure-ai-foundry-api-key --query value -o tsv

# Endpoint
az keyvault secret show --vault-name kv-ipai-dev --name azure-ai-foundry-endpoint --query value -o tsv

# OpenAI endpoint
az keyvault secret show --vault-name kv-ipai-dev --name azure-ai-foundry-openai-endpoint --query value -o tsv

# Agent ID
az keyvault secret show --vault-name kv-ipai-dev --name azure-ai-foundry-agent-id --query value -o tsv
```

### CI/CD Usage

In Azure DevOps pipelines, these secrets are accessed via Key Vault-backed variable groups (`vg-ipai-platform-secrets`). In GitHub Actions, they are stored as repository or organization secrets and injected via `env:` blocks in workflow YAML.

Never echo, log, or hardcode these values. Use `${SECRET:0:15}` prefix display for debugging only.

---

## Verification

After configuration, verify the Foundry connection:

```bash
# Confirm environment
echo "CLAUDE_CODE_USE_FOUNDRY=$CLAUDE_CODE_USE_FOUNDRY"
echo "ANTHROPIC_FOUNDRY_RESOURCE=$ANTHROPIC_FOUNDRY_RESOURCE"

# Verify Azure login (if using credential chain)
az account show --query '{subscription: name, user: user.name}' -o table

# Verify RBAC assignments
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az cognitiveservices account show --name data-intel-ph-resource --resource-group rg-data-intel-ph --query id -o tsv) \
  --query '[].roleDefinitionName' -o table
```

Expected output should show both `Azure AI User` and `Cognitive Services User` roles assigned.
