# Plan — Pulser Entra Agent ID rollout

> Draft. Deadline: 2026-05-01 (Agent 365 GA).

## Phases

### Phase 0 — Pre-flight (now → 2026-04-14)

| Step | Owner | Artifact |
|---|---|---|
| Verify M365 Copilot license on tenant | Owner | M365 Admin Center screenshot |
| Enroll in Frontier preview program | Owner | Frontier confirmation email |
| Confirm `id-ipai-dev` MI (existing) principal: `1aee831f-3813-4eed-b49c-f7665330f0f6` | Done | Audit log entry |
| Revoke global `vscode` PAT in ADO | Owner | Per `docs/security/revoke-pat-runbook.md` |

### Phase 1 — Scaffold Pulser as canonical template (2026-04-14 → 2026-04-21)

| Step | Owner | Artifact |
|---|---|---|
| `atk new --type custom-engine-agent --lang python --output agents/teams-surface/` | Code | Done (this spec's companion PR) |
| `atk provision --env dev` → creates `pulser-teams-bot-dev` + Entra app reg | Code + Owner | BOT_ID + AAD_APP_CLIENT_ID in env/.env.dev |
| Deploy bot-route.bicep → AFD route `/api/messages` live | Code | AFD shows pulser-bot-route |
| Playground test: `npx @microsoft/teams-app-test-tool start` → roundtrip | QA | Screenshot |
| Deploy to ACA (`ipai-copilot-gateway`) via `deploy-erp-canonical.yml` | CI | ACA revision ready |
| Sideload Teams app package to IPAI tenant | Owner | UAT access |
| Create first Entra Agent ID for Pulser via Frontier admin flow | Owner | Agent 365 ID in Admin Center |

### Phase 2 — Apply template to remaining 5 agents (2026-04-21 → 2026-04-28)

For each of: Tax Guru PH, Doc Intelligence, Bank Recon, AP Invoice, Finance Close:

| Step | Pattern |
|---|---|
| Fork `agents/teams-surface/` → `agents/<agent>-surface/` | Keep architecture identical |
| Create `id-ipai-agent-<name>` MI in `rg-ipai-dev-platform` | Terraform or `az identity create` |
| `atk provision --env dev` per agent | New BOT_ID + AAD app reg per agent |
| Add per-agent route to AFD via `bot-route.bicep` | New origin group per agent? Or share `og-copilot-gateway`? See open Q |
| Register Entra Agent ID via Frontier admin flow | Per agent |
| Manifest-per-agent describes scope, commands, icon | Distinct branding per agent |

### Phase 3 — Hardening (2026-04-28 → 2026-05-01)

| Step | Owner | Artifact |
|---|---|---|
| Conditional Access policy: agent identities can only access `ipai-copilot-gateway` scope | Security | CA policy ID |
| Defender for Cloud alerts → on-call Slack channel | Security | Alert rule |
| Purview audit rule: log all agent → OBO chains | Security | Purview policy |
| Remove pre-GA per-agent Frontier licenses once M365 E7 licenses land (post GA) | Owner | Billing confirmation |

## Architecture decisions

### MI scoping (open question in PRD)

**Option A**: One MI per agent, one per env (`id-ipai-agent-pulser-dev`, `-staging`, `-prod`)
- **Pro**: Clean RBAC boundary per env
- **Con**: 6 agents × 3 envs = 18 identities

**Option B**: One MI per agent, shared across envs
- **Pro**: 6 identities total, simpler RBAC
- **Con**: Single compromised MI affects all envs

**Recommended**: Option A — aligns with `rg-ipai-<env>-*` RG model and existing `id-ipai-dev` pattern.

### Custom domain strategy

**Option A**: Per-agent subdomain (`pulser-dev.insightpulseai.com`, `tax-guru-dev.insightpulseai.com`, ...)
- **Pro**: Clean URL, per-agent TLS cert
- **Con**: DNS fan-out; each cert is a KV renewal target

**Option B**: Single `agents-dev.insightpulseai.com` with path-based routing (`/pulser/messages`, `/tax-guru/messages`)
- **Pro**: One DNS record, one cert
- **Con**: All agents share an ingress — one compromise = ingress compromise

**Recommended**: Option B for dev/staging; evaluate Option A for prod at hardening phase.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Frontier preview enrollment delayed past Apr 15 | Medium | High | Defer Pulser registration to post-GA; use `ipai-copilot-gateway` MI as bridge |
| Bot Channel Registration fails for 6+ agents (Azure quota) | Low | Med | Submit quota increase preemptively |
| M365 Copilot license not on tenant | Unknown | Blocking | Buy via Partner Center or via existing admin |
| AFD route conflict with existing `ipai-copilot-gateway` path | Low | Med | Route pattern `/api/messages` is unique to bot; no overlap with existing web paths |

## Not planned

- Declarative agents for any IPAI use case (wrong model)
- Copilot Studio agents (low-code path — doesn't fit ipai-copilot-gateway)
- Per-agent Foundry projects (all share `ipai-copilot` — orchestrator-level differentiation only)

## References

- `constitution.md`, `prd.md`, `tasks.md` (this bundle)
- [overview-custom-engine-agent](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-custom-engine-agent)
- [microsoft-agent-365/overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- `agents/teams-surface/` — canonical template
- `infra/azure/modules/bot-route.bicep` — AFD routing primitive
