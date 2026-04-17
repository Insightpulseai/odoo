---
name: ipai-platform
description: >
  Master skill bundle for InsightPulseAI. Covers Azure resource constants
  (ipai-resource-map), Odoo 18 CE development conventions (ipai-odoo-platform),
  Pulser agent platform patterns (ipai-agent-platform), and Odoo docs enhancement.
  Load for any IPAI Azure, Odoo, Foundry, or agent work.
  Triggers on: IPAI, InsightPulseAI, Pulser, Odoo 18 CE, ipai_*, BIR compliance,
  ACA deployment, Foundry, rg-ipai, pg-ipai-odoo, ipai-copilot-resource.
version: "0.8.0"
updated: "2026-04-18"
scope: repo
parts:
  - index
  - ipai-resource-map
  - ipai-odoo-platform
  - ipai-agent-platform
  - odoo-docs-enhance
---

## Part 1: Index
---
name: pulser-constitution
description: Establish or update Pulser for Odoo governing principles. Use when starting a new feature, onboarding a new contributor, or when IPAI doctrine needs to be re-anchored. Triggers on "constitution", "governing principles", "architecture doctrine", or "platform rules".
disable-model-invocation: false
user-invocable: true
---

# Pulser for Odoo — constitution enforcement

You are anchoring all work to the Pulser for Odoo governing principles.
Read `spec/pulser-odoo/constitution.md` if it exists. If it does not exist, create it from the template below.
Then confirm all active work items are consistent with these principles.

## Non-negotiables to enforce

### Naming
- Product name: **Pulser for Odoo**
- Technical addon: `ipai_odoo_copilot`
- Spec slug: `pulser-odoo`
- Tenant terminology: a Pulser tenant is a customer organization — never an Odoo company, branch, or Entra tenant

### System-of-action rule
Odoo CE/OCA 18 is the system of action. Pulser does not replace Odoo transactional truth.
Pulser may: assist, route, summarize, validate, prepare, generate artifacts, enforce policy gates.
Pulser may not bypass: Odoo record truth, RBAC, approval banding, evidence controls, mutation safety.

### Ingress rule
Canonical public ingress:
- Azure DNS
- Direct custom-domain binding to Azure Container Apps origins
- Certificate binding at the app edge

Not canonical: Cloudflare, proxy-based ingress, Azure Front Door as main ingress layer.
Front Door may exist only as a legacy or migration artifact.

### Runtime topology rule
Pulser core runtime converges to three apps only:
- `pulser-odoo-web`
- `pulser-agent-api`
- `pulser-worker`

Additional apps require written justification (OCR, MCP bridge, public website portfolio).
ERP must remain separate from public website runtime.

### Deployment stamp rule
Pulser scales through deployment stamps. Each stamp:
- Is independently deployable and recoverable
- Has a dedicated Azure Database for PostgreSQL Flexible Server (no shared PG across stamps)
- Is bounded in blast radius

### IaC rule
All infrastructure converges into `infra/azure/` as Bicep modules.
No critical infrastructure left as manual Azure-only state.

### Repo authority chain
```
Azure Boards → Spec Kit → GitHub → IaC/CI-CD → Azure runtime → observability/evals → feedback
```

### RBAC rule
Pulser behavior is resolved from: surface × domain × role groups × approval band × evidence scope × expertise mode × task type × risk level.
Never infer RBAC from contact lists, email directories, or ad hoc naming conventions.

### Self-improvement bounds
Allowed: structured run tracing, domain evaluation, replay-based optimization, narrow small-model training.
Prohibited: uncontrolled online RL for finance, tax, approval, or operational mutation workflows.

## Template for spec/pulser-odoo/constitution.md

If the file does not exist, write it verbatim from `$CLAUDE_SKILL_DIR/templates/constitution-template.md`.

## Verification checklist

After creating or updating the constitution, confirm:
- [ ] Product name and slug are correct throughout
- [ ] Tenant terminology distinguishes Pulser tenant / Odoo company / Entra tenant
- [ ] Direct ingress principle is stated (no Cloudflare, no proxy)
- [ ] Odoo is named as system of action
- [ ] Deployment stamp and dedicated PG per stamp are stated
- [ ] IaC convergence target is `infra/azure/`
- [ ] Self-improvement bounds prohibit uncontrolled online RL on finance/tax/approval
- [ ] Repo authority chain is stated
-e 

---
## Part 2: IPAI Resource Map (Azure constants)
---
name: ipai-resource-map
description: >
  InsightPulseAI Azure resource constants and topology. Load whenever working
  with IPAI infrastructure, Odoo deployments, Foundry, agents, or any Azure
  resource. Provides exact subscription IDs, resource names, resource group
  topology, MI names, and IPAI-specific conventions — eliminating lookup
  round-trips and preventing wrong-version or wrong-resource errors.
  ALWAYS load this skill for any IPAI Azure, Odoo, Foundry, or agent work.
  Pairs with official azure-container-apps, microsoft-foundry, and
  azure-database-for-postgresql skills for implementation patterns.
---

# IPAI Azure Resource Map

Canonical reference for all InsightPulseAI Azure resources.
Last updated: 2026-04-13. Source: Azure portal CSV export (116 resources).

---

## Subscriptions

| Name | ID | Purpose |
|---|---|---|
| IPAI ISV Sponsored (canonical) | `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` | All workloads (dev/staging/prod) |

**Entra tenant:** `402de71a-87ec-4302-a609-fb76098d1da7` (`insightpulseai.com`)
**Default region:** Southeast Asia (`southeastasia`)
**Foundry region:** East US 2 (`eastus2`) — Foundry resource must be EUS2

---

## Resource Group Topology

```
rg-ipai-dev-odoo-runtime    (SEA) — PRIMARY runtime RG
  ACA environment, all Container Apps/Jobs, ACR, AFD, WAF,
  alerts, Redis, DNS zones, private endpoints, NSGs, VNet,
  Log Analytics, App Insights, Recovery Services vault,
  Function App, workbook, action groups

rg-ipai-dev-odoo-data       (SEA) — Data tier
  pg-ipai-odoo (PG Flex), stipaiodoodev (storage),
  private endpoint for PG

rg-ipai-dev-platform        (SEA) — Identity + secrets
  kv-ipai-dev-sea (canonical KV)
  kv-ipai-dev (STALE — consolidate and delete)
  id-ipai-agent-* (6 per-agent managed identities)

rg-data-intel-ph            (EUS2) — AI/data stack
  ipai-copilot-resource (Foundry)
  ipai-copilot project
  cosmos-ipai-dev (Cosmos DB NoSQL, serverless)
  srch-ipai-dev (AI Search, Basic)
  stipaiagentdev (Storage, ZRS — DEDICATED Foundry Agent Service)
  docai-ipai-dev (Document Intelligence)
  bing-ipai-grounding (Bing Resource)

rg-ipai-financial-intel     (EUS2) — Financial intel
  kv-admin845384060711840
  stadmin8456a384060711840

rg-ipai-stg-odoo-runtime    (SEA) — sponsored sub eba824fb (PrismaLab prod home + staging lane)
  la-ipai-stg                 (Log Analytics)
  ipai-odoo-stg-env           (ACA env, domain whitedesert-54fce6ca)
  ipai-prismalab-web          (serves prismalab.insightpulseai.com — moved here from prod sub 2026-04-13)
  id-ipai-stg                 (UAMI for ACA pulls; cross-sub AcrPull on acripaiodoo + Cognitive Services User on ipai-copilot-resource)

rg-ipai-stg-odoo-data       (SEA) — sponsored sub eba824fb — empty (PG Flex deferred)
```

**Sponsored-sub legacy/parallel stack (NOT touched, separate work):**
```
rg-ipai-dev-data-sea       (SEA) — stdevipai (containers: bir-inbox, odoo-attachments) · stlkipaidev (lakehouse, empty bronze/silver/gold) · pg-ipai-odoo-dev (PG Flex)
rg-ipai-dev-mon-sea        (SEA) — log-ipai-dev-sea · appi-ipai-dev
rg-ipai-dev-security-sea   (SEA) — id-ipai-dev (DIFFERENT MI from prod — same name, different principalId) · kv-ipai-dev-sea
rg-ipai-dev-odoo-sea       (SEA) — sb-ipai-dev-sea (Service Bus) · acae-ipai-dev-sea (ACA env, EMPTY)
rg-ipai-dev-ai-sea         (SEA) — dbw-ipai-dev (Databricks)
rg-ipai-dev-dbw-managed    (SEA) — Databricks-managed (unity-catalog-access-connector, dbmanagedidentity, dbstorage*, workers-vnet, workers-sg)
```

**Deleted this session (zombies + duplicates):** `aif-ipai-dev` (empty Foundry shell, eus2) · `srch-dev-ipai` (wrong-named empty Search) · `stlkdevipai` (wrong-named empty lakehouse) · `ipai-prismalab-stg-web` (duplicate canary) · `rg-ipai-dev-ai-eus2` (RG was holding only `aif-ipai-dev`).

---

## Container Apps (23 running)

**Odoo core (SOR):**
- `ipai-odoo-dev-web` — Odoo web tier
- `ipai-odoo-dev-cron` — Odoo cron worker
- `ipai-odoo-dev-worker` — Odoo queue worker
- ACA environment: `ipai-odoo-dev-env-v2`

**AI/Agent tier:**
- `ipai-copilot-gateway` — Foundry proxy / Pulser gateway
- `ipai-odoo-mcp` — Odoo MCP Server (13 tools, FastMCP StreamableHTTP) ✅ LIVE
- `ipai-release-manager` — MAF Release Manager agent ✅ LIVE
- `ipai-bot-proxy-dev` — Bot Framework webhook proxy
- `ipai-ocr-dev` — Document Intelligence OCR

**Platform services:**
- `ipai-mcp-dev` — General MCP server (→ rename: ipai-pg-mcp-server is separate)
- `ipai-pg-mcp-server-q7d3v77xqx` — PostgreSQL MCP server (own env)
- `ipai-odoo-connector` — Odoo integration connector

**Dev tools:**
- `ipai-code-server-dev` — VS Code server
- `ipai-grafana-dev` — Grafana
- `ipai-mailpit-dev` — Mail testing

**Portals/websites:**
- `ipai-login-dev`, `ipai-ops-dashboard`, `ipai-website-dev`
- `ipai-workload-center`, `ipai-w9studio-dev`, `w9studio-landing-dev`

**Research:**
- `ipai-prismalab-dev`, `ipai-prismalab-gateway`

**Evaluate for retirement:**
- `ipai-superset-dev` — Superset deprecated; replace with Databricks/Fabric

---

## Container App Jobs

**KEEP:**
- `ipai-build-agent` — CI/CD build agent
- `oca-audit-job` — OCA module audit
- `oca-full-audit` — Full OCA audit

**REVIEW before delete:**
- `set-auth-mode` — keyless auth migration job (verify completed)
- `clear-keys-job` — key clearing job (verify completed)

**DELETE (9 stale cleanup jobs):**
```bash
for job in asset-deep-fix asset-fix-job oauth-diag-job oauth-fix-job \
           oauth-signup-fix oauth-verify-job url-fix-job \
           pg-mcp-grant pg-mcp-entra-grant; do
  az containerapp job delete -n $job \
    -g rg-ipai-dev-odoo-runtime --yes --no-wait
done
```

---

## Key Resources (exact names)

| Resource | Name | RG | Region |
|---|---|---|---|
| Container registry | `acripaiodoo` | runtime | SEA |
| Front Door | `afd-ipai-dev` | runtime | Global |
| WAF policy | `wafipaidev` | runtime | Global |
| Redis | `cache-ipai-dev` | runtime | SEA |
| PG Flex | `pg-ipai-odoo` | data | SEA |
| PG host | `pg-ipai-odoo.postgres.database.azure.com` | — | — |
| KV (canonical) | `kv-ipai-dev-sea` | platform | SEA |
| KV (stale) | `kv-ipai-dev` | platform | SEA |
| Platform MI | `id-ipai-dev` | runtime | SEA |
| App Insights | `appi-ipai-dev` | runtime | SEA |
| Log Analytics | `la-ipai-odoo-dev` | runtime | SEA |
| VNet | `vnet-ipai-dev` | runtime | SEA |
| Foundry resource | `ipai-copilot-resource` | rg-data-intel-ph | EUS2 |
| Foundry project | `ipai-copilot` | rg-data-intel-ph | EUS2 |
| Foundry endpoint | `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot` | — | — |
| Cosmos DB | `cosmos-ipai-dev` | rg-data-intel-ph | EUS2 |
| AI Search | `srch-ipai-dev` | rg-data-intel-ph | SEA (verified 2026-04-13; sponsored-sub `srch-dev-ipai` was a wrong-named duplicate, deleted) |
| Agent storage | `stipaiagentdev` | rg-data-intel-ph | EUS2 |
| App storage | `stipaidev` | runtime | SEA |
| Document Intel | `docai-ipai-dev` | rg-data-intel-ph | EUS2 |
| DNS zone | `insightpulseai.com` | runtime | Global |
| ADO org | `insightpulseai` | — | SEA |

*srch-ipai-dev shows SEA — verify should be EUS2 to match Foundry

---

## Managed Identities

| Name | RG | Purpose |
|---|---|---|
| `id-ipai-dev` | runtime | Platform MI — all ACA apps use this |
| `id-ipai-agent-ap-invoice-dev` | platform | AP Invoice agent |
| `id-ipai-agent-bank-recon-dev` | platform | Bank Reconciliation agent |
| `id-ipai-agent-doc-intel-dev` | platform | Document Intelligence agent |
| `id-ipai-agent-finance-close-dev` | platform | Finance Close agent |
| `id-ipai-agent-pulser-dev` | platform | Core Pulser agent |
| `id-ipai-agent-tax-guru-dev` | platform | Tax Guru agent |

**Auth pattern (always):** `DefaultAzureCredential` — never API keys in code.

---

## Azure Bots (6 registered — Teams surfaces)

All in `rg-ipai-dev-odoo-runtime`, routed via `ipai-bot-proxy-dev`:
- `ipai-ap-invoice-teams-bot-dev`
- `ipai-bank-recon-teams-bot-dev`
- `ipai-doc-intel-teams-bot-dev`
- `ipai-finance-close-teams-bot-dev`
- `ipai-pulser-teams-bot-dev`
- `ipai-tax-guru-teams-bot-dev`

---

## Key Vault — Canonical Reference

**Use `kv-ipai-dev-sea` for all secrets.**
`kv-ipai-dev` is a duplicate from a naming collision — consolidate and delete.

```bash
# Verify canonical KV
az keyvault show -n kv-ipai-dev-sea -g rg-ipai-dev-platform --query id -o tsv
```

---

## Microsoft Foundry — Naming (Feb 2026)

**Rebranded from "Azure AI Foundry" → "Microsoft Foundry" (Feb 2026)**
Resource type: `Microsoft.CognitiveServices/account` kind `AIServices`
Portal: https://ai.azure.com (toggle "New Foundry" ON)
Agent API: Responses API (v2) — not Assistants API (v1)
SDK: `azure-ai-projects>=2.0.0` (unified — replaces azure-ai-inference, azure-ai-ml)
Terminology: Threads→Conversations, Messages→Items, Runs→Responses

---

## Odoo Stack Constants

```
Odoo version:  18 CE (NEVER 19 — do not apply v19 patterns)
Databases:     odoo (prod) | odoo_staging | odoo_dev
PG host:       pg-ipai-odoo.postgres.database.azure.com
RG (data):     rg-ipai-dev-odoo-data
RG (runtime):  rg-ipai-dev-odoo-runtime

View tag:      <list> ONLY — never <tree> (deprecated in 18, error in 19)
view_mode:     "list,form"
OCA path:      oca_addons/ (vendored, pinned)
Custom path:   addons/ipai/
Module prefix: ipai_

Smart Delta order: config → OCA → ipai_*_delta → ipai_*_core
```

---

## Monitoring Stack

**Alerts (metric):** 13 rules — ACA CPU/restarts/replicas, PG CPU, HTTP 5xx
**Alerts (log search):** 3 rules — agent latency P95, agent error rate, content safety blocks
**Action groups:** `ag-ipai-ops-email`, `ag-ipai-platform`
**Workbook:** `Odoo Platform Health` (in rg-ipai-dev-odoo-runtime)

Missing alerts to add after Week 1 deploy:
- Cosmos DB RU consumption threshold
- AI Search query latency
- Foundry token usage

---

## ISV + Partner Program

```
Partner ID:     7097326
Entity:         Dataverse IT Consultancy, PH, Makati
Program:        ISV Success (enrolled 3/31/2026 → 3/31/2027)
Sponsored sub:  eba824fb (IPAI ISV Sponsored — staging)

Benefits active:
  Azure sponsorship $5K    → activate at Partner Center → Benefits
  M365 E5 developer (25)  → activate at Partner Center → Cloud services
  D365 Sales/FS/CS (FREE) → https://experience.dynamics.com/requestlicense/
  D365 Operations Tier 2  → https://experience.dynamics.com/requestlicense/
  AI technical consultation → Partner Center → Benefits → Consultations
  ADS session             → Partner Center → Benefits → Consultations
  GitHub Enterprise Cloud → Partner Center → Benefits (year 1 only)

Renewal deadline: 3/31/2027
Renewal requirement: publish Transactable SaaS offer OR upgrade Contact Me → Transactable
Renewal fee: $1,550 USD
```

---

## Critical Security Findings (BLOCKER for prod)

1. **BOLA** — `copilot_gateway.py` doesn't verify user owns `thread_id`
2. **PgBouncer** — not enabled on `pg-ipai-odoo` (enable: `pgbouncer.enabled=on`)
3. **Cosmos single-region** — no failover for agent conversation state
4. **Defender for AI Services** — not enabled on `ipai-copilot-resource`
5. **WAF no prompt exclusions** — chat content triggers HTTP 403
6. **Foundry system MI was OFF** — enable: `az cognitiveservices account update -n ipai-copilot-resource -g rg-data-intel-ph --assign-identity`
7. **API keys active** — disable: `disableLocalAuth: true` on Foundry resource

---

## Azure DevOps MCP — Connection Strings

### Remote MCP Server (public preview — VS Code only now)
```
URL: https://mcp.dev.azure.com/insightpulseai
Auth: Microsoft Entra ID (OAuth)
Toolsets: repos, wit, pipelines, wiki, work, testplan, search
Insiders: X-MCP-Insiders: "true" header
Status: Claude Code/Desktop NOT supported (pending OAuth dynamic registration)
```

### Local MCP Server (use for Claude / Pulser)
```
Package: @microsoft/azure-devops-mcp
Secret: kv-ipai-dev-sea/ado-pat-ipai-platform (PAT)
Org: insightpulseai
Project: ipai-platform
Repo: InsightPulseAI/odoo
Build agent: ipai-build-agent (ACA Job, rg-ipai-dev-odoo-runtime)
```

### azd agent commands (March 2026, v1.23.x)
```bash
azd ai agent run --name <agent>       # run locally
azd ai agent invoke --name <agent>    # send message
azd ai agent show --name <agent>      # status + health
azd ai agent monitor --name <agent>   # stream logs
```

### App Insights connection string (for ACA OTel)
```
Resource: appi-ipai-dev
Secret: kv-ipai-dev-sea/appi-ipai-dev-connection-string
Env var on ACA: APPLICATIONINSIGHTS_CONNECTION_STRING
```

### Azure MCP Server (official Microsoft, not ADO-specific)
```
Project: github.com/orgs/microsoft/projects/1976
Repo: monitor for azure resource management MCP tools
```
-e 

---
## Part 3: IPAI Odoo Platform (Odoo 18 CE conventions)
---
name: ipai-odoo-platform
description: >
  InsightPulseAI Odoo 18 CE platform — module development, Extend-First
  framework, OCA-first hierarchy, view/widget authoring, BIR tax compliance,
  ACA deployment, contributing conventions, and service module patterns.
  Single authoritative reference for ALL Odoo work in the IPAI stack.
  Replaces: odoo18-ce-development, odoo19-developer, odoo19-oca-first,
  odoo19-views-widgets, odoo19-contributing, odoo19-administration,
  odoo19-services (all Odoo 19 skills are WRONG VERSION for IPAI).
  ALWAYS load for any Odoo module dev, view XML, BIR form, ACA Odoo deploy,
  or OCA module evaluation. Pairs with ipai-resource-map for Azure constants.
---

# IPAI Odoo 18 CE Platform

**VERSION: Odoo 18 CE — NEVER apply Odoo 19 patterns.**

Critical 18 CE facts:
- Use `<list>` tag — never `<tree>` (deprecated in 18, causes warnings)
- `view_mode="list,form"` not `"tree,form"`
- `_cr`, `_context`, `_uid` still work in 18 (deprecated in 19, NOT yet)
- `osv` module still exists in 18 (removed in 19, NOT yet)
- OCA modules: target `18.0` branch, not `16.0` or `17.0`

---

## §1 — Development Philosophy: Extend-First

Odoo 18 CE + OCA is already a working ERP. The default assumption is that
the capability exists somewhere in CE or OCA — your job is to find it,
extend it, or repurpose an adjacent module. Writing a new `ipai_*` module
is always the last option, not the first instinct.

**The bias to defeat:** reaching for a new module when `_inherit` on an
existing model or a reconfigured adjacent OCA module would do the same job
with less code and better upgrade safety.

### Decision Hierarchy (follow in order, stop at first YES)

```
1. CONFIGURE
   Can CE settings, approval flows, sequences, automated actions,
   mail templates, or record rules solve it?
   → YES: configure in the UI or via data XML. Zero Python. Stop.
   
   Examples:
   - Period-end locking   → account.journal.lock_date (CE setting)
   - Approval workflow    → base_automation + mail.activity rules
   - Sequence numbering   → ir.sequence configuration
   - Access control       → record rules on existing model

2. EXTEND via _inherit
   Does a CE or OCA model already own this data/logic — even partially?
   → YES: add _inherit in a thin module. Add fields, override one method,
     extend the view with xpath. No forking. No copy-paste of base code.
   
   Examples:
   - BIR fields on invoice → _inherit account.move, add 3 fields + 1 compute
   - Withholding on partner → _inherit res.partner, add wtax_type selection
   - Custom approval state → _inherit account.move, extend state selection

3. REPURPOSE an adjacent module
   Is there a CE or OCA module for a neighboring domain that can be
   reconfigured or lightly extended (_inherit) to serve this purpose?
   → YES: use it. Rename via _description, remap menus, extend views.
     Do not rebuild what already exists in a slightly different form.
   
   Examples:
   - BIR compliance tracking  → repurpose project.task with custom stages
   - Expense liquidation       → extend hr.expense before building new
   - Document filing workflow  → repurpose mail.activity + attachments
   - Vendor accreditation      → extend res.partner with accreditation fields

4. COMPOSE
   Can automated actions, server actions, computed fields, scheduled
   actions, or OCA queue_job wire existing modules together to
   produce the desired workflow?
   → YES: compose. No new model, no new module — just wiring.
   
   Examples:
   - BIR deadline reminder    → ir.cron + mail.template on account.move
   - Month-end close checklist → server action sequence on account.period
   - Multi-step approval       → base_automation chain on state field

5. NEW MODULE (last resort only)
   Genuinely missing domain — no existing CE/OCA model can be
   extended or repurposed without becoming unrecognizable.
   → Write ipai_<domain>_core. Must pass: "would _inherit on an existing
     model solve ≥60% of this?" If yes, go back to step 2.
   
   Legitimate new modules (no CE/OCA equivalent):
   - ipai_bir_tax_compliance  → BIR-specific form generation + XML export
   - ipai_agency_seed         → client-specific seed data loader
   - ipai_dev_studio_base     → foundation layer (depends on nothing)
```

### What this prevents

```
❌ ipai_finance_close as a new module
   → account.period + lock_date + an automated action = done

❌ ipai_expense_portal rebuilt from scratch
   → hr.expense + _inherit + custom stages = done

❌ ipai_bir_task as a new task model
   → project.task with BIR-specific stages and _inherited fields = done

❌ ipai_vendor_accreditation as a new model
   → res.partner + _inherit + accreditation selection + portal = done

✅ ipai_bir_tax_compliance as a new module
   → BIR 2307 XML generation, SLSP/SAWT file format, QR stamping —
     nothing in CE/OCA produces Philippine BIR output files

✅ ipai_agency_seed as a new module
   → client-specific demo/seed data has no CE/OCA home
```

### Hard Guardrails

| Guardrail | Rule |
|---|---|
| No Enterprise | Never import EE modules or IAP. Enforce `iap.disabled=True` |
| No micro-modules | Never create a module whose entire purpose fits in one `_inherit` |
| OCA vendoring | Pin OCA modules in `oca_addons/` at exact commit hash |
| No runtime git/pip | All dependencies resolved at build time, not runtime |
| Upgrade safety | `_inherit` beats fork — every fork is a future upgrade liability |
| AI-first foundation | ipai_* modules depend on `ipai_dev_studio_base` |

