# agents/ap-invoice-surface — AP Invoice processing for Microsoft Teams

Process incoming vendor invoices — create draft bills in Odoo.

## Before provisioning

Copy shared files from `teams-surface/`:

```bash
cd agents/ap-invoice-surface
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra ../teams-surface/env .
sed -i '' 's/pulser-teams/ap-invoice/g' teamsapp.yml
```

## Persona

- **Scope**: Upload vendor invoice PDF → extract → create `account.move` draft in Odoo → route for approval
- **Commands**: `/process`, `/pending`, `/approve`, `/reject`, `/vendor`, `/help`
- **Backend**: `ipai-copilot-gateway` with `surface=teams-ap-invoice` → Doc Intelligence extraction + Odoo JSON-RPC
- **Dependencies**: Doc Intelligence agent (for extraction); Odoo `account` module

## Entra Agent ID (May 1 GA)

MI: `id-ipai-agent-ap-invoice` in `rg-ipai-dev-platform`.

## Related

- Parent plan: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
- Streaming rules: [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md)
- Pulser template: [agents/teams-surface/](../teams-surface/)
