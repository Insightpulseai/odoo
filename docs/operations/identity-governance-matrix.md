# Identity Governance Matrix

> Operational reference for mailbox identities (Zoho + Google Workspace) and
> Azure identities (Entra groups, app registrations, managed identities, ADO
> access). Single source of truth for "who has access to what, via which
> identity primitive."

---

## Section 1 — Mail identity (Zoho + Google + external)

### 1.1 Current state

| Domain | Provider | Real mailboxes | Notes |
|---|---|---|---|
| `insightpulseai.com` | Zoho Mail | `business@`, `finance@` | alias-heavy on `business@` |
| `w9studio.net` | Google Workspace | `business@`, `finance@`, `accounts@` | cleanly separated |
| `omc.com` / OPRG | External | — | **treat as external contact directory, not internal mail** |

### 1.2 insightpulseai.com aliases (currently all on business@)

```
business@insightpulseai.com (real)
  ├── admin@
  ├── billing@
  ├── ceo@
  ├── devops@
  ├── expenses@
  ├── info@
  ├── jake.tolentino@
  └── jgtolentino.rn@gmail.com
```

### 1.3 Target structure (recommended rebalance)

| Address | Target | Rationale |
|---|---|---|
| `business@insightpulseai.com` | Real mailbox | Primary corp/platform voice |
| `finance@insightpulseai.com` | Real mailbox | Keep as-is |
| `info@insightpulseai.com` | Alias → `business@` | Brand entry point |
| `ceo@insightpulseai.com` | Alias → `business@` | Exec-facing |
| `jake.tolentino@insightpulseai.com` | Alias → `business@` | Individual voice |
| `admin@insightpulseai.com` | **Route to `finance@`** or new `admin@` mailbox | Admin ≠ exec, separate trail |
| `billing@insightpulseai.com` | **Route to `finance@`** | Billing belongs in finance lane |
| `expenses@insightpulseai.com` | **Route to `finance@`** | Expense lane |
| `devops@insightpulseai.com` | **Route to `business@` OR separate `engineering@` mailbox** | Engineering lane, not exec |
| `jgtolentino.rn@gmail.com` | **Remove from alias list** | Personal Gmail shouldn't be on corp alias tree |

### 1.4 w9studio.net (keep as-is, already well-structured)

| Address | Purpose |
|---|---|
| `business@w9studio.net` | Primary client-facing + bookings + operations |
| `finance@w9studio.net` | AR/AP, tax, compliance, vendor payments |
| `accounts@w9studio.net` | Bookkeeping, posting, reconciliation |

### 1.5 External contacts (OPRG / OMC / TBWA / vendors)

Model in Odoo `res.partner` with contact groups:
- `external/client/tbwa` — TBWA SMP, TBWA Worldwide contacts
- `external/client/oprg-omc` — OPRG / OMC roster (Veracruz, Meran, Lasaga, etc.)
- `external/vendor/landlord` — La Fuerza property contacts
- `external/regulatory` — BIR/DTI/SEC contact persons

**Never** create internal mailboxes for external contacts.

### 1.6 Rule

```
Real mailbox       = operational inbox with distinct responsibility
Alias              = branding/entry address only, routes to real mailbox
Routing rule       = automated delivery based on mail rules
External contact   = partner in CRM, never provisioned as internal user
```

---

## Section 2 — Azure identity (Entra + ADO + app regs + MIs)

### 2.1 Canonical rule set

| Human access | → | Entra groups |
| User sign-in app | → | App registration |
| Azure workload auth | → | Managed identity (keyless) |
| Azure DevOps access | → | Entra-connected org + group rules |
| GitHub org SSO | → | Entra SAML app registration |

### 2.2 Current Entra app registrations (20 total, from prior tenant inventory)

| App | Purpose | Type | Note |
|---|---|---|---|
| `ipai-agent-pulser-finance-dev` | Pulser finance agent identity | MI + App reg | Entra Agent ID candidate (5/1 deadline) |
| `ipai-agent-pulser-ops-dev` | Pulser ops agent | MI + App reg | Same |
| `ipai-agent-pulser-research-dev` | Pulser research agent | MI + App reg | Same |
| `ipai-pulser-teams-dev` | Pulser M365 declarative agent | M365 agent manifest | Wave 2 |
| `ipai-ap-invoice-teams-dev` | AP invoice M365 agent | M365 agent | Wave 2 |
| `ipai-bank-recon-teams-dev` | Bank recon M365 agent | M365 agent | Wave 2 |
| `ipai-finance-close-teams-dev` | Finance close M365 agent | M365 agent | Wave 2 |
| `ipai-tax-guru-teams-dev` | Tax guru M365 agent | M365 agent | Wave 2 |
| `ipai-doc-intel-teams-dev` | Document Intelligence M365 agent | M365 agent | Wave 2 |
| `ipai-copilot-gateway` | Gateway API for Pulser agents | App reg (confidential) | Current cert OK |
| `InsightPulse AI - Odoo Login` | Odoo OIDC SSO | App reg | Current cert OK |
| `InsightPulse AI - Tableau Cloud` | Tableau SSO | App reg | |
| `InsightPulseAI Azure DevOps Automation` | ADO service principal | App reg (client creds) | Automation identity |
| `IPAI PG MCP Server` | PG MCP server identity | App reg | Read-only DB access |
| `IPAI Platform Admin CLI` | Admin CLI identity | App reg | **Expiring soon — rotate** |
| `ipai-github-oidc` | GitHub OIDC federation | App reg (federated creds) | OIDC workload identity for GHA scoped exception |
| `ipai-tableau-sso` | Tableau SSO (legacy?) | App reg | Review for deduplication vs Tableau Cloud |
| `GitHub Enterprise Cloud - Insightpulseai SAML SSO` | GitHub org SSO | App reg (SAML) | Needs reconfig after org move to ipai Enterprise |
| `Diva Goals API` | Diva goals service | App reg | |
| `Diva Goals Web` | Diva goals UI | App reg | |