### Module structure

```
addons/ipai/
├── ipai_dev_studio_base/     # Foundation — all ipai_* modules depend on this
├── ipai_ce_branding/         # CE hardening, EE lock-out
├── ipai_bir_tax_compliance/  # BIR 2307/SLSP/SAWT — genuinely new domain
├── ipai_agency_seed/         # Client seed data loader
└── (new modules only when steps 1-4 fail)

oca_addons/                   # Vendored OCA 18.0 modules (pinned)
├── web_responsive/
├── auditlog/
├── account_financial_report/
├── account_reconcile_oca/
├── account_tax_balance/
├── queue_job/
└── report_xlsx/
```

### Commit tags

```
[extend] feat(account): inherit account.move, add BIR 2307 fields
[repurpose] feat(compliance): repurpose project.task for BIR deadline tracking
[compose] feat(close): wire month-end checklist via ir.cron + server actions
[configure] feat(approval): configure base_automation for 3-level expense approval
[new-module] feat(bir): ipai_bir_tax_compliance — BIR XML export engine
```

---

## §2 — OCA-First Module Selection

### Priority OCA modules for IPAI (18.0 branch)

**Accounting (R2R/BIR):**
- `account_financial_report` — balance sheet, P&L, trial balance
- `account_reconcile_oca` — bank reconciliation UI
- `account_tax_balance` — tax balance reports
- `account_journal_lock_date` — journal locking for period close
- `account_invoice_import` — invoice import from PDF/XML

**Operations:**
- `queue_job` — async job queue (required by MAF workflow agents)
- `report_xlsx` — Excel report exports
- `web_responsive` — mobile-responsive web client

**How to vendor:**
```bash
# Pin to exact commit hash — never floating branch
cd oca_addons
git submodule add -b 18.0 \
  https://github.com/OCA/account-financial-reporting \
  account-financial-reporting
cd account-financial-reporting && git checkout <commit-hash>
```

---

## §3 — Module Structure Template

```
ipai_<domain>_<type>/
├── __manifest__.py       # Always version="18.0.1.0.0"
├── __init__.py
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── <data>.xml
├── report/
│   └── <report>.xml
└── static/
    └── description/
        └── icon.png
```

### Manifest template

```python
{
    "name": "IPAI <Domain> <Type>",
    "version": "18.0.1.0.0",
    "category": "IPAI",
    "author": "InsightPulseAI",
    "license": "AGPL-3",
    "depends": ["ipai_dev_studio_base", "<base_module>"],
    "data": [
        "security/ir.model.access.csv",
        "views/<model>_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,  # True only for standalone apps
}
```

---

## §4 — View Authoring (Odoo 18 CE)

### Required: `<list>` not `<tree>`

```xml
<!-- ❌ WRONG — deprecated in 18, causes warnings -->
<record id="view_partner_tree" model="ir.ui.view">
  <field name="arch" type="xml">
    <tree>
      <field name="name"/>
    </tree>
  </field>
</record>

<!-- ✅ CORRECT -->
<record id="view_partner_list" model="ir.ui.view">
  <field name="arch" type="xml">
    <list>
      <field name="name"/>
      <field name="email"/>
    </list>
  </field>
</record>
```

### view_mode: always `list,form` not `tree,form`

```xml
<field name="view_mode">list,form</field>
```

### Form view template

```xml
<record id="view_<model>_form" model="ir.ui.view">
  <field name="name"><module>.<model>.form</field>
  <field name="model"><module>.<model></field>
  <field name="arch" type="xml">
    <form string="<Title>">
      <header>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,confirm,done"/>
      </header>
      <sheet>
        <group>
          <group>
            <field name="name"/>
            <field name="partner_id"/>
          </group>
          <group>
            <field name="date"/>
            <field name="amount_total"/>
          </group>
        </group>
        <notebook>
          <page string="Lines">
            <field name="line_ids">
              <list editable="bottom">
                <field name="product_id"/>
                <field name="quantity"/>
                <field name="price_unit"/>
              </list>
            </field>
          </page>
        </notebook>
      </sheet>
    </form>
  </field>
</record>
```

### Search view template

```xml
<record id="view_<model>_search" model="ir.ui.view">
  <field name="name"><module>.<model>.search</field>
  <field name="model"><module>.<model></field>
  <field name="arch" type="xml">
    <search>
      <field name="name" string="Name"/>
      <filter name="active" string="Active"
              domain="[('state', '=', 'active')]"/>
      <group expand="0" string="Group By">
        <filter name="group_partner" string="Partner"
                context="{'group_by': 'partner_id'}"/>
      </group>
    </search>
  </field>
</record>
```

---

## §5 — ORM + Python Patterns (Odoo 18)

### Model template

```python
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class IpaiExample(models.Model):
    _name = 'ipai.example'
    _description = 'IPAI Example'
    _order = 'date desc, id desc'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                  ondelete='restrict')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft', required=True)

    amount_total = fields.Monetary(string='Total',
                                    currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                   default=lambda self: self.env.company.currency_id)

    @api.constrains('amount_total')
    def _check_amount(self):
        for rec in self:
            if rec.amount_total < 0:
                raise ValidationError("Amount cannot be negative.")

    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Only draft records can be confirmed.")
        self.write({'state': 'confirm'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ipai.example')
        return super().create(vals_list)
```

### Compute field pattern

```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped('price_subtotal'))
```

### Domain filter (correct 18 syntax)

```python
# In 18 — both tuple and list syntax work
domain = [('state', '=', 'posted'), ('partner_id.country_id.code', '=', 'PH')]

# Preferred: use expression module for complex domains
from odoo import expression
domain = expression.AND([
    [('state', '=', 'posted')],
    [('date', '>=', date_from)],
])
```

---

## §6 — BIR Philippine Tax Compliance

### Key BIR forms implemented

| Form | Description | Module |
|---|---|---|
| BIR 2307 | Certificate of Creditable Withholding | `ipai_bir_tax_compliance` |
| SLSP | Summary List of Sales/Purchases | `ipai_bir_tax_compliance` |
| SAWT | Summary Alphalist of Withholding Tax | `ipai_bir_tax_compliance` |
| 1601-C | Monthly Compensation Tax | `ipai_finance_ssc` |
| 2550Q | Quarterly VAT return | `ipai_finance_ssc` |
| 1702-RT/EX | Annual income tax | `ipai_finance_ssc` |

### TBWA\SMP Finance team user codes

These are INDIVIDUAL USERS within TBWA\SMP — never separate tenants or agencies.
Tenant = legal entity only.

| Code | Name | Role | Email domain |
|---|---|---|---|
| CKVC | Khalil Vera Cruz | Finance Director | @omc.com |
| RIM | Rey Meran | Senior Finance Manager | @omc.com |
| BOM | Beng Manalo | Finance Supervisor | @omc.com |
| JAP | Jinky Paladin | Finance | @omc.com |
| JPAL | JP Loterte | Finance | @omc.com |
| JLI | Jasmin Ignacio | Finance | @omc.com |
| LAS | Amor Lasaga | Finance | @omc.com |
| JRMO | Jhoee Oliva | Finance | @omc.com |
| JMSM | Joana Mae Maravillas | Finance | @omc.com |
| RMQB | Sally Brillantes | Finance | @omc.com |
| CSD | Cliff Dejecacion | Finance | @omc.com |

### BIR month-end freeze window (Release Manager guardrail)

```python
BIR_FREEZE_MONTHS = [3, 6, 9, 12]  # Q-end months
BIR_FREEZE_DAYS = range(1, 15)      # First 15 days of Q-end months

def is_bir_freeze_window():
    today = date.today()
    return (today.month in BIR_FREEZE_MONTHS and
            today.day in BIR_FREEZE_DAYS)
```

---

## §7 — ACA Deployment (Odoo on Azure)

### Image build + push pattern

```bash
# Build immutable image (never latest-mutable in prod)
VERSION=$(git rev-parse --short HEAD)
IMAGE="acripaiodoo.azurecr.io/odoo:${VERSION}"

docker build -t $IMAGE \
  --build-arg ODOO_VERSION=18 \
  --no-cache .

# Push via MI (no docker login needed with ACR + MI)
az acr login -n acripaiodoo  # uses az login credentials locally
docker push $IMAGE
```

### ACA deployment pattern (idempotent)

```bash
# Update Odoo web container (rolling — no downtime)
az containerapp update \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/odoo:${VERSION} \
  --set-env-vars \
    DB_HOST="pg-ipai-odoo.postgres.database.azure.com" \
    DB_NAME="odoo" \
    AZURE_CLIENT_ID="$(az identity show -n id-ipai-dev \
      -g rg-ipai-dev-odoo-runtime --query clientId -o tsv)"
```

### PG Flex connection (Entra ID / keyless)

```python
# Odoo db config — use Entra token, not password
import subprocess

def get_pg_token():
    result = subprocess.run([
        'az', 'account', 'get-access-token',
        '--resource', 'https://ossrdbms-aad.database.windows.net/',
        '--query', 'accessToken', '-o', 'tsv'
    ], capture_output=True, text=True)
    return result.stdout.strip()
```

---

## §8 — Administration (Azure-adapted)

### PgBouncer (CRITICAL — enable immediately)

```bash
# Not yet enabled — Odoo connection exhaustion risk under multi-tenant load
az postgres flexible-server parameter set \
  -n pg-ipai-odoo \
  -g rg-ipai-dev-odoo-data \
  --name pgbouncer.enabled \
  --value on
```

### Database backup verification

```bash
# Verify backup retention (should be ≥7 days)
az postgres flexible-server show \
  -n pg-ipai-odoo \
  -g rg-ipai-dev-odoo-data \
  --query "backup.backupRetentionDays" -o tsv
```

### Module installation (production-safe)

```bash
# Install via CLI — never via UI in production
az containerapp exec \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev-odoo-runtime \
  --command "odoo -d odoo --stop-after-init -i <module_name>"
```

---

## §9 — Odoo 18 Inheritance Types

Source: https://www.odoo.com/documentation/18.0/developer/tutorials/server_framework_101/12_inheritance.html

Odoo has **three distinct inheritance mechanisms**. Choosing the wrong one
is the most common extension mistake.

### Type 1 — Extension (`_inherit`, same `_name`)

Extends an existing model in-place. The original model gains your new
fields/methods. No new table. All existing records immediately have the
new fields. This is the workhorse — use it for 90% of IPAI extensions.

```python
class AccountMove(models.Model):
    _inherit = 'account.move'  # same _name, no _name on this class

    bir_2307_ref = fields.Char(string='BIR 2307 Reference')
    wtax_amount = fields.Monetary(
        string='Withholding Tax Amount',
        compute='_compute_wtax_amount', store=True
    )

    @api.depends('line_ids.tax_ids')
    def _compute_wtax_amount(self):
        for move in self:
            move.wtax_amount = sum(
                line.balance for line in move.line_ids
                if any(t.tax_group_id.name == 'Withholding' for t in line.tax_ids)
            )
```

View extension (xpath — add fields without replacing the whole view):

```xml
<record id="view_move_form_bir" model="ir.ui.view">
  <field name="name">account.move.form.bir</field>
  <field name="model">account.move</field>
  <field name="inherit_id" ref="account.view_move_form"/>
  <field name="arch" type="xml">
    <!-- Add after existing field -->
    <xpath expr="//field[@name='ref']" position="after">
      <field name="bir_2307_ref"/>
      <field name="wtax_amount"/>
    </xpath>
  </field>
</record>
```

### Type 2 — Prototype / Copy (`_inherit` + new `_name`)

Creates a NEW model that copies the definition of the parent. Separate
table, separate records. Use for creating a parallel model that shares
behaviour but must be independent (rare — think twice before using).

```python
class IpaiBirDocument(models.Model):
    _name = 'ipai.bir.document'       # NEW model name — new table
    _inherit = 'account.move'          # copies fields + methods from account.move
    _description = 'BIR Document'

    # account.move records are NOT ipai.bir.document — completely separate table
    bir_form_type = fields.Selection([
        ('2307', 'BIR Form 2307'),
        ('slsp', 'SLSP'),
    ], required=True)
```

**When to use:** almost never for IPAI. Only if you genuinely need a
separate model that shares the shape of an existing one.

### Type 3 — Delegation (`_inherits`)

Delegates field storage to another model via a foreign key. The child
model has its own table + a Many2one to the parent. Reading parent fields
on the child works transparently. Use when extending a model that should
remain a distinct record type but share identity fields.

```python
class ResPartnerBirProfile(models.Model):
    _name = 'res.partner.bir.profile'
    _inherits = {'res.partner': 'partner_id'}  # delegation
    _description = 'Partner BIR Profile'

    partner_id = fields.Many2one('res.partner', required=True,
                                  ondelete='cascade')
    tin = fields.Char(string='TIN', required=True)
    bir_registered_name = fields.Char(string='BIR Registered Name')
```

**For IPAI:** prefer Type 1 (`_inherit` account.move) for BIR fields.
Only use Type 3 if BIR profile data must live in a completely separate
record with its own lifecycle.

### Inheritance decision quick-ref

```
Want to ADD FIELDS to an existing model?          → Type 1 (_inherit)
Want to OVERRIDE a method on existing model?      → Type 1 (_inherit)
Want to EXTEND a VIEW?                            → Type 1 + xpath
Need a COPY of a model structure (new table)?     → Type 2 (rare)
Need SHARED IDENTITY fields across two models?    → Type 3 (_inherits)
```

---

## §10 — OCA Contribution Workflow

Source: https://odoo-community.org/resources/code

### Before contributing a module to OCA

1. Find the right PSC (Project Steering Committee) and subscribe to its
   mailing list at `https://odoo-community.org/groups`
2. Sign the CLA: `https://odoo-community.org/about/cla`
3. Fork the relevant OCA repository (e.g. `OCA/account-financial-tools`)
4. Use OCA tools: **Pylint-Odoo**, **Flake8**, and OCA module templates

### PR automation gates (all must be green)

When you open a pull request, it triggers: CLA Bot (verifies CLA status),
Travis CI (automated tests), Coveralls (code coverage), Codacy and/or
CodeClimate (code quality score), and Runboat (live Odoo instance of the
contribution).

**Merge threshold:** 3 positive reviews within 5 days (or 2 reviews after
5 days), at least one from a PSC member or OCA Core Maintainer.

### Testing any OCA module via Runboat

Use Runboat to test any OCA module. Access it from the repository README
("Runboat Try me" button), from the module README, or from a PR's Checks
section ("runboat/build" → Details). Login: `admin` / `admin`.

Runboat provides two databases per build:
- `*-baseonly` — clean Odoo, no modules installed
- `*-all` — all modules in the repository installed

**For IPAI OCA module evaluation:** always test on Runboat before
vendoring into `oca_addons/`. Confirms 18.0 compatibility without
spinning up a local instance.

---

## §11 — OCA Module README Structure

Source: https://odoo-community.org/modules-documentation

Every OCA module (and every `ipai_*` module contributed upstream) needs a
`README.rst` following this structure. The `oca-maintainer-tools` package
auto-generates it from `readme/` fragments.

```
<module>/
├── readme/
│   ├── DESCRIPTION.rst      # What the module does
│   ├── INSTALL.rst          # Installation notes (optional)
│   ├── CONFIGURE.rst        # Configuration steps (optional)
│   ├── USAGE.rst            # How to use it
│   ├── ROADMAP.rst          # Known limitations, future plans
│   ├── CHANGELOG.rst        # Version history
│   └── CONTRIBUTORS.rst     # Author list
└── README.rst               # Auto-generated by oca-maintainer-tools
```

Generate `README.rst` from fragments:

```bash
pip install oca-maintainer-tools
oca-gen-addon-readme --addons-dir . --if-source-miss skip <module_name>
```

---

## §12 — Contributing Conventions

### Commit message format

```
# Extend-First commit tags
[configure] feat(account): enable SLSP report via account.journal settings
[extend] feat(bir): inherit res.partner, add withholding tax type field
[repurpose] feat(compliance): repurpose project.task for BIR deadline tracking
[compose] feat(close): wire month-end checklist via ir.cron + server actions
[new-module] feat(bir): ipai_bir_tax_compliance — BIR XML/SLSP/SAWT engine

# OCA vendoring
[oca] chore: vendor account_financial_report 18.0.1.2.0 (pinned a1b2c3d)

# Breaking change
[extend] feat!: rename fields on account.move _inherit extension

# Fixes
fix(bir): correct 2307 computation for multi-company
```

### PR requirements

- [ ] Extend-First tag in commit (`[configure]`, `[extend]`, `[repurpose]`, `[compose]`, `[new-module]`)
- [ ] If `[new-module]`: justification comment explaining why steps 1-4 failed
- [ ] OCA module has pinned commit hash (not floating branch ref)
- [ ] No `<tree>` tags in any view XML — `<list>` only
- [ ] `view_mode="list,form"` not `"tree,form"`
- [ ] Security CSV updated for new models
- [ ] Migration script if model fields changed
- [ ] `readme/` fragments present if module may be contributed upstream
- [ ] Runboat green on 18.0 branch (for OCA modules — verify at `runbot.odoo-community.org`)
- [ ] Release Manager gate passes before merge to main

### Code review checklist (architecture-judge criteria)

- No Enterprise module imports
- No `iap` module references
- All custom modules inherit from `ipai_dev_studio_base`
- OCA modules in `oca_addons/` not inline
- No hardcoded company IDs — use `self.env.company`
- Multi-company aware: `company_ids` or `company_id` field present
- Inheritance type matches use case (Type 1 for extensions, not Type 2)
- View extensions use `xpath` — never replace entire base view
- Pylint-Odoo clean: `pylint --load-plugins pylint_odoo <module>/`

---

## §13 — Web Services / External API (XML-RPC + JSON-RPC)

Source: https://www.odoo.com/documentation/18.0/developer/howtos/web_services.html

This is how `ipai-odoo-mcp` calls Odoo. All 13 MCP tools use the
XML-RPC interface under the hood. Understanding this is required for
debugging the MCP server and adding new tools.

### Authentication

```python
import xmlrpc.client

url = "https://erp.insightpulseai.com"
db  = "odoo"        # or odoo_staging / odoo_dev
username = "admin"  # use MI-backed service account in prod
password = "..."    # from kv-ipai-dev-sea

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
```

### CRUD operations (XML-RPC)

```python
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# search_read — replaces multiple MCP tool calls
records = models.execute_kw(db, uid, password,
    'account.move', 'search_read',
    [[['state', '=', 'posted'], ['move_type', '=', 'out_invoice']]],
    {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date'],
     'limit': 100, 'offset': 0}
)

# create
new_id = models.execute_kw(db, uid, password,
    'res.partner', 'create',
    [{'name': 'IPAI Test', 'email': 'test@insightpulseai.com'}]
)

# write (update)
models.execute_kw(db, uid, password,
    'res.partner', 'write',
    [[new_id], {'phone': '+63 968 269 9265'}]
)

# unlink (delete) — use with extreme caution
models.execute_kw(db, uid, password,
    'res.partner', 'unlink', [[new_id]]
)
```

### Calling business methods

```python
# Call any public method on any model
# Example: post an invoice (action_post)
models.execute_kw(db, uid, password,
    'account.move', 'action_post', [[invoice_id]]
)

# Example: compute BIR 2307 certificate
result = models.execute_kw(db, uid, password,
    'account.move', 'generate_bir_2307', [[invoice_id]], {}
)
```

### In the Odoo MCP server (ipai-odoo-mcp)

The MCP server wraps these XML-RPC calls as FastMCP tools. When adding
a new MCP tool, the pattern is:

```python
@mcp.tool()
async def get_posted_invoices(
    company_id: int,
    date_from: str,
    date_to: str
) -> list[dict]:
    """Get posted customer invoices for a company in a date range."""
    return models.execute_kw(
        DB, uid, password,
        'account.move', 'search_read',
        [[
            ['state', '=', 'posted'],
            ['move_type', 'in', ['out_invoice', 'out_refund']],
            ['company_id', '=', company_id],
            ['invoice_date', '>=', date_from],
            ['invoice_date', '<=', date_to],
        ]],
        {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date',
                    'payment_state', 'bir_2307_ref']}
    )
```

---

## §14 — Multi-Company Guidelines

Source: https://www.odoo.com/documentation/18.0/developer/howtos/company.html

IPAI's deployment is multi-company. TBWA\SMP, Dataverse IT Consultancy,
W9 Studio, and PrismaLab are all separate companies in the same Odoo
instance. All custom fields and modules must be multi-company aware.

### Company-dependent fields

Use `company_dependent=True` for fields whose value differs per company:

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Different BIR TIN per company
    bir_tin = fields.Char(
        string='BIR TIN',
        company_dependent=True
    )
    # Different withholding tax category per company context
    wtax_agent_type = fields.Selection([
        ('individual', 'Individual'),
        ('non_individual', 'Non-Individual'),
    ], company_dependent=True)
```

### Multi-company consistency

When a record is shared across companies, ensure consistency:

```python
class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('company_id', 'partner_id')
    def _check_company_consistency(self):
        for move in self:
            # partner must be accessible in the move's company
            if move.partner_id.company_id and \
               move.partner_id.company_id != move.company_id:
                raise ValidationError(
                    f"Partner {move.partner_id.name} does not belong "
                    f"to company {move.company_id.name}"
                )
```

### Default company in new records

```python
# Always use self.env.company — never hardcode company ID
company = self.env.company  # current user's active company

# For multi-company domains
domain = [('company_id', 'in', self.env.companies.ids)]
```

### Security rules (multi-company record rules)

```xml
<!-- records visible only to users of the same company -->
<record id="rule_bir_doc_company" model="ir.rule">
  <field name="name">BIR Document: company</field>
  <field name="model_id" ref="model_ipai_bir_document"/>
  <field name="domain_force">
    ['|', ('company_id', '=', False),
          ('company_id', 'in', company_ids)]
  </field>
</record>
```

---

## §15 — SQL View Reports

Source: https://www.odoo.com/documentation/18.0/developer/howtos/create_reports.html

SQL view models expose PostgreSQL views as Odoo models — ideal for
IPAI analytics dashboards (BIR SLSP summary, month-end close status,
agent activity). Avoids computed fields on live models.

### SQL view model template

```python
from odoo import fields, models


