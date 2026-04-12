# Tasks — Pulser Entra Agent ID rollout

> Draft. Deadline 2026-05-01. Ordered by phase. Check boxes as work lands.

## Phase 0 — Pre-flight

- [ ] T0.1  (Owner) Confirm M365 Copilot license on tenant
- [ ] T0.2  (Owner) Enroll in Frontier preview program at https://adoption.microsoft.com/copilot/frontier-program/
- [ ] T0.3  (Owner) Revoke global `vscode` PAT; follow `docs/security/revoke-pat-runbook.md`
- [ ] T0.4  (Owner) Run `scripts/azure/migrate-variable-groups.sh`; grant `id-ipai-dev` KV access
- [ ] T0.5  (Owner) Inspect `ipai-foundry-eval` ADO variable group (2 unknown vars) in portal

## Phase 1 — Pulser as canonical template

- [x] T1.1  (Code) Scaffold `agents/teams-surface/` — manifest v1.21, bot/app.py, teamsapp.yml, env/
- [x] T1.2  (Code) Write `infra/azure/modules/bot-route.bicep` — AFD `/api/messages` route
- [x] T1.3  (Code) Write `docs/skills/m365-copilot-streaming-contract.md` — message-ordering rules
- [ ] T1.4  (Owner) Install `atk` CLI: `npm install -g @microsoft/m365agentstoolkit-cli`
- [ ] T1.5  (Code + Owner) `cp env/.env.dev.example env/.env.dev` + fill values
- [ ] T1.6  (Code) `atk provision --env dev` — creates pulser-teams-bot-dev + Entra app reg + Bicep deploy
- [ ] T1.7  (Code) Deploy `bot-route.bicep` via `main.bicep` or standalone `az deployment group create`
- [ ] T1.8  (QA) Start Agents Playground: `npx @microsoft/teams-app-test-tool start --manifest agents/teams-surface/appPackage/manifest.json` and verify roundtrip
- [ ] T1.9  (CI) Deploy bot code to `ipai-copilot-gateway` ACA via `.github/workflows/deploy-erp-canonical.yml`
- [ ] T1.10 (Owner) Sideload Teams app package to IPAI tenant — `atk publish --env dev`
- [ ] T1.11 (Owner) Register first Entra Agent ID for Pulser via Frontier admin flow

## Phase 2 — Replicate template for 5 more agents

For each agent name in `{tax-guru, doc-intel, bank-recon, ap-invoice, finance-close}`:

- [x] T2.`<name>`.1  (Code) Scaffold `agents/<name>-surface/` — README + agent-specific files. Owner copies shared files from teams-surface per README's cp + sed recipe.
- [x] T2.`<name>`.2  (Code) `appPackage/manifest.json` v1.21 — per-agent name, description, commands, accent color
- [x] T2.`<name>`.3  (Code) `bot/bot.py` — per-agent SURFACE_TAG, WELCOME, persona wiring, file handling (where applicable)
- [x] T2.`<name>`.4  (Code) Bicep for all 6 MIs: `infra/azure/deploy-agent-identities.bicep` — Owner runs `az deployment group create --resource-group rg-ipai-dev-platform --template-file ...` (one command, all 6)
- [ ] T2.`<name>`.5  (Owner) `atk provision --env dev` — interactive, cannot automate. See [deploy.md §Step 4](./deploy.md)
- [x] T2.`<name>`.6  (Code) Bicep for all 6 AFD routes: `infra/azure/deploy-agent-routes.bicep` — Owner runs `az deployment group create` against the AFD RG. See [deploy.md §Step 2](./deploy.md)
- [ ] T2.`<name>`.7  (Owner) Register Entra Agent ID via M365 Admin Center — browser UI, cannot automate. See [deploy.md §Step 5](./deploy.md)

## Phase 3 — Hardening

- [ ] T3.1  (Security) Create Conditional Access policy — agent MIs restricted to `api://ipai-copilot-gateway/.default` scope
- [ ] T3.2  (Security) Defender for Cloud alert rule — unusual agent activity → Slack/Teams oncall
- [ ] T3.3  (Security) Purview audit rule — log every agent action with OBO user chain
- [ ] T3.4  (Owner) Post-GA: revert per-agent Frontier licenses → per-user M365 E7 / Agent 365

## Exit criteria

- All 6 agents listed in M365 Admin Center → Agents ✓
- Each agent visible to Defender + Purview ✓
- No `AZURE_CLIENT_SECRET` plaintext in git ✓
- AFD routes: `pulser-bot-route`, `tax-guru-bot-route`, `doc-intel-bot-route`, `bank-recon-bot-route`, `ap-invoice-bot-route`, `finance-close-bot-route` ✓
- Streaming contract (5 rules) verified in code review for every agent ✓

## References

- `constitution.md`, `prd.md`, `plan.md`
- `agents/teams-surface/README.md`
- `infra/azure/modules/bot-route.bicep`
- `docs/skills/m365-copilot-streaming-contract.md`
- `docs/security/revoke-pat-runbook.md`
