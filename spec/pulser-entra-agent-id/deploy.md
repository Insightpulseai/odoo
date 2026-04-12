# Deploy — Pulser Entra Agent ID (Owner-triggered commands)

Everything the code has already landed. This file is the owner-run deployment
script for the automatable half of Phase 2.

## Prereqs

```bash
az login
az account set --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070
# Confirm:
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table
```

## Step 1 — Deploy the 6 agent MIs + grant KV access

```bash
cd /path/to/Insightpulseai

az deployment group create \
  --resource-group rg-ipai-dev-platform \
  --template-file infra/azure/deploy-agent-identities.bicep \
  --parameters env=dev \
  --name agent-identities-dev-$(date +%Y%m%d%H%M)

# Output — capture client+principal IDs into env/.env.dev.<agent>
az deployment group show \
  --resource-group rg-ipai-dev-platform \
  --name agent-identities-dev-<stamp> \
  --query "properties.outputs.agentIdentities.value" -o json
```

Creates:
- `id-ipai-agent-pulser-dev`
- `id-ipai-agent-tax-guru-dev`
- `id-ipai-agent-doc-intel-dev`
- `id-ipai-agent-bank-recon-dev`
- `id-ipai-agent-ap-invoice-dev`
- `id-ipai-agent-finance-close-dev`

Each MI gets `get`/`list` on `kv-ipai-dev` secrets via access policy.

## Step 1b — Deploy the bot-proxy ACA app (public ingress boundary)

**Prereq**: `ipai-copilot-gateway` is internal-only (by design — zero-trust).
The bot-proxy is the **public ingress** for Teams/Copilot Chat webhooks; it
forwards all 6 agents' `/api/*/messages` to the internal gateway.

```bash
# Build and push the image (or trigger CI)
cd apps/bot-proxy
az acr login --name ipaiodoodevacr
docker build -t ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest .
docker push ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest
cd -

# Grab the pulser MI resource ID + clientId from Step 1 outputs
PULSER_MI_ID=$(az identity show -n id-ipai-agent-pulser-dev -g rg-ipai-dev-platform --query id -o tsv)
PULSER_MI_CLIENT=$(az identity show -n id-ipai-agent-pulser-dev -g rg-ipai-dev-platform --query clientId -o tsv)
KV_ID=$(az keyvault show -n kv-ipai-dev -g rg-ipai-dev-platform --query id -o tsv)

# Deploy the bot-proxy container app (ACA env = same as gateway)
az deployment group create \
  --resource-group rg-ipai-dev-odoo-runtime \
  --template-file infra/azure/modules/aca-bot-proxy.bicep \
  --parameters env=dev \
               userAssignedMiResourceId="$PULSER_MI_ID" \
               userAssignedMiClientId="$PULSER_MI_CLIENT" \
               keyVaultResourceId="$KV_ID" \
  --name "bot-proxy-dev-$(date +%Y%m%d%H%M)"

# Capture the external FQDN — feed into Step 2 as gatewayFqdn
PROXY_FQDN=$(az containerapp show -n ipai-bot-proxy-dev -g rg-ipai-dev-odoo-runtime --query properties.configuration.ingress.fqdn -o tsv)
echo "Bot proxy FQDN: $PROXY_FQDN"
```

**Note**: The proxy will start with empty `BOT_ID_*` values until Step 4
(`atk provision`). It will respond 401 to Bot Framework traffic until then,
but `/healthz` returns 200 so AFD probes pass.

**Bot passwords**: after `atk provision` creates the 6 Bot Framework credentials,
seed them into `kv-ipai-dev` as secrets named `bot-password-{agent}` (e.g.
`bot-password-pulser`), then restart the bot-proxy revision to pick them up.

## Step 2 — Deploy 6 AFD routes

First, look up the AFD RG + endpoint name:

```bash
az afd profile show --profile-name afd-ipai-dev \
  --query "{rg:resourceGroup, location:location}" -o table

# If unknown, find it:
az resource list --name afd-ipai-dev --query "[].{rg:resourceGroup, type:type}" -o table
```

Then deploy:

