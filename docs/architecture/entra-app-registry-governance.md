# Entra App Registry — Inventory + Governance + Migration Plan

> **Locked:** 2026-04-15
> **Authority:** this file (canonical Entra app-registration posture)
> **Tenant:** Default Directory (insightpulseai.com) — `402de71a-87ec-4302-a609-fb76098d1da7`
> **Total apps:** 21
> **Doctrine anchors:**
> - CLAUDE.md §Cross-Repo Invariants — managed-identity-first, app reg only when truly required
> - Memory `reference_partner_center_auth` — IPAI = ISV not CSP → app-only + certificate auth
> - Memory `project_entra_agent_id_visible_today` — Entra Agent ID surface visible on IPAI tenant (P2-only)
> - Memory `feedback_no_custom_default` — minimize app-reg sprawl
>
> **External signal:** Microsoft Entra blog — [ADAL + Azure AD Graph deprecated, migrate to MSAL + Microsoft Graph](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/azure-ad-change-management-simplified/2967456)

---

## 21 apps — inventory + categorization

### A. Production / customer-facing (KEEP — harden)

| App | Client ID | Created | Cert? | Action |
|---|---|---|---|---|
| **InsightPulse AI - Odoo Login** | `3446e178-…` | 2026-04-07 | ✅ Current | Keep — Odoo OAuth surface |
| **InsightPulse AI - Tableau Cloud** | `91e6b87f-…` | 2026-03-21 | ✅ Current | Keep — Tableau SSO |
| **GitHub Enterprise Cloud SAML SSO** | `c7e32cff-…` | 2026-03-30 | ❌ none | Verify config — SAML doesn't require client secret if pure SAML |
| **ipai-tableau-sso** | `3296fb56-…` | 2026-03-21 | ❌ none | **DUPLICATE?** — review vs InsightPulse AI - Tableau Cloud (consolidate) |

### B. Platform / automation (KEEP — rotate / harden)

| App | Client ID | Created | Cert? | Action |
|---|---|---|---|---|
| **InsightPulseAI Azure DevOps Automation** | `ae2df138-…` | 2026-03-10 | ✅ Current | Keep — needed for ADO MCP |
| **ipai-copilot-gateway** | `cbdc8e90-…` | 2026-04-10 | ✅ Current | Keep — Pulser gateway |
| **ipai-github-oidc** | `ede45dfb-…` | 2026-03-14 | ❌ no cert (OIDC tokens) | ✅ Correct posture — federated identity, no secret needed |
| **IPAI Platform Admin CLI** | `b0172e9f-…` | 2026-03-23 | ⚠️ **Expiring soon** | **ROTATE NOW** — flagged from session start |
| **IPAI PG MCP Server** | `40ae2f4c-…` | 2026-04-12 | ❌ none | Add cert; do not use secret |

### C. Pulser agent + Teams surface apps (KEEP — migrate to Entra Agent ID)

Per memory `project_entra_agent_id_visible_today` — these should migrate to Entra Agent ID when production GA hits (visible today on IPAI tenant in P2-only preview).

| App | Client ID | Created | Cert? | Plane |
|---|---|---|---|---|
| **ipai-agent-pulser-finance-dev** | `49aceaad-…` | 2026-04-15 | ❌ none | Pulser agent — finance |
| **ipai-agent-pulser-ops-dev** | `486bd9d1-…` | 2026-04-15 | ❌ none | Pulser agent — ops |
| **ipai-agent-pulser-research-dev** | `faab82f3-…` | 2026-04-15 | ❌ none | Pulser agent — research/PrismaLab |
| **ipai-ap-invoice-teams-dev** | `943ed298-…` | 2026-04-13 | ✅ Current | Teams app — AP invoice |
| **ipai-bank-recon-teams-dev** | `1ef45cc2-…` | 2026-04-13 | ✅ Current | Teams app — Bank recon |
| **ipai-doc-intel-teams-dev** | `fd272f5f-…` | 2026-04-13 | ✅ Current | Teams app — Doc intel |
| **ipai-finance-close-teams-dev** | `ccb8a139-…` | 2026-04-13 | ✅ Current | Teams app — Finance close |
| **ipai-pulser-teams-dev** | `b0af7d01-…` | 2026-04-13 | ✅ Current | Teams app — Pulser surface |
| **ipai-tax-guru-teams-dev** | `428c42b5-…` | 2026-04-13 | ✅ Current | Teams app — Tax Guru |

### D. External vendor (REVIEW)

| App | Client ID | Created | Cert? | Action |
|---|---|---|---|---|
| **Diva Goals API** | `ac3237cd-…` | 2026-03-23 | ❌ none | **REVIEW** — what is Diva Goals? Confirm in scope or remove |
| **Diva Goals Web** | `f2dcb8af-…` | 2026-03-23 | ❌ none | Same as above |

### E. DEPRECATED — REMOVE