### 2.3 Identity inventory — component → auth method → repo owner

| Component | Auth method | Entra object | RBAC target | Repo owner |
|---|---|---|---|---|
| `ipai-website` (ACA) | Managed identity | `id-ipai-dev` | Storage Blob Data Contributor (stdevipai) | `infra/` |
| `ipai-odoo-dev` (ACA) | Managed identity | `id-ipai-dev-runtime` | PG Flex `azure_admin`, Key Vault Secrets User | `infra/` + `addons/` |
| `ipai-prismalab` (ACA) | Managed identity | `id-ipai-dev-data` | AI Search Index Contributor, Storage Blob Data Reader | `infra/` + `web/` |
| `ipai-w9studio` (ACA) | Managed identity | `id-ipai-dev` (shared) | Storage Blob Data Reader | `infra/` |
| `ipai-copilot-resource` (Foundry) | Managed identity | `id-ipai-dev-agent` | Azure OpenAI Contributor, Cognitive Services User | `agent-platform/` |
| Pulser agent inferences | **Keyless MI**, NOT API keys | agent-specific MIs | OpenAI API call scope | `agent-platform/` |
| PG MCP Server | Workload identity | `IPAI PG MCP Server` app reg | PG Flex read-only | `agent-platform/` |
| Azure Pipelines → Azure deploy | Service connection + MI | ADO service principal + MI | Contributor on target RG | `infra/` |
| GitHub Actions OIDC → Azure | Federated credentials | `ipai-github-oidc` | Scope-limited Contributor on Sub B | scope-exception `.github/workflows/` |
| Admin CLI | App reg client credentials | `IPAI Platform Admin CLI` | Azure Contributor (elevated) | Operational |

### 2.4 Azure DevOps access model

```
Entra user or group
  ↓ member of
Entra group (e.g., `sg-ipai-devs`, `sg-ipai-admins`)
  ↓ mapped to
Azure DevOps group (via Entra-connected org)
  ↓ grants
Project permissions (Reader, Contributor, Project Admin)
  ↓ via
Azure DevOps group rules (access level: Basic, Stakeholder)
```

**Target groups for `Insightpulseai` ADO org:**

| Entra group | ADO role | Access level | Members |
|---|---|---|---|
| `sg-ipai-owners` | Project Admins + Collection Admins | Basic | Jake (founder) |
| `sg-ipai-devs` | Contributors | Basic | 4 engineers |
| `sg-ipai-readers` | Readers | Stakeholder | Finance, advisors, auditors |
| `sg-ipai-build-services` | Build Service | N/A | Azure Pipelines MIs |

Never assign Azure DevOps access to users directly in ADO UI — always via Entra group membership. Audit trail lives in Entra.

### 2.5 App registration governance

**Every app registration MUST have:**

| Field | Value |
|---|---|
| Naming | `<tenant>-<purpose>-<env>` (e.g., `ipai-pulser-finance-dev`) |
| Owner(s) | At least 2 owners (not just Jake) for bus-factor |
| Tags | `env:dev|stg|prod`, `owner:<team>`, `type:agent|sso|cli|bot` |
| Credentials | **Federated credentials preferred**, then certificates, secrets last |
| Secret expiry | Max 24 months; alert at T-60 days |
| API permissions | Least privilege; admin consent explicit per scope |
| Redirect URIs | Only what's needed; no wildcard localhost in prod |

**Deprecated app reg cleanup signals:**
- `IPAI Platform Admin CLI` — expiring soon → rotate immediately
- `ipai-tableau-sso` vs `InsightPulse AI - Tableau Cloud` — likely one duplicate → consolidate
- Duplicate Jake Tolentino user accounts (memory 6627) — deduplicate

### 2.6 Managed identity governance

**Per-agent identity rule:** each Pulser agent gets its own user-assigned MI.

```
id-ipai-agent-pulser-finance
id-ipai-agent-pulser-ops
id-ipai-agent-pulser-research
id-ipai-agent-pulser-p2p         (pending — Wave 2 M365 agent)
id-ipai-agent-pulser-r2r         (pending — Wave 2 M365 agent)
```

Not one MI shared across agents. Each MI has its own RBAC scope so cross-agent compromise is contained.

