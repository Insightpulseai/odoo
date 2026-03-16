# MCP Stack – Odoo + n8n + Mattermost + Superset + DO Agents

This document describes the **multi-server MCP architecture** used in the `fin-workspace` / `odoobo-migration-lab` ecosystem:

- Multiple **Odoo** instances (lab + ERP/SSC)
- **DigitalOcean Agents Platform** (Infra Orchestrator, Kubernetes Genius, etc.)
- **n8n** for automations
- **Mattermost** for ops/chat
- **Superset** for analytics
- Local **SQLite** for dev and **Supabase** for prod MCP data

The goal is to give MCP, Claude/Codex CLI, and agents a **consistent routing and data model** across dev and prod.

---

## 1. Odoo Instances & Purpose

We run at least two Odoo instances:

- **`odoo_lab`** (odoobo-migration-lab)
  - Sandbox for OCA modules, migration scripts, experiments.
  - Connected to dev automations (n8n-dev), dev dashboards, and dev MCP.
- **`odoo_erp`** (production ERP/SSC)
  - Primary ERP for TBWA/InsightPulse finance + SSC workflows.
  - Connected to prod automations (n8n-prod), Mattermost channels, Superset prod dashboards, and prod MCP.

> **Policy:**
> - Lab is for **experiments and migrations only**, never the source of truth for financials.
> - ERP is **authoritative** for finance, SSC, and any production workflows.

---

## 2. MCP Coordinator & Routing Strategy

The MCP coordinator is the **front door** for all agent calls into Odoo and related services.

### 2.1 Routing Modes

- **Default: Context-Based Intelligent Routing**
  - Route based on:
    - Company / workspace (e.g. TBWA, W9, SSC)
    - Module (e.g. accounting, projects, HR)
    - Operation type (e.g. "migration", "reconciliation", "SSC ticket")
  - Example:
    - `finance-ssc` → `odoo_erp`
    - `migration` / `OCA refactor` → `odoo_lab`

- **Explicit Override**
  - Agents can specify a target explicitly in tool args:
    - `target: odoo_erp`
    - `target: odoo_lab`
  - Used for scripts, batch jobs, migrations, and debugging.

- **Aggregation Mode**
  - For cross-instance reporting:
    - Coordinator queries **both** `odoo_erp` and `odoo_lab` (or other instances).
    - Prefer to push the merged data into a warehouse / Supabase → **Superset**, rather than aggregating live for every query.
  - Typical use: migration validation, global reporting, audits.

- **Active–Passive Failover**
  - `odoo_erp` is always the primary.
  - `odoo_lab` can be used as **emergency read-only fallback** for certain non-financial workflows if needed.
  - We never route from `odoo_lab` → `odoo_erp` as a failover path.

---

## 3. Core Components

### 3.1 Odoo

- **Roles:**
  - ERP & SSC workflows (production).
  - OCA experimentation and migration lab.
- **Access:**
  - MCP tools for Odoo CRUD, reporting, and metadata inspection.
  - n8n for scheduled jobs and integrations (AP, AR, HR, etc.).

### 3.2 n8n (Automation Bus)

- **Mode:** self-hosted (dev + prod)
- **Responsibilities:**
  - Orchestrate long-running jobs and external integrations.
  - Webhooks for MCP → n8n → external system workflows.
  - Nightly/cron ETL into Supabase / warehouse.
- **Usage from MCP:**
  - MCP tools call n8n via HTTP with explicit workflow IDs or tags.
  - Dev calls go to `n8n-dev`; prod calls go to `n8n-prod`.

### 3.3 Mattermost (Ops Console)

- **Mode:** self-hosted
- **Responsibilities:**
  - Main operator console for:
    - Agent runs
    - MCP decisions
    - n8n workflow statuses
    - Infra alerts / notifications
- **Usage from MCP & Agents:**
  - Agents post summaries + links (Odoo records, Superset dashboards).
  - n8n posts success/failure and approval requests.
  - Humans trigger certain workflows via slash commands.

### 3.4 Superset (Analytics UX)

- **Mode:** self-hosted
- **Responsibilities:**
  - Dashboards for:
    - ERP and SSC metrics
    - MCP usage, latency, token costs
    - n8n job status and throughput
    - Infra & agent performance
  - Read-only UX for stakeholders.
- **Usage from MCP & Agents:**
  - Agents link to Superset charts instead of generating ad-hoc SQL in responses.
  - Queries use **Supabase / warehouse views** as the canonical source, not live Odoo where possible.

### 3.5 DigitalOcean Agents (DO Agent Platform)

Key agents include:

- **Infra Orchestrator**
  - Default infra + platform front door for fin-workspace.
  - Routes high-level requests across Odoo, DOKS, n8n, Mattermost, Superset, etc.
- **Kubernetes Genius**
  - K8s/DOKS specialist for cluster design, manifests, and debugging.
  - Called conceptually by Infra Orchestrator for deep K8s problems.
