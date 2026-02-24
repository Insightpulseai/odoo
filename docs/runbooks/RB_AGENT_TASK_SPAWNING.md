# Runbook: Agent Task Spawning

**ID**: RB_AGENT_TASK_SPAWNING
**Domain**: Agent Operations
**Last Updated**: 2026-02-24

---

## Purpose

Defines the canonical policy for spawning sub-agents via the Task tool, including permission modes, file-write constraints, and evidence requirements.

---

## Task Spawn Modes

### Default mode (use this unless you have a reason not to)

```json
{ "mode": "default" }
```

Use for: analysis, reads, research, safe file writes via Write/Edit tool.

**Constraint**: Bash file redirects (`cat >`, `tee`, `echo >`) are blocked by sandbox. Use Write/Edit tool for file mutations.

### acceptEdits mode

```json
{ "mode": "acceptEdits" }
```

Use for: agents that need to write or edit files without user prompts. Write/Edit tool still works; Bash redirects still blocked.

### bypassPermissions mode

```json
{ "mode": "bypassPermissions" }
```

Use **only** when:
- Write/Edit tool is confirmed unavailable in the target agent's tool list
- Shell-level file operations are genuinely required (e.g., `chmod`, `mv`, `git mv`)
- Task is trusted, path-constrained, and scoped to known outputs
- Reason is documented in the task prompt

**Do not use bypassPermissions as a default.** It disables safety boundaries and reduces audit confidence.

---

## Required Prompt Clause for File-Writing Tasks

Always include this clause in the `prompt` field when the agent's task involves creating or editing files:

```
Use the Write tool (or Edit tool) for all file creation and edits.
Do NOT use Bash heredocs or shell redirects (cat >, tee, echo >) for writing files.
Report file paths written and confirm Write tool was used.
```

### Example task spawn

```json
{
  "subagent_type": "general-purpose",
  "description": "Write spec file",
  "mode": "default",
  "prompt": "Write /path/to/spec/prd.md with the following content:\n...\n\nUse the Write tool. Do NOT use Bash heredocs."
}
```

---

## File-Write Decision Tree

```
Agent needs to create/edit a file?
│
├─ Write/Edit tool available?
│   ├─ YES → use Write/Edit tool (default, sandbox-safe)
│   └─ NO  → use bypassPermissions mode, document reason
│
└─ Never use Bash cat/tee/echo redirects for file writes
```

---

## Evidence Requirements

Every file-writing agent MUST include in its output:

```
FILES WRITTEN:
- <path>: <line count or section summary>
  Write method: Write/Edit tool | elevated Bash (bypassPermissions)
```

This allows the orchestrator to verify completion without reading every file.

---

## Common Failure Mode: Bash heredoc in sandbox

**Symptom**: Agent output says `Bash tool is being denied` or agent requests `dangerouslyDisableSandbox`.

**Root cause**: Agent attempted `cat > file <<'EOF'` — blocked by Claude Code sandbox.

**Fix**: Respawn agent with explicit Write tool instruction, or write the file directly in the orchestrator context using the Write tool.

**Do NOT**: Set `dangerouslyDisableSandbox: true` unless in a fully controlled, non-production context.

---

## Bash vs Write Tool — Scope Boundary

| Operation | Correct Tool |
|-----------|-------------|
| Create a file | Write tool |
| Edit a file | Edit tool |
| Run tests | Bash |
| Run git operations | Bash |
| Read file contents | Read tool |
| Validate/lint | Bash |
| Move files (`git mv`) | Bash (may need acceptEdits/bypassPermissions) |

---

## Related

- `agents/skills/file-writer/SKILL.md` — skill-level policy
- `agents/policies/NO_CLI_NO_DOCKER.md` — web environment constraints
- `spec/odoo-platform-personas/tasks.md` T1 — agent persona contract template
