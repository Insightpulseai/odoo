# Pulser — Foundry Connections, Tools & Capability Matrix

> `docs/runbooks/foundry-connections-and-tools.md`
> Rev: 2026-04-14 | Status: CANONICAL
> Doctrine anchors: `CLAUDE.md` §"Cross-Repo Invariants",
> `feedback_foundry_reuse_doctrine`, `feedback_engineering_execution_doctrine`.
> Complements: `docs/runbooks/claude-code-foundry.md`,
> `ssot/foundry/runtime-contract.yaml`.

---

## 0. Resource constants

### 0.1 Single-Foundry posture (as of 2026-04-15)

IPAI runs ONE canonical Foundry resource. User directive: no Claude on Foundry;
stick to gpt-4.1 + fine-tune to create a competitive custom model.

| Foundry resource | Subscription | Lane | Status |
|---|---|---|---|
| `ipai-copilot-resource` | Microsoft Azure Sponsorship (`eba824fb-...`) | All Foundry workloads (gpt-4.1 + future fine-tuned variants) | **CANONICAL** |
| `ipai-copilot-payg` | Azure subscription 1 (`eba824fb-...`) | — | **RETIRED — delete in next cleanup** |

`ipai-copilot-payg` was a short-lived experiment (provisioned 2026-04-14,
retired 2026-04-15) to bypass the Sponsored-sub Anthropic block.
Discovery: Enterprise/MCA-E quota gate makes Anthropic-on-Foundry
infeasible on either subscription. Decision: standardize on gpt-4.1,
fine-tune for Pulser-specific capability. Claude Code continues via
Anthropic direct (not Foundry).

Project name `ipai-copilot` lives on the Sponsorship resource.
See `ssot/foundry/runtime-contract.yaml §activation.fine_tuning_roadmap`
for the 6-phase fine-tuning path.

### 0.2 Backing resource inventory

Cross-region note: Foundry + Document Intelligence are in **East US 2**.
All other IPAI resources are in **SEA**. Acceptable for dev; reduce
latency at GA if operationally visible.

| Resource | Name | Type | Region | RG | Subscription |
|---|---|---|---|---|---|
| Foundry account (OpenAI lane) | `ipai-copilot-resource` | Foundry | East US 2 | `rg-data-intel-ph` | Sponsorship |
| Foundry project (OpenAI lane) | `ipai-copilot` | Foundry project | East US 2 | `rg-data-intel-ph` | Sponsorship |
| Foundry account (Anthropic lane) | `ipai-copilot-payg` | Foundry | East US 2 | `rg-data-intel-ph` | PAYG |
| Foundry project (Anthropic lane) | `ipai-copilot` | Foundry project | East US 2 | `rg-data-intel-ph` | PAYG |
| App Insights (agent) | `appi-ipai-dev-agent-sea` | App Insights | SEA | `rg-ipai-dev-mon-sea` | Sponsorship |
| App Insights (runtime) | `appi-ipai-dev-runtime-sea` | App Insights | SEA | `rg-ipai-dev-mon-sea` | Sponsorship |
| AI Search | `srch-ipai-dev-sea` | Search service | SEA | `rg-ipai-dev-ai-sea` | Sponsorship |
| Storage (agent) | `stipaidevagent` | Storage account | SEA | `rg-ipai-dev-data-sea` | Sponsorship |
| Storage (lake) | `stlkipaidev` | Storage account | SEA | `rg-ipai-dev-data-sea` | Sponsorship |
| Storage (dev) | `stdevipai` | Storage account | SEA | `rg-ipai-dev-data-sea` | Sponsorship |
| PostgreSQL (canonical) | `pg-ipai-odoo` | PG Flex | SEA | `rg-ipai-dev-odoo-data` | **PAYG** |
| Document Intelligence | `docai-ipai-dev` | Cognitive Services | East US 2 | `rg-data-intel-ph` | Sponsorship |
| Key Vault | `kv-ipai-dev-sea` | Key Vault | SEA | `rg-ipai-dev-security-sea` | Sponsorship |
| Container Registry | `acripaiodoo` | ACR | SEA | `rg-ipai-shared` | Sponsorship |
| ACA Environment | `acae-ipai-dev-sea` | ACA Env | SEA | `rg-ipai-dev-odoo-sea` | Sponsorship |
| Databricks | `dbw-ipai-dev` | Databricks | SEA | `rg-ipai-dev-ai-sea` | Sponsorship |
| Managed Identity (agent) | `id-ipai-dev-agent` | MI | SEA | `rg-ipai-dev-security-sea` | Sponsorship |
| Managed Identity (runtime) | `id-ipai-dev-runtime` | MI | SEA | `rg-ipai-dev-security-sea` | Sponsorship |
| Log Analytics (agent) | `log-ipai-dev-agent-sea` | Log Analytics | SEA | `rg-ipai-dev-mon-sea` | Sponsorship |
| Service Bus | `sb-ipai-dev-sea` | Service Bus | SEA | `rg-ipai-dev-odoo-sea` | Sponsorship |
| Purview | `pv-ipai-dev-sea` | Purview | SEA | `rg-ipai-dev-security-sea` | Sponsorship |
| Private Endpoint (Search) | `pe-ipai-dev-search` | Private Endpoint | SEA | `rg-ipai-dev-net-sea` | Sponsorship |

