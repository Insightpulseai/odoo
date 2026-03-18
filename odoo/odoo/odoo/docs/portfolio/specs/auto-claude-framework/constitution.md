# Auto-Claude Framework Constitution

## 1. Purpose

Define an autonomous multi-agent coding framework for Odoo CE/OCA that **plans, builds, and validates** changes using Claude Code CLI, with safe worktree isolation and deterministic skill execution.

## 2. Non-Negotiable Constraints

### 2.1 License Compliance
- **AGPL-3.0 awareness**: Auto-Claude reference implementation is AGPL-3.0; we build compatible patterns without embedding their code
- **CE Only**: No Odoo Enterprise modules or odoo.com IAP dependencies
- **OCA First**: Prefer OCA modules (`queue_job`, `base_rest`, `component`) over custom implementations

### 2.2 Architecture Boundaries
- **Odoo Runtime**: Skills execute via `ipai.agent.run` → tool chain → Odoo model methods
- **External Execution**: Claude Code CLI / agents run **outside** Odoo container via MCP or REST
- **Supabase**: Knowledge Graph + embeddings live in Supabase Postgres, NOT Odoo DB
- **Isolation**: Each agent task uses git worktree (for code tasks) or sandbox tenant (for data tasks)

### 2.3 Security
- **Tool Allowlist**: Agents can only call tools registered in `ipai.agent.tool` with `is_active=True`
- **Admin Tools**: Tools with `requires_admin=True` require `base.group_system`
- **No Raw SQL**: Agents cannot execute arbitrary SQL; all data access via ORM methods
- **Audit Trail**: Every run logged in `ipai.agent.run` with full `tool_trace_json`

### 2.4 Determinism
- **Workflow Order**: Skills define `workflow_json` as ordered array of tool keys
- **Retry Policy**: Failed runs can be reset to draft and retried; no automatic retry loops
- **Idempotency**: Tool methods should be idempotent where possible

## 3. Success Criteria

### 3.1 Functional
- [ ] Agent can execute a skill with >1 tool in deterministic order
- [ ] Run trace shows inputs/outputs for each tool step
- [ ] Failed runs provide actionable error_text
- [ ] Skills can be discovered via REST API (OpenAPI documented)

### 3.2 Integration
- [ ] OCA `queue_job` can enqueue skill runs asynchronously
- [ ] REST endpoints (base_rest pattern) expose skill execution
- [ ] Knowledge Graph queries available as tool sources
- [ ] Claude Code CLI can invoke skills via MCP or REST

### 3.3 Quality
- [ ] E2E test covers: install → seed → execute skill → verify output
- [ ] Playwright smoke test: Agent Core menu → create run → execute
- [ ] API contract tests against OpenAPI spec
