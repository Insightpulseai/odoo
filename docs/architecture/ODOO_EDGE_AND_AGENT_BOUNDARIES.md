# Odoo Edge and Agent Boundaries

> Status: **Active**
> Decision date: 2026-04-10
> Parent: [`API_LAYER_DOCTRINE.md`](API_LAYER_DOCTRINE.md)
> SSOT: `ssot/agent-platform/foundry_tool_policy.yaml`

---

## Purpose

Define the canonical boundary between:

- Odoo addon/business logic (system of record)
- Pulser/Foundry agent runtime (assistive intelligence)
- Thin HTTP/MCP/OpenAPI adapter edges (external ingress)
- Azure control-plane integrations (official SDK/REST)

---

## Core Rule

Odoo is the sole business system of record for:

- Workflow state (stages, activities, transitions)
- Approvals (expense sheets, purchase orders, journal entries)
- Accounting (chart of accounts, journal postings, reconciliation)
- Tax (regime logic, BIR compliance, withholding computation)
- Expense/liquidation state (cash advances, liquidation lifecycle)
- Posting and document lifecycle (draft → posted → cancelled)

No external service may own, duplicate, or override these states.

---

## Replacement Doctrine

We do not replace Odoo with REST/FastAPI. We replace broad custom REST/FastAPI business layers with:

1. **Odoo-native addon services** for business logic
2. **Foundry/Pulser** for assistive orchestration
3. **Thin HTTP/OpenAPI/MCP adapters** only where external ingress or tool calling is required
4. **Official Azure REST/SDK/Foundry SDK** for Azure control-plane operations

---

## Allowed Thin-Edge Use Cases

Thin edges are allowed only for:

| Use case | Example |
|----------|---------|
| Webhook ingress | Payment gateway callback, EDI notification |
| Bounded tool/function-call adapter | Foundry tool → Odoo JSON-RPC bridge |
| Foundry/OpenAPI tool surface | OpenAPI spec for `base_rest` endpoints |
| File upload ingress | Document pre-processing before `ir.attachment` |
| Async callback handler | External approval webhook, bank feed notification |
| External integration shim | Third-party API adapter (AvaTax, bank sync) |
| Stateless transformation | PDF render, format conversion |

---

## Prohibited Patterns

Do not implement these outside Odoo:

| Pattern | Why prohibited |
|---------|---------------|
| Accounting state machines | Diverges from Odoo journal posting authority |
| Tax regime logic | BIR/AvaTax rules must be in Odoo for audit trail |
| Posting rules | `account.move` lifecycle is Odoo-native |
| Invoice/bill lifecycle logic | Draft → open → paid must flow through Odoo ORM |
| Approval workflows | `hr.expense.sheet.action_approve()` etc. are Odoo server actions |
| Broad CRUD wrappers | Leaky abstraction over Odoo models creates maintenance burden |
| Duplicated finance logic | Two sources of accounting truth is a compliance risk |

---

## Foundry Boundary

Foundry/Pulser **may**:

- Classify intent (informational, navigational, transactional)
- Explain results (variance analysis, reconciliation suggestions)
- Orchestrate bounded tool calls (via approved tool adapters)
- Evaluate and monitor assistant behavior (evals, safety gates)
- Ground on approved knowledge sources (KB, file search)

Foundry/Pulser **may not**:

- Become the source of accounting truth
- Own tax posting state
- Bypass approval gates for risky actions
- Write directly to Odoo ORM without human-in-the-loop for mutations

---

## Azure Boundary

For Azure/runtime/control-plane operations:

- Prefer official Azure SDKs (`azure-mgmt-*`, `azure-identity`)
- Prefer Azure REST API with Entra authentication
- Prefer Foundry SDK v2 / Azure AI Projects client for agent/runtime control
- Do not add custom proxy APIs unless there is a hard integration requirement

---

## Target Topology

```
client / user / Pulser chat
  -> Foundry agent (intent classification + tool routing)
  -> thin adapter surface (if external HTTP required)
  -> Odoo-native action/service (server action, wizard, model method)
  -> Odoo models / PostgreSQL
```

---

## Migration Rule

When an existing FastAPI/REST surface contains business logic:

1. **Inventory** the endpoint (URL, method, what it does)
2. **Classify** as business logic or thin edge
3. **Move** business logic into Odoo addon/service layer
4. **Leave** only the minimum adapter contract in the edge layer
5. **Verify** parity before removing the old path

Register all endpoints in `ssot/agent-platform/odoo_edge_inventory.yaml`.

---

*Last updated: 2026-04-10*