class IpaiBirSlspReport(models.Model):
    _name = 'ipai.bir.slsp.report'
    _description = 'BIR SLSP Summary Report'
    _rec_name = 'partner_name'
    _auto = False   # ← tells Odoo not to create a table; use SQL view

    # All fields must be readonly=True in SQL views
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    partner_name = fields.Char(string='Vendor Name', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    period = fields.Char(string='Period (YYYY-MM)', readonly=True)
    total_purchases = fields.Monetary(string='Total Purchases', readonly=True)
    total_vat = fields.Monetary(string='Total VAT', readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def init(self):
        """Called once at module install to create/replace the SQL view."""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW ipai_bir_slsp_report AS (
                SELECT
                    row_number() OVER () AS id,
                    aml.partner_id,
                    rp.name AS partner_name,
                    am.company_id,
                    to_char(am.invoice_date, 'YYYY-MM') AS period,
                    SUM(am.amount_untaxed_signed) AS total_purchases,
                    SUM(am.amount_tax_signed) AS total_vat,
                    am.currency_id
                FROM account_move am
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN res_partner rp ON rp.id = aml.partner_id
                WHERE am.state = 'posted'
                  AND am.move_type IN ('in_invoice', 'in_refund')
                GROUP BY
                    aml.partner_id, rp.name, am.company_id,
                    to_char(am.invoice_date, 'YYYY-MM'), am.currency_id
            )
        """)
```

**Key rules:**
- `_auto = False` — no ORM table; SQL view only
- `row_number() OVER ()` — always required as the `id` field
- Never use JOINs that duplicate rows without accounting for it (causes wrong pivot/graph aggregations)
- Fields not needed as measures: add `store=False` to hide from pivot

---

## §16 — Accounting Localization (Philippines / BIR)

Source: https://www.odoo.com/documentation/18.0/developer/howtos/accounting_localization.html

IPAI's BIR compliance module extends the Philippines fiscal localization
(`l10n_ph`). Always build on top of the existing localization — never
replace it.

### Installation procedure

The localization module depends on `account` and `l10n_ph`:

```python
# __manifest__.py
{
    'depends': ['account', 'l10n_ph', 'ipai_dev_studio_base'],
    'data': [
        'data/account_tax_data.xml',
        'data/bir_form_data.xml',
        'views/account_move_views.xml',
        'report/bir_2307_report.xml',
    ],
}
```

### Chart of Accounts extension

```xml
<!-- Extend existing PH chart of accounts — don't create from scratch -->
<record id="account_2307_payable" model="account.account">
  <field name="name">Withholding Tax Payable (2307)</field>
  <field name="code">21400</field>
  <field name="account_type">liability_current</field>
  <field name="chart_template_ids" eval="[Command.link(ref('l10n_ph.l10n_ph_chart_template'))]"/>
</record>
```

### Withholding tax definition

```xml
<record id="tax_ewt_professional_10" model="account.tax">
  <field name="name">EWT - Professional (10%)</field>
  <field name="type_tax_use">purchase</field>
  <field name="amount_type">percent</field>
  <field name="amount">-10</field>  <!-- negative = tax reduces amount -->
  <field name="tax_group_id" ref="tax_group_ewt"/>
  <field name="chart_template_ids" eval="[Command.link(ref('l10n_ph.l10n_ph_chart_template'))]"/>
</record>
```

### BIR report using QWeb

```xml
<!-- report/bir_2307_report.xml -->
<report
  id="report_bir_2307"
  model="account.move"
  string="BIR Form 2307"
  report_type="qweb-pdf"
  name="ipai_bir_tax_compliance.report_bir_2307_document"
  file="ipai_bir_tax_compliance.report_bir_2307_document"
  attachment_use="False"
/>

<template id="report_bir_2307_document">
  <t t-call="web.html_container">
    <t t-foreach="docs" t-as="doc">
      <div class="page">
        <h2>BIR Form 2307</h2>
        <table class="table">
          <tr>
            <td>Payee TIN:</td>
            <td><t t-esc="doc.partner_id.vat"/></td>
          </tr>
          <tr>
            <td>Amount of Income Payment:</td>
            <td><t t-esc="doc.amount_untaxed"/></td>
          </tr>
          <tr>
            <td>Amount of Tax Withheld:</td>
            <td><t t-esc="doc.wtax_amount"/></td>
          </tr>
        </table>
      </div>
    </t>
  </t>
</template>
```

---

## §17 — Custom OWL Fields and Client Actions (Pulser UI)

Source: https://www.odoo.com/documentation/18.0/developer/howtos/javascript_field.html
Source: https://www.odoo.com/documentation/18.0/developer/howtos/javascript_client_action.html

These patterns are needed for the Pulser chat widget embedded in Odoo
and for any custom field widgets in the Finance team forms.

### Custom field widget (OWL component)

```javascript
// static/src/js/bir_status_field.js
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class BirStatusField extends Component {
    static template = "ipai_bir.BirStatusField";
    static props = { ...standardFieldProps };

    get statusClass() {
        const status = this.props.record.data[this.props.name];
        return {
            'draft': 'text-muted',
            'filed': 'text-success',
            'overdue': 'text-danger',
        }[status] || 'text-secondary';
    }
}

registry.category("fields").add("bir_status", BirStatusField);
```

```xml
<!-- static/src/xml/bir_status_field.xml -->
<templates>
  <t t-name="ipai_bir.BirStatusField">
    <span t-att-class="statusClass">
      <t t-esc="props.record.data[props.name]"/>
    </span>
  </t>
</templates>
```

Use in view:
```xml
<field name="bir_filing_status" widget="bir_status"/>
```

### Pulser client action (chat panel)

```javascript
// static/src/js/pulser_action.js
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

class PulserChatAction extends Component {
    static template = "ipai_odoo_copilot.PulserChatAction";

    setup() {
        this.state = useState({
            messages: [],
            input: "",
            loading: false,
        });
    }

    async sendMessage() {
        this.state.loading = true;
        const response = await fetch("/pulser/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: this.state.input,
                context: { company_id: this.env.company.id },
            }),
        });
        const data = await response.json();
        this.state.messages.push({ role: "assistant", content: data.reply });
        this.state.input = "";
        this.state.loading = false;
    }
}

registry.category("actions").add(
    "ipai_odoo_copilot.PulserChatAction",
    PulserChatAction
);
```

Register as a client action in XML:
```xml
<record model="ir.actions.client" id="action_pulser_chat">
  <field name="name">Pulser AI Copilot</field>
  <field name="tag">ipai_odoo_copilot.PulserChatAction</field>
</record>

<menuitem
  id="menu_pulser_chat"
  name="Pulser"
  action="action_pulser_chat"
  sequence="100"
  web_icon="ipai_odoo_copilot,static/description/icon.png"
/>
```

---

## §18 — OCA/ai Bridge (Odoo 18 CE AI Integration)

Source: https://github.com/OCA/ai (branch: 18.0)
Repo: `OCA/ai` — 5 modules, all available for Odoo 18 CE

This is the CE path to embedded AI in Odoo. The OCA bridge connects
external LLMs (Claude via `ipai-copilot-gateway`) to Odoo's native
surfaces (chatter, documents, systray chat). This is how Pulser appears
inside Odoo without requiring Odoo 19 Enterprise.

### Module inventory (all on 18.0 branch)

| Module | Version | Purpose |
|---|---|---|
| `ai_oca_bridge` | 18.0.2.0.0 | Base configuration — bridge to external AI systems |
| `ai_oca_bridge_chatter` | 18.0.2.0.0 | AI in Odoo chatter (message thread on every record) |
| `ai_oca_bridge_document_page` | 18.0.1.0.0 | AI sync for Knowledge/Document pages |
| `ai_oca_bridge_extra_parameters` | 18.0.x | Extra parameters for bridge configuration |
| `ai_oca_native_generate_ollama` | 18.0.x | Ollama local LLM connector (reference pattern) |

**For IPAI:** use `ai_oca_bridge` + `ai_oca_bridge_chatter`. Skip
`ai_oca_native_generate_ollama` — IPAI uses Azure Foundry/Claude, not
Ollama. Use it as a code pattern reference for building an
`ai_oca_native_generate_foundry` connector.

### Vendor into oca_addons/

```bash
cd oca_addons/
git submodule add -b 18.0 https://github.com/OCA/ai ai
cd ai && git checkout <pinned-commit-hash>
```

Install: `ai_oca_bridge`, `ai_oca_bridge_chatter`

### Architecture: OCA bridge + ipai-copilot-gateway = Pulser in Odoo

```
User in Odoo chatter
  → ai_oca_bridge_chatter (OCA module in Odoo 18 CE)
  → ai_oca_bridge (OCA) → HTTP call to configured AI endpoint
  → ipai-copilot-gateway (ACA, internal)
    → Azure AI Foundry → claude-sonnet-4-6
    → Pulser agent logic (MAF)
  ← Response → ai_oca_bridge → chatter message posted
```

### Creating a Foundry provider (ipai_ai_foundry_provider)

The OCA bridge is provider-agnostic. Implement a new provider by
inheriting `ai.model.provider`:

```python
from odoo import fields, models


class AiModelProviderFoundry(models.Model):
    _inherit = 'ai.model.provider'

    @property
    def _provider_key(self):
        return 'foundry'

    def _call_provider(self, prompt, model, **kwargs):
        """Call ipai-copilot-gateway → Foundry → Claude."""
        import requests
        from azure.identity import ManagedIdentityCredential

        # Get token for Foundry via MI
        cred = ManagedIdentityCredential(
            client_id=self.env['ir.config_parameter'].sudo()
            .get_param('ipai.azure_client_id')
        )
        token = cred.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token

        gateway_url = self.env['ir.config_parameter'].sudo().get_param(
            'ipai.copilot_gateway_url',
            default='http://ipai-copilot-gateway'
        )

        response = requests.post(
            f"{gateway_url}/pulser/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": model or "claude-sonnet-4-6",
            },
            timeout=30,
        )
        return response.json().get('content', '')
```

---

## §19 — Odoo 19 AI Agents (Strategic Context — NOT for 18 CE)

Source: https://www.odoo.com/documentation/19.0/applications/productivity/ai/agents.html

**⚠️ Odoo 19 Enterprise only — NOT available in IPAI's Odoo 18 CE.**

Document this architecture as:
1. The upgrade target when IPAI moves to 19 CE/Enterprise
2. The benchmark against which Pulser must be positioned in GTM
3. The reference for what Odoo will natively offer to customers

### Odoo 19 AI Agent architecture

```
Agent
├── System Prompt      — role, personality, scope, behavior
├── Response Style     — Analytical | Balanced | Creative
├── LLM Model          — ChatGPT (OpenAI) | Gemini | Claude (partial)
├── Topics             — what the agent can DO (actions)
│   ├── Instructions   — topic-specific prompt layer
│   └── AI Tools       — actual Odoo functions (create record, open view, etc.)
└── Sources            — what the agent KNOWS (RAG)
    ├── Documents       — uploaded files
    ├── Knowledge       — Odoo Knowledge articles
    └── Weblinks        — external URLs (indexed)
```

### Preconfigured topics (out of box in Odoo 19)

- **Natural Language Search** — interprets user queries, opens correct view with filters
- **Information Retrieval** — tools to fetch data about any Odoo model
- **Create Leads** — automated lead creation (if CRM installed)

An agent with no topics assigned = read-only chatbot. Topics = action capability.

### AI Server Actions (Manager/Worker pattern)

```
AI Server Action (Manager)
  → reads the record + context
  → interprets the AI prompt
  → decides which Tool to call + arguments
  ← calls Tool

Tool (Worker — standard server action with "Use in AI" enabled)
  → contains all execution logic
  → performs record updates, moves, writes
  → enforces business rules in Python
  → executes unconditionally if called (guard logic must be in Tool code)
```

**Critical:** The AI does not infer arguments from Python code. Arguments
passed to a Tool are declared explicitly in the tool's `AI Schema` (Usage tab).
The `Name` column in AI Schema must match the Python variable name exactly.

### IPAI positioning against Odoo 19 AI Agents

| Capability | Odoo 19 EE AI Agent | Pulser (IPAI 18 CE) |
|---|---|---|
| Embedded in Odoo | ✅ native | ✅ via OCA bridge |
| Custom LLM | ChatGPT / Gemini only | ✅ Claude (Anthropic) |
| RAG sources | Documents + Knowledge + Weblinks | ✅ AI Search + Odoo MCP |
| Action execution | Topics + Tools | ✅ MAF + policy-gated execution |
| RBAC | Role-based agents | ✅ approval bands + mutation safety |
| BIR compliance | ❌ not Philippine-specific | ✅ native 2307/SLSP/SAWT |
| Multi-company | Varies | ✅ company_id aware |
| Azure-native | ❌ | ✅ Foundry + ACA |
| Audit trail | Limited | ✅ `ops.run_events` append-only |

**GTM message:** "Pulser does what Odoo 19 Enterprise AI Agents do — without
the Enterprise license, natively on Azure, with Philippine BIR compliance
built in, and governed by RBAC and approval bands."

### Upgrade path (when IPAI moves to 19)

When upgrading from 18 CE to 19 CE/Enterprise:
1. OCA bridge modules (`ai_oca_bridge`, `ai_oca_bridge_chatter`) migrate to
   native Odoo 19 AI App
2. `ipai_ai_foundry_provider` extends native AI model registry with Claude
3. Pulser Topics map 1:1 to the Topics architecture in Odoo 19
4. Pulser AI Tools map to the Worker pattern (server actions with `Use in AI`)
5. Sources stay: `srch-ipai-dev` (AI Search) indexes → Odoo 19 Sources

The OCA bridge is the bridge to both directions — it works today on 18 CE
and provides the correct abstraction for the 19 upgrade.

---

## §20 — D365 Benchmark Resources (for P2P/R2R Spec Validation)

Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/
GitHub: https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets

**Purpose for IPAI:** Every claim in the P2P and R2R spec bundles needs
validation against actual D365 behavior. IPAI now has D365 Finance + Project
Operations sandbox access (ISV Success → `experience.dynamics.com/requestlicense/`).
These resources tell you how to use it.

### D365 FastTrack Implementation Assets (repo structure)

| Folder | IPAI relevance |
|---|---|
| `ERP/Finance` | R2R benchmark — GL, AP, AR, period close, tax |
| `ERP/SCM/SPS` | P2P benchmark — procurement, vendor invoices |
| `Administration/Integration` | D365 ↔ Odoo integration patterns (dual-write reference) |
| `Administration/Analytics` | D365 analytics pipeline — compare vs IPAI Fabric/Databricks |
| `Administration/Dual-write` | If any customer needs D365 + Odoo side-by-side |

### Success by Design — implementation framework (5 stages)

The D365 implementation methodology that enterprise consultants follow.
IPAI must have an equivalent implementation path for Pulser to be credible
in enterprise sales:

```
D365 Success by Design    →    Pulser Implementation Path (to build)
────────────────────────────────────────────────────────────────────
1. Strategize             →    1. IPAI Discovery & Fit Assessment
2. Initiate               →    2. Environment Setup (ACA + Odoo 18 CE)
3. Implement              →    3. Module Configuration + OCA vendoring
4. Prepare                →    4. BIR localization + TBWA\SMP seed data
5. Operate                →    5. Pulser agent activation + Release Manager gate
```

### D365 data entity → Odoo model mapping (P2P/R2R validation)

D365 uses "data entities" for its data model. Map these to Odoo models
to validate feature parity claims in the spec bundles:

| D365 Data Entity | D365 Module | Odoo Equivalent | Pulser spec |
|---|---|---|---|
| `VendorInvoiceHeader` | Finance / AP | `account.move` (move_type=in_invoice) | P2P §AP-01 |
| `VendorInvoiceLine` | Finance / AP | `account.move.line` | P2P §AP-02 |
| `VendorInvoiceCharges` | Finance / AP | `account.move.line` (product=charges) | P2P §AP-03 |
| `VendorInvoiceDocumentAttachment` | Finance | `ir.attachment` on `account.move` | P2P §AP-04 |
| Customer entity | Finance / AR | `res.partner` (customer_rank > 0) | R2R §AR-01 |
| Sales order header | Finance | `sale.order` | P2P §SO-01 |
| Product entity | Finance / SCM | `product.template` | P2P §PRD-01 |
| Journal entry | Finance / GL | `account.move` (move_type=entry) | R2R §GL-01 |
| Project operations | Project Ops | `project.project` + `project.task` | P2P §POps-01 |

**Validation workflow:**
```
1. Open D365 Finance sandbox (experience.dynamics.com/requestlicense/)
2. Navigate to the D365 feature (e.g., AP → Vendor invoices)
3. Screenshot the D365 UI and data flow
4. Open Odoo 18 CE → same workflow
5. Screenshot Odoo equivalent
6. Update spec bundle with side-by-side comparison
7. Note gaps → evaluate via §1 Extend-First hierarchy
```

### D365 import entities as Odoo migration reference

The import entities (customers, products, sales orders, vendor invoices)
define D365's canonical data model. When migrating a D365 customer to
Odoo/Pulser, these entities map the fields to transform:

```python
# D365 VendorInvoiceHeader → Odoo account.move
D365_TO_ODOO_VENDOR_INVOICE = {
    'InvoiceDate': 'invoice_date',
    'DueDate': 'invoice_date_due',
    'VendorAccountNumber': 'partner_id',  # lookup by ref
    'CurrencyCode': 'currency_id',        # lookup by name
    'InvoiceNumber': 'ref',
    'Description': 'narration',
    'TotalInvoiceAmount': None,           # computed by Odoo from lines
}
```

### Free trial environments (from ISV Success)

```
D365 Finance + Project Operations Tier 2 sandbox:
→ https://experience.dynamics.com/requestlicense/
→ Request: "Dynamics 365 Operations Application Partner Sandbox (Tier 2)"
→ Prereq: Tier 1 sandbox (request first)
→ Includes: Finance, Supply Chain, Commerce HQ, Project Operations
→ Cost: FREE (retail value $7,500/month)
→ Credentials: use partner@insightpulseai.com (must be in Entra tenant)

D365 Sales/FS/CS (already in Partner Center):
→ Partner Center → Benefits → Cloud services → D365 Partner Sandbox
→ 25 users, free until Apr 30, 2027
```

### Using FastTrack assets for Odoo feature parity proof

When a prospect asks "can Odoo do what D365 does?" — use this workflow:
1. Find the D365 FastTrack asset for the feature (GitHub repo)
2. Run it against the D365 sandbox
3. Find the OCA equivalent or Odoo CE equivalent
4. Run Pulser's MCP tool on the Odoo result
5. Document the comparison in `spec/pulser-*/benchmarks/`

This is the evidence base for the Marketplace listing and co-sell claims.

---

## §21 — D365 Project Operations → Odoo 18 CE Mapping (P2P Spec)

Source: https://learn.microsoft.com/en-us/dynamics365/project-operations/welcome-to-project-operations

**For IPAI's Pulser Project-to-Profit spec validation.** D365 Project Operations
is what Pulser must match and replace. This section maps every D365 PO concept
to its Odoo 18 CE equivalent so the P2P spec claims can be validated.

### D365 Project Operations — 3 deployment modes

| Mode | Description | IPAI relevance |
|---|---|---|
| **Core (Lite)** | Dataverse only, proforma invoicing, no ERP required | Closest to Odoo standalone — validate P2P Core features |
| **Integrated with ERP** | Full Finance + PO + dual-write for revenue recognition | Full enterprise benchmark for R2R integration |
| **Manufacturing** | WBS + production orders | Not in IPAI scope |

TBWA\SMP's use case = **Core + Integrated**. They need time tracking, expense,
invoicing, and revenue recognition — all within the Integrated deployment.

### D365 billing methods → Odoo equivalents

**Time and Material billing** (D365 Core concept):
```
D365: Hours logged → actuals → proforma → customer invoice → revenue recognized
Odoo: hr.timesheet → sale.order (invoice_policy=timesheet) → account.move
```

**Fixed price billing** (D365 billing milestones):
```
D365: Billing schedule → milestone trigger → invoice → Completed Contract/Percent Completion
Odoo: sale.order.line (invoice_policy=milestone) → account.move
```

### Full entity mapping (D365 PO → Odoo 18 CE)

| D365 Entity | D365 Module | Odoo Model | Notes |
|---|---|---|---|
| Project contract | Sales | `sale.order` | One contract = one SO |
| Contract line | Sales | `sale.order.line` | Each deliverable = one SOL |
| Project | Project Ops | `project.project` | Link via `analytic_account_id` |
| Work Breakdown Structure | Project Ops | `project.task` (hierarchy) | Subtasks = WBS levels |
| Time entry | Time tracking | `account.analytic.line` (timesheet) | `so_line` links to SOL |
| Expense | Expense Mgmt | `hr.expense` + `hr.expense.sheet` | |
| Material usage | Inventory | `stock.move` (analytic line) | |
| Proforma invoice | Billing | `account.move` (state=draft, type=out_invoice) | Don't post = proforma |
| Customer invoice | Billing | `account.move` (state=posted) | |
| Revenue recognition | Finance | `account.analytic.account` + journal entries | WIP = analytic account |
| WIP account | Finance | `account.account` (asset type, WIP) | |
| Accrued revenue | Finance | `account.account` (credit) | Reverse at invoicing |
| Project cost/revenue profile | Finance | Odoo account configuration | |
| Billable/non-billable | Finance | `so_line` on timesheet | NULL = non-billable |
| Resource | Resource Mgmt | `hr.employee` + `resource.resource` | |
| Role pricing | Pricing | `product.pricelist` + `hr.employee.skill` | |
| Budget | Project Ops | `project.project` planned_hours | |

### Revenue recognition in Odoo (matching D365 methods)

**Time and Material — accrue at transaction (D365 → Odoo):**
```python
# D365: posts WIP debit + accrued revenue credit when hours are approved
# Odoo equivalent: enable revenue accrual on project group

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # When timesheet posted and approved:
    # DR: WIP Sales Value (asset)        = hours × billing rate
    # CR: Accrued Revenue Sales Value    = hours × billing rate
    # Reverse at invoicing — same as D365
```

**Fixed Price — Completed Contract method:**
```python
# D365: Revenue recognized only at final invoice
# Odoo equivalent: sale.order.line invoice_policy=milestone
# Create milestone with 100% amount = final delivery = full revenue recognized
```

**Fixed Price — Percent Completion method:**
```python
# D365: Revenue = (actual cost / total budgeted cost) × contract value
# Odoo equivalent: compute from timesheet hours vs budget
@api.depends('timesheet_ids.unit_amount', 'planned_hours')
def _compute_percent_complete(self):
    for project in self:
        if project.planned_hours > 0:
            actual = sum(project.timesheet_ids.mapped('unit_amount'))
            project.percent_complete = (actual / project.planned_hours) * 100
        else:
            project.percent_complete = 0.0
```

### Pulser P2P benchmark validation workflow

```
1. Open D365 Project Operations sandbox
   (Tier 2 from experience.dynamics.com/requestlicense/)

2. Create a project contract:
   - Contract type: Time and Material
   - Client: TBWA\SMP equivalent
   - Line: Creative Services @ ₱5,000/hr

3. Log timesheets → approve → generate proforma → post invoice

4. Screenshot the D365 UI at each step

5. In Odoo:
   - sale.order (confirmed) → project.project → analytic timesheets
   → invoice (timesheet-based) → posted
   Screenshot each step

6. Document in spec/pulser-project-to-profit/benchmarks/
   "D365_PO_vs_Odoo_TM_billing.md"
```

### Key gaps: what D365 PO has that Odoo CE does not

| Feature | D365 | Odoo 18 CE | OCA solution |
|---|---|---|---|
| Microsoft Project for the Web (WBS) | ✅ | `project.task` hierarchy (limited) | `project_wbs` OCA |
| Universal Resource Scheduling | ✅ AI-powered | `resource.resource` + `planning.slot` | `resource_planning` OCA |
| Multidimensional pricing (role + org unit + date) | ✅ | `product.pricelist` (one dimension) | Custom `ipai_*_delta` |
| Revenue recognition periodic calculation | ✅ | Manual journal entries | `account_analytic` OCA |
| Receipt OCR (Integrated mode) | ✅ | ✅ `account.vendor.bill` AI (18 CE) | Native |
| Proforma invoice workflow | ✅ | Draft invoice = proforma | Native |
| Fixed-price % completion | ✅ | Compute from timesheets | `[extend]` on `project.project` |

**Pulser's advantage over D365 PO:**
- BIR 2307/SLSP/SAWT compliance (native, not available in D365)
- Philippine tax localization (D365 PH localization is minimal)
- AI-native (Pulser copilot in Odoo vs D365's separate Copilot licensing)
- Zero licensing cost (Odoo 18 CE vs D365 Project Operations ≈ $120/user/mo)
- Single system for ERP + AI (Odoo unified vs D365 fragmented across Dataverse + Finance)

---

## §22 — D365 Business Process Catalog → Odoo Module Map

Source: https://learn.microsoft.com/en-us/dynamics365/guidance/business-processes/overview
Download: https://aka.ms/BusinessProcessCatalog (updated quarterly)

**The canonical framework for all Pulser spec bundles.** D365 organizes all
ERP functionality into 15 end-to-end scenarios (catalog IDs 10–99). IPAI's
Pulser spec bundles must map 1:1 to these scenarios. This section provides
the D365 scenario → Odoo module mapping for the 4 scenarios relevant to
TBWA\SMP Finance operations.

### D365 End-to-End Scenarios (all 15)

| ID | Scenario | IPAI priority | Odoo coverage |
|---|---|---|---|
| 10 | Acquire to dispose | Low | `account.asset` |
| 20 | Case to resolution | Low | `helpdesk` (OCA) |
| 30 | Concept to market | Low | `product` |
| 40 | Design to retire | Low | `mrp` |
| 50 | Forecast to plan | Medium | `stock.warehouse.orderpoint` |
| 55 | Hire to retire | Medium | `hr.*` + payroll OCA |
| 60 | Inventory to deliver | Medium | `stock.*` |
| **65** | **Order to cash** | **High** | `sale.*` + `account.move` (AR) |
| 70 | Plan to produce | Low | `mrp.*` |
| **75** | **Source to pay** | **High** | `purchase.*` + AP + BIR 2307 |
| **80** | **Project to profit** | **Primary** | `project.*` + analytic + invoicing |
| 85 | Prospect to quote | Medium | `crm.*` + `sale.order` |
| **90** | **Record to report** | **High** | `account.*` + period close |
| 95 | Service to deliver | Low | `helpdesk` + `field.service` |
| 99 | Administer to operate | Medium | Odoo admin + Azure RBAC |

---

### Project to Profit (ID 80) — 6 areas → Odoo modules

| D365 Business Process Area | Odoo Module | OCA / Custom |
|---|---|---|
| Develop project strategy | `project.project` (settings) | — |
| Manage project contracts | `sale.order` + `sale.order.line` | — |
| Plan projects (WBS, schedule, budget) | `project.task` (hierarchy) + `project.project` planned_hours | `project_wbs` (OCA) |
| Manage project delivery (time, expense) | `account.analytic.line` + `hr.expense` | `hr_timesheet_sheet` (OCA) |
| Manage project financials (billing, revenue) | `account.move` + analytic accounts + milestones | `account_analytic_*` (OCA) |
| Analyze project performance | SQL view reports + Power BI / Fabric | `project_report` (OCA) |

---

### Record to Report (ID 90) — 6 areas → Odoo modules

| D365 Business Process Area | Odoo Module | BIR relevance |
|---|---|---|
| Define accounting policies | `account.chart.template` + `account.account` | Chart of accounts = PH GAAP |
| Manage cash | `account.bank.statement` + bank reconciliation | — |
| Manage budgets | `account.budget` (OCA) | — |
| Record financial transactions | `account.move` + `account.journal` | All posted moves = BIR audit trail |
| Close financial periods | `account.move` period locking + year-end | Month-end close = TBWA\SMP workflow |
| Analyze financial performance | SQL views + `account.report` | FS reports + BIR forms |

**TBWA\SMP Finance team month-end close** maps to "Close financial periods":
- Lock prior period → Odoo: `account.journal` sequence lock date
- Accrue expenses → Odoo: manual journal entries on `account.move`
- Reconcile subledgers → Odoo: `account.reconcile.model`
- Post BIR returns → IPAI: `ipai_bir_tax_compliance` module
- Generate trial balance → Odoo: `account.report` (General Ledger)

---

### Source to Pay (ID 75) — 6 areas → Odoo modules

| D365 Business Process Area | Odoo Module | BIR relevance |
|---|---|---|
| Develop procurement strategy | `purchase.order` settings | — |
| Define procurement catalogs | `product.template` (purchase) | — |
| Manage supplier relationships | `res.partner` (supplier_rank > 0) | BIR TIN on partner |
| Source and contract goods/services | `purchase.requisition` (OCA) | — |
| Procure goods and services | `purchase.order` + `stock.picking` | — |
| Manage accounts payable | `account.move` (in_invoice) + `account.payment` | **BIR 2307** = EWT on vendor payment |

**Critical AP → BIR link:**
```
D365: Invoice capture → OCR → vendor invoice → payment → tax withheld
Odoo: account.move (in_invoice) → account.payment → wtax_amount → BIR 2307
```

---

### Order to Cash (ID 65) — 5 areas → Odoo modules

| D365 Business Process Area | Odoo Module | Notes |
|---|---|---|
| Develop sales policies | `product.pricelist` + `res.partner` credit | — |
| Manage sales orders | `sale.order` + `sale.order.line` | |
| Manage accounts receivable | `account.move` (out_invoice) + payments | |
| Manage credit and collections | `account.credit.limit` (OCA) | Odoo CE: limited native |
| Analyze sales performance | `sale.report` SQL view + Power BI | |

---

### Pulser Spec Bundle → D365 Catalog Alignment

Each Pulser spec bundle should reference the D365 catalog ID and area:

```
spec/
  pulser-project-to-profit/    ← D365 Catalog ID 80
    benchmarks/
      D365_80_vs_Odoo_mapping.md    ← this section (§22)
      D365_billing_methods.md       ← §21
    P2P_spec_bundle.md
  pulser-record-to-report/     ← D365 Catalog ID 90
    benchmarks/
      D365_90_month_end_close.md
    R2R_spec_bundle.md
  pulser-source-to-pay/        ← D365 Catalog ID 75
    benchmarks/
      D365_75_AP_BIR2307.md
    S2P_spec_bundle.md
  pulser-order-to-cash/        ← D365 Catalog ID 65
    benchmarks/
      D365_65_AR_invoicing.md
    O2C_spec_bundle.md
```

### Business Process Catalog download and use

The catalog is available as Excel at https://aka.ms/BusinessProcessCatalog
Updated at least 4x/year (latest: December 2025 version).

**Use the catalog to:**
1. Find the exact D365 business process name for any feature claim
2. Identify which D365 module(s) support it (Finance, SCM, PO, Sales, etc.)
3. Map it to the Odoo equivalent using this section
4. Validate in the D365 sandbox
5. Document in the spec bundle with catalog ID reference

This is the evidence base that makes Pulser claims defensible in
enterprise sales and in Microsoft co-sell conversations.

---

## §23 — OCA "Must Have" Modules (Curated Baseline)

Source: https://odoo-community.org/page/must-have-oca-modules

OCA volunteer consultants curated this list. Every IPAI Odoo 18 CE instance
should have these installed. Add to `oca_addons/` submodule accordingly.

### Core / Base (all instances)

| Module | Technical Name | OCA Repo | Purpose | IPAI relevance |
|---|---|---|---|---|
| Queue Job | `queue_job` | `queue` | Async background job execution via JobRunner | BIR form generation, period close, batch invoice |
| Report XLSX | `report_xlsx` | `reporting-engine` | Excel report generation base class | SLSP, SAWT, month-end reports |
| Password Security | `password_security` | `server-auth` | Company-level password requirements | Security hardening |
| Disable Odoo Online | `disable_odoo_online` | `server-brand` | Removes odoo.com links/menus (CE cleanup) | **Required for CE** |
| Remove Odoo Enterprise | `remove_odoo_enterprise` | `server-brand` | Removes Enterprise-only UI elements (CE) | **Required for CE** |
| Audit Log | `auditlog` | `server-tools` | Logs create/read/write/delete per model | BIR audit trail, RR90 record keeping |
| Name Search Improved | `base_name_search_improved` | `server-tools` | Fuzzy name search across fields | partner TIN search, product search |
| Date Range | `date_range` | `server-ux` | Global date range filters for list views | BIR period filters, month-end |
| Mass Edit | `server_action_mass_edit` | `server-ux` | Bulk edit multiple records at once | Bulk withholding tax category updates |
| Advanced Search | `web_advanced_search` | `web` | Advanced multi-field search | Cross-model filtering |
| Environment Ribbon | `web_environment_ribbon` | `web` | Dev/Staging/Prod ribbon (configurable) | **Required** — distinguish prod/staging |
| Favicon per Company | `web_favicon` | `web` | Company-specific favicons | Multi-company (TBWA\SMP, Dataverse, W9) |
| Mail Debrand | `mail_debrand` | `mail` | Removes "Powered by Odoo" from emails | Client-facing professionalism |
| Mail Tracking | `mail_tracking` | `mail` | Email delivery status per recipient | Collection follow-up tracking |
| Search Mail Content | `base_search_mail_content` | `social` | Search task/record by message content | AR collections search |

### Install commands (vendor as submodules)

```bash
cd oca_addons/

# Server brand (CE cleanup — install first)
git submodule add -b 18.0 https://github.com/OCA/server-brand server-brand
# Install: disable_odoo_online, remove_odoo_enterprise

# Queue (async jobs)
git submodule add -b 18.0 https://github.com/OCA/queue queue
# Install: queue_job

# Reporting engine (XLSX)
git submodule add -b 18.0 https://github.com/OCA/reporting-engine reporting-engine
# Install: report_xlsx

# Server tools (audit, search)
git submodule add -b 18.0 https://github.com/OCA/server-tools server-tools
# Install: auditlog, base_name_search_improved

# Server UX (mass edit, date range)
git submodule add -b 18.0 https://github.com/OCA/server-ux server-ux
# Install: date_range, server_action_mass_edit

# Web (search, ribbon, favicon)
git submodule add -b 18.0 https://github.com/OCA/web web
# Install: web_advanced_search, web_environment_ribbon, web_favicon,
#          web_listview_range_select, web_m2x_options, web_no_bubble,
#          web_refresher, web_responsive, web_search_with_and,
#          web_tree_many2one_clickable, web_dialog_size, web_pivot_computed_measure

# Mail
git submodule add -b 18.0 https://github.com/OCA/social social
# Install: mail_debrand, mail_tracking, base_search_mail_content, mail_activity_plan
```

### Environment ribbon configuration (system parameters)

```sql
-- Set in Settings → Technical → Parameters → System Parameters
-- ribbon.name = Dev / Staging / Production
-- ribbon.color = #000000
-- ribbon.background.color = #ff6633  (orange for staging, red for dev)
INSERT INTO ir_config_parameter (key, value)
VALUES
  ('ribbon.name', 'Staging'),
  ('ribbon.color', '#ffffff'),
  ('ribbon.background.color', '#ff0000');
```

### queue_job pattern for BIR form generation

```python
from odoo import models
from odoo.addons.queue_job.job import job


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_generate_bir_2307_async(self):
        """Queue BIR 2307 generation as background job."""
        for move in self:
            move.with_delay(
                channel='root.bir',
                priority=5,
                description=f'BIR 2307 for {move.name}',
            ).generate_bir_2307_job()

    @job(default_channel='root.bir')
    def generate_bir_2307_job(self):
        """Actual BIR 2307 generation — runs in background."""
        # ... generation logic ...
        self.write({'bir_2307_generated': True})
```

**queue_job setup on ACA:**
```yaml
# ACA container: ipai-odoo-dev-worker
# env vars needed:
ODOO_QUEUE_JOB_CHANNELS: root:1,root.bir:2
# The worker ACA container handles job execution
# Web container queues jobs via with_delay()
```

### report_xlsx pattern for BIR SLSP

```python
from odoo import models


class BirSlspXlsxReport(models.AbstractModel):
    _name = 'report.ipai_bir_tax_compliance.slsp_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        sheet = workbook.add_worksheet('SLSP')
        bold = workbook.add_format({'bold': True})

        # Headers
        headers = ['TIN', 'Vendor Name', 'Period', 'Gross Purchases', 'VAT']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        # Data rows from SQL view (§15)
        for row, rec in enumerate(records, start=1):
            sheet.write(row, 0, rec.partner_id.vat or '')
            sheet.write(row, 1, rec.partner_name)
            sheet.write(row, 2, rec.period)
            sheet.write(row, 3, rec.total_purchases)
            sheet.write(row, 4, rec.total_vat)
```

---

## §24 — Microsoft Entra SSO for Odoo 18 CE (Azure Sign-in)

Source: https://www.odoo.com/documentation/18.0/applications/general/users/azure.html

Enables TBWA\SMP users to sign in to `erp.insightpulseai.com` with their
Microsoft 365 (@omc.com) credentials. No separate Odoo password needed.

### Azure App Registration steps

```
Azure Portal → Entra ID → App registrations → New registration
  Name: Odoo IPAI ERP (or erp.insightpulseai.com)
  Supported account types: Accounts in this organizational directory only
                           (TBWA\SMP tenant) — single tenant
                           OR Multitenant (for multiple customer tenants)
  Redirect URI: Web  →  https://erp.insightpulseai.com/auth_oauth/signin

→ Authentication tab:
  Token types: ✅ Access tokens (implicit flows)
              ✅ ID tokens (implicit and hybrid flows)
  Save.

→ API Permissions tab:
  + Add Permission → Microsoft Graph → Delegated → User.Read
  (User.Read is usually added by default — verify it's present)

→ Overview tab:
  Copy: Application (client) ID  →  save to KV secret odoo-azure-client-id

→ Endpoints tab:
  Copy: OAuth 2.0 authorization endpoint (v2)
  Format: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize
  Save to notepad
```

### Odoo configuration (database-level)

```bash
# 1. Enable developer mode first
# Settings → Activate Developer Mode (or add ?debug=1 to URL)

# 2. Set system parameter (Settings → Technical → Parameters → System Parameters)
# Key:   auth_oauth.authorization_header
# Value: 1
# Click Save

# 3. Enable OAuth (Settings → Integrations → OAuth Authentication → ☑ Enable)
# Save and sign back in when prompted

# 4. Create OAuth Provider
# Settings → Integrations → OAuth Authentication → OAuth Providers → New
# Name:              Azure
# Client ID:         <Application (client) ID from Azure>
# Authorization URL: <OAuth 2.0 authorization endpoint (v2) from Azure>
# UserInfo URL:      https://graph.microsoft.com/oidc/userinfo
# Scope:             openid profile email
# CSS class:         fa fa-fw fa-windows
# Enabled:           ✅
# Save
```

### Store credentials in Key Vault (not hardcoded)

```bash
# Store Client ID in kv-ipai-dev-sea
az keyvault secret set \
  --vault-name kv-ipai-dev-sea \
  --name odoo-azure-sso-client-id \
  --value "<Application (client) ID>"

# Odoo reads from system parameter (set via Odoo UI or XML data file)
# Do NOT store Client Secret — OAuth2 implicit flow has no client secret
# For PKCE/auth code flow, store secret here:
# az keyvault secret set -n odoo-azure-sso-client-secret ...
```

### Automating the OAuth provider via XML data (for seed module)

```xml
<!-- ipai_agency_seed/data/oauth_provider.xml -->
<odoo>
  <data noupdate="1">
    <record id="provider_azure_ipai" model="auth.oauth.provider">
      <field name="name">Microsoft (TBWA\SMP)</field>
      <field name="auth_endpoint">
        https://login.microsoftonline.com/TBWA_TENANT_ID/oauth2/v2.0/authorize
      </field>
      <!-- Client ID injected from system parameter at runtime -->
      <field name="client_id">%(auth_oauth.authorization_header_placeholder)s</field>
      <field name="validation_endpoint">
        https://graph.microsoft.com/oidc/userinfo
      </field>
      <field name="scope">openid profile email</field>
      <field name="css_class">fa fa-fw fa-windows</field>
      <field name="enabled">True</field>
    </record>
  </data>
</odoo>
```

### First sign-in (user flow)

```
1. Navigate to erp.insightpulseai.com
2. Click "Microsoft (TBWA\SMP)" button on login page
3. Redirected to Microsoft login → enter @omc.com email
4. Complete MFA if required
5. First time: Accept permissions page (Odoo reads User.Read from Microsoft)
6. Odoo auto-creates user linked to Microsoft account
   (user must exist in Odoo with matching email first OR
    enable auto-provisioning via res.users.create on OAuth callback)
```

### Multi-tenant variant (for marketplace — multiple customer Entra tenants)

```
For each new customer tenant (e.g., new enterprise Pulser customer):
  Azure App Registration → Supported account types:
    "Accounts in any organizational directory (Multitenant)"
  Authorization URL becomes:
    https://login.microsoftonline.com/common/oauth2/v2.0/authorize
  Each customer's users sign in with their OWN Entra credentials
  Odoo maps by email → res.users matching
```

### Mail integration via Azure OAuth (Outlook for Odoo)

Separate from SSO — see: https://www.odoo.com/documentation/18.0/applications/general/email_communication/azure_oauth.html

```
Azure App Registration → Mail.ReadWrite, Mail.Send, offline_access permissions
Odoo: Apps → install "Microsoft Outlook"
Settings → General Settings → Emails → Use Custom Email Servers → Outlook Credentials
Paste Application (client) ID + Client Secret Value
Configure outgoing/incoming mail servers using Outlook connector
```

**Client Secret expiry warning:** Set the longest available expiry (24 months).
Note the expiry date in KV secret metadata. Rotation causes mail outage if missed.

---

## §25 — LandingAI ADE — BIR Document Extraction Alternative

Source: https://github.com/landing-ai (org page reviewed)
SDK: `pip install landingai-ade`
Docs: https://docs.landing.ai/ade/ade-overview
MCP Server: `landing-ai/ade-document-processing-skills` (pre-built, Claude-tagged)

**ADE (Agentic Document Extraction)** by LandingAI (founded by Andrew Ng).
DPT-2 model achieves **99.16% accuracy on DocVQA** — significantly better
than Azure Document Intelligence's standard OCR for complex financial docs.
Three APIs: **Parse → Split → Extract**.

### Why ADE over Azure Document Intelligence for BIR docs

| Capability | Azure Document Intelligence | LandingAI ADE |
|---|---|---|
| DocVQA accuracy | ~85–90% | **99.16%** |
| Table extraction | ✅ | ✅ Better on complex tables |
| Confidence scores | ✅ | ✅ Per-field + grounding coords |
| Multi-doc splitting | ❌ | ✅ Split API (classify by type) |
| Bounding box grounding | ✅ | ✅ Pixel-level for audit trail |
| MCP server | ❌ | ✅ Pre-built |
| Azure-native | ✅ (Key Vault, MI) | ❌ External API key |
| PH localization | ❌ | ❌ (both need custom schema) |
| Cost | Per-page Azure pricing | Per-API-call ADE pricing |

**Recommendation for IPAI:** Use ADE for complex BIR documents (2307, SAWT,
multi-page vendor invoices with tables), Azure DocIntel for standard invoices.
Store `VISION_AGENT_API_KEY` in `kv-ipai-dev-sea`.

### Three ADE APIs

```python
from pathlib import Path
from pydantic import BaseModel, Field
from landingai_ade import LandingAIADE

client = LandingAIADE()  # reads VISION_AGENT_API_KEY from env

# 1. PARSE — convert any document to structured JSON + Markdown
parse_response = client.parse(
    document=Path("/path/to/bir-2307.pdf"),
    model="dpt-2-latest"
)
# Returns: chunks (text, tables, images, form fields, barcodes)
#          markdown (ready for AI ingestion)
#          grounding coordinates per chunk

# 2. SPLIT — classify mixed-document PDFs
split_response = client.split(
    split_class=[
        {
            "name": "BIR Form 2307",
            "description": "Certificate of Creditable Tax Withheld at Source",
            "identifier": "Form 2307"
        },
        {
            "name": "Vendor Invoice",
            "description": "AP invoice from a Philippine vendor"
        },
        {
            "name": "Official Receipt",
            "description": "BIR-registered official receipt (OR)"
        }
    ],
    markdown=parse_response.markdown,
    model="split-latest"
)

# 3. EXTRACT — pull specific BIR fields with type safety
class BIR2307Fields(BaseModel):
    payee_tin: str = Field(description="Payee TIN in format 000-000-000-000")
    payee_name: str = Field(description="Name of the payee/vendor")
    income_payment_date: str = Field(description="Date of income payment YYYY-MM-DD")
    amount_of_income: float = Field(description="Amount of income payment in PHP")
    amount_withheld: float = Field(description="Amount of tax withheld in PHP")
    atc_code: str = Field(description="ATC code e.g. WC010, WI010")
    period_from: str = Field(description="Period from YYYY-MM-DD")
    period_to: str = Field(description="Period to YYYY-MM-DD")

from landingai_ade.lib import pydantic_to_json_schema
schema = pydantic_to_json_schema(BIR2307Fields)

extract_response = client.extract(
    document=Path("/path/to/bir-2307.pdf"),
    schema=schema,
    model="dpt-2-latest"
)
bir_data = extract_response.extraction  # BIR2307Fields instance
confidence = extract_response.extraction_metadata  # per-field confidence
```

### Async jobs for batch BIR processing

```python
import asyncio
from landingai_ade import AsyncLandingAIADE

async def batch_process_bir_docs(pdf_paths: list[Path]):
    """Process multiple BIR documents in parallel."""
    async with AsyncLandingAIADE() as client:
        jobs = []
        for pdf in pdf_paths:
            job = await client.parse_jobs.create(
                document=pdf,
                model="dpt-2-latest",
            )
            jobs.append(job.job_id)

        # Poll for completion
        results = []
        for job_id in jobs:
            while True:
                status = await client.parse_jobs.get(job_id)
                if status.status == "completed":
                    results.append(status)
                    break
                await asyncio.sleep(2)

        return results
```

### BIR OCR pipeline with ADE (replaces docai-ipai-dev for complex docs)

```
Vendor invoice/BIR doc received (email attachment or upload)
  → Blob Storage (stipaidev/bir-inbox)
  → Service Bus trigger → ACA Function
  → ADE Split API → classify doc type
    ├── BIR Form 2307 → ADE Extract (BIR2307Fields schema)
    ├── Vendor Invoice → ADE Extract (VendorInvoiceFields schema)
    └── Official Receipt → ADE Extract (OfficialReceiptFields schema)
  → Validated fields (with confidence scores) → Cosmos DB metadata
  → Low confidence fields → human review queue (ops.exceptions)
  → High confidence fields → Odoo vendor bill creation via XML-RPC
  → Odoo: account.move (in_invoice) created with EWT populated
  → BIR 2307 generated from validated data
```

### ADE MCP Server (add to Pulser tool catalog)

```python
# Add ADE MCP server to ipai-copilot project tool connections
# Portal: ipai-copilot → Tools → Add MCP server

# Or wire in copilot_gateway.py:
# The pre-built ADE MCP server is at: landing-ai/ade-document-processing-skills
# Clone and run as ACA sidecar to ipai-release-manager or as standalone ACA
# MCP endpoint: http://ipai-ade-mcp-server/mcp

# Key Vault: store VISION_AGENT_API_KEY in kv-ipai-dev-sea
az keyvault secret set \
  --vault-name kv-ipai-dev-sea \
  --name ade-vision-agent-api-key \
  --value "<VISION_AGENT_API_KEY from landing.ai>"
```

### ade-fintech community repo

`landing-ai/ade-fintech` contains community-built financial services projects
using ADE. Monitor for BIR-relevant reference implementations:
- Bank statement extraction
- Financial statement parsing (10-K/annual report patterns)
- Invoice processing workflows

These patterns map directly to IPAI's BIR SLSP (bank statement matching),
SAWT (withholding agent summary), and AP invoice automation workflows.
-e 

---
## Part 4: IPAI Agent Platform (Pulser / MAF / Foundry)
---
name: ipai-agent-platform
description: >
  InsightPulseAI agent platform — Pulser canonical classification, Microsoft
  Agent Framework (MAF) patterns, Foundry Agent Service wiring, judge
  infrastructure, release manager, and IPAI-specific SDK fixes. Load whenever
  working with Pulser agents, MAF orchestration, agent deployment, Foundry
  integration, judge evaluation, or the release manager. Essential for any
  agent code in the IPAI stack. Pairs with ipai-resource-map for resource
  constants and official microsoft-foundry skill for Foundry patterns.
---

# IPAI Agent Platform

Everything needed to build, deploy, and evaluate agents in the IPAI stack.

---

## Pulser — Canonical Classification

**Never describe Pulser as a chatbot, RAG bot, or declarative agent.**

```
Core type:        Custom-engine agent
                  Owns runtime, tools, policies, retrieval, validators.
                  Not host-product copilot. Not declarative agent.

Functional type:  Transactional and operational copilot
                  System-of-action inside Odoo:
                  prepares → validates → routes → summarizes → publishes

Architecture:     Multi-agent orchestrated system
                  planner/router + specialist agents (finance, project,
                  research, ops) + fallback/self-heal + tool calling +
                  retrieval + validators

Governance:       Policy-gated agent
                  RBAC + approval bands + evidence scope +
                  mutation safety + surface/domain/role behavior matrix
```

**Labels (use verbatim):**
- GTM: `"Pulser is an AI operating copilot for Odoo."`
- Technical: `"Custom-engine, multi-agent, policy-gated enterprise copilot for Odoo-centered workflows."`
- Architecture: `"Custom-engine agent platform with planner/router, specialist agents, tool adapters, retrieval, validators, and policy-gated action execution."`

**What Pulser is NOT:**
- Not a simple chatbot
- Not a pure RAG bot
- Not a declarative agent (no host orchestration as source of truth)
- Not an open autonomous agent (every mutation is policy-gated)

---

## Deployed Agent Inventory

| Service | FQDN | Status | Purpose |
|---|---|---|---|
| `ipai-odoo-mcp` | `ipai-odoo-mcp.internal.blackstone-0df78186.southeastasia.azurecontainerapps.io` | ✅ LIVE | Odoo MCP Server — 13 tools |
| `ipai-release-manager` | `ipai-release-manager.internal.blackstone-0df78186.southeastasia.azurecontainerapps.io` | ✅ LIVE | MAF Release Manager |
| `ipai-copilot-gateway` | internal ACA | ✅ LIVE | Foundry proxy / Pulser gateway |
| `ipai-bot-proxy-dev` | internal ACA | ✅ LIVE | Bot Framework webhook proxy |

**Release Manager caveat:** `/health` → 200 OK. `/release-manager/evaluate` → `{decision: "ERROR", error: "agent_framework not available"}` — MAF not yet wired to Foundry endpoint at runtime. Fix: set `IPAI_FOUNDRY_ENDPOINT` + `AZURE_CLIENT_ID` env vars.

---

## Microsoft Agent Framework (MAF) — IPAI Patterns

### Correct import path (SDK changed — do not use top-level import)

```python
# ❌ WRONG — breaks at module load
from agent_framework import FoundryChatClient

# ✅ CORRECT
from agent_framework.azure_ai import AzureAIAgentClient
```

### Lazy factory pattern (REQUIRED — prevents import-time failures)

All MAF-dependent objects must be behind lazy factories. This lets `/health`
respond even when Foundry isn't fully wired at runtime.

```python
# ❌ WRONG — fails at startup if Foundry not available
client = AzureAIAgentClient(endpoint=FOUNDRY_ENDPOINT)
tools = [MCPStreamableHTTPTool(url=MCP_URL)]

# ✅ CORRECT — lazy, health endpoint always responds
_client = None
_tools = None

def _get_client():
    global _client
    if _client is None:
        _client = AzureAIAgentClient(
            endpoint=os.environ["IPAI_FOUNDRY_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
    return _client

def _get_tools():
    global _tools
    if _tools is None:
        _tools = [
            MCPStreamableHTTPTool(url=os.environ["ODOO_MCP_URL"]),
        ]
    return _tools
```

### FastMCP server (SDK API — current version)

```python
# ❌ WRONG — old API
mcp = FastMCP(description="Odoo MCP Server")

# ✅ CORRECT — current API
mcp = FastMCP(instructions="Odoo MCP Server")
```

### FoundryChatClient (keyless, DefaultAzureCredential)

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from agent_framework.azure_ai import AzureAIAgentClient

# In ACA — uses id-ipai-dev MI automatically
client = AzureAIAgentClient(
    endpoint="https://ipai-foundry-sea.services.ai.azure.com/api/projects/ipai-copilot",
    credential=DefaultAzureCredential(),
    model="claude-sonnet-4-6",
)

# Never: client = AzureAIAgentClient(api_key="...")
```

### Wire Release Manager to Foundry (pending fix)

```bash
az containerapp update \
  -n ipai-release-manager \
  -g rg-ipai-dev-odoo-runtime \
  --set-env-vars \
    IPAI_FOUNDRY_ENDPOINT="https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot" \
    AZURE_CLIENT_ID="$(az identity show -n id-ipai-dev \
      -g rg-ipai-dev-odoo-runtime --query clientId -o tsv)"
```

---

## Odoo MCP Server — Tool Surface

13 tools across 4 categories:

**Data (7):** `search_read`, `get_record`, `get_fields`, `get_model_list`,
`search_count`, `get_related_records`, `get_field_metadata`

**Form (3):** `create_record`, `update_record`, `delete_record`

**Action (2):** `execute_method`, `execute_workflow`

**BIR-exclusive (2):** `generate_bir_form`, `get_bir_summary`

Endpoints: `/mcp` (FastMCP StreamableHTTP), `/health`

---

## Foundry Agent Service — Standard Setup

IPAI uses **Standard Setup** (BYO resources). All three dependencies deployed:

| Resource | Name | Region | Purpose |
|---|---|---|---|
| Cosmos DB NoSQL | `cosmos-ipai-dev` | EUS2 | Thread/conversation store |
| Storage (dedicated) | `stipaiagentdev` | EUS2 | File/blob store — DO NOT SHARE |
| AI Search | `srch-ipai-dev` | SEA* | Vector/knowledge store |

⚠️ `stipaiagentdev` is EXCLUSIVELY for Foundry Agent Service.
Never use it for application data. Never interact directly with
system-managed collections inside it.

Capability host wiring: `ipai-copilot` project → all three resources.
Foundry system-assigned MI must be ON (verify in portal → Identity → Status).

---

## Judge Infrastructure

### 6 Judge passports

| Judge | Pass threshold | Domain | First eval |
|---|---|---|---|
| `security-judge` | 90 | governance | 2026-04-12: 96 PASS |
| `architecture-judge` | 75 | governance | 2026-04-12: 91 PASS |
| `platform-fit-judge` | 70 | governance | 2026-04-12: 87 PASS |
| `governance-judge` | 70 | governance | 2026-04-12: 79 PASS |
| `customer-value-judge` | 60 | governance | 2026-04-12: 76 PASS |
| `finops-judge` | 65 | governance | 2026-04-12: 77 PASS |

### Judge-map registration (judge-map.yaml)

```yaml
version: "1.0.0"
judges:
  - name: security-judge
    domain: governance
    passport: agents/passports/security-judge.yaml
    pass_threshold: 90
  - name: architecture-judge
    domain: governance
    passport: agents/passports/architecture-judge.yaml
    pass_threshold: 75
  # ... (all 6 registered)
```

### Missing: test entrypoint

`llm-judge.ts` and `regex-judge.ts` exist in `packages/agents/` but nothing
calls them with real agent I/O. Judge scores are self-assessed, not
programmatically computed. To fix: create `tests/run-judge.ts` that:
1. Loads an agent's recent output from `ops.run_events`
2. Calls `llm-judge.ts` with rubric + output
3. Writes score to `passport.evaluation_history[]`

---

## Skills Consolidation Status

### Install (official Microsoft skills — do NOT build from scratch)

```bash
# Azure Skills Plugin — 20 workflow skills + Azure MCP + Foundry MCP
claude plugin install azure@azure-skills

# Service skills (MicrosoftDocs/Agent-Skills)
git clone https://github.com/MicrosoftDocs/Agent-Skills.git /tmp/msdocs-skills
for skill in azure-container-apps microsoft-foundry azure-database-for-postgresql \
             azure-cosmos-db azure-key-vault azure-front-door \
             azure-cognitive-search azure-container-registry; do
  cp -r /tmp/msdocs-skills/skills/$skill ~/.claude/skills/
done

# SDK skills (microsoft/skills)
git clone https://github.com/microsoft/skills.git /tmp/ms-sdk-skills
for skill in agents-v2-py azure-ai-projects-py azure-cosmos-db-py \
             azure-postgres-ts azure-ai-contentsafety-py azure-identity-py; do
  cp -r /tmp/ms-sdk-skills/.github/plugins/azure-skills/skills/$skill ~/.claude/skills/
done
```

### Delete (deprecated/wrong-version)

```bash
# Delete from agents/skills/ or wherever they live in the repo
rm -rf agents/skills/superset-dashboard-automation
rm -rf agents/skills/superset-dashboard-designer
rm -rf agents/skills/superset-sql-developer
rm -rf agents/skills/odoo19-developer
rm -rf agents/skills/odoo19-oca-first
rm -rf agents/skills/odoo19-views-widgets
rm -rf agents/skills/odoo19-contributing
rm -rf agents/skills/odoo19-administration
rm -rf agents/skills/odoo19-services
```

### IPAI-specific skills to keep/build

```
ipai-resource-map     → this session ✅
ipai-agent-platform   → this session ✅
ipai-odoo-platform    → this session ✅
ipai-bir-compliance   → build next (extract from odoo18-ce-development)
```

---

## Agent 365 + M365 E7 (GA: May 1, 2026)

**Direct impact on IPAI:**

Each Pulser specialist agent needs an **Entra Agent ID** under Agent 365 to
be manageable in customer M365 admin centers. The 6 Azure Bot registrations
(`id-ipai-agent-*` MIs) map directly to this pattern.

Post-GA: agents must be visible in the M365 admin center Agent Registry for
enterprise customer IT admins to govern them. Without Agent 365, Pulser bots
appear as unmanaged — hard blocker for TBWA\SMP and enterprise sales.

**Activate M365 E5 developer subscription (25 licenses) now:**
`Partner Center → Benefits → Cloud services → M365 E5 Developer Subscription`

This gives the Teams dev sandbox needed to test all 6 bot registrations
before May 1 GA.

---

## Pulser Behavior Constraints (always active)

```
Write tools:  approval_mode="always_require"
Read tools:   approval-free (Research mode safe)
Mutations:    must have evidence linkage before execution
Odoo data:    no writes from outside Odoo ORM
Publish:      no action without source evidence
Tenant:       tenant_id + RLS on every customer-facing table
```

---

## 12-Issue Backlog Status

| # | Issue | Skills coverage |
|---|---|---|
| 1 | Break-glass identity | `cloud-security-architect` persona — no executor |
| 2 | Dependency burn-down | ADO MCP can query — no triage agent |
| 3 | FinOps controls | `finops-judge` can score — no enforcer |
| 4 | Fabric vs Databricks | `data-forge` passport — decision pending |
| 5 | SLOs | ⚠️ MISSING — build `slo-definer` skill |
| 6 | Canary rollout proof | Release Manager built — needs one live run |
| 7 | AI Search population | ⚠️ MISSING — build `search-indexer` skill |
| 8 | Agent eval coverage | Judge infra built — zero runtime runs |
| 9 | Cost controls as policy | ⚠️ MISSING — build `policy-enforcer` skill |
| 10 | Gate deploys on SLO | `odoo_health_agent.py` has logic — needs wiring |
| 11 | Gate agents on evals | Schema ready — needs eval data |
| 12 | Recurring readiness scoring | WAF grounding doc exists — needs scheduler |

---

## Microsoft Foundry — Canonical Reference (Feb 2026 rebrand)

Source: https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry
Blog: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/microsoft-foundry-an-end-to-end-platform-for-building-governing-and-scaling-ai/4496736

**The platform previously called "Azure AI Studio" / "Azure AI Foundry"
is now called "Microsoft Foundry."**

### Terminology migration table (apply in all new code)

| Old term | New term | IPAI impact |
|---|---|---|
| Azure AI Studio / Azure AI Foundry | **Microsoft Foundry** | Update all docs/comments |
| Azure AI Services (endpoint) | **Foundry Tools** | Update resource descriptions |
| Assistants API (Agents v1) | **Responses API (Agents v2)** | `agent_orchestrator.py` audit needed |
| Threads | Conversations | Update agent state terminology |
| Messages | Items | Update agent state terminology |
| Runs | Responses | Update agent state terminology |
| Assistants | Agent Versions | Update agent state terminology |
| Multiple SDKs (`azure-ai-inference`, `azure-ai-ml`, etc.) | **`azure-ai-projects` 2.x** (unified) | Update requirements.txt |
| Monthly `api-version` params | v1 stable routes (`/openai/v1/`) | Update API calls |
| Hub + Azure OpenAI + Azure AI Services | **Foundry resource** (single, with projects) | ✅ IPAI already has this |

### IPAI resource mapping (confirmed correct names)

```
Resource name:    ipai-copilot-resource
Resource type:    Microsoft.CognitiveServices/account (kind: AIServices)
Resource label:   Microsoft Foundry resource ← use this term
Project name:     ipai-copilot
Project type:     Microsoft.CognitiveServices/account/project
Project label:    Foundry project
Portal:           https://ai.azure.com (toggle "New Foundry" ON)
Endpoint:         https://ipai-foundry-sea.services.ai.azure.com/api/projects/ipai-copilot
Model inference:  https://ipai-foundry-sea.services.ai.azure.com/models
```

### Architecture: resource vs project separation

```
Foundry resource (ipai-copilot-resource)    ← governance layer
├── Networking, security, RBAC              ← IT/admin scope
├── Model deployments                       ← claude-sonnet-4-6, claude-haiku
└── Projects
    └── ipai-copilot                        ← development layer
        ├── Agents, evaluations, files      ← developer scope
        ├── Agent state (Standard Setup)    ← cosmos-ipai-dev
        ├── File store (Standard Setup)     ← stipaiagentdev
        └── Vector store (Standard Setup)   ← srch-ipai-dev
```

### RBAC starter (least privilege — confirmed by architecture docs)

```bash
# Two assignments required — both at Foundry RESOURCE scope
# (not project scope — resource scope covers everything below)

# 1. For each developer user
az role assignment create \
  --role "Azure AI User" \
  --assignee <developer-upn> \
  --scope /subscriptions/eba824fb/.../ipai-copilot-resource

# 2. For project managed identity (and id-ipai-dev)
az role assignment create \
  --role "Azure AI User" \
  --assignee-object-id <mi-principal-id> \
  --assignee-principal-type ServicePrincipal \
  --scope /subscriptions/eba824fb/.../ipai-copilot-resource
```

### Responses API (Agents v2) — unified SDK pattern

```python
# requirements.txt — replace all azure-ai-* with:
# azure-ai-projects>=2.0.0

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# In ACA — uses id-ipai-dev MI (client_id from env var)
credential = DefaultAzureCredential()

client = AIProjectClient(
    endpoint="https://ipai-foundry-sea.services.ai.azure.com/api/projects/ipai-copilot",
    credential=credential,
)

# Agents v2 — Responses API terminology
# Create agent (was "assistant")
agent = client.agents.create_agent(
    model="claude-sonnet-4-6",
    name="pulser-finance",
    instructions="You are Pulser, an AI operating copilot for Odoo finance workflows.",
    tools=[...],  # from 1,400+ tool catalog or custom MCP tools
)

# Conversations (was "threads")
conversation = client.agents.create_thread()

# Items (was "messages")
client.agents.create_message(
    thread_id=conversation.id,
    role="user",
    content="Prepare the month-end BIR 2307 certificate for TBWA\\SMP."
)

# Responses (was "runs")
response = client.agents.create_and_process_run(
    thread_id=conversation.id,
    agent_id=agent.id,
)
```

### Key new capabilities (relevant to IPAI)

**1,400+ tool catalog** — Foundry agents can use tools from a catalog without
custom MCP server code. Check catalog before building custom tools:
```
Portal → ipai-copilot project → Agents → Tools catalog
```
IPAI's `ipai-odoo-mcp` provides the 13 Odoo-specific tools not in catalog.
Standard tools (code interpreter, file search, Bing grounding) come free.

**Foundry IQ** — citation-backed knowledge integration using `srch-ipai-dev`.
This is the native grounding feature — may reduce need for custom RAG code
once AI Search index is populated.

**Publishing to M365/Teams** — agents in `ipai-copilot` can be published
directly to Teams channels (direct path for TBWA\SMP Finance team bots).
Post-Agent 365 GA (May 1, 2026), each published agent gets an Entra Agent ID.

**Memory** — agents retain and recall context across interactions without
repeated input. IPAI impact: reduces prompt-stuffing in Pulser finance agents.
Enable per-agent in project settings. Stored in agent state (cosmos-ipai-dev).

**Multi-agent orchestration** — SDK-native workflow orchestration for
collaborative agent behavior. Python and C# SDKs. IPAI impact: validates
our supervisor-mediated pattern; evaluate native Foundry orchestration
vs custom `agent-platform` dispatcher for simpler flows.

**Foundry Control Plane** — centralized governance for AI resources, policies,
and access across teams. IPAI impact: aligns with our `platform/` control plane;
evaluate adoption for RBAC/policy enforcement layer.

**MCP + A2A authentication** — enterprise controls with full auth support for
MCP and A2A protocols. IPAI impact: validates our three-protocol model
(A2A + MCP + Agent365). Native auth reduces custom middleware.

**Real-time observability dashboard** — `appi-ipai-dev` + Foundry dashboard
provides continuous agent evaluation metrics. Set up at:
```
Portal → ipai-copilot → Operate → Monitoring
```

### Pending IPAI migration items (from v1 → v2)

```
1. Audit agent_orchestrator.py — check if using Assistants API v1 or v2
   Search for: "threads", "messages", "runs", "AssistantsClient"
   Replace with: Conversations/Items/Responses or AIProjectClient

2. Update requirements.txt:
   - azure-ai-inference → azure-ai-projects>=2.0.0
   - azure-ai-generative → azure-ai-projects>=2.0.0
   Keep: azure-identity (unchanged)

3. Rename in all comments/docs:
   "Azure AI Foundry resource" → "Microsoft Foundry resource"
   "Azure AI Services endpoint" → "Foundry Tools endpoint"
```

### Microsoft Foundry for VS Code Extension

Source: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/get-started-projects-vs-code
Marketplace: `TeamsDevApp.vscode-ai-foundry`

**Install:** Extensions → search "Foundry" → Install. Or: `code --install-extension TeamsDevApp.vscode-ai-foundry`

**Connect to IPAI project:**
1. Azure icon → Sign in → select subscription `eba824fb`
2. Resources → Foundry → `ipai-copilot-resource` → right-click `ipai-copilot` → "Open in Foundry Extension"

**Extension sections:**
| Section | Contents | IPAI use |
|---|---|---|
| Resources | Deployed models, agents, connections, vector stores | View gpt-4.1-mini deployment, agent versions |
| Tools | Model Catalog, Model Playground, Agent Playgrounds (remote+local), Local Visualizer, Deploy Hosted Agents | Test Pulser prompts, deploy new models post-RTFP |
| Help | Docs, GitHub, feedback | — |

**Key actions from VS Code:**
- **Browse model catalog** — Cmd+Shift+P → `Foundry: Open Model Catalog` — filter by publisher, feature, fine-tuning support
- **Deploy model** — right-click Models → "Deploy new AI model" → set name, type, version, TPM
- **Generate sample code** — right-click deployed model → "Open code file" → choose SDK (Python/C#/JS/Java) + auth method → generates Responses API starter
- **Model playground** — Tools → Model Playground → interactive chat with system prompt, view code
- **Agent playground** — remote (cloud) or local agent testing

**IPAI-specific setup:**
```
# After installing extension + signing in:
# 1. Default project = ipai-copilot
# 2. Right-click project → copy endpoint:
#    https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot
# 3. Models section shows: gpt-4.1-mini (only surviving deployment post-RTFP)
# 4. Use Model Catalog to deploy additional models after RTFP unblock
```

**Relation to Claude Code:** Both are dev-time tools. Foundry extension manages Azure AI resources (models, agents, deployments). Claude Code manages repo execution (code, IaC, CI/CD). They coexist — different concerns, same workspace.

---

## Microsoft Agent Framework (MAF) — Canonical Install + DevUI

Source: https://github.com/microsoft/agent-framework (7.2k ⭐, 1.1k forks)
Docs: https://learn.microsoft.com/agent-framework/

```bash
pip install agent-framework --pre
# Installs all sub-packages. May take a minute on Windows.
```

NuGet (.NET): `dotnet add package Microsoft.Agents.AI`

### Key capabilities beyond what IPAI currently uses

**Graph-based workflows** (upgrade from SequentialBuilder):
```python
from agent_framework.workflows import WorkflowGraph

# Time-travel debugging — replay from any checkpoint
# Human-in-the-loop nodes — pause for approval
# Streaming — real-time token streaming
graph = WorkflowGraph()
graph.add_node("plan", planner_agent)
graph.add_node("execute", executor_agent)
graph.add_node("review", human_review_node)  # blocks until approval
graph.add_edge("plan", "execute")
graph.add_edge("execute", "review")
```

**AF Labs** (experimental — benchmarking + RL):
```
python/packages/lab/
  benchmarking/    # agent quality measurement
  rl/              # reinforcement learning for agent improvement
```
Maps directly to Issue 8 (agent eval coverage) and Issue 12 (recurring readiness scoring).

**DevUI** — interactive developer UI for testing workflows locally:
```bash
pip install agent-framework[devui] --pre
agent-framework devui  # opens browser UI at http://localhost:7860
```
Use DevUI to debug `agent_orchestrator.py` locally before deploying to
`ipai-release-manager` ACA. Eliminates "deploy to see if it works" cycle.

**Migration guides** (if transitioning from other frameworks):
- From Semantic Kernel: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel
- From AutoGen: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen

### Agent workflow sample structure

```
microsoft/agent-framework/
  python/samples/
    01-agents/        ← single agent patterns
    02-tools/         ← tool calling patterns
    03-workflows/     ← graph-based multi-agent
  workflow-samples/   ← complete workflow examples
    release-manager/  ← matches ipai-release-manager pattern
```

---

## Solution Template: Release Manager (Official Microsoft Match)

**Found in Foundry portal → Discover → Solution templates:**
"Create a multi-agent Release Manager Assistant"
+3 services: Azure AI Agent Service, Azure Container Apps, MAF, ADO MCP

This is the official Microsoft template for what `ipai-release-manager`
already implements. Compare IPAI's implementation against this template:

```bash
# Clone the template to compare architecture
# Portal → Discover → Solution templates →
# "Create a multi-agent Release Manager Assistant" → Clone repository
```

Key differences to look for:
- Does the template use Responses API (v2) or Assistants API (v1)?
- Does it use `AIProjectClient` or the older `AgentsClient`?
- What ADO MCP server integration pattern does it use?

**Other relevant templates in IPAI's stack (filter: ACA + MAF + Foundry IQ):**

| Template | IPAI relevance | Action |
|---|---|---|
| Multi-Agent Workflow Automation | MAF graph pattern | Review workflow-samples/ |
| Get started with AI agents | ACA + Agent Service baseline | Compare vs ipai-copilot-gateway |
| Generate documents from your data | Closes Issue 7 (AI Search population) | Reference for indexer skill |
| Multi-modal content processing | docai-ipai-dev use case (invoices, BIR forms) | Wire docai → OCR pipeline |
| Deploy your AI application in production | Production baseline | See §below |
| Agentic applications for unified data | Fabric + agents (fcipaidev decision) | Fabric trial decision reference |

---

## Deploy-Your-AI-Application-In-Production (Production Baseline)

Source: https://github.com/microsoft/Deploy-Your-AI-Application-In-Production

Official Microsoft production accelerator. Single `azd up` deploys:
- Microsoft Foundry
- Azure AI Search + OneLake index
- Microsoft Fabric workspace and lakehouses
- Optional Microsoft Purview integration
- Private networking, managed identities, governance (WAF-aligned)

```bash
# One-command production deployment
git clone https://github.com/microsoft/Deploy-Your-AI-Application-In-Production
cd Deploy-Your-AI-Application-In-Production
# Review infra/main.bicepparam — disable Fabric/Purview for first run
azd up
```

**IPAI gap vs this template (what IPAI has vs what template adds):**

| Component | IPAI has | Template adds |
|---|---|---|
| Foundry + AI Search + ACA | ✅ | same |
| Private networking | ✅ Partial (pe-pg, pe-kv) | End-to-end VNet isolation |
| Microsoft Fabric | ✅ fcipaidev (trial) | Fabric workspace + lakehouses (permanent) |
| OneLake index | ❌ | AI Search wired to OneLake (lakehouse federation) |
| Microsoft Purview | ❌ | Optional but scaffolded |
| PostgreSQL mirroring to Fabric | ❌ | Scripted (via OneLake mirroring) |

**PostgreSQL → Fabric mirroring** is the most relevant gap. The template
scripts Odoo's `pg-ipai-odoo` → OneLake mirroring — this is the Fabric
trial decision answer: if IPAI mirrors PG to Fabric, Databricks becomes
redundant for the ERP analytics layer. Decision deadline: May 20.

---

## M365 Agents Toolkit — Channel Deployment for the 6 Bots

Source: https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/overview-agents-toolkit

**Previously "Teams Toolkit" → now "Microsoft 365 Agents Toolkit"**

This is the deployment tool for IPAI's 6 Azure Bot registrations:
- `ipai-ap-invoice-teams-bot-dev`
- `ipai-bank-recon-teams-bot-dev`
- `ipai-doc-intel-teams-bot-dev`
- `ipai-finance-close-teams-bot-dev`
- `ipai-pulser-teams-bot-dev`
- `ipai-tax-guru-teams-bot-dev`

### Install

```bash
# VS Code extension
# Extensions → search "Microsoft 365 Agents Toolkit" → Install

# CLI
npm install -g @microsoft/teamsfx-cli
```

### Write once, run everywhere

Agents Toolkit + M365 Agents SDK deploys the same agent to:
```
Microsoft 365 Copilot  ← primary enterprise surface
Microsoft Teams        ← TBWA\SMP Finance team chat
Outlook                ← email-based agent interactions
Web                    ← web portal surface
SMS / Email            ← lightweight notification channels
+10 other channels
```

The 6 Azure Bot registrations (`ipai-*-teams-bot-dev`) map to this.
Each bot registration = one agent deployed to one or more channels.

### Microsoft 365 Agents Playground (local testing — no tenant needed)

```bash
npm install -g @microsoft/teams-app-test-tool
# Opens local Teams-like sandbox — no M365 developer tenant required
# No ngrok, no bot registration needed for local dev/test
```

**Use this to test `ipai-bot-proxy-dev` routing locally** before wiring
to the 6 registered Azure bots. Eliminates the "register → deploy → test"
cycle for the Teams surface.

### Connection to Agent 365 (GA: May 1, 2026)

Post-May 1: each bot deployed via Agents Toolkit gets an Entra Agent ID
under Agent 365. IT admins at TBWA\SMP see it in M365 admin center →
Agents → All agents → Registry. This is the governance requirement for
enterprise Teams deployment.

Timeline:
```
Now:    Activate M365 E5 developer subscription (Partner Center → Cloud services)
        → gives dev tenant for Agents Playground
Apr 21: Business Applications Partner Office Hours → ask about agent deployment
May 1:  Agent 365 GA → assign Agent 365 licenses to TBWA\SMP users
        → deploy 6 bots via Agents Toolkit → Entra Agent IDs created
```

---

## azd (Azure Developer CLI) — Deployment Mechanism for All Templates

Source: https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-templates
Gallery: https://azure.github.io/awesome-azd/ (64 AI templates)

All 64 Foundry AI templates deploy with one command. IPAI's current
deployment is `az containerapp create` + manual Bicep — it should be
`azd`-compatible so every template in the gallery can be compared,
cloned, or adapted.

### Template structure (what IPAI needs to add)

```
ipai-repo/
├── infra/                  ✅ EXISTS (infra/azure/modules/*.bicep)
│   └── azure/
│       └── modules/
│           ├── foundry-agent-dependencies.bicep
│           └── release-manager-aca.bicep
├── azure.yaml              ❌ MISSING — maps source code to Azure resources
├── .azure/                 ❌ MISSING — environment configs, sub IDs
│   └── dev/
│       └── .env            ← AZURE_SUBSCRIPTION_ID, AZURE_LOCATION, etc.
├── .github/
│   └── workflows/          ✅ EXISTS (8 active workflows)
│       └── azure-dev.yml   ❌ MISSING — the azd-specific CI/CD workflow
└── src/                    ← or addons/, agents/, etc.
```

### `azure.yaml` (add to repo root)

```yaml
# azure.yaml — maps IPAI services to Azure resources for azd
name: ipai-platform
metadata:
  template: ipai-platform@0.0.1

services:
  odoo-web:
    project: ./addons
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      context: .

  release-manager:
    project: ./agent-platform/agents/release-manager
    language: python
    host: containerapp

  odoo-mcp:
    project: ./mcp/servers/odoo
    language: python
    host: containerapp
```

### Make IPAI azd-compatible (convert existing repo)

```bash
# From repo root — initializes azd without overwriting existing infra
azd init --no-prompt

# Creates .azure/dev/.env with defaults
# Then set IPAI-specific values:
azd env set AZURE_SUBSCRIPTION_ID eba824fb-332d-4623-9dfb-2c9f7ee83f4e
azd env set AZURE_LOCATION southeastasia
azd env set FOUNDRY_ENDPOINT https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot
azd env set AZURE_CONTAINER_REGISTRY_NAME acripaiodoo

# Deploy everything (provisions + deploys in one command)
azd up

# Deploy to staging sub (ISV sponsored)
azd env new staging
azd env set AZURE_SUBSCRIPTION_ID eba824fb-332d-4623-9dfb-2c9f7ee83f4e
azd up --environment staging
```

---

## Template Gallery — IPAI Priority List (from 64 templates)

Ranked by direct relevance to IPAI's stack and open issues.

### Tier 1 — Clone and compare immediately

| Template | Repo | Why |
|---|---|---|
| **Release Manager Assistant** | Azure-Samples/release-manager-assistant | Exact match to `ipai-release-manager`. Python + TypeScript, GPT-4 Omni, 14+ services. Diff against `agent_orchestrator.py` |
| **Home Banking Assistant** | Azure-Samples/home-banking-assistant | MAF + Foundry, closest Pulser architecture analog. Bank transactions ≈ BIR/accounting workflows |
| **Prior Authorization Multi-Agent** | Azure-Samples/prior-auth-multi-agent | Most modern pattern: MAF hosted agents + MCP servers + `azd up`. Uses **GPT-5.4** — monitor this model |
| **Get started with AI agents** | Azure-Samples/get-started-with-ai-agents | Baseline agent ACA template (fork 553, star 317) — compare vs `ipai-copilot-gateway` |

```bash
# Clone Release Manager to compare architecture
azd init --template Azure-Samples/release-manager-assistant
# Review: which API version (v1 Assistants or v2 Responses)?
# Review: how does it wire ADO MCP vs IPAI's implementation?
grep -r "AssistantsClient\|AIProjectClient\|create_thread\|create_conversation" .
```

### Tier 2 — Reference for open issues

| Template | Closes issue | Key pattern |
|---|---|---|
| **Document Generation and Summarization** | Issue 7 (AI Search population) | Odoo docs → AI Search indexing pipeline |
| **Multi-modal Content Processing** | docai-ipai-dev wiring | Invoice/BIR form OCR → structured output |
| **Agentic Applications for Unified Data Foundation** | Fabric trial decision (May 20) | Fabric workspace + Foundry agents + Semantic Kernel |
| **Medallion Architecture with Fabric** | stipaidevlake Bronze→Gold | Bronze/Silver/Gold lakehouses + Power BI |
| **RAG chat on PostgreSQL** | pg-ipai-odoo RAG pattern | PG vector search as alternative to AI Search |
| **Conversation Knowledge Mining** | TBWA\SMP audio transcription | Large audio/text dataset insights |

### Tier 3 — Monitor

| Template | Why |
|---|---|
| **Prior Authorization Multi-Agent** | Uses **GPT-5.4** — new model, may be available in Foundry soon |
| **NLWeb Agent Demo** | NLWeb open project by Microsoft — natural language for any website |
| **Serverless GenAI assistant + Purview Data Security** | If IPAI pursues Purview integration post-Marketplace |

---

## GPT-5.4 — New Model Sighting

The "Prior Authorization Multi-Agent" template lists `GPT-5.4` as its model.
This model name is non-standard — monitor for availability in `ipai-copilot-resource`:

```bash
# Check available deployments in IPAI's Foundry project
az cognitiveservices account deployment list \
  -n ipai-copilot-resource \
  -g rg-data-intel-ph \
  --query "[].{name:name, model:properties.model.name, version:properties.model.version}" \
  -o table

# If GPT-5.4 (or gpt-4.5) becomes available — deploy for evaluation
az cognitiveservices account deployment create \
  -n ipai-copilot-resource \
  -g rg-data-intel-ph \
  --deployment-name gpt-5-4-eval \
  --properties '{"model":{"format":"OpenAI","name":"gpt-5.4","version":"0"},"sku":{"name":"Standard","capacity":1}}'
```

---

## Microsoft Finance Agents — Competitive and Integration Reference

Source: https://learn.microsoft.com/en-us/copilot/finance/

**Previously "Copilot for Finance" → now "Finance agents"** (Feb 2026 rebrand,
parallel to Microsoft Foundry rebrand). The pattern: every Microsoft AI product
is dropping "Copilot" branding and becoming "[Product] agents."

### What Finance agents is

Two surfaces, two agent types:

| Surface | Agent | Function | Relevant to IPAI |
|---|---|---|---|
| Microsoft 365 Excel | **Financial Reconciliation agent** | Reconciles two table datasets, suggests rules, generates report | Competes with `ipai-bank-recon-teams-bot-dev` |
| Microsoft 365 Outlook | **Collections agent** | AR collections in Outlook — ERP data, email AI, save back to ERP | Integration opportunity via custom connector |

**Reconciliation agent** — Assistive (in-moment) OR Autonomous (scheduled):
- Compares two Excel tables (e.g., bank statement vs GL)
- AI suggests key field mappings and monetary column mappings
- Categorizes: unmatched / potentially matched / perfectly matched
- Generates AI summary with troubleshooting steps
- Saves report to SharePoint; sends email with link

**Collections agent** — AR workflow entirely in Outlook:
- Pulls ERP customer data directly into Outlook sidepanel
- Summarizes inbound customer emails
- AI-drafts reply emails
- Saves summaries, action items, promise-to-pay dates back to ERP

### Three ERP integration paths (critical for Pulser positioning)

```
Finance agents ERP integrations:
  1. Dynamics 365 Finance   ← native, direct
  2. SAP                    ← Power Platform SAP ERP connector + flows
  3. Custom connector       ← ANY OAuth 2.0 backend ← ODOO PATH
```

### Custom Connector → Odoo Integration (build this)

Finance agents exposes a Power Platform custom connector path:
any backend that supports OAuth 2.0 can be wired to the Finance agents
Outlook add-in. Connector must be named `copilotforfinancecomms`.

**Build path: Odoo → Finance agents Outlook (Collections):**

```
Step 1: Enable OAuth 2.0 on Odoo 18 CE
  → OCA module: auth_oauth (OCA/server-auth)
  → Or Odoo CE native: Settings → Technical → OAuth providers
  → Register Finance agents as OAuth client in Odoo

Step 2: Build Odoo Finance agents OpenAPI definition
  → Expose Odoo AR endpoints as REST JSON (via ipai-odoo-mcp or new controller)
  → Endpoints needed for Collections:
      GET /api/finance-agents/customers/{id}       ← customer balance + aging
      GET /api/finance-agents/customers/{id}/invoices  ← open invoices
      POST /api/finance-agents/customers/{id}/notes   ← save action items back
      POST /api/finance-agents/customers/{id}/promises ← promise-to-pay date

Step 3: Import OpenAPI definition into Power Platform
  → Power Apps (make.powerapps.com) → Data → Custom Connectors → New
  → Import OpenAPI (Swagger) file
  → Name connector exactly: copilotforfinancecomms
  → Auth: OAuth 2.0 → point to Odoo's OAuth endpoint

Step 4: Deploy Finance agents Outlook add-in
  → M365 Admin Center → Integrated apps → Finance agents
  → Requires: M365 E5 developer subscription (IPAI has this from ISV Success)
  → Connect to copilotforfinancecomms custom connector
```

**Odoo controller for Finance agents (add to `ipai_finance_agents` module):**
```python
from odoo import http
from odoo.http import request


class FinanceAgentsController(http.Controller):

    @http.route('/api/finance-agents/customers/<int:partner_id>',
                type='json', auth='oauth2', methods=['GET'])
    def get_customer_summary(self, partner_id):
        """Return customer AR summary for Finance agents Outlook sidecar."""
        partner = request.env['res.partner'].browse(partner_id)
        moves = request.env['account.move'].search([
            ('partner_id', '=', partner_id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
        ])
        return {
            'id': partner.id,
            'name': partner.name,
            'vat': partner.vat,  # TIN for BIR
            'total_receivable': partner.total_receivable,
            'overdue_amount': sum(
                m.amount_residual for m in moves
                if m.invoice_date_due < fields.Date.today()
            ),
            'invoices': [{
                'id': m.id,
                'name': m.name,
                'date': str(m.invoice_date),
                'due_date': str(m.invoice_date_due),
                'amount': m.amount_total,
                'residual': m.amount_residual,
                'status': m.payment_state,
            } for m in moves[:20]],
        }

    @http.route('/api/finance-agents/customers/<int:partner_id>/notes',
                type='json', auth='oauth2', methods=['POST'])
    def save_collection_note(self, partner_id, **kwargs):
        """Save Finance agents Outlook action item back to Odoo chatter."""
        partner = request.env['res.partner'].browse(partner_id)
        partner.message_post(
            body=kwargs.get('note', ''),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )
        return {'status': 'ok'}
```

### Critical limitation — English-only (Pulser's BIR moat)

Finance agents is currently **English (En-US) only** — both UI and all
AI-generated content. No Philippine localization, no BIR compliance,
no Filipino language support. This is Pulser's permanent moat for the
Philippine market:

```
Finance agents (Microsoft):        Pulser (IPAI):
  ✅ Excel reconciliation          ✅ Bank recon in Odoo + BIR 2307
  ✅ Outlook collections           ✅ AR chatter + Outlook via custom connector
  ❌ English-only UI               ✅ Filipino/English support
  ❌ No BIR (2307, SLSP, SAWT)     ✅ Native BIR compliance
  ❌ Requires M365 E5 + D365/SAP   ✅ Works with Odoo CE (zero licensing)
  ❌ No PH tax localization         ✅ Philippine fiscal localization
```

### Deployment prerequisites (from ISV Success benefits)

```
Required:
  ✅ M365 E5 developer subscription → already in ISV Success benefits
     (activate at Partner Center → Benefits → Cloud services)
  ✅ Dataverse environment → created during M365 E5 activation
  ✅ Power Platform (included in M365 E5)

Steps:
  1. Activate M365 E5 dev subscription (Partner Center)
  2. Create Dataverse environment (Power Platform admin center)
  3. Install Finance agents from AppSource / Copilot Studio
  4. Import copilotforfinancecomms custom connector with Odoo OpenAPI
  5. Deploy Finance agents Outlook add-in via M365 admin center
  6. Connect TBWA\SMP Finance team (CKVC, RIM, BOM) as test users
```

### Reconciliation agent vs ipai-bank-recon — decision

The Finance agents Reconciliation agent runs autonomously in Excel.
IPAI's `ipai-bank-recon-teams-bot-dev` runs as a Pulser agent in Teams.

**Recommended:** Use Finance agents Reconciliation for the Excel workflow
(bank statement CSV vs GL export), and use `ipai-bank-recon` for the
Odoo-native reconciliation (bank.statement.line → account.move matching).
They're complementary, not competing — Excel layer vs ERP layer.

---

## Azure Architecture Center — Foundry Reference Architectures

Sources:
- Baseline chat: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- Landing zone: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-landing-zone
- Doc classification: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/automate-document-classification-durable-functions
- Secure research: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/secure-compute-for-research
- Reference impl: https://github.com/Azure-Samples/microsoft-foundry-baseline

### Baseline Foundry Chat Architecture — critical findings for IPAI

**Reference implementation (clone first):**
```bash
git clone https://github.com/Azure-Samples/microsoft-foundry-baseline
# Landing zone variant:
git clone https://github.com/Azure-Samples/microsoft-foundry-baseline-landing-zone
```

**BOLA vulnerability — MUST FIX in copilot_gateway.py:**
Foundry Agent Service does not enforce per-user authorization on conversations.
The app server must verify the authenticated user owns the conversation before
forwarding to Agent Service. Passing a client-supplied conversation ID directly
without server-side validation is a BROKEN OBJECT LEVEL AUTHORIZATION vulnerability.

```python
# FIX NEEDED in copilot_gateway.py — conversation ownership check
async def chat_with_agent(request: Request, conversation_id: str):
    user_id = request.state.user_id  # from JWT / Entra token

    # VERIFY USER OWNS THIS CONVERSATION before forwarding to Agent Service
    owned = await verify_conversation_ownership(
        user_id=user_id,
        conversation_id=conversation_id,
        cosmos_client=cosmos_client,
    )
    if not owned:
        raise HTTPException(status_code=403, detail="Conversation not found")

    # Only then call Agent Service
    response = await agent_client.conversations.create_item(
        thread_id=conversation_id,
        ...
    )
```

**Agent definitions as code (current IPAI gap):**
- Store agent definitions, system prompts, connections, and parameters in source control
- Never make untracked changes via Foundry portal
- Use CI/CD + Foundry SDK to deploy from `ipai-build-agent` (ACA Job)
- Agent changes → create new immutable version → published Agent Application
  references the new version atomically (100% traffic switch)

**WAF tuning for chat (afd-ipai-dev WAF):**
Chat content triggers WAF false positives. User prompts contain SQL, code, HTML.
In multi-turn conversations, OWASP anomaly score accumulates → HTTP 403.
```
Fix: Add WAF exclusion scoped to request body field carrying chat messages
Portal → afd-ipai-dev → WAF policy → Custom rules → Exclusions
Scope: RequestBodyContent matching the chat message field name
NOT: disable rules globally
Also: increase request body inspection limits for chat payload sizes
```

**Agent egress subnet → Azure Firewall rules (IPAI production requirement):**
All agent egress MUST route through Azure Firewall for FQDN-based egress control.
```
snet-agentsEgress → UDR → Azure Firewall
Allow outbound TCP/443 to: srch-ipai-dev.search.windows.net (AI Search)
Allow outbound TCP/443 to: cosmos-ipai-dev.documents.azure.com (Cosmos)
Allow outbound TCP/443 to: any approved MCP server FQDNs
Deny all other egress
```

**Foundry Agent Service dependencies — isolation rule:**
DO NOT share `cosmos-ipai-dev`, `stipaiagentdev`, `srch-ipai-dev` with other
workload components. These are managed exclusively by Agent Service.
Any other workload Cosmos DB data → separate account.
Never interact directly with Agent Service-managed collections/containers.

**DR for Agent Service — critical gaps:**
- Agent Service has NO built-in DR — incident can permanently delete agents/conversations
- Enable Cosmos DB continuous backup (PITR 7-day RPO)
- Maintain separate source-of-truth for grounding knowledge (rebuild AI Search index)
- Add delete resource lock to Cosmos, Storage, AI Search:
```bash
az lock create --name no-delete --resource-group rg-ipai-dev-odoo-data \
  --resource-name cosmos-ipai-dev \
  --resource-type Microsoft.DocumentDB/databaseAccounts \
  --lock-type CanNotDelete
```

**Reliability: zone redundancy for Agent Service deps:**
```bash
# Cosmos DB — enable zone redundancy (EUS2 already has AZ support)
az cosmosdb update -n cosmos-ipai-dev -g rg-ipai-dev-data \
  --enable-multiple-write-locations false \
  --locations regionName=eastus2 failoverPriority=0 isZoneRedundant=true

# Storage — upgrade to ZRS (if currently LRS)
az storage account update -n stipaiagentdev -g rg-ipai-dev-data \
  --sku Standard_ZRS

# AI Search — add replicas (need 3 for zone redundancy)
az search service update -n srch-ipai-dev -g rg-ipai-dev-data \
  --replica-count 3
```

**Model deployment strategy:**
- Dev/POC: Global Standard (highest quota, routes to most available region)
- Production: Data Zone Standard (for PH data residency) or
  Data Zone Provisioned (for predictable throughput/latency)
- Use spillover: provisioned + standard for overflow

---

### Document Classification Pipeline → BIR Form OCR (docai-ipai-dev)

Reference architecture maps directly to IPAI's BIR document processing need:
D365 AP vendor invoice OCR → Odoo → BIR 2307 generation

```
Vendor invoice upload (email/portal)
  → Blob Storage (stipaidev/bir-inbox)
  → Service Bus queue (trigger)
  → Azure Functions (Durable) orchestration
    → Activity 1: Document Intelligence Analyze
        → Splits multi-page PDF into individual documents
        → NER: vendor TIN, invoice number, date, amount, tax
    → Activity 2: Cosmos DB metadata store
        → Saves doc type, page ranges, correlation ID
    → Activity 3: Embedding + AI Search index
        → Semantic Kernel chunks + vectorizes
        → Stores in srch-ipai-dev
  ← User queries via Pulser (RAG against AI Search)
  ← BIR 2307 generation (from Cosmos DB metadata + Odoo account.move)
```

**Implementation notes:**
- Trigger: Azure Service Bus (NOT Azure Queue Storage — more reliable)
- Doc Intelligence model: prebuilt-invoice (covers PH vendor invoices)
- Correlation ID links AI Search results → Cosmos DB doc metadata
- Alternative trigger: Azure Event Grid on Blob Storage upload
- Agent Framework as alternative to Semantic Kernel for embeddings

**Cost control:**
- Document Intelligence: commitment tier pricing (predictable monthly cost)
- AI Search: single replica for dev, 3 replicas for prod (zone redundancy)
- Model: Global Standard for dev → Data Zone Standard for prod

---

### Secure Research Environment → PrismaLab R&D (rg-ipai-ai-dev)

Architecture pattern for PrismaLab Medical Sciences (registered Apr 8 2026).
Handles HIPAA-equivalent sensitive research data (CAVE score PSE, toxoplasmosis,
HIV-TB co-infection manuscripts for JBLMGH Neurology).

**Data isolation pattern:**
```
Data owner uploads → public stipaidev/research-upload (Blob)
  → Fabric Data Factory trigger → copies to private stipaidev/research-secure
  → DELETES original (immutable — data owners can't access after upload)
  → Researchers access via Azure Virtual Desktop (not Bastion)
    → Data Science VMs (inside secure VNet)
    → Private endpoint only — no public IP on compute
  → Model/de-identified output → export-path → Logic App trigger
  → Manual approval (PI/ethics board) → approved
  → Data Factory moves to public research-outputs
```

**Why Azure Virtual Desktop over Bastion for researchers:**
- Stream VS Code as application (not just RDP/SSH)
- Limits copy/paste and screen capture (prevents data exfiltration)
- Supports Entra ID authentication to VMs
- Multiple researcher concurrent sessions

**Security must-haves for PrismaLab:**
- No public IP on any compute (enable `No public IP` on VMs)
- Private endpoint for all storage access
- Azure Machine Learning compute for model training (not just VMs)
- Key Vault for all credentials (inside secure VNet)
- Logic Apps approval workflow (outside secure VNet — metadata only, no data)
- Microsoft Sentinel for SIEM (HIPAA-equivalent audit trail)
- Defender for Cloud compliance score tracking

**IPAI resource mapping (what to provision for PrismaLab):**
```
rg-ipai-ai-dev (existing) → add:
  stprismalabsecure         ← private research data (Blob, ZRS)
  vm-prismalab-dsvm-01      ← Data Science VM (NC-series for ML)
  ml-prismalab-workspace    ← Azure Machine Learning workspace
  avd-prismalab-hostpool    ← Azure Virtual Desktop
  logic-prismalab-approval  ← approval workflow
Fabric: fcipaidev → PrismaLab workspace → Data Science lakehouse
```

---

## Microsoft Entra — Full Product Family + Agent ID

Source: https://learn.microsoft.com/en-us/entra/

### Entra product family (all 10 products)

| Product | Purpose | IPAI relevance |
|---|---|---|
| **Entra ID** | User identity + access (was Azure AD) | IPAI tenant (402de71a), TBWA\SMP users |
| **Entra Agent ID** | AI agent identities | Pulser specialist agents (post-May 1 2026) |
| Entra ID Protection | Identity risk detection | Security monitoring |
| Entra ID Governance | Access lifecycle | Marketplace tenant provisioning |
| **Entra External ID** | Customer/partner identity | Marketplace multi-tenant portal auth |
| Entra Internet Access | Secure Web Gateway (ZTNA) | Client VPN alternative |
| Entra Private Access | Zero Trust Network Access | Odoo portal access |
| Entra Verified ID | Verifiable credentials | DTI/BIR credential use case |
| **Entra Workload ID** | App/service identities | `id-ipai-dev` managed identity |
| Security Copilot + Entra | AI-driven SecOps | Threat investigation |

### Critical distinction: Workload ID vs Agent ID

```
Entra Workload ID = apps and services (non-human)
  → id-ipai-dev (Managed Identity for ACA containers)
  → Used for: Foundry, Cosmos DB, Key Vault, AI Search access

Entra Agent ID = AI agents (post-Agent 365 GA May 1 2026)
  → Each Pulser specialist agent gets an Entra Agent ID
  → IT admins see agents in M365 admin center → Agents → Registry
  → Governance: policy, monitoring, revocation per agent

Current IPAI: 6 Azure Bot registrations = pre-GA agent identity method
Post-May 1: redeploy via M365 Agents Toolkit → Entra Agent IDs created
```

### Entra External ID — Marketplace multi-tenant portal

For IPAI's ops-console SaaS portal (ISV Marketplace), the auth pattern is:
```
Tenant A (TBWA\SMP) signs up → Entra External ID tenant provisioning
Tenant B (Dataverse IT) signs up → separate External ID tenant
Tenant C (new enterprise customer) → separate External ID tenant

Each tenant signs in with their OWN Entra ID credentials
IPAI's application (ops-console) trusts External ID as identity broker
Tenant ID in JWT claim → maps to IPAI's marketplace.subscriptions table
```

Reference sample for multitenant SaaS:
`https://github.com/Azure-Samples/active-directory-aspnetcore-webapp-openidconnect-v2/tree/master/4-WebApp-your-API/4-3-AnyOrg`

---

## Entra Auth Patterns — IPAI-specific Code Samples

Source: https://learn.microsoft.com/en-us/entra/identity-platform/sample-v2-code

### Four auth flows IPAI uses

| Flow | Used for | Library |
|---|---|---|
| **Client Credentials Grant** | Pulser agents → Azure services (no user) | `DefaultAzureCredential` / MSAL |
| **Auth Code + PKCE** | ops-console portal user sign-in | MSAL React / MSAL Node |
| **On-Behalf-Of (OBO)** | ops-console → calls Pulser API → calls Foundry on user's behalf | MSAL |
| **Managed Identity** | ACA containers → Foundry, Cosmos, KV, AI Search | `DefaultAzureCredential` |

### Managed Identity pattern (current IPAI — already deployed)

```python
# agents/copilot_gateway.py — DefaultAzureCredential chain
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# In ACA: uses id-ipai-dev system MI automatically
# Order: EnvVar → WorkloadIdentity → ManagedIdentity → AzureCLI → VisualStudio
credential = DefaultAzureCredential()

# For explicit MI (when multiple MIs on same ACA):
credential = ManagedIdentityCredential(
    client_id="<id-ipai-dev-client-id>"  # from AZURE_CLIENT_ID env var
)
```

### Multitenant SaaS portal auth (ops-console)

```typescript
// web/ops-console/src/auth/config.ts
// MSAL configuration for multitenant SaaS (any Entra tenant can sign in)
import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID!,       // ops-console app reg
    authority: "https://login.microsoftonline.com/common", // multitenant
    redirectUri: process.env.REACT_APP_REDIRECT_URI!,
    postLogoutRedirectUri: "/",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

// Scopes for calling Pulser API (On-Behalf-Of pattern)
export const pulserApiScopes = {
  scopes: [`api://${process.env.REACT_APP_PULSER_API_CLIENT_ID}/access_as_user`],
};
```

### API protection pattern (copilot_gateway.py)

```python
# Protect Pulser API with Entra Bearer token validation
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

security = HTTPBearer()
TENANT_ID = "402de71a-..."  # IPAI Entra tenant
VALID_AUDIENCES = [
    f"api://{PULSER_API_CLIENT_ID}",
    PULSER_API_CLIENT_ID,
]


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Validate Entra Bearer token on every request."""
    token = credentials.credentials
    try:
        # Fetch JWKS (cache in production)
        openid_config_url = (
            f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
            "/.well-known/openid-configuration"
        )
        async with httpx.AsyncClient() as client:
            config = (await client.get(openid_config_url)).json()
            jwks = (await client.get(config["jwks_uri"])).json()

        # Validate JWT
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=VALID_AUDIENCES,
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
        )

        # Extract tenant_id for RLS
        payload["tenant_id"] = payload.get("tid")  # Entra tenant ID
        payload["oid"] = payload.get("oid")         # User object ID

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


# Use in endpoint:
@app.post("/pulser/chat")
async def chat(request: ChatRequest, claims: dict = Depends(verify_token)):
    tenant_id = claims["tenant_id"]
    user_oid = claims["oid"]

    # Verify conversation ownership (BOLA fix)
    await verify_conversation_ownership(user_oid, request.conversation_id)

    # Proceed with agent call
    ...
```

### Python daemon with managed identity (Pulser background agents)

```python
# Pattern for ACA job containers calling Microsoft Graph or Azure services
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

# No explicit credentials needed in ACA with MI
credential = DefaultAzureCredential()

# Example: Pulser release-manager calling ADO REST API
async def get_ado_work_items(project: str, ids: list[int]):
    """Call Azure DevOps REST API via managed identity."""
    token = credential.get_token("499b84ac-1321-427f-aa17-267ca6975798/.default")
    # 499b84ac... = Azure DevOps resource ID

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://dev.azure.com/insightpulseai/{project}/_apis/wit/workitems",
            params={"ids": ",".join(map(str, ids)), "api-version": "7.1"},
            headers={"Authorization": f"Bearer {token.token}"},
        )
    return response.json()