**Cross-subscription note:** `pg-ipai-odoo` is the only canonical resource on PAYG
apart from the new Foundry. Foundry ↔ Postgres connections will cross subscription
boundaries; this is supported but requires identity and networking alignment.

---

## 1. Connections — ordered activation sequence

Connect in this order on each Foundry project. Each unlocks a Pulser
capability tier. All authentication uses **Entra ID** unless the specific
connection type forbids it (e.g., App Insights requires ApiKey per Foundry
policy — key lives in Key Vault, not in git).

### Step 1 — Application Insights
**Resource:** `appi-ipai-dev-agent-sea` (SEA, `rg-ipai-dev-mon-sea`)

Unlocks: full agent trace pipeline — every tool call, token count, latency,
error logged. Mandatory before any agent goes to prod. No observability = no
production.

### Step 2 — Azure AI Search
**Resource:** `srch-ipai-dev-sea` (SEA, `rg-ipai-dev-ai-sea`)
**Private endpoint:** `pe-ipai-dev-search` (already provisioned)

Unlocks: grounded retrieval. Agent can cite from indexed Odoo docs, BIR
rulings, PrismaLab corpus, internal runbooks.

Index targets (provision in order):
1. `pulser-odoo-docs` — Odoo 18 CE + OCA module documentation
2. `pulser-bir-rulings` — BIR Revenue Regulations, RMCs, ATCs
3. `pulser-prismalab` — PrismaLab SR/MA corpus
4. `pulser-runbooks` — `automations/runbooks/` from IPAI monorepo

### Step 3 — Storage
**Resources (in order of priority):**
1. `stipaidevagent` — agent file I/O, output artifacts, BIR PDFs/DATs
2. `stlkipaidev` — lakehouse Bronze layer (ADLS Gen2)
3. `stdevipai` — general dev storage

Unlocks: file creation and retrieval. Agent can produce DOCX, PDF, XLSX,
DAT, PNG artifacts and hand download links back.

---

## 2. Tools — per-agent enable matrix

Enable tools **per agent**, not globally. Wrong tool scope = security
boundary violation.

| Foundry Tool | IPAI Target | Enable for | Status |
|---|---|---|---|
| Azure MCP Server | Cross-sub (Sponsorship + PAYG) | Ops/Infra agent | Adopt |
| Azure DevOps MCP Server | ADO org `insightpulseai` | Ops/Infra agent | Adopt |
| Azure Database for PostgreSQL | `pg-ipai-odoo` (PAYG) | Finance agent | Adopt |
| Azure AI Search | `srch-ipai-dev-sea` | Finance, Research agents | Adopt |
| Foundry MCP Server | Both Foundry resources | All agents | Adopt |
| GitHub MCP | `InsightPulseAI/odoo` | Ops agent, Code agent | Conditional (repo context only) |
| Bing Search (web) | Foundry built-in | Research agent | Adopt |
| Code Interpreter | Foundry built-in | Finance agent (DAT/PDF gen), Research | **Adopt — built-in, replaces custom rendering services** |
| Browser Automation | Foundry built-in | Finance agent (eBIRForms/eFPS submission) | **Adopt — built-in, replaces Playwright sidecar** |
| File Search | Foundry built-in | Finance agent (form templates), Research | Adopt |
| Document Intelligence | `docai-ipai-dev` | Finance agent (receipt/invoice OCR) | Adopt |
| Azure Databricks Genie | `dbw-ipai-dev` | Analytics agent | Defer — until Gold layer production-ready |
| Fabric Data Agent | `fcipaidev` | Analytics agent | Defer — until Fabric mirror live (trial ~2026-05-20) |
| Azure Managed Redis | — | All agents (semantic cache) | Defer — adopt when latency visible |
| Azure Cosmos DB | — | All agents (durable state) | Defer — not yet required |
| Work IQ (Mail/Calendar/Teams/SharePoint/OneDrive/User/Planner/Word/Copilot) | M365 tenant | — | **Defer — licensing + tenant prerequisites NOT YET REAL (GA date alone is not the trigger)** |
| Microsoft 365 Admin Center | M365 tenant | — | Defer — licensing prerequisite |
| Azure Language in Foundry | Cognitive Services | Compliance agent | Defer — not first-wave |
| Dataverse | Power Platform | — | **SKIP — permanent; collides with Odoo SOR doctrine** |
| SharePoint (built-in) | — | — | Skip as core dependency; revisit if tenant ops need |

