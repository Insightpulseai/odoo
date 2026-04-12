# PAT Revocation Runbook
# dev.azure.com/insightpulseai

## Step 1 — Open PAT management (click this URL)
https://dev.azure.com/insightpulseai/_usersSettings/tokens

## Step 2 — For each PAT listed:
- Click the "..." menu next to it
- Select "Revoke"
- Confirm
- Repeat for ALL tokens, especially any with:
  - Scope: "All accessible organizations" (global PAT — retired Dec 2025)
  - Expiry: None / > 30 days
  - Name: n8n, vercel, supabase, cloudflare, old-ci (all deprecated stacks)

## Step 3 — Replace VS Code PAT with Entra auth
```bash
# Run this in your terminal — authenticates VS Code to ADO via Entra (no PAT)
az devops configure --defaults organization=https://dev.azure.com/insightpulseai
az devops login
# → Select "Entra ID / work account" when prompted
# → DO NOT create a new PAT
```

## Step 4 — Replace ipai-build-agent PAT (if it has one)
```bash
# The build agent should use workload identity federation, not PATs
# Check current auth method:
az pipelines agent list \
  --org https://dev.azure.com/insightpulseai \
  --pool-name "ipai-build-agent" \
  --query "[].{name:name, status:status}" \
  -o table

# If using PAT, migrate to managed identity service connection:
az devops service-endpoint create \
  --org https://dev.azure.com/insightpulseai \
  --project ipai-platform \
  --service-endpoint-configuration @- << 'EOF'
{
  "name": "ipai-build-agent-mi",
  "type": "azurerm",
  "authorization": {
    "scheme": "WorkloadIdentityFederation",
    "parameters": {
      "tenantid": "402de71a-87ec-4302-a609-fb76098d1da7",
      "serviceprincipalid": "1aee831f-3813-4eed-b49c-f7665330f0f6"
    }
    // id-ipai-dev user-assigned MI in rg-ipai-dev-odoo-runtime
    // clientId: 2d9a8328-c8cb-47fc-ba4e-01c1cf9b75d8
  },
  "data": {
    "subscriptionId": "536d8cf6-89e1-4815-aef3-d5f2c5f4d070",
    "subscriptionName": "Azure subscription 1",
    "environment": "AzureCloud",
    "scopeLevel": "Subscription"
  }
}
EOF
```

## Step 5 — Set PAT policies to prevent recreation
Organization settings → Policies (do this in the portal):
https://dev.azure.com/insightpulseai/_settings/policy

Enable:
- ✅ Restrict creation of global PATs (tenant policy — prevents all-org tokens)
- ✅ Enforce maximum PAT lifespan: 30 days
- ✅ Restrict full-scoped PATs

## Step 6 — Verify devops@insightpulseai.com account
```bash
# This account was added 3/23/2026 and has NEVER accessed ADO (Stakeholder)
# It was likely a service account for n8n or another deprecated integration
# If no current use: remove it
az devops user remove \
  --org https://dev.azure.com/insightpulseai \
  --user devops@insightpulseai.com
```

## Step 7 — Git credential manager (local dev)
```bash
# Ensures local git uses Entra, not a stored PAT
git credential-manager configure
# → Set "github.com" to use OAuth
# → Set "dev.azure.com" to use OAuth (browser-based Entra login)

# Clear any cached PAT credentials:
git credential-manager erase <<EOF
protocol=https
host=dev.azure.com
username=insightpulseai
EOF
```