**Shared MIs** (OK to share when they don't hold sensitive per-agent scope):
- `id-ipai-dev-data` — shared storage blob reader
- `id-ipai-dev-runtime` — shared runtime compute identity

### 2.7 Keyless pattern for runtime

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

credential = DefaultAzureCredential()  # picks up MI on ACA; az-login for local dev
client = AIProjectClient(
    endpoint="https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot",
    credential=credential,
)
```

**Forbidden patterns:**
- Hard-coded `OPENAI_API_KEY` in code or env files tracked in git
- Long-lived client secrets in env vars outside Key Vault
- Shared service principal used across multiple unrelated workloads

---

## Section 3 — Cross-cutting policies

### 3.1 Secret lifecycle

| Secret type | Store | Max lifetime | Rotation trigger |
|---|---|---|---|
| Mail provider passwords | Zoho admin, Google admin | Forever (password hygiene policy applies) | Compromise, offboarding |
| Zoho/Google SMTP creds (for Odoo outbound) | Azure Key Vault `kv-ipai-dev-sea` (canonical per `.claude/rules/ssot-platform.md` Rule 7) | 12 months | Scheduled |
| App reg client secrets | Key Vault | 24 months | Expiry alert T-60d |
| App reg certificates | Key Vault (auto-rotated) | Certificate policy | Auto |
| Federated credentials | No secret — trust-based | N/A | On subject change |
| Managed identity | Azure-managed | Auto-rotated | Never by user |

### 3.2 Access review cadence

| Identity class | Review period | Owner |
|---|---|---|
| Entra users (humans) | Quarterly | Jake |
| Entra groups membership | Quarterly | Jake |
| App registrations | 6-monthly | Per app owner (from tag) |
| Managed identity RBAC | 6-monthly | `infra/` owner |
| Azure DevOps access | Quarterly | Jake |
| Mail aliases | Annually | Jake |
| External partner contacts | Annually (in Odoo) | `accounts@w9studio.net` |

### 3.3 Onboarding / offboarding checklist

**Onboarding (new team member):**
1. Create Entra user
2. Add to appropriate `sg-ipai-*` Entra groups (not individual ADO access)
3. Provision ISV Success benefit seat (VS Enterprise, M365 E5)
4. Add to Zoho or Google mailbox if role-specific (usually NOT needed — most use M365 E5 mailbox)
5. Git commit: update `docs/operations/identity-inventory.yaml` (new: see §3.4)

**Offboarding:**
1. Remove from all Entra groups (cascades to ADO + Azure RBAC)
2. Review app registrations where they were a listed owner; transfer ownership
3. Revoke any personal PATs (ADO / GitHub)
4. Wipe + archive mailbox per retention policy
5. Git commit: update identity inventory

### 3.4 Inventory manifest (machine-readable source)

Not yet created. Proposed: `platform/ssot/identity/inventory.yaml` capturing:
- Users (humans, with Entra GUID)
- Groups (with membership)
- App registrations (with owners, credentials summary, RBAC)
- Managed identities (with RBAC, attached resources)
- Mailboxes (real vs alias)
- External contacts (reference only)

Machine-readable so identity audits and quarterly reviews run against the YAML truth, not manual Partner Center crawls.

---

## Section 4 — Immediate remediation backlog

From current tenant state:

| Item | Action | Urgency |
|---|---|---|
| Duplicate Jake Tolentino Entra users | Dedupe — keep primary, transfer memberships | High (per memory 6627) |
| `IPAI Platform Admin CLI` expiring soon | Rotate secret | High |
| `ipai-tableau-sso` vs `InsightPulse AI - Tableau Cloud` | Audit, consolidate | Medium |
| `jgtolentino.rn@gmail.com` on business@ alias tree | Remove from corp aliases | Medium |
| `billing@`, `expenses@`, `admin@` all on business@ | Route to `finance@` or new real mailbox | Medium |
| GitHub SAML SSO app reg | Reconfigure after org move Dataverse → ipai Enterprise | Medium |
| Entra groups not yet created (`sg-ipai-*`) | Create + populate | Medium |
| Azure DevOps access via direct user vs Entra groups | Migrate to group-based access | Low |
| Identity inventory YAML file | Create at `platform/ssot/identity/inventory.yaml` | Medium |
| Quarterly access review cadence | Establish + calendar | Low |
| Identity Secure Score 43.91% → 70%+ | Enable MFA everywhere, block legacy auth, risk-based CA | Medium |

---

## Section 5 — References

- [Azure DevOps org management + Entra integration](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/manage-users-teams)
- [Entra ID groups + app registrations](https://learn.microsoft.com/en-us/entra/identity/users/groups-roles-users)
- [Managed identities overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Keyless Azure OpenAI sample](https://github.com/Azure-Samples/azure-openai-keyless-js)
- `.claude/rules/ssot-platform.md` Rules 3 (secrets) + 7 (Zoho SMTP via Key Vault)
- `.claude/rules/security-baseline.md`
- `docs/architecture/plane-separation.md`
- `docs/architecture/ipai-governance-model.md`

---

*This is an operational reference. Real TINs, secrets, passwords, and personal emails never belong in this repo — always Odoo DMS, Key Vault, or secure out-of-band channels.*
