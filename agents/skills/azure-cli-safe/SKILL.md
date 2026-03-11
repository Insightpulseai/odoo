# Azure CLI Safe Skill

## Purpose

Interact with Azure resources through the `az` CLI in non-interactive mode.
Specialized for Container Apps, ACR, and Key Vault operations in the IPAI Odoo stack.

## Preconditions

- `az` CLI installed
- Logged in via `az login` or OIDC (`az account show` succeeds)
- Subscription set (`AZURE_SUBSCRIPTION_ID` or `az account set`)
- Target resource group exists

## Critical lesson: REST-first for Container App Jobs

**Problem**: `az containerapp create --args "odoo --db_host ..."` fails because
Azure CLI's argument parser consumes `--` prefixed flags meant for the container.
Multiple workarounds failed: `--command`, YAML escaping, base64 encoding.

**Solution**: Use `az rest --method PUT` with the ARM REST API for Container App
Job create/update/start operations. The REST API accepts JSON bodies where container
commands and args are properly isolated from CLI argument parsing.

**Rule**: Any operation that passes `--` prefixed arguments to a container must
use `az rest`, not `az containerapp`.

## Allowed operations

### Read-only
- `az containerapp show`
- `az containerapp list`
- `az containerapp logs show`
- `az containerapp job show`
- `az containerapp job execution show`
- `az containerapp job execution list`
- `az acr show`
- `az acr repository list`
- `az keyvault secret show` (metadata only — value via `--query value`)
- `az group show`
- `az deployment group show`

### Controlled write
- `az containerapp update --image` (image swap)
- `az containerapp job start` (trigger existing job)
- `az acr build` (build + push image)
- `az rest --method PUT` (Container App Job create/update)
- `az role assignment create` (grant AcrPull to managed identity)

### Health/verification
- `curl -s https://<fqdn>/web/health` (Container App health)
- `az containerapp job execution show --query status` (job completion)

## Disallowed operations

- `az containerapp exec` — requires TTY, not skill-compatible
- `az ssh` — interactive, requires TTY
- `az serial-console` — interactive
- `az group delete` — broad destructive, requires explicit approval
- `az containerapp delete` — destructive without `--yes`
- `az ad sp create-for-rbac` — bootstrap only, not runtime
- `az login` — bootstrap only
- Any command writing secrets to files

## Output contract

- All queries use `-o json` (forced by wrapper)
- Job status polling returns structured: `{ "status": "Succeeded|Failed|Running" }`
- Health checks return HTTP status code

## Verification contract

```bash
# After image update:
FQDN=$(az containerapp show -n <app> -g <rg> --query "properties.configuration.ingress.fqdn" -o tsv)
curl -sf "https://${FQDN}/web/health"

# After job execution:
az containerapp job execution show -n <job> -g <rg> \
  --job-execution-name <exec> --query "properties.status" -o tsv
# Expected: "Succeeded"
```