- Other workspace agents (finance-ssc, odoo-dev, devops-engineer, bi-architect, etc.) can sit on top of MCP.

---

## 4. Data Strategy – SQLite vs Supabase

We separate **dev** and **prod** storage:

### 4.1 Dev (Local / SQLite)

- **RAG embeddings**
  - Stored in **SQLite**.
  - Used for experimentation, small corpora, and local agents.
  - Never auto-synced to prod.

- **Skills metadata**
  - Source-of-truth is **Git** (YAML/JSON definitions).
  - Loaded into local SQLite for developer convenience.

- **Conversation history**
  - Local-only, kept in SQLite or local disk.
  - For debugging and iteration in dev.

### 4.2 Prod (Supabase)

- **RAG embeddings**
  - Stored in **Supabase** with environment-specific corpora.
  - Populated via **explicit CI pipelines** or n8n-powered ETL.
  - No blind promotion from dev → prod.

- **Skills metadata**
  - Git is still the source-of-truth.
  - Only skills marked `stable` / `approved` are loaded into Supabase prod.
  - MCP only exposes approved skills to production agents.

- **Telemetry & metrics**
  - Only **aggregated, anonymized metrics** (e.g. latency, volume, error rates) travel to Supabase for dashboarding in Superset.
  - No raw conversation logs in Supabase by default.

---

## 5. Skill Promotion & CI/CD

### 5.1 Skill Lifecycle

1. **Draft**
   - Edited in Git + tested locally with SQLite and local MCP.
2. **Candidate**
   - Evaluated using structured tests/evals.
3. **Approved**
   - Marked via metadata (`status: approved`).
   - Auto-synced to Supabase prod via CI/n8n.
4. **Deprecated**
   - Kept for backward compatibility but hidden from most agents.

### 5.2 Auto-Sync Critical Skills

- Certain skills are eligible for automated promotion:
  - `finance-ssc`
  - `odoo-developer`
  - `devops-engineer`
  - `kubernetes-genius`
- Promotion pipeline:
  - Git push → CI runs tests/evals → if pass:
    - Update Supabase skill metadata.
    - Trigger n8n workflow for rollout.
    - Send status/alerts to Mattermost.
    - Optionally log promotion in Superset via a "promotions" table.

---

## 6. Developer UX & VS Code Workflow

We standardize on **VS Code + Claude/Codex CLI + MCP**:

### 6.1 Workspaces

- `mcp-dev`
  - Connects to local MCP servers and SQLite.
  - Uses **dev URLs** for n8n, Mattermost, Superset.
- `mcp-prod`
  - Connects to remote MCP (Supabase-backed).
  - Uses **prod URLs**.

### 6.2 Dual MCP Connection (Conceptually)

- Each workspace may talk to both local and remote MCP:
  - Local: for fast prototyping and debugging.
  - Remote: for production-aware operations.
- Routing based on:
  - Tool configuration
  - Environment variables
  - Workspace-specific settings.

### 6.3 Feedback Loops

- Devs mostly live in **VS Code**:
  - Run tasks via Claude/Codex CLI.
  - Observe automation runs in **Mattermost**.
  - Validate effects through **Superset** (metrics) and **Odoo** (records).

---

## 7. Operational Workflows

Examples of the full stack in action:

1. **New SSC automation**
   - Design skill locally → test against `odoo_lab` via dev MCP.
   - Wire automation in `n8n-dev`, validate outputs.
   - Promote skill + workflow via CI.
   - Use `n8n-prod` + `odoo_erp` for production.
   - Monitor in Superset dashboards; alerts in Mattermost.

2. **Migration testing**
   - MCP coordinator uses **Aggregation Mode** to compare `odoo_lab` vs `odoo_erp`.
   - n8n pulls data snapshots into Supabase.
   - Superset provides diff/validation dashboards.

3. **Kubernetes incident**
   - Dev pings Infra Orchestrator or Kubernetes Genius.
   - Agent suggests `kubectl` commands, manifests, and rollback steps.
   - Results posted in Mattermost; K8s metrics can be visualized via Superset.

---

## 8. Naming & Conventions

- **Instances**
  - `odoo_lab` – migration lab
  - `odoo_erp` – ERP/SSC
- **n8n**
  - `n8n-dev`, `n8n-prod`
- **MCP Databases**
  - Dev: SQLite
  - Prod: Supabase (`mcp` schema)
- **Agents**
  - Infra Orchestrator – default infra front door
  - Kubernetes Genius – K8s/DOKS specialist
  - Finance SSC Expert – SSC/finance workflows
  - Odoo Developer – Odoo/OCA technical work

---

This README is the **single source of truth** for how MCP, Odoo, n8n, Mattermost, and Superset are intended to work together in the `fin-workspace` / `odoobo-migration-lab` environment.
