# apps/bot-proxy — Pulser Bot Framework proxy

> Single ACA container app (**external ingress**) that hosts Bot Framework
> webhook endpoints for all 6 IPAI agents. Forwards chat activities to
> the internal `ipai-copilot-gateway` via its ACA-VNet DNS name.
>
> This is the **public ingress boundary** for Teams / M365 Copilot Chat
> traffic. The `ipai-copilot-gateway` itself stays internal-only —
> narrowest possible attack surface.

## Routes

| Path | Agent | Gateway endpoint |
|---|---|---|
| `/api/messages` | pulser | `/chat` |
| `/api/tax-guru/messages` | tax-guru | `/chat` |
| `/api/doc-intel/messages` | doc-intel | `/extract` (files) |
| `/api/bank-recon/messages` | bank-recon | `/chat` |
| `/api/ap-invoice/messages` | ap-invoice | `/chat` |
| `/api/finance-close/messages` | finance-close | `/chat` |
| `/healthz` | — | (internal health probe) |

All routes preserve the Bot Framework `Authorization` header and stream
NDJSON responses back to the client, matching the streaming contract in
[docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md).

## Local dev

```bash
cd apps/bot-proxy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Required env — normally injected by ACA (see infra/azure/modules/aca-bot-proxy.bicep)
export COPILOT_GATEWAY_URL=http://localhost:8088
export BOT_ID_PULSER=... BOT_PASSWORD_PULSER=...
# (set the other 5 per-agent creds too, or leave empty to accept anonymous for local smoke tests)

python -m src.main
```

The M365 Agents Playground (`npx @microsoft/teams-app-test-tool`) can
connect to `http://localhost:8088/api/messages` directly for local chat
testing without a Bot Channel Registration.

## Build + push image

```bash
az acr login --name acripaiodoo
docker build -t acripaiodoo.azurecr.io/ipai-bot-proxy:latest .
docker push acripaiodoo.azurecr.io/ipai-bot-proxy:latest
```

## Deploy to ACA

```bash
az deployment group create \
  --resource-group rg-ipai-dev-odoo-runtime \
  --template-file ../../infra/azure/modules/aca-bot-proxy.bicep \
  --parameters env=dev \
               userAssignedMiResourceId=<id-ipai-agent-pulser-dev resource ID> \
               userAssignedMiClientId=<id-ipai-agent-pulser-dev clientId> \
               botIds='{"PULSER":"<from atk>","TAX_GURU":"","DOC_INTEL":"","BANK_RECON":"","AP_INVOICE":"","FINANCE_CLOSE":""}' \
  --name ipai-bot-proxy-dev-$(date +%Y%m%d%H%M)
```

Outputs the external FQDN — feed that into
`infra/azure/deploy-agent-routes.bicep` `gatewayFqdn` param so AFD
routes forward `/api/*/messages` traffic to this proxy.

## Architecture

```
Teams / Copilot Chat
     │ HTTPS (public)
     ▼
Azure Front Door (afd-ipai-dev)
     │ route: /api/<agent>/messages
     ▼
apps/bot-proxy  ← THIS APP (external ingress ACA, :8088)
     │ Bot Framework adapter per agent
     │ NDJSON stream to ↓
     ▼
ipai-copilot-gateway (internal ACA, :8088)
     │ Foundry SDK 2.x
     ▼
ipai-copilot-resource (Foundry) → claude-sonnet-4-6
```

## Security posture

- **External surface**: just the 6 `/api/*/messages` paths + `/healthz`.
  Every other gateway endpoint stays internal.
- **Auth**: Bot Framework JWT validates inbound requests. Invalid tokens
  are rejected by `BotFrameworkAdapter.process_activity` before the
  handler runs.
- **Outbound**: Managed identity (`id-ipai-agent-pulser-dev`) acquires a
  bearer token for `api://ipai-copilot-gateway/.default`. No shared
  secrets, no PATs.
- **No file storage**: files referenced by URL only; proxy never
  downloads or stores content. Extraction happens gateway-side.
