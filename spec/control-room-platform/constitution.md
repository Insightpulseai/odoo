# Constitution — Control Room Platform

> Non-negotiable rules and constraints for the Control Room Platform.

---

## 1. Platform Boundaries (Never Violate)

Each platform owns exactly one concern. No platform duplicates another's role.

| Platform | Role | Boundary |
|----------|------|----------|
| **Plane** | Workspace, execution, knowledge | Initiatives, epics, work items, wiki, approvals, inbox |
| **Databricks Apps** | Operational analytics | KPI dashboards, AI summaries, risk monitoring, forecasts |
| **Azure Foundry** | Agent runtime | Copilots, tool orchestration, multi-step agents |
| **Odoo** | System of record | Transactional truth, ERP operations |
| **Supabase** | Control plane | Integration state, auth, Edge Functions, Vault |
| **GitHub** | Engineering platform | Source code, CI/CD, spec-driven development |

**Rule**: If a capability maps to a platform's role, it MUST live there. Never build analytics in Plane, never build project management in Databricks.

---

## 2. Planning Hierarchy (Three Layers)

```
Strategy:     Figma roadmap (executives, quarterly)
Execution:    Plane workspace (teams, weekly)
Engineering:  Spec Kit bundles (engineers, per-feature)
```

Each layer flows down:
- Figma roadmap item → Plane initiative/epic
- Plane epic → Spec bundle
- Spec bundle → GitHub implementation

**Rule**: No engineering work starts without a Plane epic. No Plane epic exists without a roadmap alignment.

---

## 3. Source of Truth per Layer

| Data | SSOT | Not SSOT |
|------|------|----------|
| Product roadmap | Figma board | Slides, docs, spreadsheets |
| Delivery status | Plane workspace | GitHub issues, Slack threads |
| Engineering contract | Spec bundle | PRDs in Google Docs, Notion |
| Runtime metrics | Databricks Apps | Manual reports, spreadsheets |
| Agent definitions | GitHub (agents repo) | Foundry console alone |

---

## 4. Integration Contracts

### Plane ↔ GitHub
- Plane Silo service handles GitHub integration
- Work items link to GitHub PRs/issues
- Status syncs bidirectionally

### Plane ↔ Agents (via MCP)
- Agents create/update work items via Plane MCP server
- Agents summarize projects and generate updates
- No agent writes directly to Plane DB — always via API/MCP

### Databricks Apps ↔ Lakehouse
- Apps read from Gold/Platinum layers only
- No raw data access from apps
- Unity Catalog governs all access

### Foundry ↔ Tools
- Agents access external systems via defined tools only
- No direct database access from agents
- Tool schemas are versioned in the agents repo

---

## 5. Non-Negotiable Rules

1. **No shadow planning**: All planning artifacts converge into Plane. No parallel Trello/Notion/Sheets.
2. **No console-only changes**: Every infrastructure/config change has a repo commit.
3. **Secrets never cross boundaries in plaintext**: Vault/Key Vault only.
4. **Agents are read-mostly**: Agents can query and summarize, but create/update actions require explicit tool authorization.
5. **Dashboards are not data stores**: Databricks Apps display, they don't persist business state.
