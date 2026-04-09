# Agent Execution Model

> How IPAI agents execute, hand off, and produce evidence.

---

## Execution Surfaces

| Surface | Role | Example |
|---------|------|---------|
| **Claude Code CLI** | Primary agent runtime | Skills, hooks, subagents |
| **Azure DevOps** | Pipeline execution + board management | Odoo CI/CD, estate audit |
| **GitHub Actions** | CI + docs deploy | PR checks, spec validation |
| **Azure Container Apps** | Runtime target | Odoo 18 CE deployment |

## Agent Lifecycle

```
invoke → initialize → execute → [handoff?] → evidence → trace → stop
```

### Phases

1. **Invoke**: Agent spawned via `/spawn` or skill trigger. Gets worktree isolation if defined.
2. **Initialize**: Load skills (SKILL.md frontmatter), apply guardrails (PreToolUse hooks).
3. **Execute**: Perform task. Tool calls validated by PostToolUse hooks.
4. **Handoff** (optional): Delegate to another subagent. Logged as a trace span.
5. **Evidence**: Save output to `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`.
6. **Trace**: Emit execution trace (OTLP format) to `trace.json` alongside evidence.
7. **Stop**: Stop hook fires — evidence reminder, uncommitted change check, trace export.

## Trace Model

Each agent run produces an execution trace with three span types:

| Span Type | Scope | Attributes |
|-----------|-------|------------|
| `agent_run` | Entire session | name, task_class, duration, outcome, evidence_path |
| `handoff` | Subagent delegation | source, target, reason |
| `tool_group` | Parallel tool batch | tool_names, count, duration |

### Required Attributes

Every span includes:
- `agent.name` — which agent (e.g. `odoo-reviewer`)
- `agent.task_class` — what kind of work (e.g. `code_review`, `pipeline_trigger`)
- `agent.repo_path_scope` — what part of repo was touched
- `agent.evidence_path` — where evidence was saved
- `agent.duration_ms` — how long it took
- `agent.outcome` — `success | partial | failed | blocked`
- `agent.handoff_target` — downstream agent (null if no handoff)

### Never Exported

- Prompt body or system prompt
- File contents
- Secrets, passwords, tokens, API keys
- Environment variables matching `*_KEY`, `*_SECRET`, `*_TOKEN`, `PASSWORD`

## Handoff Rules

When one agent delegates to another:

1. Source agent logs handoff span with target name and reason
2. Target agent starts a new `agent_run` span linked to parent trace
3. Evidence from both agents correlates via shared trace ID
4. Handoff must be logged — silent delegation is not allowed

## Evidence Correlation

```
trace.json (OTLP)
  ├── agent_run span → evidence_path: "docs/evidence/20260405-0641/go-live/"
  ├── handoff span → target: "qa-evidence-runner"
  └── tool_group span → tools: ["Bash", "Read", "Write"]
```

The `trace_id` appears in both the trace file and the evidence directory README (if present), enabling bidirectional lookup.

## Outcome Classification

| Outcome | Meaning |
|---------|---------|
| `success` | Task completed, all verification passed |
| `partial` | Task partially completed, some items blocked |
| `failed` | Task failed, error evidence captured |
| `blocked` | Task could not start (missing access, missing resource) |

---

*Policy: `ssot/agents/execution_policy.yaml`*
*Hook: `.claude/plugins/ipai-odoo-azure/hooks/stop/evidence-capture.json`*