| App | Client ID | Created | Why | Action |
|---|---|---|---|---|
| **ipai-n8n-entra** | `bf78cade-…` | 2026-03-21 | n8n DEPRECATED 2026-04-07 per CLAUDE.md | **DELETE** |

---

## Migration matrix (ADAL→MSAL + AAD Graph→MS Graph + Secret→Cert/MI)

Per Microsoft Entra blog posture:

```
ADAL                  →  MSAL
Azure AD Graph        →  Microsoft Graph
Client secret         →  Certificate OR Managed Identity (preferred)
Long-lived secret     →  OIDC federated identity (where possible — see ipai-github-oidc)
```

### Action per app

| App | Current auth | Target auth | Migration cost |
|---|---|---|---|
| Odoo Login | Cert (good) | Cert (no change) | none |
| Tableau Cloud / SSO | Cert / SAML | Cert (no change) | dedupe with `ipai-tableau-sso` |
| GitHub Enterprise SAML | SAML | SAML (no change) | none |
| ADO Automation | Cert | Cert (no change) | none |
| `ipai-copilot-gateway` | Cert | Cert (no change) | none |
| `ipai-github-oidc` | OIDC federated | OIDC (best practice) | none |
| **`IPAI Platform Admin CLI`** | Cert (expiring) | **Federated identity via az CLI** | **rotate cert OR move to az-cli MI** |
| **`IPAI PG MCP Server`** | none / public | **Add cert + use Entra MI for Azure-side** | add cert, MI for backend |
| **3 × Pulser agent apps** | none | **Entra Agent ID** when GA | Wait for GA + migrate |
| **6 × Teams apps** | Cert | Cert (until Agent ID GA) | rotate certs annually |
| **Diva Goals (×2)** | none | Verify scope; if external, leave; if our own, add cert | verify first |
| **`ipai-n8n-entra`** | n/a | DELETE | Delete app reg + remove tenant assignment |

---

## Per-tenant app pattern (TBWA\SMP, future customers)

When TBWA\SMP signs (per `docs/programs/tbwa-smp-finance-program.md`), they get a **separate Entra app registration in IPAI tenant** for Pulser-on-Teams delivery:

```
ipai-pulser-tbwasmp-prod     ← per-customer Teams surface
                                Cert auth (rotated annually)
                                Tenant-scoped to TBWA\SMP M365 tenant
                                Per-customer Bot Service registration
```

Per `docs/architecture/multitenant-saas-target-state.md` §"Identity per tenant".

---

## Doctrine alignment — what should NOT be in this list

Per CLAUDE.md + multitenant doctrine, app registrations must be MINIMIZED:

| Anti-pattern | Mitigation |
|---|---|
| App reg per dev/staging environment | ❌ Use single app + per-env certs/secrets |
| App reg per individual user | ❌ Use Entra users, not app regs |
| App reg for Azure-internal service-to-service | ❌ Use Managed Identity (system-assigned or user-assigned) |
| App reg with long-lived client secret | ❌ Use cert (or OIDC federated) |
| Stale / unused app reg | ❌ Audit + delete (this exercise) |

### What we have RIGHT (keep doing)

- ✅ `ipai-github-oidc` uses federated identity (no secret) — **gold standard**
- ✅ Cert-based auth on production apps (Odoo Login, Tableau, Copilot Gateway, Teams apps)
- ✅ Per-agent app reg for Teams surface (correct per multitenant doctrine)

### What we have WRONG (fix this sprint)

- ❌ `ipai-n8n-entra` — n8n deprecated, app should be deleted
- ❌ Possible duplicate `Tableau Cloud` + `ipai-tableau-sso` — consolidate to one
- ❌ `IPAI Platform Admin CLI` cert expiring — rotate or move to `az` CLI MI
- ❌ 3 Pulser agent dev apps with no auth (`-` cert column) — add cert OR migrate to Entra Agent ID preview
- ❌ `IPAI PG MCP Server` no cert — add cert; the Azure side should use MI

---

## Entra Agent ID readiness

Per memory `project_entra_agent_id_visible_today`:
- **Visible** on IPAI tenant today (P2-only preview)
- **2 identities + 1 blueprint** visible
- **Frontier gates creation** — wait for GA
- **Hard deadline:** Microsoft Agent ID for M365 Copilot registration before **2026-05-01** (per `ms-startups-navigator` skill)

When Agent ID GA hits:
- Migrate the 3 `ipai-agent-pulser-*-dev` apps → Entra Agent ID
- Migrate the 6 `ipai-*-teams-dev` apps → Entra Agent ID + Bot Service hybrid
- Each agent gets a real identity, not a synthetic app reg

---

## Action checklist (sequenced)

### TODAY (or this week)