### 2.1 Built-in simplification (confirmed 2026-04-14)

Two Foundry built-ins eliminate entire custom-service workstreams:

- **Code Interpreter** → Python sandbox for BIR DAT file generation,
  PDF rendering (WeasyPrint/reportlab), XLSX→DAT conversion. Replaces the
  planned "rendering ACA Job."
- **Browser Automation** → eBIRForms / eFPS portal submission. Replaces
  the planned "Playwright ACA sidecar."

Net effect: BIR filing agent Phase 1 + Phase 2 collapse into a single
deployment with zero custom infrastructure beyond what Foundry provides.

### 2.2 Redis vs Cosmos decision rule

```
Redis  = fast ephemeral memory, semantic cache, low-latency vector lookup
         -> adopt when agent response latency becomes operationally visible
         -> NOT for durable application state

Cosmos = durable session / agent / application state
         -> adopt when a specific agent requires durable state that
            cannot live in `pg-ipai-odoo` (Odoo's canonical DB)
         -> NOT yet — Postgres `ops` schema on pg-ipai-odoo is sufficient
```

Current: neither Redis nor Cosmos provisioned. State lives in Postgres
(`ops` schema on `pg-ipai-odoo`). Both are DEFER, not SKIP.

---

## 3. Per-agent binding plan

### Agent 1 — Pulser Ops / Infra
```yaml
agent: pulser-ops
purpose: Azure inspection, pipeline actions, model/agent deploy and eval
tools:
  - azure-mcp-server          # resource graph, ARM, cost queries
  - azure-devops-mcp-server   # ADO pipelines, work items, PRs
  - foundry-mcp-server        # model catalog, agent eval, deployment
  - github-mcp                # IPAI monorepo (conditional)
connections:
  - appi-ipai-dev-agent-sea   # traces
identity: id-ipai-dev-agent (UserAssignedManagedIdentity)
```

### Agent 2 — Pulser Finance / Reconciliation
```yaml
agent: pulser-finance
purpose: Odoo ledger access, BIR compliance, AR collections, reconciliation
tools:
  - azure-database-postgresql  # pg-ipai-odoo (PAYG — cross-sub)
  - azure-ai-search            # srch-ipai-dev-sea (BIR rulings index)
  - code-interpreter           # DAT gen, PDF render, data transform
  - browser-automation         # eBIRForms/eFPS submission
  - document-intelligence      # docai-ipai-dev (receipt OCR)
  - file-search                # form templates on stipaidevagent
  - foundry-mcp-server         # eval access
connections:
  - appi-ipai-dev-agent-sea
  - stipaidevagent             # BIR PDF/DAT output storage
identity: id-ipai-dev-agent
skills:
  - agents/skills/bir_tax_compliance/SKILL.md
  - agents/skills/finance_recon/SKILL.md
  - agents/skills/ar_collections/SKILL.md
  - agents/skills/expense_liquidation/SKILL.md
```

### Agent 3 — Pulser Research / Strategy
```yaml
agent: pulser-research
purpose: Cited retrieval, internal corpus grounding, docs/repo strategy support
tools:
  - azure-ai-search            # srch-ipai-dev-sea (all indexes)
  - bing-search                # web grounding (built-in Foundry)
  - file-search                # uploaded research artifacts
  - github-mcp                 # repo context when needed
connections:
  - appi-ipai-dev-agent-sea
identity: id-ipai-dev-agent
skills:
  - agents/skills/prismalab_research/SKILL.md
  - agents/skills/bir_rulings_lookup/SKILL.md
```