```bash
# Use the bot-proxy FQDN from Step 1b as gatewayFqdn (NOT the internal gateway)
az deployment group create \
  --resource-group rg-ipai-dev-odoo-runtime \
  --template-file infra/azure/deploy-agent-routes.bicep \
  --parameters env=dev \
               afdEndpointName=afd-ipai-dev-ep \
               gatewayFqdn="$PROXY_FQDN" \
  --name "agent-routes-dev-$(date +%Y%m%d%H%M)"
```

Creates 6 routes on the existing `afd-ipai-dev` profile:
| Agent | Pattern |
|---|---|
| pulser | `/api/messages` |
| tax-guru | `/api/tax-guru/messages` |
| doc-intel | `/api/doc-intel/messages` |
| bank-recon | `/api/bank-recon/messages` |
| ap-invoice | `/api/ap-invoice/messages` |
| finance-close | `/api/finance-close/messages` |

All routes share the same origin group (`og-copilot-gateway`) pointing at
`ipai-copilot-gateway.insightpulseai.com`. Traffic is disambiguated server-side
by path prefix.

## Step 3 — Install atk CLI (one-time per dev machine)

```bash
npm install -g @microsoft/m365agentstoolkit-cli
atk --version
```

## Step 4 — Provision each agent in M365 / Teams

For each agent in `{teams-surface, tax-guru-surface, doc-intel-surface, bank-recon-surface, ap-invoice-surface, finance-close-surface}`:

```bash
cd agents/<surface-dir>

# Copy shared files from teams-surface (if not already)
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra ../teams-surface/env .
# Replace the name placeholder in teamsapp.yml:
sed -i '' "s/pulser-teams/$(basename $(pwd) -surface)/g" teamsapp.yml

# Fill env/.env.dev from template (BOT_ID and AAD client IDs will be filled
# by the next command automatically)
cp env/.env.dev.example env/.env.dev

atk provision --env dev
atk deploy --env dev
atk publish --env dev   # sideload to IPAI tenant
```

This creates:
- Entra app registration (for SSO) per agent
- Azure Bot Channel Registration per agent
- Teams app package (`appPackage/build/appPackage.dev.zip`)

## Step 5 — Register Entra Agent ID (Frontier preview — browser UI only)

Cannot be automated. Portal flow:

1. Go to [M365 Admin Center](https://admin.microsoft.com) → Copilot → Settings → Copilot Frontier
2. Grant user access to Frontier program
3. Go to [Admin Center → Agents](https://admin.microsoft.com/#/agents)
4. Register each agent with its Bot Channel Registration ID (from Step 4 output)
5. Confirm 6 agents listed: Pulser, Tax Guru PH, Doc Intelligence, Bank Recon, AP Invoice, Finance Close

## Step 6 — Verify

```bash
# Sanity-check MIs exist
for agent in pulser tax-guru doc-intel bank-recon ap-invoice finance-close; do
  az identity show -n "id-ipai-agent-${agent}-dev" -g rg-ipai-dev-platform \
    --query "{name:name, principalId:principalId}" -o table
done

# Confirm AFD routes
az afd route list --profile-name afd-ipai-dev \
  --endpoint-name <ENDPOINT_NAME> \
  --resource-group <AFD_RG> \
  --query "[?starts_with(name, 'pulser-bot-route') || starts_with(name, 'route-')].{name:name, patternsToMatch:patternsToMatch}" -o table

# Confirm KV access
az keyvault show --name kv-ipai-dev --resource-group rg-ipai-dev-platform \
  --query "properties.accessPolicies[?permissions.secrets != null].[objectId, permissions.secrets]" -o table
```

## Rollback

Each artifact is reversible:

```bash
# Delete the identity deployment (cascades to MIs)
az deployment group delete --resource-group rg-ipai-dev-platform --name agent-identities-dev-<stamp>

# Delete the route deployment (cascades to route/origin-group)
az deployment group delete --resource-group <AFD_RG> --name agent-routes-dev-<stamp>

# Delete the KV access policy entries (if retaining MIs but revoking access)
az keyvault delete-policy --name kv-ipai-dev --object-id <principalId>

# atk cleanup
cd agents/<surface-dir>
atk entra app delete --env dev
atk azure bot delete --env dev
```
