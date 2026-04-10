# MCP Policy

> SSOT: `ssot/agent-platform/mcp_policy.yaml`
> Last updated: 2026-04-10

---

## Overview

MCP (Model Context Protocol) is a **first-class tool channel** for Foundry Agent Service. Agents can connect to remote MCP servers (public or private) to extend their capabilities with structured tool access.

MCP is **not** a business-state ownership layer. Odoo remains the authoritative system of record for all ERP truth (expenses, taxes, approvals, accounting).

---

## Hosting Patterns

### Public MCP

Third-party or Microsoft-hosted MCP endpoints. Allowed for general-purpose tools (docs search, Azure resource management, browser testing).

### Private MCP

For sensitive data access (database ops, internal APIs). Required components:

- Standard Agent Setup with private networking
- MCP server hosted on **Azure Container Apps**
- **Internal-only ingress**
- **Dedicated MCP subnet** in VNet

---

## Authentication

- Use **Foundry project connections** for MCP auth
- **Never** hardcode credentials in prompts, app code, or env-var sprawl
- Maintain identity separation: Foundry-side identity vs ACA-side identity (separate managed identities)

---

## Controls (Mandatory)

| Control | Required |
|---------|----------|
| `allowed_tools` allow-list | Yes |
| Approval for high-risk tools | Yes |
| Review tool name + arguments before approval | Yes |
| Audit log all tool calls | Yes |
| Audit log all approvals | Yes |

---

## Timeouts

- Non-streaming MCP tool calls: **100-second timeout** (hard limit)
- Long-running tasks must be async: short MCP request, enqueue background job, poll or continue later

---

## Allowed MCP Tools (Current)

| Tool | Purpose | Permissions |
|------|---------|-------------|
| Azure DevOps MCP | CI/CD pipeline ops, work items | Standard |
| Azure MCP Server | Azure resource management | Standard |
| Postgres MCP | Read-only ops/investigation | **Read-only first** |
| Playwright MCP | Browser testing, critical path validation | Standard |
| Chrome DevTools MCP | Debug/triage only | Standard |
| Microsoft Learn MCP | Documentation search | Standard |
| Markitdown | Document conversion | Standard |

### Optional / Not Critical Path

- **Azure AI Foundry MCP** — experimental, not on MVP critical path

---

## Postgres MCP Guardrails

Source: [azure-postgres-mcp-demo](https://github.com/Azure-Samples/azure-postgres-mcp-demo)

**Placement**: `agent-platform` or `infra` (never `odoo`)

### Allowed

- Read-only schema discovery
- Admin ops queries
- Troubleshooting and support investigation
- Migration/verification helpers
- Databricks/reporting support patterns

### Prohibited

- Direct business writes
- Approval state changes
- Accounting state changes
- Tax state mutation
- Expense workflow mutation
- Any ORM bypass for ERP work

---

## Repo Ownership

| Repo | MCP Responsibility |
|------|--------------------|
| `agent-platform` | MCP server integrations, tool binding, approval workflows, audit logging, private ACA-hosted MCP servers |
| `odoo` | ERP truth, final business actions, thin bridge actions only. **No MCP server hosting or orchestration.** |
| `agents` | Tool policy metadata, allowed tool lists, routing contracts, eval scenarios for MCP usage |

---

## Per-Vertical Applicability

### Pulser (Reverse SAP Joule)

MCP is a valid tool extension mechanism. Keep tools tightly allow-listed, require approval for risky tools, keep Odoo as final authority.

### Reverse AvaTax

MCP helps with controlled external tools, review assistance, ops tooling. **Not for** tax truth, posting logic, or ledger ownership.

### Reverse SAP Concur

MCP supports bounded companion tools, reminders, safe external integrations. **Not for** cash advance truth, liquidation truth, or finance workflow ownership.

---

## Global Prohibitions

- Direct ERP truth mutation via MCP
- Direct accounting/tax state changes via MCP
- Broad unrestricted tool exposure
- MCP as business-state ownership layer

---

## References

- [Azure Agent Service — MCP Servers](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/mcp-servers)
- [Azure Postgres MCP Demo](https://github.com/Azure-Samples/azure-postgres-mcp-demo)
- [Azure Agent Service Transparency Note](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/agents/transparency-note)
