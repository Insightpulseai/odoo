# Agent Coordination MCP Server

Agent-to-Agent (A2A) communication server implementing Microsoft's multi-agent orchestration pattern on MCP.

## Overview

This MCP server enables direct agent-to-agent communication, following the pattern described in [Microsoft's A2A on MCP blog post](https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                          │
│                    (Human/Claude CLI)                           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Coordination Server                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Registry   │  │  Coordinator │  │   Message Queue      │  │
│  │  (Supabase)  │  │   (A2A RPC)  │  │   (Jobs System)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │  Odoo ERP │       │  Finance  │       │   Infra   │
    │   Agent   │       │   Agent   │       │   Agent   │
    └───────────┘       └───────────┘       └───────────┘
```

## Features

### Agent Registry
- Register agents with capabilities, transport type, and tools
- Discover agents by capability, status, tags, or tools
- Heartbeat mechanism for health monitoring
- Automatic stale agent cleanup

### Inter-Agent Communication
- **Synchronous invocation**: `invoke_agent` - wait for response
- **Async jobs**: `submit_job` - fire and forget with status polling
- **Handoff**: Transfer conversation context to another agent
- **Delegation**: Assign subtasks with constraints
- **Broadcast**: Send to multiple agents simultaneously

### Context Propagation
- Session tracking across agent calls
- Call chain tracing for distributed debugging
- Workspace context (Odoo instance, company, user)
- Memory references for knowledge sharing

## Installation

```bash
cd mcp/servers/agent-coordination-server
npm install
npm run build
```

## Configuration

Required environment variables:

```bash
# Supabase for registry persistence
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Usage

### Register an Agent

```typescript
// Register the Odoo ERP agent
await invoke("register_agent", {
  id: "odoo-erp-agent",
  name: "Odoo ERP Agent",
  version: "1.0.0",
  description: "Handles accounting, HR, and inventory operations",
  capabilities: ["odoo_erp", "finance", "hr", "inventory"],
  transport: "http",
  endpoint: "http://localhost:8767",
  tools: ["create_invoice", "post_journal_entry", "get_partners"],
  timeout_ms: 30000,
  max_concurrent: 5,
  tags: ["production", "core"]
});
```

### Discover Agents

```typescript
// Find all finance-capable agents
const agents = await invoke("discover_agents", {
  capabilities: ["finance"],
  status: ["active", "idle"]
});
```

### Invoke Agent (Synchronous)

```typescript
// Call another agent and wait for response
const response = await invoke("invoke_agent", {
  target_agent_id: "odoo-erp-agent",
  tool_name: "create_invoice",
  arguments: {
    partner_id: 123,
    lines: [{ product_id: 456, quantity: 1, price: 100 }]
  },
  caller_agent_id: "orchestrator",
  priority: "normal"
});
```

### Submit Async Job

```typescript
// Submit job without waiting
const job = await invoke("submit_job", {
  source_agent_id: "orchestrator",
  target_agent_id: "analytics-agent",
  tool_name: "generate_report",
  arguments: { report_type: "monthly_sales" },
  priority: "low",
  max_retries: 3
});

// Poll for status
const status = await invoke("get_job_status", { job_id: job.job_id });
```

### Handoff Conversation

```typescript
// Transfer to specialist agent
await invoke("handoff", {
  from_agent_id: "general-agent",
  to_agent_id: "finance-specialist",
  reason: "User needs detailed tax advice",
  conversation_context: { messages: [...] },
  user_intent: "Calculate Q4 tax liability"
});
```

### Delegate Task

```typescript
// Delegate with constraints
await invoke("delegate", {
  delegator_id: "orchestrator",
  delegate_id: "research-agent",
  tool_name: "search_documents",
  arguments: { query: "compliance requirements" },
  timeout_ms: 60000,
  allowed_tools: ["search", "read"]
});
```

### Invoke by Capability

```typescript
// Let the system find the best agent
const response = await invoke("invoke_by_capability", {
  capability: "analytics",
  tool_name: "analyze_data",
  arguments: { dataset: "sales_2024" }
});
```

## Tools Reference

### Registry Tools
| Tool | Description |
|------|-------------|
| `register_agent` | Register or update agent in registry |
| `unregister_agent` | Remove agent from registry |
| `discover_agents` | Find agents by criteria |
| `list_agents` | List all registered agents |
| `get_agent` | Get specific agent details |

### Invocation Tools
| Tool | Description |
|------|-------------|
| `invoke_agent` | Synchronous agent call |
| `submit_job` | Async job submission |
| `get_job_status` | Get job status |
| `cancel_job` | Cancel queued job |
| `list_pending_jobs` | List agent's pending jobs |

### Coordination Tools
| Tool | Description |
|------|-------------|
| `handoff` | Transfer conversation to another agent |
| `delegate` | Assign subtask with constraints |
| `broadcast` | Send to multiple agents |
| `invoke_by_capability` | Find and invoke best agent |

### State Tools
| Tool | Description |
|------|-------------|
| `get_agent_state` | Get runtime state |
| `update_agent_state` | Update runtime state |
| `heartbeat` | Send keep-alive |
| `update_agent_status` | Change agent status |

### History/Stats Tools
| Tool | Description |
|------|-------------|
| `get_message_history` | Get messages between agents |
| `get_registry_stats` | Get registry statistics |
| `cleanup_stale_agents` | Mark inactive agents offline |

## Database Schema

The server uses Supabase with the `agent_coordination` schema:

- `agent_registry` - Agent metadata and capabilities
- `agent_state` - Runtime state (queue depth, current task)
- `agent_messages` - Inter-agent message log
- `agent_responses` - Response history
- `agent_jobs` - Async job queue

See `db/migrations/20260120_agent_coordination_schema.sql` for full schema.

## Integration with MCP Coordinator

The MCP Coordinator automatically routes A2A requests:

```python
# Requests with a2a_context or A2A tool names route to agent-coordination
if a2a_context.caller_agent_id or "invoke_agent" in tool_name:
    return MCPTarget.AGENT_COORDINATION
```

## Related Documentation

- [Microsoft A2A on MCP Blog](https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes)
- [MCP Jobs System](../../../docs/infra/MCP_JOBS_SYSTEM.md)
- [MCP Stack README](../../../docs/README_MCP_STACK.md)
