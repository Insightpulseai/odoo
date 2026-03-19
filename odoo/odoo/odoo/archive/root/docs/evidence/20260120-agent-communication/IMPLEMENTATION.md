# A2A Communication Implementation Evidence

**Date**: 2026-01-20
**Scope**: Agent-to-Agent Communication on MCP
**Reference**: https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes

## Summary

Implemented Agent-to-Agent (A2A) communication capabilities following Microsoft's multi-agent orchestration pattern on MCP.

## Files Created

### MCP Server (`mcp/servers/agent-coordination-server/`)
- `package.json` - NPM package configuration
- `tsconfig.json` - TypeScript configuration
- `src/types.ts` - Type definitions for A2A protocol
- `src/agent-registry.ts` - Supabase-backed agent registry
- `src/coordinator.ts` - A2A coordination logic
- `src/index.ts` - Main MCP server with 22 tools
- `README.md` - Documentation

### Database Schema
- `db/migrations/20260120_agent_coordination_schema.sql`
  - Tables: agent_registry, agent_state, agent_messages, agent_responses, agent_jobs
  - RPCs: upsert_agent, agent_heartbeat, discover_agents, claim_next_job, complete_job, fail_job

### Configuration Updates
- `.claude/mcp-servers.json` - Added agent-coordination server
- `mcp/coordinator/app/config.py` - Added agent_coordination_url
- `mcp/coordinator/app/routing.py` - Added A2A routing context

## Tools Implemented (22 total)

### Registry (5)
1. `register_agent` - Register/update agent
2. `unregister_agent` - Remove agent
3. `discover_agents` - Find by criteria
4. `list_agents` - List all
5. `get_agent` - Get details

### Invocation (5)
6. `invoke_agent` - Synchronous call
7. `submit_job` - Async job
8. `get_job_status` - Poll status
9. `cancel_job` - Cancel queued
10. `list_pending_jobs` - List queue

### Coordination (4)
11. `handoff` - Transfer conversation
12. `delegate` - Assign subtask
13. `broadcast` - Multi-agent send
14. `invoke_by_capability` - Capability-based routing

### State (4)
15. `get_agent_state` - Get runtime state
16. `update_agent_state` - Update state
17. `heartbeat` - Keep-alive
18. `update_agent_status` - Change status

### History/Stats (4)
19. `get_message_history` - Message log
20. `get_registry_stats` - Statistics
21. `cleanup_stale_agents` - Maintenance

## Architecture Pattern

```
Orchestrator Agent (Claude CLI / Human)
         │
         ▼
Agent Coordination Server (MCP)
    ├── Registry (Supabase)
    ├── Coordinator (A2A RPC)
    └── Job Queue (mcp-jobs integration)
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
Odoo ERP  Finance      Analytics
 Agent     Agent        Agent
```

## Key Features

1. **Service Discovery**: Agents register capabilities, tools, transport type
2. **Context Propagation**: Session ID, call chain, trace ID across calls
3. **Multiple Invocation Patterns**:
   - Sync: Wait for response
   - Async: Job queue with polling
   - Broadcast: Multiple agents
   - Capability-based: Auto-select best agent
4. **Handoff/Delegation**: Transfer tasks with context
5. **Load Balancing**: Route to agent with lowest queue depth

## Verification

### Build Verification
```bash
cd mcp/servers/agent-coordination-server
npm install
npm run build
```

### Schema Verification
```bash
psql "$SUPABASE_URL" -f db/migrations/20260120_agent_coordination_schema.sql
```

### Integration Test
```bash
# Start server
node mcp/servers/agent-coordination-server/dist/index.js

# Register test agent
echo '{"method":"tools/call","params":{"name":"register_agent","arguments":{"id":"test-agent","name":"Test","version":"1.0.0","description":"Test agent","capabilities":["testing"],"transport":"http"}}}' | nc localhost 8768
```

## Dependencies

- `@modelcontextprotocol/sdk`: ^0.5.0
- `@supabase/supabase-js`: ^2.39.0
- `uuid`: ^9.0.0

## Environment Variables

```bash
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
```

## Related Documents

- [Microsoft A2A Blog](https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes)
- [MCP Jobs System](../../infra/MCP_JOBS_SYSTEM.md)
- [Server README](../../../mcp/servers/agent-coordination-server/README.md)
