# agents/tax-guru-surface — Tax Guru PH for Microsoft Teams

BIR compliance + Philippine tax queries. Custom engine agent surface.

## Before provisioning

This directory contains only the **agent-specific** files:
- `appPackage/manifest.json`
- `bot/bot.py`
- this README

Copy the shared files from `teams-surface/`:

```bash
cd agents/tax-guru-surface
cp ../teams-surface/teamsapp.yml .
cp -r ../teams-surface/bot/app.py ../teams-surface/bot/requirements.txt bot/
cp -r ../teams-surface/infra .
cp -r ../teams-surface/env .
# Then replace 'pulser' with 'tax-guru-ph' in teamsapp.yml names
sed -i '' 's/pulser-teams/tax-guru-ph/g' teamsapp.yml
```

## Provision

```bash
cp env/.env.dev.example env/.env.dev
# Fill values — use the same ipai-copilot-gateway URL as Pulser
atk provision --env dev
atk deploy   --env dev
atk publish  --env dev
```

## Persona

- **Scope**: BIR (Philippines) compliance, tax forms, deadlines, computations
- **Commands**: `/2550q`, `/2307`, `/1601c`, `/1702`, `/forms`, `/help`
- **Backend**: `ipai-copilot-gateway` with `surface=teams-tax-guru` → Foundry `ipai-copilot` + `claude-sonnet-4-6`
- **Grounding**: 6-tier PH source hierarchy (see memory `project_ph_grounding_hierarchy`)

## Entra Agent ID (May 1 GA)

User-assigned MI to create: `id-ipai-agent-tax-guru` in `rg-ipai-dev-platform`.
Register via Frontier admin flow once provisioned.

## Related

- Parent plan: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
- Streaming rules: [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md)
- Pulser template: [agents/teams-surface/](../teams-surface/)
