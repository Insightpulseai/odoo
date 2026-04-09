# Custom Agent Roles — IPAI Plugin

> Defines what each subagent can do, which MCP tools it may use, and its trace/evidence obligations.
> Policy source: `ssot/agents/execution_policy.yaml`

---

## Role Summary

| Agent | Layer | ADO MCP | Trace | Pipeline Trigger | Board Mutate |
|-------|-------|---------|-------|-----------------|--------------|
| `odoo-reviewer` | A-domain | read | optional | no | no |
| `azure-runtime-operator` | B-platform | read | **required** | no | no |
| `governance-auditor` | C-governance | **read/write** | **required** | no | **yes** (scoped) |
| `qa-evidence-runner` | A-domain | read | **required** | **yes** (scoped) | no |
| `board-normalizer` | C-governance | **read/write** | **required** | no | **yes** (scoped) |
| `foundry-copilot-operator` | C-governance | read | **required** | no | no |

---

## Per-Role Details

### odoo-reviewer

**Purpose**: Review Odoo 18 CE module code against OCA standards.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | Read-only (work item context lookup) |
| Trace obligation | Optional (read-only code review) |
| Pipeline trigger | Not allowed |
| Board mutation | Not allowed |
| Allowed ADO tools | `work_item.read`, `board.read` |
| Handoff targets | `qa-evidence-runner` (if tests needed) |
| Approval required | No |

### azure-runtime-operator

**Purpose**: Manage ACA deployments, revisions, health probes.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | Read-only (pipeline/build status lookup) |
| Trace obligation | **Required** (mutates infrastructure) |
| Pipeline trigger | Not allowed (uses Azure CLI directly) |
| Board mutation | Not allowed |
| Allowed ADO tools | `pipeline.read`, `build.read`, `run.read` |
| Handoff targets | `governance-auditor` (post-deploy audit) |
| Approval required | Yes, for destructive operations (scale-to-zero, revision deactivation) |

### governance-auditor

**Purpose**: Verify Azure estate, policy compliance, drift detection.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | **Read/write** |
| Trace obligation | **Required** |
| Pipeline trigger | Not allowed |
| Board mutation | **Yes** — state, tags, comments only |
| Allowed ADO tools | `work_item.read`, `work_item.update`, `pipeline.read`, `build.read`, `board.read` |
| Board mutation scope | `state`, `tags`, `comment` fields only |
| Handoff targets | None (terminal auditor) |
| Approval required | No for read; yes for board state changes on production boards |

### qa-evidence-runner

**Purpose**: Execute Odoo module tests, capture evidence.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | Read-only |
| Trace obligation | **Required** (produces evidence artifacts) |
| Pipeline trigger | **Yes** — test pipelines only |
| Pipeline scope | `azure-pipelines-test-*.yml` patterns only |
| Board mutation | Not allowed |
| Allowed ADO tools | `pipeline.read`, `pipeline.trigger`, `build.read`, `run.read`, `artifact.read` |
| Handoff targets | None |
| Approval required | No for test pipelines; yes for non-test pipelines |

### board-normalizer

**Purpose**: Sync Azure Boards ↔ GitHub Issues, normalize naming.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | **Read/write** |
| Trace obligation | **Required** |
| Pipeline trigger | Not allowed |
| Board mutation | **Yes** — state, tags, title, comment, assigned_to |
| Allowed ADO tools | `work_item.read`, `work_item.update`, `board.read` |
| Board mutation scope | `state`, `tags`, `title`, `comment`, `assigned_to` fields |
| Handoff targets | None |
| Approval required | Yes, for closing work items |

### foundry-copilot-operator

**Purpose**: Manage Foundry agent deployments and copilot gateway.

| Attribute | Value |
|-----------|-------|
| ADO MCP access | Read-only |
| Trace obligation | **Required** |
| Pipeline trigger | Not allowed |
| Board mutation | Not allowed |
| Allowed ADO tools | `pipeline.read`, `build.read` |
| Handoff targets | None |
| Approval required | Yes, for model deployment changes |
| Activation | Only when `CLAUDE_CODE_USE_FOUNDRY=1` |

---

## Permission Escalation

No agent can self-escalate permissions. If an agent needs write access beyond its defined scope:

1. The agent must report the need and stop
2. The user (or a governance-auditor review) must approve
3. The approval is logged in the execution trace

## Unattended Runs

All agents running unattended (CI/scheduled):
- ADO MCP mode: **read-only**
- Pipeline triggering: **denied**
- Board mutation: **denied**
- Trace: **required**
- Evidence: **required**
- Override: set `IPAI_UNATTENDED_WRITE=1` to enable writes (explicit opt-in)

---

*Policy: `ssot/agents/execution_policy.yaml`*
*Model: `docs/agents/AGENT_EXECUTION_MODEL.md`*
*Observability: `docs/agents/AGENT_OBSERVABILITY.md`*
