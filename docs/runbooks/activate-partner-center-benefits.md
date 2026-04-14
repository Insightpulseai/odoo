# Runbook — Activate Partner Center Benefits

**Owner-only** (requires Partner Center login + tenant admin). No CLI path.

This runbook closes the **M365 tenant gap** flagged in
[docs/gtm/M365_TENANT_GAP.md](../gtm/M365_TENANT_GAP.md) by activating the
**M365 E5 Developer Subscription (25 licenses)** already awarded to IPAI as
part of ISV Success enrollment. Activating this benefit provisions
Microsoft Teams + M365 services on tenant `402de71a-87ec-4302-a609-fb76098d1da7`
and unblocks Teams/Copilot agent deployment.

## Unredeemed benefits (as of 2026-04-13)

From Partner Center → Benefits → Cloud services, IPAI has three available:

| Benefit | Source | Quantity | Activate by | Status |
|---|---|---|---|---|
| **Microsoft 365 E5 Developer Subscription** | ISV Success | 25 licenses | 2027-04-30 | Unknown |
| Dynamics 365 discounted and free licenses | ISV Success | 25 licenses | 2027-04-30 | Unknown |
| Dynamics 365 Partner Sandbox — Sales, Field Service and Customer Service | ISV Success | 25 licenses | 2027-04-30 | **Not Redeemed** |

**Priority:** redeem the M365 E5 Developer Subscription FIRST — it provisions
the Teams/Copilot backbone the 6 Bot Framework registrations need.

---

## Activation steps (M365 E5 Developer Subscription)

### Step 1 — Retrieve product key in Partner Center

1. Sign in to [Partner Center](https://partner.microsoft.com/dashboard)
2. Navigate: **Benefits → Cloud services**
3. Locate **Microsoft 365 E5 Developer Subscription**
4. Click **Get Keys** → copy the 25-digit cloud license key

### Step 2 — Redeem the key against the IPAI tenant

**Use a private / incognito browser window** to avoid session contamination
with other Microsoft accounts.

1. Open `https://signup.microsoft.com/productkeystart`
2. Sign in with the tenant admin account — **must be the account associated
   with tenant `402de71a-87ec-4302-a609-fb76098d1da7` (`@insightpulseai.com`)**
3. Enter the 25-digit product key → **Next**
4. Verify the product details:
   - Product: Microsoft 365 E5 Developer Subscription
   - Licenses: 25
   - Duration: (per benefit terms)
5. Click **Redeem**

### Step 3 — Verify provisioning in M365 Admin Center

Within 5-10 minutes of redemption:

1. Open [M365 Admin Center](https://admin.microsoft.com) → **Billing → Your products**
2. Confirm **Microsoft 365 E5 Developer** is listed as Active
3. **Users → Active users** → assign 1-2 licenses to test users

### Step 4 — Verify Teams provisioning on the tenant

Back in Claude Code or a terminal:

```bash
# Should now return Teams-bearing SKUs (instead of only AAD_PREMIUM_P2)
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/subscribedSkus" \
  --resource "https://graph.microsoft.com/" \
  --query "value[?contains(skuPartNumber, 'DEVELOPERPACK') || contains(skuPartNumber, 'TEAMS')]" -o table
```

Expected output: one or more SKUs containing `DEVELOPERPACK_E5` or
`Microsoft_Teams_*`. Prior to activation this query returned `[]`.

### Step 5 — Unblock the Agent 365 Teams path

Once Teams is provisioned:

1. **Test Graph API Teams app upload** (previously failed with "Microsoft
   Teams hasn't been provisioned on the tenant"):

```bash
# Using any of the 6 app.dev.zip bundles already built
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps" \
  --resource "https://graph.microsoft.com/" \
  --headers "Content-Type=application/zip" \
  --body "@agents/teams-surface/appPackage/build/app.dev.zip"
```

Expected: HTTP 201 Created + app id returned.

2. Sideload each of the 6 custom-engine-agent packages (teams-surface,
   tax-guru-surface, doc-intel-surface, bank-recon-surface, ap-invoice-surface,
   finance-close-surface).

3. Register each of the 6 Entra Agent IDs via Microsoft 365 Admin Center →
   Copilot → Frontier program (requires Frontier preview enrollment —
   separate owner step).

---

## Secondary benefits (activate after M365 E5 is verified)

### Dynamics 365 Partner Sandbox (Sales / Field Service / Customer Service)

Redeemable directly in Partner Center → **ISV Success program page**
(not via this form flow if enrolled after 2023-01-24 — which IPAI was).
No product key step required.

### Dynamics 365 discounted and free licenses

Same redemption path. Useful for Tax Guru PH benchmark work against
Dynamics 365 Finance — see memory `project_benchmark_stack_matrix`.

---

## What NOT to do

**Do not submit the form at `https://experience.dynamics.com/requestlicense/`**
for this activation. That form is for partners **requesting new/additional**
sandbox licenses. IPAI already has 3 benefits awarded in Partner Center
(table above) — they just need redemption, not a new request.

If this runbook is followed in the wrong order, you can end up with:
- Duplicate sandbox licenses consuming quota
- Extra ISV Success license requests flagged for review
- Confused Partner Center billing records

---

## Failure modes + fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| "This product key is not valid" at signup.microsoft.com | Key mistyped or redeemed already | Re-retrieve via Partner Center → Get Keys (copy-paste, no manual entry) |
| "Sign in with a work or school account" loop | Signed in as personal Microsoft account | Use incognito + paste tenant admin email explicitly |
| "Can't activate for this tenant" | Wrong tenant signed in | Sign out fully, incognito, use `admin@insightpulseai.com` |
| SKU activation succeeds but Teams not provisioned after 30 min | Backend provisioning lag | File Partner Center support ticket — cite benefit activation time + M365 Admin Center status |

---

## References

- [docs/gtm/M365_TENANT_GAP.md](../gtm/M365_TENANT_GAP.md) — the blocker this runbook resolves
- [spec/pulser-entra-agent-id/deploy.md](../../spec/pulser-entra-agent-id/deploy.md) — next-step runbook once M365 is live
- [agents/teams-surface/](../../agents/teams-surface/) — canonical Teams custom engine agent waiting for sideload
- Microsoft Partner Center — https://partner.microsoft.com/dashboard
- Cloud product key redemption — https://signup.microsoft.com/productkeystart
- Partner Center Benefits FAQ — https://learn.microsoft.com/partner-center/benefits-overview
- View and Use Your Cloud Services Benefits — https://learn.microsoft.com/partner-center/software-keys

---

*Last updated: 2026-04-13*
