# agents/doc-intel-surface — Document Intelligence for Microsoft Teams

Structured extraction from invoices, receipts, IDs, BIR 2307 forms, tax documents. Custom engine agent surface backed by Azure Document Intelligence + MCP pipeline (13 tools).

## Before provisioning

Copy shared files from `teams-surface/` (teamsapp.yml, bot/app.py, bot/requirements.txt, infra/, env/) and substitute `pulser-teams` → `doc-intel` in teamsapp.yml.

```bash
cd agents/doc-intel-surface
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra ../teams-surface/env .
sed -i '' 's/pulser-teams/doc-intel/g' teamsapp.yml
```

## Persona

- **Scope**: Document extraction → structured JSON → optional Odoo upload
- **Commands**: `/invoice`, `/receipt`, `/id`, `/2307`, `/extract`, `/help`
- **Backend**: `ipai-copilot-gateway` with `surface=teams-doc-intel` → Foundry DI pipeline (see memory `project_invoice_pipeline`)
- **Special**: supports file attachments (`supportsFiles: true` in manifest)

## Entra Agent ID (May 1 GA)

MI: `id-ipai-agent-doc-intel` in `rg-ipai-dev-platform`.

## Related

- Parent plan: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
- Streaming rules: [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md)
- Pulser template: [agents/teams-surface/](../teams-surface/)
