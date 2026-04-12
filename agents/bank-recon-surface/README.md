# agents/bank-recon-surface — Bank Reconciliation for Microsoft Teams

Reconciles bank statements against Odoo `account.move` entries.

## Before provisioning

Copy shared files from `teams-surface/`:

```bash
cd agents/bank-recon-surface
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra ../teams-surface/env .
sed -i '' 's/pulser-teams/bank-recon/g' teamsapp.yml
```

## Persona

- **Scope**: Import bank statements (OFX, CSV, PDF) → match against Odoo moves → propose reconciliations
- **Commands**: `/match`, `/unreconciled`, `/stmt`, `/summary`, `/banks`, `/help`
- **Backend**: `ipai-copilot-gateway` with `surface=teams-bank-recon` → Odoo JSON-RPC + reconciliation rules engine
- **Files**: accepts OFX/CSV/PDF uploads

## Entra Agent ID (May 1 GA)

MI: `id-ipai-agent-bank-recon` in `rg-ipai-dev-platform`.

## Related

- Parent plan: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
- Streaming rules: [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md)
- Pulser template: [agents/teams-surface/](../teams-surface/)