```
[ ] 1. Delete ipai-n8n-entra (deprecated)
       Portal → App registrations → ipai-n8n-entra → Delete
       
[ ] 2. Rotate IPAI Platform Admin CLI cert (or migrate to az CLI MI)
       Portal → App registrations → IPAI Platform Admin CLI → Certificates & secrets
       Generate new cert, upload, deprecate old, update consumers
       
[ ] 3. Verify Diva Goals (×2) — what is it?
       If external SaaS we use, document in upstream-adoption-register
       If unknown / unused, delete
       
[ ] 4. Decide on Tableau dedup
       Compare InsightPulse AI - Tableau Cloud vs ipai-tableau-sso
       Pick one, update Tableau side, delete the other
       
[ ] 5. Add cert to IPAI PG MCP Server
       Or document why no auth (e.g., it's just a pinned name, not in active use)
```

### NEXT SPRINT

```
[ ] 6. Add certs to 3 ipai-agent-pulser-*-dev apps
       Or wait for Entra Agent ID GA if imminent
       
[ ] 7. Audit Teams app cert rotation cadence
       6 Teams apps all created 2026-04-13 — first rotation due 2027-04-13
       Set up calendar reminders + automation for cert rotation
       
[ ] 8. ADAL → MSAL audit on consuming apps
       For every IPAI Python/Node/C# code that calls Azure AD,
       confirm it uses MSAL (not deprecated ADAL)
       grep for: adal | azure.identity (MSAL is azure-identity in Python)
       
[ ] 9. AAD Graph → Microsoft Graph audit
       For every IPAI integration calling Graph API,
       confirm it uses graph.microsoft.com (NOT graph.windows.net which is AAD Graph)
       grep for: graph.windows.net  ← reject if found
```

### WHEN ENTRA AGENT ID GAS

```
[ ] 10. Migrate 3 ipai-agent-pulser-*-dev apps to Agent ID
[ ] 11. Migrate 6 ipai-*-teams-dev apps to Agent ID
[ ] 12. Re-document multitenant Identity section
```

---

## Per-customer app pattern (when first customer signs)

```
Naming:        ipai-<surface>-<customer>-<env>
Examples:      ipai-pulser-tbwasmp-prod
               ipai-erp-tbwasmp-prod
               ipai-bookings-w9-prod (already covered by Odoo Login app, may not need new)
Auth:          Cert (rotated annually) + Bot Service registration
Tenant scope:  Customer's M365 tenant
Owner:         IPAI tenant (we host; customer consumes)
Cleanup:       Delete on customer offboarding
```

---

## Audit query (for repeat use)

Periodic governance check:

```bash
# Via Microsoft Graph (after MSAL migration):
az ad app list --query "[].{name:displayName, id:appId, created:createdDateTime}" -o table

# Filter for stale (>365 days no use, no recent cert/secret update)
# Filter for missing cert (.passwordCredentials present without .keyCredentials)
# Filter for naming-non-compliant (not matching ipai-* or InsightPulse pattern)
```

Add as a scheduled Azure Pipelines job after multitenant onboarding hits Phase 2.

---

## What this changes for `pulser-assistant-surface-design.md`

The Pulser surfaces design assumed per-customer Entra apps. Now we have the **canonical app naming + auth posture**:

```
Surface 5 (Teams) per customer:
  App name:      ipai-pulser-<customer>-<env>
  Auth:          Cert (until Agent ID GA)
  Bot Service:   Single per app
  Adaptive Cards manifest: per app
  Tenant scope:  Customer's M365 tenant
```

---

## Doctrine summary

```
21 apps today           → reduce to ~16 after this cleanup
                          (delete n8n, dedupe Tableau, verify Diva Goals)

Auth posture:
  Federated OIDC        Best — adopt where possible (already on ipai-github-oidc)
  Certificate           Default for app-only — adopt for all our apps
  Managed Identity      Default for Azure service-to-service (no app reg needed)
  Client secret         Last resort — actively migrate away

ADAL → MSAL              Audit consuming code; replace adal with msal/azure-identity
AAD Graph → MS Graph     Audit code; replace graph.windows.net with graph.microsoft.com

Per-customer pattern:    1 app per customer Teams surface (when TBWA\SMP signs)
Agent ID migration:      Wait for GA; migrate 9 apps when ready
                         Hard deadline: 2026-05-01 for M365 Copilot agent registration
```

---

## References

- [Microsoft Entra blog — Azure AD change management simplified](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/azure-ad-change-management-simplified/2967456)
- [MSAL migration guide (Python)](https://learn.microsoft.com/azure/active-directory/develop/msal-migration)
- [Microsoft Graph migration from AAD Graph](https://learn.microsoft.com/graph/migrate-azure-ad-graph-overview)
- Memory: `reference_partner_center_auth`, `project_entra_agent_id_visible_today`, `project_entra_bootstrap`
- Internal: [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md), [`docs/architecture/pulser-assistant-surface-design.md`](./pulser-assistant-surface-design.md)
- IPAI tenant ID: `402de71a-87ec-4302-a609-fb76098d1da7`

---

*Last updated: 2026-04-15*
