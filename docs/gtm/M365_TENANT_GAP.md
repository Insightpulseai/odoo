# M365 Tenant Gap — Blocking Teams / Agent 365 Rollout

**Discovered:** 2026-04-13
**Tenant:** `402de71a-87ec-4302-a609-fb76098d1da7` (insightpulseai.com)
**Blocker for:** Teams sideload · M365 Copilot Chat · Agent 365 GA (May 1)

## Finding

`az rest GET /v1.0/subscribedSkus` on the IPAI tenant returned ONLY:

| SKU | Units | Status |
|---|---|---|
| `AAD_PREMIUM_P2` | 100 | Enabled |
| `POWER_BI_STANDARD` | 1,000,000 (free) | Enabled |

**Missing for Teams/Copilot path:**
- Microsoft 365 Business Standard / Premium / E3 / E5 (base plan with Teams)
- Microsoft 365 Copilot add-on
- Microsoft Agent 365 Frontier

When we attempted `POST /v1.0/appCatalogs/teamsApps` (Graph API sideload), Microsoft returned:

```json
{
  "error": {
    "code": "Forbidden",
    "message": "Microsoft Teams hasn't been provisioned on the tenant. Ensure the tenant has a valid Office365 subscription."
  }
}
```

## What this blocks

- All 6 agent surfaces (`agents/*-surface/appPackage/`) — zip bundles built but have no Teams catalog to upload to
- `atk provision` / `atk publish` workflows — same Teams backend
- Agent 365 GA onboarding (May 1) — requires M365 Copilot license
- Cross-user OBO licensing model — requires M365 E7 or Agent 365 add-on

## What still works

Everything upstream of Teams delivery:

- 6 Entra app registrations (live in IPAI tenant)
- 6 Bot Channel Registrations (pointed at AFD bot endpoints)
- Key Vault secret material for all 6 bots
- `ipai-bot-proxy-dev` ACA app with JWT validation active
- 6 AFD routes on `afd-ipai-dev-bots` endpoint
- Internal `ipai-copilot-gateway` → Foundry `ipai-copilot` chain

These can be reused for non-Teams surfaces (direct REST chat, web embed, Slack Bot Framework connector, email ingestion) without any changes.

## UPDATE 2026-04-13 — option D discovered (recommended)

Partner Center → Benefits workspace shows **3 unredeemed benefits** from
IPAI's ISV Success enrollment that were missed in the original gap analysis:

| Benefit | Qty | Activate by |
|---|---|---|
| **Microsoft 365 E5 Developer Subscription** | 25 licenses | 2027-04-30 |
| Dynamics 365 discounted and free licenses | 25 licenses | 2027-04-30 |
| Dynamics 365 Partner Sandbox — Sales, Field Service, Customer Service | 25 licenses | 2027-04-30 |

**The M365 E5 Developer Subscription redemption closes this gap without
buying anything.** It provisions Teams + M365 on the IPAI tenant via the
existing ISV Success benefit. Zero license spend.

Activation runbook: [docs/runbooks/activate-partner-center-benefits.md](../runbooks/activate-partner-center-benefits.md)

This supersedes Options A–C below for short- and medium-term. Options
B and C remain valid fallbacks only if the benefit redemption fails.

---

## Options — pick one

### Option A: Buy M365 on the IPAI tenant

- **M365 Business Standard** — ~$12.50/user/month — includes Teams, SharePoint, Exchange, OneDrive
- **+ M365 Copilot** — ~$30/user/month — required for custom engine agent Chat surface
- **+ Agent 365** — GA May 1, pricing TBD, required for per-user OBO model post-GA

**Pros:** Owner remains in IPAI tenant; simplest admin model.
**Cons:** Recurring cost; Finance team (CKVC/RIM/BOM) still lives on `omc.com`, so IPAI license doesn't cover them.

### Option B: Deploy Teams surface to TBWA/SMP `omc.com` tenant

Per memory `project_pulser_capability_taxonomy`, the end-users are Finance team on `omc.com`. That's a different tenant entirely.

Cross-tenant bot deployment requires:
1. Multi-tenant Entra app registrations (`signInAudience: AzureADMultipleOrgs` on the 6 apps we created)
2. Admin consent grant on `omc.com` for each app
3. Teams sideload on `omc.com` Teams Admin Center
4. Owner on `omc.com` agrees to host the Teams apps

**Pros:** Uses TBWA/SMP's existing M365 subscription; no IPAI license spend.
**Cons:** Requires ongoing coordination with TBWA/SMP admin; IPAI doesn't control the tenant.

### Option C: Delay Teams surface, ship non-Teams channels first

The bot-proxy + gateway + Foundry chain can serve any HTTP channel. Near-term alternatives:

- **Direct REST chat** — `POST /api/chat` to bot-proxy from a web SPA. No Teams needed. Works today.
- **Embedded web chat widget** — iframe/React snippet on `insightpulseai.com`.
- **Email ingestion** — Exchange/IMAP → gateway.
- **Slack** — Bot Framework has a Slack connector; create 6 Slack apps; IPAI has some Slack footprint.

**Pros:** Zero license spend; ships immediately.
**Cons:** No Teams in-chat surface; Finance team still needs browser access.

## Recommendation

**Short term**: Option C (ship non-Teams surface via web embed) — keep the investment productive.

**Medium term**: Option B (deploy to `omc.com`) — aligns with where the Finance users actually work. Requires TBWA/SMP CTO sign-off.

**Only buy M365 on IPAI tenant (Option A) if** IPAI plans to expand to other M365-only clients who can't license Pulser via their own tenants.

## Immediate action items

1. Confirm which path with stakeholders
2. If B: update the 6 Entra app registrations to `signInAudience: AzureADMultipleOrgs`
3. If C: build a minimal web chat widget → POST to AFD bot endpoint (bypassing Bot Framework auth — route proxy /api/chat/* around the BF adapter)
4. If A: purchase flow via Partner Center

## Evidence

```bash
# Reproduce this finding
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/subscribedSkus" \
  --resource "https://graph.microsoft.com/" \
  --query "value[].{sku:skuPartNumber, consumed:consumedUnits, status:capabilityStatus}" -o table
```
