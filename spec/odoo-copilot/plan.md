# Implementation Plan — Odoo Copilot

> Runtime: Azure AI Foundry Agent Service (`data-intel-ph`)
> Module: `ipai_odoo_copilot`
> SSOT: `ssot/agents/odoo_copilot_precursor.yaml`, `ssot/agents/diva_copilot.yaml`
> Status: Draft

---

## Go-Live Foundry Tool Selection

### First-wave tools (enable now)

The Foundry tool catalog exposes 35+ connectors. Go-live uses a controlled subset of 9 tools:

| Tool | Auth | Purpose |
|------|------|---------|
| Foundry MCP Server (preview) | Managed identity | Agent runtime orchestration |
| GitHub | OAuth | Code/repo context, PR inspection |
| Vercel | OAuth | Deployment status, preview URLs |
| Azure DevOps MCP Server (preview) | OAuth | Boards, pipelines, work items |
| Azure Databricks Genie | Managed identity | Semantic analytics Q&A |
| Azure Database for PostgreSQL | Managed identity | Operational data access |
| Supabase | OAuth / key | App backend context |
| Azure Managed Grafana | Managed identity | Metrics, logs, dashboards |
| Azure MCP Server | Managed identity | Azure platform context |

### Explicitly deferred (not first-wave dependencies)

These tools are **not** part of go-live. They expand blast radius, auth complexity, and governance surface:

| Category | Tools |
|----------|-------|
| **Work IQ suite** | Mail, Calendar, Teams, SharePoint, Word, OneDrive, Copilot |
| **Admin** | Microsoft 365 Admin Center |
| **Data platforms** | Dataverse |
| **Third-party automation** | Pipedream, ClickUp, Atlassian |
| **Industry connectors** | Infobip, Morningstar, Marketnode, MiHCM |

**Rule**: No deferred tool is enabled until a concrete workflow justifies it and first-wave stability is proven.

### Enable next (after first-wave)

| Tool | Trigger |
|------|---------|
| Azure Managed Redis | Agent memory / semantic cache requirement |
| Azure Language in Foundry Tools | NLP pipeline requirement |
| Selected Work IQ tools | Specific workflow need with defined scope |

---

## Tool Profile: `odoo_copilot_internal_beta`

| Property | Value |
|----------|-------|
| Enabled tools | Foundry MCP Server, GitHub, Vercel, Azure DevOps MCP Server, Azure Managed Grafana, Azure MCP Server |
| Action mode | Fail-closed (read-only default, write requires explicit allowlist) |
| Tenant scope | Trusted internal users only |
| Auth | Odoo user session + Entra OAuth for tool access |

### What this profile provides

- Code/repo context (GitHub)
- Deployment context (Vercel)
- DevOps context — boards, pipelines, work items (Azure DevOps MCP)
- Runtime/ops context — Azure resources, health (Azure MCP Server)
- Observability — metrics, logs, dashboards (Grafana)
- Foundry-native evaluation and agent visibility (Foundry MCP Server)

### What this profile does NOT provide

- Microsoft 365 action surfaces (mail, calendar, teams)
- Broad remote MCP sprawl
- Unscoped write actions
- Third-party SaaS integrations

---

## Auth Policy

| Auth mode | Tools | When |
|-----------|-------|------|
| Managed identity | Foundry MCP, Databricks Genie, PostgreSQL, Grafana, Azure MCP | Azure-native services |
| OAuth | GitHub, Vercel, Azure DevOps MCP, Supabase | Human-scoped / dev tools |
| Key-based | Avoid | Only if no cleaner identity option exists |

Enforce per-profile, not by accepting connector defaults.

---

## Implementation Phases

### Phase A: Core Precursor (from `odoo_copilot_precursor.yaml`)

- Systray chat entry
- Foundry provider bridge
- Read-only tools
- Structured responses
- Audit trail
- Specialist handoff stub

### Phase B: TaxPulse Specialist

- Tax exception review
- Rule source citation
- Audit note generation
- Human escalation
- Fail-closed on unresolved ATC

### Phase C: Foundry Tool Integration

- Wire first-wave tools per `diva_copilot.yaml` profile
- Validate fail-closed behavior
- Audit logging for all tool invocations
- Monitor and stabilize before enabling next-wave tools

---

## Verification

| Criterion | Test |
|-----------|------|
| Only first-wave tools enabled | Tool audit shows exactly 6 tools for `odoo_copilot_internal_beta` |
| Fail-closed on missing context | Missing tool context returns advisory, not error |
| No deferred tools active | Work IQ, M365 Admin, Dataverse not accessible |
| Auth policy enforced | Managed identity for Azure-native, OAuth for dev tools |
| Audit trail active | Every tool invocation logged with user, tool, action, timestamp |
