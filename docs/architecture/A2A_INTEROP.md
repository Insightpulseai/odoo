# A2A Interop and MCP Doctrine

> When to use direct retrieval, MCP tools, and A2A delegation.
> SSOT: `ssot/governance/agentops_policy.yaml`

---

## Routing Doctrine

| Mechanism | When to Use | Examples |
|-----------|------------|---------|
| **Direct retrieval / provider call** | Simple, single-step work within one assistant surface | KB lookup, single API call, record read |
| **MCP (Model Context Protocol)** | Tool and resource access — structured input/output, reusable across surfaces | Odoo record CRUD, Azure resource queries, Databricks SQL, GitHub operations |
| **A2A (Agent-to-Agent)** | Complex cross-assistant delegation or handoff — when the receiving agent has distinct context, permissions, or capabilities | Diva routes to Odoo Copilot for ERP execution; Studio hands off to Document Intelligence for extraction |

---

## Decision Rules

### Prefer Direct Calls When:

- The task is a single retrieval or generation step
- No cross-surface context assembly is needed
- The calling surface has the necessary permissions
- Response latency matters (direct is fastest)

### Use MCP When:

- A tool provides structured, reusable access to a resource
- Multiple surfaces need the same tool (e.g., Odoo record API)
- The tool contract is stable and versioned
- Auth is handled by managed identity or OAuth token

### Use A2A When:

- The task requires delegation to a surface with different permissions
- The task requires context that only the receiving agent can assemble
- The handoff is between distinct product surfaces (not modes within one surface)
- The interaction model is request-response or streaming with completion signals

---

## A2A Interaction Model

```
Diva Copilot (orchestrator)
  |
  |-- classifies intent
  |-- picks target surface
  |-- assembles handoff context
  |
  +---> [A2A] Odoo Copilot (ERP execution)
  +---> [A2A] Studio Copilot (creative finishing)
  +---> [A2A] Genie (analytics Q&A)
  +---> [A2A] Document Intelligence (extraction)
```

### Handoff Contract

Each A2A handoff includes:

| Field | Required | Description |
|-------|----------|-------------|
| `source_surface` | Yes | Originating assistant surface ID |
| `target_surface` | Yes | Receiving assistant surface ID |
| `customer_tenant_id` | Yes | Tenant context |
| `intent_class` | Yes | Classified user intent |
| `context_payload` | Yes | Assembled context for the target surface |
| `correlation_id` | Yes | Trace ID for observability |
| `timeout_ms` | Yes | Maximum wait before fallback |

### What A2A Is Not

- A2A is not a message bus for fire-and-forget events (use n8n workflows)
- A2A is not a replacement for MCP tools (tools are simpler)
- A2A does not mean every surface talks to every other surface (hub-spoke via Diva)

---

## MCP Tool Governance

### First-Wave Tool Envelope

Keep the tool set small and explicit. Only enable tools that have:
- A stable contract
- Auth via managed identity or OAuth
- Audit logging
- A defined owner

See `docs/architecture/AI_RUNTIME_AUTHORITY.md` for the current tool profiles per surface.

### Tool Registration

Tools are registered in Azure AI Foundry Agent Service. Each tool has:
- A versioned schema
- An auth mode (managed identity, OAuth, API key)
- A tenant scope (none, internal, governed, tenant-isolated)
- An action mode (read-only, fail-closed, controlled)

---

## Current State

| Capability | Status |
|-----------|--------|
| Direct retrieval | Active — Odoo Copilot uses KB + runtime context |
| MCP tools | Active — Azure DevOps, GitHub, Foundry MCP servers connected |
| A2A delegation | Not implemented — Diva modes are internal routing, not true A2A |

A2A is a target-state capability. Current architecture uses Diva's internal mode routing. True cross-surface A2A handoff will be implemented when multi-surface deployments are live.

---

## SSOT References

- AgentOps policy: `ssot/governance/agentops_policy.yaml`
- Assistant surfaces: `ssot/agents/assistant_surfaces.yaml`
- Tool profiles: `ssot/agents/diva_copilot.yaml#tool_profiles`

---

*Last updated: 2026-03-24*
