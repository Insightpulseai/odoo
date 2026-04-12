# PRD — Pulser Entra Agent ID rollout

> Draft. Target: complete before 2026-05-01 (Agent 365 GA).

## Problem

At Microsoft Agent 365 general availability (May 1, 2026), every AI agent
running in a Microsoft 365 tenant must have its own **Entra Agent ID** for
identity, lifecycle, access management, observability, and threat protection.

IPAI currently runs agents (Pulser, Tax Guru PH, Doc Intelligence, Bank
Recon, AP Invoice, Finance Close) through a single managed identity
(`id-ipai-dev`). Without per-agent Entra IDs at GA:

- Agents will not appear in the M365 Admin Center agent registry
- Purview cannot audit agent actions per-agent
- Defender cannot scope threat detection per-agent
- Conditional Access policies cannot target specific agents
- Future M365 E7 OBO licensing coverage is unclear

## Goals

| # | Goal | Success criterion |
|---|---|---|
| 1 | Every production agent has its own Entra Agent ID by 2026-05-01 | All 6+ agents visible in M365 Admin Center → Agents |
| 2 | Zero client secrets in code or config | `grep -r AZURE_CLIENT_SECRET` returns only env var refs |
| 3 | Per-agent observability via native M365 tooling | Purview audit trail shows agent → user OBO chain |
| 4 | Agents Toolkit-packaged Teams surface for each agent | `appPackage/manifest.json` v1.21 validates |
| 5 | Bot route `/api/messages` behind AFD per agent | AFD route exists for pulser-bot-route, tax-guru-bot-route, etc. |

## Non-goals

- Migrating off `ipai-copilot-gateway` as the orchestrator (it's the custom engine)
- Adopting Copilot Studio (low-code path — wrong model)
- Rewriting existing agent logic — only adding the identity wrapper

## Users

| Persona | Need |
|---|---|
| Finance team (CKVC/RIM/BOM + 8) | Ask Pulser in Teams about BIR, invoices, reconciliation |
| Tax reviewer | Ask Tax Guru PH about 2550Q, 1601C, 2307 etc. from Outlook |
| Ops admin | See all IPAI agents in M365 Admin Center, review their activity |
| Security team | Apply Conditional Access to agent identities; Defender alerts per agent |

## Scope

### In scope

- Create 6 user-assigned MIs: `id-ipai-agent-pulser`, `id-ipai-agent-tax-guru`,
  `id-ipai-agent-doc-intel`, `id-ipai-agent-bank-recon`,
  `id-ipai-agent-ap-invoice`, `id-ipai-agent-finance-close`
- Register each as an Entra Agent ID via Agent 365 admin flow
- Package each as a Teams custom engine agent (Agents Toolkit)
- Wire `/api/messages` routes through AFD per agent
- Attach Application Insights per agent for telemetry bridging

### Out of scope

- Migrating from the shared `ipai-copilot-gateway` backend — each agent
  still calls the gateway; only the *identity* fronting the bot is per-agent
- Retiring the `ops.agent_runs` table (supplemental, not authoritative)

## Licensing

| Phase | Model | Source |
|---|---|---|
| Pre-GA (Frontier preview) | Per-agent license, max 25 per tenant | MS Learn — Agent 365 FAQ |
| Post-GA (2026-05-01+) | Per-user — agents covered by user's Agent 365 or M365 E7 license OBO | Same |

**Action:** enroll tenant in Frontier preview to start registering agents
before GA. Buy `Microsoft 365 Copilot` license if not already held.

## Success metrics

- **6/6 agents** registered in M365 Admin Center → Agents by 2026-05-01
- **100%** of agent activity visible in Purview audit log with OBO user chain
- **Zero** `AZURE_CLIENT_SECRET` plaintext in git
- **P0 alerts** wired from Defender for Cloud → on-call (Slack/Teams channel)

## Open questions

- [ ] One MI per agent per environment, or one MI per agent shared across envs? (implications for KV access policies)
- [ ] Custom domain strategy — `pulser-dev.insightpulseai.com` per-agent or a single `agents.insightpulseai.com` with path-based routing?
- [ ] Do we participate in Frontier preview (pre-GA access) or wait for GA?

## Dependencies

- `agents/teams-surface/` scaffold complete (done — this spec's companion work)
- `infra/azure/modules/bot-route.bicep` available (done — additive)
- M365 Copilot license present on tenant (verify)
- `id-ipai-dev` principal ID confirmed: `1aee831f-3813-4eed-b49c-f7665330f0f6`
