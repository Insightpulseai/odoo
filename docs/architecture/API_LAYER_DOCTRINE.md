# API Layer Doctrine

> Status: **Active** (supersedes `UNIFIED_API_GATEWAY_TARGET_STATE.md`)
> Decision date: 2026-04-10
> SSOT: `ssot/agent-platform/foundry_tool_policy.yaml`
> Companion: [`ODOO_EDGE_AND_AGENT_BOUNDARIES.md`](ODOO_EDGE_AND_AGENT_BOUNDARIES.md)
> Migration register: `ssot/agent-platform/odoo_edge_inventory.yaml`

---

## 1. Premise

We are **not** replacing Odoo with REST/FastAPI. We are eliminating the pattern
of wrapping Odoo business logic in a fat FastAPI/REST layer.

**Old pattern** (eliminated):

```
client -> FastAPI -> duplicated business logic -> Odoo/DB
```

**New pattern** (canonical):

```
client/agent -> Foundry tool adapter -> Odoo-native action/service -> Odoo/DB
```

For infra/control work:

```
ops tooling -> official Azure REST/SDK/Foundry SDK
```

---

## 2. Layer Responsibilities

| Layer | What lives there | What must NOT live there |
|-------|-----------------|------------------------|
| **Odoo addon layer** | Business rules, workflows, accounting, tax, posting rules, approvals, state machines | Duplicated logic in FastAPI |
| **Foundry / agent layer** | Chat, tool routing, skill invocation, explainability, evals | Source-of-truth accounting/workflow state |
| **Thin gateway/API layer** | Webhook ingress, tool adapters, bounded OpenAPI/function surfaces | Full finance/tax engine |
| **Azure control plane** | Deployment/runtime ops, agent config, monitoring, official service APIs | Custom business logic wrappers |

---

## 3. Decision Rule

Use **no FastAPI at all** if the capability can be done:

- Directly inside an Odoo addon (models, server actions, wizards, scheduled jobs)
- Through Odoo server actions/jobs
- Through a Foundry tool that calls a bounded Odoo action

Use a **thin FastAPI/HTTP edge** only when ALL of these are true:

- External system requires HTTP callback/webhook, OR
- You need a clean OpenAPI surface for Foundry tool calling, OR
- You need stateless ingress separate from Odoo, OR
- You need async upload/processing ingress, OR
- You must isolate a non-Odoo runtime concern

---

## 4. What Gets Removed

### Remove (prohibited patterns)

- Duplicated business rules in FastAPI
- Tax logic outside Odoo
- Approval logic outside Odoo
- Invoice/expense state machines outside Odoo
- Broad CRUD REST wrappers over Odoo tables
- "Microservice for everything" around a monolithic ERP core

### Keep (justified thin edges only)

- Authentication/ingress adapter
- Webhook listener (external callbacks)
- File upload edge (pre-processing before Odoo attachment)
- Foundry tool adapter (bounded JSON-RPC bridge)
- External callback processor (payment gateway, EDI)
- Stateless formatting/transformation endpoint

---

## 5. Skills and Tools Mapping

Microsoft's Foundry pattern:

- **Skills** = judgment layer (decide when to use Odoo, Foundry, Azure, or docs)
- **MCP/Tools** = execution layer (do the actual call)
- **Odoo** = authoritative backend (system of record)

For this stack:

- Repo-local skills decide **when** to invoke
- Bounded tools/adapters do the actual call
- Odoo remains the authoritative backend for all ERP state

Tool preference order (from `foundry_tool_policy.yaml`):

1. Built-in tools (web_search, file_search, code_interpreter)
2. Function calling (OpenAPI-defined Odoo actions)
3. OpenAPI (bounded Odoo REST endpoints via `base_rest`)
4. MCP (for reusable agent tools)
5. A2A (preview, later)

---

## 6. Practical Examples

### Tax calculation

- **Wrong**: FastAPI endpoint that reimplements BIR tax rules
- **Right**: `ipai_tax_intelligence` Odoo addon with `compute_tax()` method, exposed via bounded `base_rest` endpoint if needed by Foundry tool

### Expense approval

- **Wrong**: FastAPI service with approval state machine calling Odoo DB directly
- **Right**: Odoo `hr.expense.sheet` with `action_approve()` server action, triggered by Odoo activity workflow

### Agent-assisted invoice check

- **Wrong**: FastAPI endpoint that reads invoice, calls GPT, writes result to DB
- **Right**: Foundry agent with tool that calls `ipai_odoo_copilot` addon's JSON-RPC endpoint, which internally uses `ir.attachment` + Odoo ORM

### Azure infra operations

- **Wrong**: Custom FastAPI wrapper around `az` CLI commands
- **Right**: Official Azure SDKs / `azure-mgmt-*` / Foundry SDK v2

---

## 7. Migration Path

For existing FastAPI services in the repo:

1. **Audit**: Identify which business logic is duplicated from Odoo
2. **Absorb**: Move business logic into Odoo addon (model method, server action, or wizard)
3. **Thin**: If external HTTP surface is still needed, reduce to a stateless adapter
4. **Wire**: Connect Foundry tools to the Odoo-native endpoint
5. **Remove**: Delete the fat FastAPI service

---

## 8. Superseded Documents

| Document | Status |
|----------|--------|
| `UNIFIED_API_GATEWAY_TARGET_STATE.md` | Superseded — referenced Supabase, n8n, APIM gateway, and Odoo CE 19 (all deprecated or changed) |

The APIM Consumption tier gateway described in the superseded doc is NOT part of the
current target state. API surface is provided by:

- Azure Front Door (edge, WAF, TLS) for public ingress
- Odoo `base_rest` / JSON-RPC for bounded API surfaces
- Foundry Agent Service for agent-to-tool routing
- Thin Azure Functions / ACA sidecars for webhook/callback ingress

---

*Last updated: 2026-04-10*
