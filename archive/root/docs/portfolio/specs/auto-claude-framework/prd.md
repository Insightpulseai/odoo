# Auto-Claude Framework PRD

## 1. Overview

Build an autonomous agent framework for InsightPulse AI that enables Claude Code CLI and other agent surfaces to execute Odoo-native skills with full audit trail, knowledge graph context, and safe isolation.

## 2. Problem Statement

Current agent tooling lacks:
- **Deterministic execution**: Ad-hoc tool calls with no workflow structure
- **Audit trail**: No record of what tools ran, with what inputs/outputs
- **Knowledge context**: Agents don't have access to structured entity relationships
- **Safe parallelism**: No isolation between concurrent agent tasks
- **E2E testing**: No automated validation of agent flows

## 3. Solution Components

### 3.1 Skill Registry (ipai_agent_core - existing)

**Models already implemented:**
- `ipai.agent.skill` - workflow definitions with intents, guardrails, tool bindings
- `ipai.agent.tool` - callable actions mapped to Odoo model/methods
- `ipai.agent.run` - execution logs with state machine
- `ipai.agent.knowledge_source` - document/URL/model sources

**Enhancements needed:**
- Add `rate_limit` and `timeout_s` fields to skills
- Add `required_groups` M2M to skills for RBAC
- Add `cooldown_seconds` to prevent runaway loops

### 3.2 Skill API (ipai_skill_api - new)

REST endpoints using `base_rest` pattern:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/skills` | GET | List available skills |
| `/api/v1/skills/{key}` | GET | Get skill definition + schema |
| `/api/v1/runs` | POST | Create and optionally execute a run |
| `/api/v1/runs/{id}` | GET | Get run status + trace |
| `/api/v1/runs/{id}/execute` | POST | Execute a draft/failed run |

**Auth**: JWT (auth_jwt) or API key for agent-to-Odoo calls.

### 3.3 Knowledge Graph (Supabase)

**Schema**: `kg.nodes`, `kg.edges`, `kg.evidence`

**Integration**:
- Tool: `kg.neighborhood` RPC for entity context expansion
- Tool: `kg.semantic_search` via pgvector for embedding queries
- Odoo skill: `ipai.kg.fetch_context` wraps KG calls

### 3.4 Queue Integration (OCA queue_job)

**Pattern**:
```python
# Enqueue skill execution
run = env['ipai.agent.run'].create({
    'skill_id': skill.id,
    'input_json': json.dumps(inputs),
})
run.with_delay(priority=10).action_execute()
```

**Benefits**:
- Durable execution with retries
- Concurrency control via channels
- Batch runs via `queue_job_batch`

### 3.5 Worktree Isolation (for code tasks)

**Pattern** (Claude Code CLI side):
```bash
# Create isolated worktree for task
git worktree add ../wt/<run_id> <base_branch>
cd ../wt/<run_id>

# Agent operates in worktree
claude --spec task.md

# On success: cherry-pick/merge
git checkout <target_branch>
git cherry-pick <worktree_commits>

# Cleanup
git worktree remove ../wt/<run_id>
```

**Odoo integration**: Run artifacts stored as attachments.

## 4. User Stories

### US-1: Execute Skill via API
As an **agent (Claude Code CLI)**, I want to execute a registered skill via REST API so that I can perform Odoo operations with audit trail.

**Acceptance**:
- POST to `/api/v1/runs` with skill_key + inputs creates and executes run
- Response includes run_id, state, output
- Trace shows each tool step

### US-2: Discover Available Skills
As an **agent**, I want to list skills with their schemas so that I can decide which skill to invoke.

**Acceptance**:
- GET `/api/v1/skills` returns active skills with descriptions
- Each skill includes input_schema, intents, guardrails

### US-3: Knowledge Context
As an **agent**, I want to fetch entity context from Knowledge Graph so that I can make informed decisions.

**Acceptance**:
- Tool `kg.fetch_context` takes entity reference, returns neighbors
- Evidence/provenance included in response

### US-4: Async Skill Execution
As a **system**, I want skills to run asynchronously so that long-running tasks don't block.

**Acceptance**:
- Runs enqueued via `queue_job`
- Status polling available via API
- Webhook notification on completion (future)

## 5. Technical Requirements

### 5.1 OCA Dependencies
```yaml
repos:
  - name: OCA/queue
    branch: "18.0"
    modules:
      - queue_job
      - queue_job_cron
      - queue_job_batch

  - name: OCA/rest-framework
    branch: "18.0"
    modules:
      - base_rest
      - base_rest_pydantic

  - name: OCA/server-auth
    branch: "18.0"
    modules:
      - auth_jwt
      - auth_api_key
```

### 5.2 Supabase Schema
See `supabase/migrations/20250106_kg_schema.sql`

### 5.3 E2E Tests
- `tests/e2e/test_skill_execution.py` - Odoo test
- `tests/e2e/playwright/smoke.spec.ts` - UI smoke

## 6. Out of Scope (v1)

- Multi-model routing (single model per skill)
- Real-time streaming of tool outputs
- Marketplace for third-party skills
- Automatic retry with backoff (manual retry only)
