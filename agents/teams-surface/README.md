# agents/teams-surface — Pulser for Microsoft Teams

> Custom engine agent (Bot Framework proxy) that surfaces Pulser inside
> Microsoft 365 Copilot + Teams, backed by `ipai-copilot-gateway` + Foundry.

## Architecture

```
Teams / Copilot Chat  →  Bot Framework  →  THIS APP  →  ipai-copilot-gateway (ACA)
                                            (proxy)      → Foundry ipai-copilot
                                                         → Odoo JSON-RPC
                                                         → Plane / ops.* Postgres
```

This is the **custom engine agent** integration path (Agents Toolkit proxy),
NOT a declarative agent. Chosen because IPAI needs:

- Custom Entra SSO (`apps/odoo-connector/src/auth/entra-oauth.ts`)
- Multi-environment (dev/staging/prod ACA apps)
- BYO orchestration (`ipai-copilot-gateway` owns the agent loop)
- Access to Microsoft Graph + Retrieval API for M365 grounding

## Prereqs

- Python 3.11+
- Azure CLI (`az login`)
- `atk` CLI: `npm install -g @microsoft/m365agentstoolkit-cli`
- M365 Copilot license on tenant + (optional) Frontier preview enrollment for Agent 365

## Local dev

```bash
# Install deps
pip install -r bot/requirements.txt

# Launch M365 Agents Playground (local sandbox — no Teams / ngrok / bot registration)
npx @microsoft/teams-app-test-tool start --manifest appPackage/manifest.json

# Run the bot (listens on :3978)
python bot/app.py
```

Playground URL appears in the terminal — paste into a browser to chat with Pulser locally.

## Provision to Azure (dev)

```bash
cp env/.env.dev.example env/.env.dev
# Fill: ENTRA_TENANT_ID, ENTRA_CLIENT_ID, COPILOT_GATEWAY_URL, etc.

atk provision --env dev
atk deploy --env dev
atk publish --env dev   # sideload to tenant for UAT
```

`atk provision` creates:
- **Azure Bot Channel Registration** (globally, not in an RG)
- **Entra App Registration** (for the bot identity)
- **Teams app package** (`appPackage/build/appPackage.dev.zip`)

Connection to `ipai-copilot-gateway` uses managed identity (`id-ipai-dev`,
principalId `1aee831f-3813-4eed-b49c-f7665330f0f6`) via Foundry SDK 2.x.

## Files

| Path | Purpose |
|---|---|
| `teamsapp.yml` | `atk` lifecycle (provision/deploy/publish) |
| `teamsapp.playground.yml` | Local Playground lifecycle |
| `appPackage/manifest.json` | Teams app manifest (v1.21 — required for custom engine agents) |
| `bot/app.py` | aiohttp server + Bot Framework adapter |
| `bot/bot.py` | Activity handler — proxies to `ipai-copilot-gateway /chat` |
| `bot/requirements.txt` | botbuilder-* SDKs + azure-identity |
| `infra/azure.bicep` | Supplemental Bicep (Bot Channel Registration reference) |
| `env/.env.dev.example` | Env template — secrets from `kv-ipai-dev` |

## Streaming contract

See [docs/skills/m365-copilot-streaming-contract.md](../../docs/skills/m365-copilot-streaming-contract.md) for the
message ordering rules (single `StreamingResponse` per turn, `endStream()`
before additional messages, media via `setAttachments()` inside stream).

## AFD routing

`/api/messages` must be routed through Azure Front Door to the
`ipai-copilot-gateway` origin group. See
[infra/azure/modules/bot-route.bicep](../../infra/azure/modules/bot-route.bicep).

## Links

- [Custom engine agent overview](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-custom-engine-agent)
- [Agents Toolkit](https://learn.microsoft.com/en-us/microsoft-365/developer/overview-m365-agents-toolkit)
- [M365 Agents SDK](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/m365-agents-sdk)
- Spec: [spec/pulser-entra-agent-id/](../../spec/pulser-entra-agent-id/)
