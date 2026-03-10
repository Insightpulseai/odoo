# PRD — ChatGPT Ops Assistant

> Product requirements for the `ops-assistant` ChatGPT App.
> Platform: OpenAI Apps SDK. Backend: MCP server with SSE transport.

## Problem Statement

Operations teams context-switch between Odoo (CRM, projects), Plane (work items),
and Slack (communication) throughout the day. There is no unified interface to
query, update, and coordinate across these systems without opening each tool separately.

## Solution

A ChatGPT App named **Ops Assistant** that exposes three tool families
(`odoo.*`, `plane.*`, `slack.*`) via an MCP server. Users interact through
ChatGPT's natural language interface and the app executes actions on their behalf
with appropriate guardrails.

## Target Users

- Operations managers
- Project coordinators
- Sales team leads
- Engineering leads tracking work items

## Core Capabilities

### Tool Family: `odoo.*`

| Tool | Description | Approval |
|------|-------------|----------|
| `odoo.search_read` | Read-only search across CRM, partners, tasks, sales | No |
| `odoo.update_partner` | Update contact info on res.partner | Yes (prod) |
| `odoo.update_opportunity` | Update stage, revenue, probability on crm.lead | Yes (prod) |
| `odoo.create_activity` | Schedule activities on allowed models | No |

**Backend**: XML-RPC (`/xmlrpc/2/object`) with dedicated service user `odoo_chatgpt_rpc`.
**Auth**: Service user with restricted access rights group.

### Tool Family: `plane.*`

| Tool | Description | Approval |
|------|-------------|----------|
| `plane.list_work_items` | Search/list work items in a project | No |
| `plane.create_work_item` | Create new work item (issue) | No |
| `plane.update_work_item` | Update existing work item fields | No |
| `plane.create_page` | Create wiki/doc page | No |
| `plane.add_comment` | Comment on a work item | No |

**Backend**: Plane REST API v1 (`/api/v1/workspaces/{slug}/...`).
**Auth**: Bot Token (`X-API-Key` header).
**Rate limit**: 60 req/min (upstream Plane constraint).

### Tool Family: `slack.*`

| Tool | Description | Approval |
|------|-------------|----------|
| `slack.post_message` | Post message to allowed channels | No |
| `slack.request_approval` | Interactive approval request (blocks until response) | No |

**Backend**: Slack Web API.
**Auth**: Bot token (`xoxb-`), signing secret for inbound verification.

## Authentication

- **User auth**: OAuth 2.1 with PKCE per OpenAI Apps SDK spec.
- **Odoo backend**: Dedicated XML-RPC service user (not user's credentials).
- **Plane backend**: Bot Token (workspace-level, not user-scoped).
- **Slack backend**: Bot token with `chat:write`, `chat:write.public` scopes.

## Approval Workflow

1. User asks ChatGPT to update an Odoo record in production.
2. MCP server checks allowlist: tool requires approval.
3. MCP server calls `slack.request_approval` with change details.
4. Slack message includes Approve/Reject buttons.
5. On approval: MCP server executes the Odoo write, logs result.
6. On rejection or timeout (60 min): action cancelled, logged.

## Cross-System Linking

When an action spans systems (e.g., "create a Plane work item for this Odoo lead"),
the MCP server writes both IDs to `ops.external_identities`:

```sql
INSERT INTO ops.external_identities
  (entity_type, source_system, source_id, target_system, target_id, created_by)
VALUES
  ('crm.lead', 'odoo', 42, 'plane', 'uuid-here', 'chatgpt_ops_assistant');
```

## Audit & Observability

- All tool calls logged to `ops.run_events` (Supabase).
- Dashboard: Superset or Supabase Studio for ops team.
- Alerts: Slack notification on tool errors or approval timeouts.

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Latency (tool response) | < 3s for reads, < 5s for writes |
| Availability | 99.5% (dependent on upstream APIs) |
| Rate limit | 60 req/min per user session |
| Audit retention | 90 days minimum |
| PKCE enforcement | Required for all OAuth flows |

## Out of Scope (v1)

- Odoo financial module writes (account.move, account.payment)
- Odoo user/role management
- Plane webhook inbound processing (handled by existing plane-webhook function)
- File attachments / document uploads
- Multi-workspace Plane support