### 3.1 Binding policy
- Planner/router agent: NO write-capable MCPs directly. Delegates to specialists.
- Tool additions require PR updating this section + eval run showing no regression.
- Read/write posture is declared per tool in the agent manifest
  (e.g., `postgresql: {read_only: true}` unless policy explicitly allows writes).

---

## 4. Pulser capability parity matrix

### vs. Claude (this interface)

| Claude capability | Pulser equivalent | Implementation | Status |
|---|---|---|---|
| Web search | Bing Search via Foundry built-in | Enable on Research agent | Wire now |
| File creation (DOCX, PDF, XLSX) | Code Interpreter + `stipaidevagent` | Foundry built-in + Storage connection | Wire now |
| Code execution | Code Interpreter (Foundry built-in) | No custom ACA needed | Wire now |
| Document reading/analysis | Document Intelligence | `docai-ipai-dev` + Foundry tool | Wire now |
| Image analysis | GPT-4o vision via Foundry | `gpt-4.1` deployment (Sponsorship Foundry) | Available |
| Artifact preview (HTML/React) | `web/ops-console` render surface | Roadmap |  — |
| Cited retrieval | AI Search grounded agent | `srch-ipai-dev-sea` indexes | Wire now |
| Multi-turn memory | Postgres `ops` schema on `pg-ipai-odoo` | Schema creation required | Build |
| Tool orchestration | MAF workflow pattern | `microsoft/agent-framework` SDK | Build |

### vs. Notion 3.0 Agents

| Notion 3.0 capability | Pulser equivalent | Gap? |
|---|---|---|
| 20-min autonomous runs | MAF long-running workflow (ACA Job) | Pattern exists, not wired |
| Create/update structured records | Odoo JSON-RPC write | Doctrine-compliant path exists |
| Cross-platform context (Slack/Teams) | Work IQ tools | Deferred — licensing |
| Web context | Bing Search (Foundry built-in) | Wire now |
| Code execution (Workers) | Code Interpreter + ACA Job patterns | Wire (built-in) + build (custom) |
| Custom skills/commands | `agents/skills/<domain>/SKILL.md` | Structure exists |
| Database agents (self-updating) | Pulser Finance agent with PG MCP | Build |
| Knowledge base maintenance | AI Search re-indexing (pg_cron + indexer ACA Job) | Build |
| File I/O (CSV, doc) | Code Interpreter + `stipaidevagent` + Document Intelligence | Wire now |
| MCP integrations | Foundry MCP Server + Azure MCP | Wire now |

---

## 5. Skill → Foundry tool binding pattern

Each IPAI skill file (`agents/skills/<domain>/SKILL.md`) declares its
required Foundry tools, storage, connections, triggers, and commands.

```markdown
# SKILL: bir_tax_compliance

## Required Foundry Tools
- azure-database-postgresql   # read account.move, account.tax
- code-interpreter            # generate DAT files, render BIR PDFs
- browser-automation          # submit to eBIRForms/eFPS portal
- document-intelligence       # OCR receipts, validate uploaded forms
- azure-ai-search             # BIR rulings grounding
- file-search                 # BIR form templates

## Required Storage
- stipaidevagent              # output: BIR PDF, DAT files

## Required Connections
- appi-ipai-dev-agent-sea     # traces

## Trigger conditions
- User mentions: "2307", "2550M", "SAWT", "QAP", "SLSP", "1601-C", "BIR filing"
- Context: account.move posted, period closed, filing deadline proximity

## Slash commands
/bir-generate [form] [period]   # generate BIR artifact
/bir-status [period]            # check filing state in ops schema
/bir-preview [artifact_id]      # retrieve artifact URL from stipaidevagent
```

---

## 6. Auth pattern

Prefer **`ManagedIdentityCredential`** with explicit `client_id` in production.
`DefaultAzureCredential` is acceptable when configured with
`managed_identity_client_id` to pin the credential chain — do not leave the
chain unpinned in prod (unpredictable fallback order).

```python
from azure.identity import ManagedIdentityCredential
from agent_framework.foundry import FoundryChatClient

credential = ManagedIdentityCredential(
    client_id="<id-ipai-dev-agent client_id>"
)
client = FoundryChatClient(
    credential=credential,
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
)
```

All secrets in `kv-ipai-dev-sea`. Never in git, never as env-var literals in
committed files. See `CLAUDE.md` §Secrets Policy.

---

## 7. Agent 365 registration (deadline 2026-05-01)

Every published Pulser agent receives an Entra Agent ID:

```
Published agent -> distinct Entra service principal
                -> AgentId extension on SP
                -> Agent 365 admin catalog (IPAI tenant + TBWA tenant)
                -> reconfigure resource permissions post-publish
```

Agents to register before 2026-05-01:

1. `pulser-finance` — highest GTM value, parity with D365 Time and Expense Agent
2. `pulser-ops` — infra/devops automation surface
3. `pulser-research` — PrismaLab + BIR rulings knowledge surface

Registration artifacts: `spec/pulser-agent-365-registration/` — create this
directory with one manifest file per agent.

---

## 8. Adopt / Defer / Skip — locked decision

```
ADOPT NOW
  Connections (in order):
    1. Application Insights (appi-ipai-dev-agent-sea)
    2. Azure AI Search (srch-ipai-dev-sea)
    3. Storage (stipaidevagent, stlkipaidev, stdevipai)

  Tools (per agent, per §3):
    Azure MCP Server
    Azure DevOps MCP Server
    Azure Database for PostgreSQL (pg-ipai-odoo on PAYG)
    Azure AI Search
    Foundry MCP Server
    Code Interpreter (built-in)
    Browser Automation (built-in)
    File Search (built-in)
    Bing Search (built-in)
    Document Intelligence (docai-ipai-dev)
    GitHub MCP (conditional — repo context only)

DEFER (with triggers)
  Work IQ (all 9)            — tenant prerequisites must be REAL (not just GA date)
  Microsoft 365 Admin Center — licensing prerequisite
  Databricks Genie           — after Gold layer production-ready
  Fabric Data Agent          — after Fabric mirror live (~2026-05-20)
  Azure Language             — not first-wave, add for NLP/compliance later
  Redis                      — adopt when latency becomes operationally visible
  Cosmos DB                  — adopt when Postgres `ops` schema is insufficient

SKIP (permanent)
  Dataverse           — collides with Odoo SOR doctrine
  SharePoint built-in — not a core dependency
```

---

## 9. Next artifacts to create

```
agents/skills/bir_tax_compliance/SKILL.md     # declare tools, triggers, commands
agents/skills/finance_recon/SKILL.md
agents/skills/ar_collections/SKILL.md
agents/skills/expense_liquidation/SKILL.md
agents/system/pulser-finance.system.md        # finance agent system prompt
agents/system/pulser-ops.system.md
agents/system/pulser-research.system.md
agents/registry/skills-index.json             # add all skill entries
spec/pulser-agent-365-registration/           # Entra Agent ID manifests
  manifest-pulser-finance.json
  manifest-pulser-ops.json
  manifest-pulser-research.json

# State and triggers — Azure-native (NOT Supabase; Supabase is deprecated 2026-03-26)
ops-platform/functions/bir-filing-trigger/    # Azure Function signed webhook intake
  function.json
  index.ts
migrations/odoo/20260414_bir_filing_runs.sql  # ops.bir_filing_runs on pg-ipai-odoo
```

---

## 10. Verification (run after each connection / tool lands)

```bash
# Project context
az account set --subscription "Microsoft Azure Sponsorship"
# or the PAYG lane
az account set --subscription "Azure subscription 1"

# List deployments (authoritative — per Foundry project)
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://<foundry-host>/api/projects/ipai-copilot/deployments?api-version=2025-05-01" \
  | python3 -m json.tool

# List connections
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://<foundry-host>/api/projects/ipai-copilot/connections?api-version=2025-05-01" \
  | python3 -m json.tool
```

Connections are expected to show `authType: AAD` (Entra ID) except App Insights
which is forced to `authType: ApiKey` by Foundry policy (key is fetched from
Key Vault, never committed).

---

## 11. Related

- `docs/runbooks/claude-code-foundry.md` — Claude Code + Foundry activation
- `ssot/foundry/runtime-contract.yaml` — endpoint/auth/deployment SSOT
- `CLAUDE.md` §Deprecated — Supabase fully deprecated 2026-03-26 (Azure-native only)
- Memory: `feedback_foundry_reuse_doctrine`, `project_foundry_anthropic_sponsorship_blocker`,
  `project_m365_e7_agent365`, `project_supabase_fully_deprecated`,
  `feedback_foundry_tools_adoption`, `feedback_engineering_execution_doctrine`

---

*Rev 2026-04-14. Validated against live resource state on Sponsorship +
PAYG subscriptions. Supabase references stripped per
`project_supabase_fully_deprecated`.*
