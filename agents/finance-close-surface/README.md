# agents/finance-close-surface — Monthly Close for Microsoft Teams

Orchestrate Odoo monthly close — checklist, status, variance review.

## Before provisioning

Copy shared files from `teams-surface/`:

```bash
cd agents/finance-close-surface
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra ../teams-surface/env .
sed -i '' 's/pulser-teams/finance-close/g' teamsapp.yml
```

## Persona

- **Scope**: Run the monthly close checklist (see memory `project_monthly_close_checklist`), check status, investigate variances, reopen period if needed
- **Commands**: `/status`, `/checklist`, `/close`, `/reopen`, `/variance`, `/help`
- **Backend**: `ipai-copilot-gateway` with `surface=teams-finance-close` → Odoo `account.period` API + variance reports

## Entra Agent ID (May 1 GA)

MI: `id-ipai-agent-finance-close` in `rg-ipai-dev-platform`.

## Related

- Parent plan: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
- Streaming rules: [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md)
- Pulser template: [agents/teams-surface/](../teams-surface/)