```

---

## SaaS Multitenant Architecture — IPAI Marketplace Design

Source: https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/
Full guide: https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/overview

### Tenant definition for IPAI

```
IPAI's model = B2B SaaS
Tenant = customer organization (e.g., TBWA\SMP, Dataverse IT Consultancy)
Users  = employees of that tenant (e.g., CKVC, RIM, BOM at TBWA\SMP)
NOT: Microsoft Entra tenant (that's a directory — different concept)
```

**In IPAI's schema** (already correct per doctrine):
```sql
-- Every customer-facing table has tenant_id + RLS
-- tenant_id = marketplace.subscriptions.id (IPAI's SaaS tenant)
-- NOT the Entra tenant ID (tid claim in JWT)

-- Map Entra tenant (tid) → IPAI tenant (subscription)
CREATE TABLE marketplace.entra_tenant_mapping (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_tenant_id text NOT NULL UNIQUE,  -- JWT tid claim
    subscription_id uuid REFERENCES marketplace.subscriptions(id),
    created_at timestamptz DEFAULT now()
);
```

### Multitenancy isolation models

The architecture guide covers these isolation options for each Azure service:

| Isolation model | Cost | Security | Complexity | Best for |
|---|---|---|---|---|
| Fully isolated (per-tenant infra) | Highest | Strongest | Highest | Enterprise/MACC customers |
| Pooled (shared + row-level security) | Lowest | RLS-enforced | Lowest | **IPAI default — all SMB tenants** |
| Hybrid (pool + isolated for premium) | Medium | Mixed | Medium | Tiered pricing (Starter/Pro/Enterprise) |

**IPAI current approach: Pooled + RLS** (correct for SMB tier):
- Single `pg-ipai-odoo` PostgreSQL instance
- `tenant_id` on every table + RLS policy
- Premium/Enterprise tier → dedicated ACA environment + separate PG Flex

### WAF SaaS pillar — design areas

The Azure WAF SaaS workload documentation covers these areas IPAI must address
before Marketplace listing:

```
1. Tenant lifecycle management
   → marketplace.subscriptions state machine (trial → active → suspended → deleted)
   → Entra tenant provisioning on signup

2. Data isolation and sovereignty
   → RLS on all tables (tenant_id) ✅
   → Data residency: all in SEA (correct for PH customers)

3. Metering and billing
   → ops.metering_events → Azure Metering API ❌ not yet wired
   → Billing tiers: Starter ($150/mo), Professional ($450/mo), Enterprise ($1,200+)

4. Tenant onboarding
   → Self-service signup portal (ops-console External ID auth)
   → Odoo company creation per tenant
   → Seed data module per tenant

5. Identity per tenant
   → Entra External ID for external portal
   → Each tenant's Entra users → IPAI JWT tenant_id mapping
```

### Marketplace readiness checklist (from multitenant guide)

```
[ ] tenant_id on every customer-facing table with RLS ✅
[ ] marketplace.subscriptions + state machine ✅ (designed)
[ ] ops.metering_events → Azure Metering Service API ❌
[ ] Entra External ID tenant provisioning ❌
[ ] Self-service signup portal (ops-console) ❌
[ ] Transactable SaaS offer in Partner Center ❌
[ ] Co-sell ready documentation (solution pitch deck) ❌
[ ] Azure IP Co-sell ($100K ACR threshold) ❌ (in progress)
[ ] Delete resource locks on all tenant data stores ❌
[ ] Tenant data export/deletion (GDPR/NPC) ❌
```

---

## Databricks + Fabric — IPAI Lakehouse Decision

Sources:
- https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621
- https://learn.microsoft.com/en-us/azure/architecture/example-scenario/dataplate2e/data-platform-end-to-end

**TL;DR: Databricks and Fabric are complementary, not competing.**
Keep both. Fabric for Odoo ERP mirroring + Power BI OKR (simple, SaaS).
Databricks for Pulser agent telemetry + ML training (complex, code-driven).

### The End-to-End Architecture (canonical reference)

```
Data Sources
  pg-ipai-odoo (PostgreSQL)  →  Fabric Mirroring  →  OneLake (Gold)
  Event Hubs (agent events)  →  Databricks DLT    →  Delta Lake
  stipaidevlake (ADLS)       →  Databricks Auto Loader → Delta Lake
  External APIs              →  Databricks        →  Unity Catalog

Processing Layer
  Databricks: Delta Live Tables, Photon Engine, Spark
  Fabric: Data Factory (Power Query, 200+ connectors), Notebooks

Storage
  OneLake (Fabric): Delta Lake format, used by Fabric workloads + Power BI
  Delta Lake on ADLS (Databricks): Unity Catalog governed, used by Databricks

Serving Layer
  Power BI → fcipaidev Finance PPM workspace → OKR dashboard
  Databricks SQL Serverless → ad-hoc analytics
  AI/BI Genie → natural language SQL (Databricks)
  Direct Lake mode → Power BI reads OneLake without import

Governance
  Unity Catalog (Databricks) → governs Delta Lake tables, ML models, vectors
  Microsoft Purview → enterprise-wide metadata from Unity Catalog sync
```

### IPAI layer assignment: Fabric vs Databricks

| Use case | Use | Why |
|---|---|---|
| Odoo ERP mirror → Power BI | **Fabric** | PostgreSQL mirroring built-in, no code |
| Finance PPM OKR dashboard | **Fabric** | fcipaidev → Power BI workspace |
| Agent telemetry (ops.run_events) | **Databricks** | Event Hubs → DLT → UC, needs Spark |
| ML model training (Pulser evals) | **Databricks** | MLflow + Photon + GPU clusters |
| Vector search for Pulser RAG | **Databricks** | Databricks Vector Search + Unity Catalog |
| BIR compliance reports | **Fabric** | Power BI + OneLake, no ETL needed |
| Ad-hoc analytics (non-technical) | **Fabric** | AI/BI Genie + no-code |
| Cross-cloud/on-prem data | **Databricks** | Lakehouse Federation, multi-cloud |

### PostgreSQL → Fabric Mirroring (Fabric trial decision — deadline May 20)

Fabric native mirroring of `pg-ipai-odoo` replaces the Databricks DLT
pipeline for the Odoo ERP analytics layer. This closes the biggest Fabric gap:

```
pg-ipai-odoo (PostgreSQL 16, PG Flex)
  → Fabric Mirroring (near-real-time CDC)
  → OneLake lakehouse (fcipaidev)
  → Power BI Direct Lake mode (no import, live data)
  → Finance PPM OKR dashboard

Setup (Fabric portal):
  fcipaidev → New → Mirrored Database
  → Select "Azure Database for PostgreSQL"
  → Enter host: pg-ipai-odoo.postgres.database.azure.com
  → Credentials: MI or connection string from kv-ipai-dev-sea
  → Select schemas/tables to mirror (start with: account_move, account_move_line,
    res_partner, project_project, account_analytic_line)
  → Start mirroring → tables appear as shortcuts in OneLake

Mirroring limitations:
  - Requires PostgreSQL with CDC enabled (logical replication)
  - PG Flex supports logical replication ✅
  - Enable: az postgres flexible-server parameter set \
      -n pg-ipai-odoo -g rg-ipai-dev-odoo-data \
      --name wal_level --value logical
  - Mirrored tables are read-only in Fabric → no write-back ✅
```

### Databricks Unity Catalog → Fabric shortcuts

The end-to-end architecture enables bidirectional browsing:

```
# In Fabric: create shortcuts to Databricks Unity Catalog tables
Fabric portal → fcipaidev → New → Shortcut
  → External sources → Azure Databricks (Unity Catalog)
  → Workspace URL: https://adb-<id>.azuredatabricks.net
  → Catalog: hive_metastore (or Unity Catalog)
  → Select: agent_telemetry.runs, agent_telemetry.events

# Required on Databricks side:
# Enable External Data Access on Unity Catalog metastore
# Grant EXTERNAL USE SCHEMA + Data Reader to Fabric service principal
```

### Databricks AI layer (IPAI-specific)

```
dbw-ipai-dev (rg-ipai-ai-dev, SEA)
  ├── Unity Catalog: governs all Delta Lake tables
  ├── Vector Search: Pulser RAG index (knowledge base for BIR docs)
  ├── MLflow: Pulser agent quality evaluation experiments
  ├── Feature Store: agent behavior features for RL training
  └── Model Serving: Pulser judge model (evaluation endpoint)

Integration with Foundry:
  → Pulser agents call Databricks Model Serving endpoints as tools
  → Agent evaluation results stored in Unity Catalog
  → Foundry Observability reads from Databricks SQL endpoint
```

---

## WAF Service Guides — IPAI Service Reference

Source: https://learn.microsoft.com/en-us/azure/well-architected/service-guides/?product=popular

WAF service guides exist for every IPAI primary service. Read before
modifying configuration of any of these services:

| IPAI Resource | WAF Guide URL |
|---|---|
| `afd-ipai-dev` (Front Door) | /service-guides/azure-front-door |
| `cosmos-ipai-dev` (Cosmos DB) | /service-guides/cosmos-db |
| `pg-ipai-odoo` (PostgreSQL) | /service-guides/postgresql |
| `stipaidev` / `stipaidevlake` (Blob) | /service-guides/azure-blob-storage |
| ACA Jobs / Functions | /service-guides/azure-functions |
| Service Bus (if added) | /service-guides/azure-service-bus |
| `appi-ipai-dev` (App Insights) | /service-guides/application-insights |
| Azure Firewall | /service-guides/azure-firewall |
| API Management (if added) | /service-guides/azure-api-management |
| `dbw-ipai-dev` (Databricks) | /service-guides/azure-databricks |
| `srch-ipai-dev` (AI Search) | → use Foundry WAF SaaS guide |

All guides at: `https://learn.microsoft.com/en-us/azure/well-architected/service-guides/`

### WAF Design Guides — apply to IPAI

Source: https://learn.microsoft.com/en-us/azure/well-architected/design

| Design guide | IPAI application |
|---|---|
| Background jobs | `queue_job` + ACA worker pattern for BIR generation |
| Handle transient faults | Retry in Pulser agent tools (Odoo MCP, AI Search) |
| Health modeling | `appi-ipai-dev` custom health model for Pulser |
| DR for multi-region | Cosmos DB PITR + AI Search DR (documented in agent skill) |
| Continuous integration | `.github/workflows/` → ipai-build-agent ACA job |
| Availability zones + regions | ACA env SEA + zone redundancy on Cosmos/Storage/Search |

**Completing the WAF assessments (ISV Success benefit):**
```
GenAIOps Maturity:  https://learn.microsoft.com/en-us/assessments/e14e1e9f-d339-4d7e-b2bb-24f056cf08b6/
WAF Review:         https://learn.microsoft.com/en-us/assessments/azure-architecture-review/
SaaS Workload:      https://learn.microsoft.com/en-us/assessments/d349c8c3-fe9c-4829-afdd-a5228e72a570/
```
All three should be completed before Marketplace listing. Results generate
a WAF report that serves as evidence for ISV co-sell technical validation.

---

## Agentic DevOps — Microsoft's Current DevOps Taxonomy

Source: https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/what-is-devops/
Agentic DevOps: https://azure.microsoft.com/en-us/solutions/devops

### DevOps definition (current — 2025)

DevOps breaks down Dev/Ops silos using cloud, AI, and emerging technologies.
**Agentic DevOps** is the 2025 evolution: AI agents operate autonomously in
every phase of the software lifecycle — from planning through monitoring.

```
DevOps lifecycle (8 phases):
  1. Plan      → Azure Boards + GitHub Issues + GitHub Copilot agents
  2. Code      → GitHub / Azure Repos + Copilot coding agents
  3. Build     → Azure Pipelines / GitHub Actions
  4. Test      → Azure Test Plans + AI-generated test cases
  5. Deploy    → Azure Pipelines CD + azd / Bicep IaC
  6. Operate   → Azure Monitor + ACA autoscaling
  7. Monitor   → Application Insights + AI anomaly detection
  8. Feedback  → GitHub Issues → Boards → back to Plan
```

### Azure DevOps services (IPAI uses all five)

| Service | IPAI usage | Notes |
|---|---|---|
| **Azure Boards** | `dev.azure.com/insightpulseai` → ipai-platform | Work items, sprints, epics |
| **Azure Repos** | ADO repo → GitHub InsightPulseAI/odoo | Code hosting + PRs |
| **Azure Pipelines** | `.github/workflows/` via ADO integration | CI/CD for ACA containers |
| **Azure Artifacts** | Python packages, Odoo wheels | Package management |
| **Azure Test Plans** | Agent evaluation test suites | Quality gate for Pulser |

### Agentic DevOps patterns (emerging — apply to IPAI)

```
Current IPAI:
  ipai-build-agent (ACA Job) → builds + deploys containers
  ipai-release-manager (ACA) → evaluates release readiness

Agentic DevOps extension (add these):
  Kubernetes / ACA management agent → auto-scales based on Pulser load
  Code review agent → GitHub Copilot PR review on Odoo module PRs
  Deployment health agent → post-deploy verification via AI
  Security agent → ADO pipeline dependency scanning (OWASP)
```

### GenAIOps = DevOps for AI/agent workloads (IPAI's operating model)

GenAIOps extends DevOps with AI-specific stages:
```
Standard DevOps     +     AI-specific additions
─────────────────────────────────────────────────────────
Plan/Code           +     Prompt engineering, system prompt versioning
Build/Test          +     Agent evaluation (AF Labs benchmarking)
Deploy              +     A/B agent versions, agent canary rollout
Monitor             +     Token usage, response quality, agent SLOs
Feedback            +     Human-in-the-loop corrections → fine-tuning
```

**IPAI's GenAIOps toolchain (current + target):**
```
Current:
  ipai-build-agent (ACA Job) → CI/CD
  ipai-release-manager → release gate evaluation
  GitHub Actions → test + lint gates
  Foundry observability → token usage, response metrics

Target:
  AF Labs benchmarking → agent quality scoring (Issues 8, 12)
  Prompt versioning in ADO → system prompt as code
  Evaluation CI gate → `azd deploy` only if eval score > threshold
  Foundry continuous evaluation → production quality monitoring
```

### Platform engineering (trend — IPAI ISV play)

Organizations build internal developer platforms (IDPs) so product teams
can self-service infrastructure. IPAI's Pulser IS an IDP-like offering:
- Pulser gives TBWA\SMP Finance team a self-service AI workflow platform
- The same pattern applies to each new Marketplace customer tenant
- The sponsored sub (`eba824fb`) becomes the staging "platform stamp"

---

## D365 Agentic ERP — Competitive Intelligence (Wave 1 2026)

Sources:
- https://www.microsoft.com/en-us/dynamics-365/solutions/erp
- Convergence 2025 blog (Feb 2026)
- D365 2026 Wave 1 release (Apr–Sep 2026)

**The competitive framing has shifted:** D365 ERP is now officially
"Agentic ERP" — Microsoft's page title is "Agentic ERP Software Solutions."
The narrative: "systems of record → systems of action." Pulser must use
the same language and demonstrate the same capability in Odoo.

### D365 ERP agents shipping NOW (direct Pulser competitors)

| D365 Agent | D365 Product | What it does | Pulser equivalent |
|---|---|---|---|
| **Account Reconciliation Agent** | D365 Finance | Auto-matches subledger → GL, flags exceptions | `ipai-bank-recon-teams-bot-dev` |
| **Supplier Communications Agent** | D365 Supply Chain | Handles vendor emails autonomously | `ipai-ap-invoice-teams-bot-dev` |
| **Sales Order Agent** | D365 Business Central | NL order processing | (not built yet) |
| **Payables Agent** | D365 Business Central | AP + reconciliations | `ipai-ap-invoice-teams-bot-dev` |
| **Time and Expense Agent** | D365 Project Operations | Timesheet entry + approval | `ipai-finance-close-teams-bot-dev` |
| **Activity Approvals Agent** | D365 Project Operations | Approval workflows | Pulser approval band |
| **Finance Agent** (Wave 1) | D365 Finance | Reconciliation + Excel + Outlook | vs Finance agents integration |

### D365 ERP MCP Server (D365 equivalent of ipai-odoo-mcp)

The Dynamics 365 ERP Model Context Protocol (MCP) server is evolving from static actions to a dynamic, configurable framework that adapts as business needs evolve. A new analytics MCP server extends this capability to structured metrics and insights, supporting agents to reason over governed operational and financial data—not snapshots or exports, but live business signals.

**IPAI parallel:** `ipai-odoo-mcp` is IPAI's equivalent of the D365 MCP server.
The D365 MCP server scales to "millions of ERP actions" — IPAI's current
13-tool implementation is the foundation to scale similarly.

### 2026 Wave 1 impact on Pulser positioning

The Finance Agent, expanding in wave 1, now supports reconciliation, variance analysis and data preparation in Excel as well as customer communications in Outlook, bringing financial intelligence into the productivity tools finance teams already use rather than requiring them to navigate separate ERP screens.

This is exactly what IPAI built independently:
- Finance agents Reconciliation (Excel) ← IPAI's bank recon bot
- Finance agents Outlook Collections ← IPAI's Finance agents custom connector
- D365 Finance Account Reconciliation Agent ← IPAI's Odoo bank reconciliation

**The convergence:** All major ERP vendors are racing to the same pattern.
IPAI's differentiation cannot be "we have agents" (everyone does now).
IPAI's differentiation must be:
1. **Philippine BIR compliance** (2307/SLSP/SAWT) — no D365 equivalent
2. **Zero licensing cost** (Odoo CE vs D365 Finance ~$180/user/mo + Copilot Credits)
3. **Unified ERP + AI on Azure** (Odoo + Foundry vs D365 + Copilot = same cloud)
4. **SMB-first** (Odoo is simpler, D365 Business Central is the SMB tier but still ~$70/user/mo)

### D365 pricing reference (for sales conversations)

| D365 Product | ~Price/user/month | Pulser equivalent | Pulser price |
|---|---|---|---|
| D365 Finance | ~$180 | Odoo CE (accounting) | $0 (CE) |
| D365 Supply Chain | ~$180 | Odoo CE (inventory/PO) | $0 (CE) |
| D365 Project Operations | ~$120 | Odoo CE (project + timesheet) | $0 (CE) |
| D365 Business Central (Essentials) | ~$70 | Odoo CE (full ERP) | $0 (CE) |
| D365 Business Central (Premium) | ~$100 | Odoo CE + OCA modules | $0 (CE) |
| Copilot Credits (agents) | Additional | Pulser (Foundry-backed) | Included in Pulser tier |

**Total cost for 25-user TBWA\SMP Finance team:**
- D365 Finance + Copilot: 25 × ($180 + $30) ≈ **$5,250/month**
- Pulser (Odoo CE + ACA): **$450/month** (Professional tier) + ~$200 Azure compute

### Business Central — the SMB competitive battleground

Business Central is "Best Cloud ERP System of 2025" (Forbes) and targets
the same SMB segment as IPAI. Key difference:
- Business Central Essentials = $70/user/month → still $1,750/mo for 25 users
- Pulser Starter = $150/month flat for up to N users

For the Philippines SMB market where per-user SaaS pricing is a major barrier,
flat-rate Pulser pricing is a structural advantage over both Business Central
and D365 Finance.

---

## LandingAI ADE — Document Processing MCP Tool

Source: https://github.com/landing-ai (org — 32 repos, 12 people)
Key repos: `ade-python`, `ade-document-processing-skills`, `ade-fintech`

**LandingAI ADE (Agentic Document Extraction)** — founded by Andrew Ng.
Pre-built MCP server (`ade-document-processing-skills`) tagged `claude` and
`agent-skills` — directly integrable with Pulser as a document AI tool.

### Repo inventory (what to use)

| Repo | Status | Use for IPAI |
|---|---|---|
| `ade-python` | ✅ Active (2 days ago) | BIR doc extraction SDK |
| `ade-document-processing-skills` | ✅ Active (last month) | Claude MCP agent skill |
| `ade-fintech` | ✅ Active (2 days ago) | Financial services reference implementations |
| `ade-typescript` | ✅ Active (3 days ago) | ops-console TypeScript integration |
| `agentic-doc` | ❌ Deprecated → use `ade-python` | Legacy |
| `vision-agent-mcp` | ❌ Deprecated → use ADE | Legacy |
| `vision-agent` | ❌ Deprecated → use ADE | Legacy |

### ADE as Pulser MCP tool

```
ipai-copilot project (Foundry)
  └── Tools
      ├── ipai-odoo-mcp (13 tools — Odoo ERP)         ✅ live
      ├── ADE MCP Server (document extraction)          ← ADD THIS
      │   Source: landing-ai/ade-document-processing-skills
      │   Endpoint: https://ipai-ade-mcp-server.internal/mcp
      └── srch-ipai-dev (AI Search — knowledge)        ✅ live
```

### ade-document-processing-skills — Claude skill file

This repo is a Claude skill (`ade-document-processing-skills`) tagged:
`ocr`, `pdf-parsing`, `ade`, `claude`, `document-processing`,
`document-extraction`, `rag`, `agent-skills`, `landingai`

**Deploy it to IPAI agents:**
```bash
# Clone agent skill into IPAI skills library
cd agents/skills/
git clone https://github.com/landing-ai/ade-document-processing-skills \
  document-extraction/

# Update skills-index.json
# Add entry: "document-extraction": {
#   "path": "agents/skills/document-extraction/",
#   "description": "LandingAI ADE — parse, split, extract structured data from PDFs",
#   "tools": ["parse_document", "split_document", "extract_fields"]
# }
```

### DPT-2 model — accuracy benchmark

- 99.16% accuracy on DocVQA validation split
- Handles: tables, pictures, charts, form fields, barcodes
- Returns: hierarchical JSON + Markdown + grounding coordinates per chunk
- Confidence scores per extracted field (routes low-confidence to human review)
- <2 second processing time for standard documents
- Scales to 1000+ page PDFs via async jobs + parallel processing

### Integration with Pulser Release Manager

The Release Manager agent can use ADE to:
```python
# In release_manager_agent.py — add ADE as a tool
@tool(description="Extract structured data from a PDF document")
async def extract_document(pdf_url: str, schema_name: str) -> dict:
    """
    Use ADE to extract structured fields from a document.
    schema_name: 'bir_2307', 'vendor_invoice', 'bank_statement'
    """
    from landingai_ade import AsyncLandingAIADE

    schemas = {
        'bir_2307': BIR2307Fields,
        'vendor_invoice': VendorInvoiceFields,
        'bank_statement': BankStatementFields,
    }

    async with AsyncLandingAIADE() as client:
        parse_resp = await client.parse(
            document=pdf_url,
            model="dpt-2-latest"
        )
        extract_resp = await client.extract(
            markdown=parse_resp.markdown,
            schema=pydantic_to_json_schema(schemas[schema_name]),
        )
    return {
        "data": extract_resp.extraction.model_dump(),
        "confidence": {
            k: v.confidence
            for k, v in extract_resp.extraction_metadata.__dict__.items()
        }
    }
```

### Pulser Agents tool catalog update

```json
// agents/registry/skills-index.json — add ADE entry
{
  "document-extraction": {
    "domain": "document-ai",
    "provider": "landingai",
    "model": "dpt-2-latest",
    "sdk": "landingai-ade",
    "accuracy": "99.16% DocVQA",
    "tools": [
      "parse_document",
      "split_document",
      "extract_fields",
      "batch_parse_async"
    ],
    "use_cases": [
      "BIR Form 2307 extraction",
      "Vendor invoice field extraction",
      "Bank statement reconciliation",
      "SAWT multi-document processing"
    ],
    "secret": "kv-ipai-dev-sea/ade-vision-agent-api-key",
    "mcp_server": "landing-ai/ade-document-processing-skills"
  }
}
```

---

## Anthropic Financial Services Plugins — Plugin Architecture Reference

Source: https://github.com/anthropics/financial-services-plugins (6.7k ⭐, 764 forks)
Platform: Claude Cowork (`claude.com/product/cowork`) + Claude Code

**41 skills, 38 commands, 11 MCP integrations** for financial services.
This is the canonical pattern for how IPAI should package Pulser capabilities
as Claude plugins — installable from claude.com/plugins marketplace.

### Plugin structure (copy this for Pulser)

```
pulser-bir-plugin/           ← IPAI equivalent of "financial-analysis"
├── .claude-plugin/
│   ├── plugin.json          ← plugin metadata, name, version, description
│   ├── skills/              ← passive behaviors that fire automatically
│   │   ├── bir-context.md   ← BIR terminology and compliance context
│   │   ├── odoo-context.md  ← Odoo accounting conventions
│   │   └── ph-tax-rules.md  ← Philippine tax rules (EWT, VAT, SLSP)
│   ├── commands/            ← slash commands
│   │   ├── bir-2307.md      ← /bir-2307 [vendor] [period]
│   │   ├── slsp.md          ← /slsp [company] [quarter]
│   │   ├── month-end.md     ← /month-end-close [company] [period]
│   │   ├── vendor-invoice.md← /vendor-invoice [file]
│   │   └── p2p-status.md    ← /p2p-status [company]
│   └── connectors/          ← MCP integrations
│       ├── odoo-mcp.json    ← ipai-odoo-mcp (13 tools)
│       ├── ade.json         ← LandingAI ADE document extraction
│       └── ai-search.json   ← srch-ipai-dev knowledge retrieval
├── CLAUDE.md                ← developer notes
└── README.md
```

### Pulser slash commands (modeled on financial-analysis plugin)

```bash
# Install Pulser plugin via Claude Code
claude plugin marketplace add insightpulseai/pulser-plugins
claude plugin install bir-compliance@pulser-plugins
claude plugin install odoo-finance@pulser-plugins

# Slash commands after install:
/bir-2307 [vendor_tin] [period]      # Generate BIR Form 2307 certificate
/slsp [company] [quarter]            # Summary List of Suppliers
/sawt [company] [year]               # Summary Alphalist of Withholding Tax
/month-end [company] [period]        # Month-end close checklist
/vendor-invoice [pdf_path]           # Parse vendor invoice → Odoo draft bill
/p2p-status [company]                # Procure-to-pay pipeline status
/r2r-status [company] [period]       # Record-to-report close status
/bir-forms [company] [period]        # All BIR returns due this period
```

### Plugin marketplace listing (IPAI → claude.com/plugins)

IPAI can list Pulser plugins on the Claude marketplace at `claude.com/plugins`.
This is the distribution channel for reaching new Claude Enterprise customers
who need Philippine ERP + BIR compliance capabilities.

**IPAI plugin marketplace entries to create:**

| Plugin | Type | Target user | Commands |
|---|---|---|---|
| `pulser-bir-compliance` | Core | PH finance teams | /bir-2307, /slsp, /sawt |
| `pulser-odoo-finance` | Add-on | Odoo accounting | /month-end, /p2p-status |
| `pulser-ph-erp` | Add-on | SMB operators | /vendor-invoice, /r2r-status |

**Partner page:** `claude.com/partners/powered-by-claude` — IPAI should apply
to the "Powered by Claude" partner program for marketplace visibility.

### Claude Platform partner page

The Anthropic engineering footer confirms Microsoft Foundry is a named
Claude Platform partner: `claude.com/partners/microsoft-foundry`

This means: IPAI's Claude deployment via Azure Foundry is an officially
supported and partnered path. The co-sell story is even stronger:
- Foundry is an official Claude Platform partner
- IPAI uses Claude via Foundry
- IPAI is in the Azure Startup Program
- Pulser can be sold as "Claude + Azure" solution on both marketplaces

---

## Managed Agents — Anthropic's Architecture (IPAI Already Implements This)

Source: https://www.anthropic.com/engineering/managed-agents
Docs: https://platform.claude.com/docs/en/managed-agents/overview

**"Scaling Managed Agents: Decoupling the brain from the hands"**
This is Anthropic's hosted service for long-horizon agent work. The key
insight: harnesses that encode assumptions about model limitations go stale
as models improve. The solution is stable interfaces above changing implementations.

### Brain / Hands / Session — the three interfaces

```
Brain (Claude + harness)
  → calls: execute(name, input) → string
  → calls: provision({resources})  ← only if needed
  → calls: emitEvent(id, event)    ← writes to session
  → calls: getEvents()             ← reads from session

Session (durable event log)
  → getSession(id)     ← full event log
  → wake(sessionId)    ← resume after harness crash
  → emitEvent(id, event)

Hands (sandboxes, tools, MCP servers)
  → execute(name, input) → string  ← universal interface
  → provision({resources})         ← spin up new environment
```

**IPAI already implements this correctly:**
- Brain: `ipai-release-manager` ACA (MAF orchestrator)
- Session log: `ops.run_events` (Supabase append-only) = the durable session
- Hands: `ipai-odoo-mcp` + ADE MCP + Foundry tools = `execute(name, input) → string`
- Credential proxy: MI + KV secret store = credentials never in sandbox ✅

### Security pattern — credentials never in sandbox

```python
# CORRECT (what Managed Agents does, what IPAI does):
# Credentials in KV, accessed via proxy with session token
# Claude never sees the raw token

# For MCP: OAuth tokens stored in kv-ipai-dev-sea
# Requests from agent → MCP proxy → KV fetch → external service
# Agent never handles credentials

# For Git (if added): clone repo with token during init
# Wire token into local git remote
# Agent uses git push/pull without seeing token
```

### Context window vs session log

The session log is NOT Claude's context window. They're separate:

```
Context window:  what Claude sees RIGHT NOW (limited, can be compacted)
Session log:     everything that ever happened (durable, append-only)

getEvents() interface lets brain:
  - Pick up from last stop
  - Rewind a few events before a specific moment
  - Reread context before a specific action
  - Apply context engineering transforms before passing to Claude
```

**IPAI implementation:** `ops.run_events` IS the session log.
`ipai-release-manager` reads from `ops.run_events` to resume after ACA restart.
This is the correct architecture — not just good practice, it's Anthropic's
production pattern.

### "Context anxiety" — example of stale harness assumptions

Managed Agents discovered Claude Sonnet 4.5 would wrap up tasks prematurely
as it sensed its context limit approaching. They added context resets to the
harness. When Claude Opus 4.5 arrived, the behavior was gone — the resets
became dead weight.

**IPAI implication:** Don't hardcode context management for specific model
versions in `agent_orchestrator.py`. Use the session/harness split so
context management can evolve without changing the agent's tool interfaces.

---

## Agent Evaluation Framework (Anthropic Engineering)

Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
Published: Jan 9, 2026

This is the canonical eval framework for IPAI's open Issues 5 (SLOs),
8 (agent evals), and 12 (recurring readiness scoring).

### Terminology (use these exact terms in IPAI eval code)

```python
# Task / problem / test case = single test with inputs + success criteria
# Trial = one attempt at a task (run multiple → consistent results)
# Grader = logic that scores agent performance (code, model, or human)
# Transcript / trace / trajectory = full messages array at end of eval run
# Outcome = final environment state (not what Claude said — what actually happened)
# Evaluation harness = infrastructure that runs evals end-to-end
# Agent harness / scaffold = system that enables model to act as agent
# Evaluation suite = collection of tasks for a specific capability/domain
```

### Three grader types (combine all three for Pulser evals)

```python
# 1. CODE-BASED GRADERS (fast, cheap, objective — use for BIR form validation)
def grade_bir_2307(transcript: list, outcome: dict) -> bool:
    """Check BIR 2307 has all required fields with correct format."""
    required_fields = ['payee_tin', 'amount_withheld', 'atc_code', 'period']
    for field in required_fields:
        assert field in outcome, f"Missing required field: {field}"
    # TIN format check
    assert re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', outcome['payee_tin'])
    # ATC code check
    assert outcome['atc_code'] in VALID_ATC_CODES
    return True

# 2. MODEL-BASED GRADERS (flexible, nuanced — use for report quality)
def grade_monthly_report_quality(transcript: list, outcome: dict) -> float:
    """LLM judge: is this month-end report professional and complete?"""
    response = anthropic.messages.create(
        model="claude-haiku-4-5",
        messages=[{
            "role": "user",
            "content": f"""Grade this financial report (0-1):
            Criteria: accuracy, completeness, BIR compliance, professional tone
            Report: {outcome['report_text']}
            Score only. No explanation."""
        }]
    )
    return float(response.content[0].text.strip())

# 3. HUMAN GRADERS (gold standard — use for quarterly calibration)
# Spot-check 10% of BIR form outputs with CKVC or BOM review
# Use human ratings to calibrate model graders
```

### Capability vs Regression evals for IPAI

```python
# CAPABILITY EVALS (start low pass rate → hill-climb)
# "What can Pulser do well?"
CAPABILITY_SUITE = [
    "Generate BIR 2307 from complex multi-page vendor invoice",
    "Handle BIR 2307 for mixed-ATX code invoice",
    "Reconcile bank statement with 50+ transactions",
    "Generate SLSP for 200+ vendors in one quarter",
]
# Target: start at 40% → improve to 80%+ before declaring GA

# REGRESSION EVALS (near 100% pass rate → don't break things)
# "Does Pulser still handle what it used to?"
REGRESSION_SUITE = [
    "Generate BIR 2307 for simple professional services invoice",
    "Standard month-end close checklist (TBWA\SMP pattern)",
    "EWT calculation for mixed non-resident/resident vendors",
]
# Gate: deployment blocked if regression suite < 95%
```

### Eval harness for IPAI Release Manager

```python
# .github/workflows/pulser-evals.yml
# Run on every PR to main — block merge if regression suite fails
# Run capability suite nightly — track improvement over time

# Infrastructure noise caveat (from engineering headline):
# "Infrastructure configuration can swing benchmarks by several percentage points"
# → Run each task 3 trials minimum
# → Use fixed seed where possible
# → Track p50 and p95, not just mean pass rate
```

### When to build evals

Per Anthropic: start evals when:
1. **Users report the agent feels worse after changes** — "flying blind" problem
2. **Can't distinguish real regressions from noise**
3. **Want to adopt a new model** — teams with evals upgrade in days, not weeks

IPAI is at stage 1 for `ipai-release-manager`. The eval harness should be
the first PR after the Foundry wiring is complete.

---

## Azure DevOps Remote MCP Server — IPAI Configuration

Source: https://learn.microsoft.com/en-us/azure/devops/mcp-server/remote-mcp-server?view=azure-devops
Repo: https://github.com/microsoft/azure-devops-mcp

### TL;DR — what works NOW vs what doesn't

| Client | Remote ADO MCP | Local ADO MCP |
|---|---|---|
| VS Code + GitHub Copilot | ✅ Works | ✅ Works |
| Visual Studio 2022+ | ✅ Works | ✅ Works |
| Claude Code / Claude Desktop | ❌ Blocked (needs OAuth dynamic registration in Entra) | ✅ Works with PAT |
| Claude via Foundry (ipai-copilot) | ❌ Coming soon | ✅ Use local + PAT |
| M365 Copilot / Copilot Studio | ❌ Not yet available | — |

**IPAI action:** Use the LOCAL ADO MCP server with a PAT stored in `kv-ipai-dev-sea`.
Remote server endpoint is configured for future Claude support when it ships.

### Remote server endpoint (IPAI)

```json
// .vscode/mcp.json (for VS Code with GitHub Copilot — works today)
{
  "servers": {
    "ado-remote-mcp": {
      "url": "https://mcp.dev.azure.com/insightpulseai",
      "type": "http",
      "headers": {
        "X-MCP-Toolsets": "repos,wit,pipelines",
        "X-MCP-Insiders": "true"
      }
    }
  }
}
```

### Local server (Claude / Pulser — use this now)

```bash
# Install local ADO MCP server (requires Node.js 20+)
npx @microsoft/azure-devops-mcp@latest

# Configure for Claude Code or copilot_gateway.py
export AZURE_DEVOPS_PAT="$(az keyvault secret show \
  --vault-name kv-ipai-dev-sea \
  --name ado-pat-ipai-platform \
  --query value -o tsv)"
export AZURE_DEVOPS_ORG="insightpulseai"
export AZURE_DEVOPS_PROJECT="ipai-platform"

# Store PAT in Key Vault (one-time)
az keyvault secret set \
  --vault-name kv-ipai-dev-sea \
  --name ado-pat-ipai-platform \
  --value "<PAT with Read/Write scope>"
```

### ADO MCP toolsets available for IPAI

| Toolset | Key tools | IPAI use case |
|---|---|---|
| `wit` | `wit_create_work_item`, `wit_update_work_item`, `wit_my_work_items`, `search_workitem` | Release Manager creates bugs from prod failures |
| `repos` | `repo_create_pull_request`, `repo_list_pull_requests_by_repo_or_project`, `repo_create_branch` | Review agent creates PRs for prompt updates |
| `pipelines` | `pipelines_get_build_status`, `pipelines_run_pipeline`, `pipelines_get_build_log` | Release Manager checks pipeline status before deploy |
| `wiki` | `wiki_create_or_update_page`, `wiki_get_page_content` | Pulser writes runbooks to ADO wiki |
| `testplan` | `testplan_create_test_case`, `testplan_show_test_results_from_build_id` | Eval harness creates test cases in Azure Test Plans |
| `search` | `search_code`, `search_workitem` | Pulser searches codebase and work items |

### Release Manager → ADO MCP integration pattern

```python
# In release_manager_agent.py — wire ADO MCP tools
# Tool: create a bug when production failure detected

@tool(description="Create a bug work item in Azure Boards for a production failure")
async def create_prod_bug(title: str, description: str, severity: str) -> dict:
    """
    Calls ADO MCP local server via MCP protocol.
    severity: '1 - Critical', '2 - High', '3 - Medium', '4 - Low'
    """
    # MCP call via local server: wit_create_work_item
    result = await mcp_client.call_tool("wit_create_work_item", {
        "organization": "insightpulseai",
        "project": "ipai-platform",
        "type": "Bug",
        "title": title,
        "description": description,
        "fields": {
            "System.AreaPath": "ipai-platform\\Pulser",
            "Microsoft.VSTS.Common.Severity": severity,
            "System.Tags": "production;automated"
        }
    })
    return result

@tool(description="Trigger Azure Pipeline deployment after eval gate passes")
async def trigger_pipeline(pipeline_id: int, branch: str = "main") -> dict:
    """Calls pipelines_run_pipeline via ADO MCP."""
    return await mcp_client.call_tool("pipelines_run_pipeline", {
        "organization": "insightpulseai",
        "project": "ipai-platform",
        "pipelineId": pipeline_id,
        "branch": branch
    })
```

### What's coming soon (don't build workarounds)

- Azure AI Foundry → ADO MCP Server (direct, no PAT needed)
- Copilot Studio → ADO MCP Server
- AgentId support in ADO MCP Server
- Dynamic OAuth registration for Claude Code / Claude Desktop

---

## azd March 2026 — IPAI Relevant Commands

Source: https://devblogs.microsoft.com/azure-sdk/azure-developer-cli-azd-march-2026/

### New azd ai agent commands (March 2026 — v1.23.x)

```bash
# Run agent locally for testing
azd ai agent run --name ipai-release-manager

# Send a test message to the running agent
azd ai agent invoke --name ipai-release-manager \
  --message "Evaluate release readiness for PR #142"

# Check agent container status and health
azd ai agent show --name ipai-release-manager

# Stream container logs in real time
azd ai agent monitor --name ipai-release-manager

# Deploy agent to Microsoft Foundry (ipai-copilot project)
azd up --environment ipai-dev
```

### azd init + GitHub Copilot (preview)

```bash
# AI-assisted project scaffolding — now available
azd init
# Select: "Set up with GitHub Copilot (Preview)"
# Copilot scaffolds project structure based on your description
# Includes MCP server tool consent upfront
```

### Container App Jobs — first-class azd support (March 2026)

```bash
# azure.yaml now supports ACA Jobs directly (no workaround needed)
# This is how ipai-build-agent should be declared:
```

```yaml
# azure.yaml — ACA Job example for ipai-build-agent
name: ipai-platform
services:
  ipai-build-agent:
    type: container-app-job
    path: ./agents/build-agent
    docker:
      dockerfile: Dockerfile
    hooks:
      preup:
        shell: sh
        run: az acr login -n acripaiodoo
```

---

## ACA + Foundry + MAF Observability (OpenTelemetry)

Source: Azure-Samples/python-agentframework-demos
Blog: https://techcommunity.microsoft.com/blog/appsonazureblog/agentic-applications-on-azure-container-apps-with-microsoft-foundry/4467601

### Wire OpenTelemetry from ACA agent to Foundry + App Insights

```python
# In every Pulser agent container (ipai-release-manager, ipai-*-bot)
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource
from agent_framework.observability import setup_observability

# SERVICE_NAME comes from ACA_SERVICE_NAME env var (set in ACA container spec)
SERVICE_NAME = os.getenv("ACA_SERVICE_NAME", "ipai-release-manager")

configure_azure_monitor(
    resource=Resource.create({"service.name": SERVICE_NAME}),
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
    # Connection string from: az monitor app-insights component show -a appi-ipai-dev
)

# Enable MAF gen_ai and tool spans
setup_observability(enable_sensitive_data=False)  # False = don't log message content
```

### ACA container spec — environment variables for observability

```bicep
// infra/azure/aca/ipai-release-manager.bicep
env: [
  {
    name: 'ACA_SERVICE_NAME'
    value: 'ipai-release-manager'
  }
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    secretRef: 'appi-connection-string'
  }
]
secrets: [
  {
    name: 'appi-connection-string'
    keyVaultUrl: 'https://kv-ipai-dev-sea.vault.azure.net/secrets/appi-ipai-dev-connection-string'
    identity: '/subscriptions/.../userAssignedIdentities/id-ipai-dev'
  }
]
```

### What Foundry observability shows per agent run

After wiring OpenTelemetry:
- Transaction search: end-to-end traces (agent invocation → tool calls → responses)
- Live Metrics: real-time request rates + performance
- Performance: operation durations, tool call latency
- Agent threads: visible in Foundry portal (ipai-copilot project → Agents)
- Telemetry lag: 2-5 minutes to appear in portal

### ACA Content Factory lab (March 2026)

```
# Reference implementation: LangGraph + MAF + GitHub Copilot CLI on ACA
# URL: azure-container-apps content agent factory lab (Simon & Jan)
# Pattern: bring any agent framework to ACA + Foundry regardless of framework
# Relevant for IPAI: MAF (already using) → wire same OTel pattern
```

---

## Azure GitHub Org — Key Projects to Monitor

Source: https://github.com/orgs/Azure/projects (91 open)

### Relevant active projects (updated within 72h)

| Project | Why monitor |
|---|---|
| **Bicep** (#115) | Bicep IaC templates for ACA, PG Flex, AFD — IPAI uses Bicep |
| **AVM - Module Issues** (#566) | Azure Verified Modules — use AVM Bicep modules in infra/ |
| **AI Landing Zones Roadmap** (#899) | AI-specific ALZ patterns for IPAI's Azure foundation |
| **Cloud Native Security & Registries** (#773) | ACR (acripaiodoo) security roadmap |
| **AKS MCP Server Roadmap** (#851) | MCP server for K8s — pattern for ACA equivalent |
| **Azure SDK for Key Vault** (#150) | KV SDK updates (kv-ipai-dev-sea) |
| **Durable Task Scheduler Roadmap** (#818) | Durable task patterns for long-running Pulser agents |

### Azure MCP Server — canonical location

The "Azure MCP Server (OLD)" project (#812) in the Azure org notes:
**"Work has moved to https://github.com/orgs/microsoft/projects/1976"**

This is the official Microsoft Azure MCP Server (separate from ADO MCP server).
Monitor for: Azure resource management tools that Pulser agents can use directly.
-e 

---
## Part 5: Odoo Docs Enhancement
---
name: odoo-docs-enhance
description: Fetch and annotate Odoo 18 developer documentation with IPAI-specific context — OCA-first alternatives, Azure ACA deployment notes, IPAI module conventions, and Odoo 18 CE breaking changes. Use before ingesting docs into the product-help RAG index. Triggers on "odoo docs", "annotate howto", or "enhance documentation".
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(curl *) Read Write
---

# Odoo docs enhancer

You are annotating official Odoo 18 developer documentation for IPAI's codebase context.
The output is an enhanced `.md` file ready for ingestion into the `product-help-index` RAG index.

## IPAI overlays to apply to every Odoo doc

### 1. Odoo version pin
Add at the top of every enhanced doc:
```
> IPAI context: Odoo **18 CE** (not EE, not 19). ACA deployment.
> View XML: use `<list>` tag, never `<tree>`. Use `view_mode="list,form"`.
```

### 2. OCA-first annotation
For every topic that has an OCA module equivalent, add:
```
> OCA-first: Before implementing custom code, check [oca/<repo>] for a maintained module.
> IPAI rule: configure → OCA → minimal custom `ipai_*` bridge module.
```

### 3. Azure ACA deployment notes
For topics involving server config, workers, or infrastructure:
```
> Azure ACA: IPAI runs ipai-odoo-dev-web / cron / worker on Container Apps (rg-ipai-dev-odoo-runtime).
> PG Flex host: pg-ipai-odoo.postgres.database.azure.com (rg-ipai-dev-odoo-data, SEA).
> Secrets: Azure Key Vault via DefaultAzureCredential — never in environment variables or git.
```

### 4. Breaking changes — Odoo 18 CE
Add a warning block for any API that changed between 16/17 and 18:
```
> Odoo 18 CE breaking change: [specific change]
> Migration: [what to do instead]
```

Known Odoo 18 CE breaking changes to annotate:
- `_cr`, `_context`, `_uid` deprecated on models — use `self.env.cr`, `self.env.context`, `self.env.uid`
- `osv.osv` removed — use `models.Model`
- `<tree>` view tag deprecated — use `<list>`
- `type="tree"` in `ir.actions.act_window` deprecated — use `type="list"`
- `fields.Datetime.now()` returns aware datetime — ensure comparisons use aware datetimes
- HTTP controllers: `@http.route` signature changed for JSON endpoints

### 5. IPAI module naming
For any howto covering module creation:
```
> IPAI convention: custom modules use `ipai_` prefix. OCA modules use their upstream name unchanged.
> Module placement: odoo/custom/ipai_<name>/ for IPAI bridges, odoo/OCA/<repo>/ for OCA.
> Never modify OCA module source — create a thin `ipai_*` bridge that inherits.
```

### 6. Security / RLS alignment
For any howto covering access rights or security:
```
> IPAI security: all custom models must have ir.model.access.csv entries.
> Finance models: restrict to canonical pulser_* role groups (see pulser-finance-rbac skill).
> No ir.rule bypass for app clients — service role exceptions only.
```

## Operations

### Enhance a single howto page (`/pulser-odoo:odoo-docs-enhance $0`)
Argument: URL or local file path

1. Fetch the page content (use `curl -s $0` or read from file)
2. Strip HTML nav / sidebar — extract only the main content body
3. Convert to clean markdown
4. Apply IPAI overlays (sections 1–6 above) at relevant locations
5. Add a metadata header:
   ```
   ---
   source: $0
   version: odoo-18-ce
   enhanced: $(date -u +%Y-%m-%dT%H:%M:%SZ)
   index_target: product-help-index
   ipai_reviewed: false
   ---
   ```
6. Save to `docs/odoo-18-enhanced/<slug>.md`
7. Flag any sections that need manual IPAI review with `> ⚠️ REVIEW NEEDED:`

### Enhance all howtos (`/pulser-odoo:odoo-docs-enhance all`)
Run against the full howtos index:
- `web_services` — XML-RPC / JSON-RPC API
- `javascript_view` — Custom view types
- `website_themes` — Website Builder themes
- `define_module_data` — Demo and seed data
- `company` — Multi-company
- `translations` — i18n

Produce one enhanced file per page, then generate an index at
`docs/odoo-18-enhanced/INDEX.md` listing all pages, their status, and RAG ingestion readiness.

### Check ingestion readiness (`/pulser-odoo:odoo-docs-enhance check $0`)
For file `$0`, verify:
- [ ] Metadata header present
- [ ] IPAI version pin present
- [ ] No raw HTML remaining
- [ ] All `⚠️ REVIEW NEEDED` items have been addressed or marked as accepted
- [ ] File is under 100KB (Azure AI Search chunk limit)
Output: READY / NEEDS REVIEW with specific items
