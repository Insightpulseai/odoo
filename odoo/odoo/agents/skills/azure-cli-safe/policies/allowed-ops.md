# Allowed Operations — Azure CLI

## Read-only (always safe)

- `az containerapp show -n <app> -g <rg>`
- `az containerapp list -g <rg>`
- `az containerapp logs show -n <app> -g <rg>`
- `az containerapp job show -n <job> -g <rg>`
- `az containerapp job execution show -n <job> -g <rg> --job-execution-name <exec>`
- `az containerapp job execution list -n <job> -g <rg>`
- `az acr show -n <acr>`
- `az acr repository list -n <acr>`
- `az keyvault secret show --vault-name <kv> -n <secret>`
- `az group show -n <rg>`
- `az deployment group show -g <rg> -n <name>`

## Controlled write (requires verification after)

- `az containerapp update --name <app> --resource-group <rg> --image <ref>`
- `az containerapp job start -n <job> -g <rg>`
- `az acr build --registry <acr> --image <ref> --file <dockerfile> .`
- `az rest --method PUT --url <arm-url> --body <json>` (Container App Jobs)
- `az role assignment create --assignee <id> --role AcrPull --scope <acr-id>`

## Blocked by default

- `az containerapp exec` — requires TTY
- `az ssh` — interactive
- `az serial-console` — interactive
- `az group delete` — broad destructive (set AZ_SAFE_ALLOW_DELETE=1 to override)
- `az containerapp delete` — destructive
- `az ad sp create-for-rbac` — bootstrap only
- `az login` — bootstrap only

## Known CLI pitfalls

### Container App Job argument parsing

`az containerapp job create --args "odoo --db_host X"` fails because Azure CLI
interprets `--db_host` as its own flag. Use `az rest` with ARM JSON instead.

### Container App exec requires TTY

`az containerapp exec` calls `tty.setcbreak()` which fails in non-interactive
environments with `Operation not supported by device`.
