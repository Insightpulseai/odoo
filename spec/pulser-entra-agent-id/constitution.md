# Constitution — Pulser Entra Agent ID rollout

> Draft — to be expanded before May 1, 2026 (Agent 365 GA).
> Spec bundle files: `constitution.md` (this), `prd.md`, `plan.md`, `tasks.md`.

## Mandate

Every IPAI agent that acts on behalf of a user in Microsoft 365 must be
registered with its own **Entra Agent ID** by **May 1, 2026** — the date
Microsoft Agent 365 reaches general availability and the licensing model
switches from per-agent to per-user (OBO).

## Non-negotiables

1. **One Entra Agent ID per agent persona** — Pulser, Tax Guru PH, Doc
   Intelligence, Bank Recon, AP Invoice, Finance Close, and any future
   IPAI agent each get their own ID. Not one shared identity.
2. **Managed identity, not secrets** — each Agent ID is backed by a
   user-assigned managed identity (`id-ipai-agent-<name>`) in
   `rg-ipai-<env>-platform`. No client secrets stored anywhere.
3. **Observability via M365 Admin Center + Purview + Defender** — do not
   rebuild agent telemetry that Agent 365 provides natively. The
   custom `ops.agent_runs` table is **supplemental**, not authoritative.
4. **MCP-first tooling** — agent tools exposed via MCP interfaces
   (Outlook / Teams / SharePoint / Odoo). Aligns with cross-repo
   invariant #10 (MCP First).
5. **OBO licensing** — at GA, agents are covered under the calling
   user's Agent 365 or M365 E7 license. Agents never hold their own
   license post-GA. Any pre-GA Frontier per-agent license is a
   **temporary bridge only**.

## Authority

- **Identity registry**: Microsoft Entra — canonical source of Agent IDs
- **Access policy**: Conditional Access for agents — owner: Security team
- **Runtime runtime**: Azure Container Apps — canonical host for all
  agent proxy services (no separate hosting plane per agent)
- **Orchestrator**: `ipai-copilot-gateway` — canonical agent loop. M365
  Agents SDK is a channel layer only (cross-repo invariant #1).
- **Channel surfaces**: Microsoft Teams, M365 Copilot Chat, Outlook,
  Web (embedded), SMS (future) — each agent declares supported channels
  in its `appPackage/manifest.json`.

## What this constitution is NOT

- Not a replacement for agent-platform's `constitution.yaml`
- Not a Copilot Studio migration plan (low-code path — not IPAI's)
- Not a declarative-agents strategy (wrong model for IPAI)

## Decision log

| Decision | Date | Rationale |
|---|---|---|
| Use Agents Toolkit proxy, not Foundry portal direct publish | 2026-04-12 | Need custom SSO + multi-env + CI/CD built-in |
| Python for teams-surface bot code | 2026-04-12 | Matches `ipai-copilot-gateway` language; reduces cross-lang surface |
| One MI per agent, not per environment | TBD | Decision pending — see plan.md |

## References

- [Microsoft Agent 365 Overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [Cross-repo invariants](../../CLAUDE.md)
- Memory: `project_m365_e7_agent365`, `project_foundry_managed_identity`
