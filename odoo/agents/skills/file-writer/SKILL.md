# Skill: file-writer

**Skill ID**: `file-writer`
**Domain**: Agent Execution / File Operations
**Status**: Production

---

## Purpose

Provides sandbox-safe file creation and editing standards for all sub-agents operating in constrained environments (Claude Code sandbox, CI containers, restricted shells).

---

## Sandbox-safe file writes (Required)

When creating or editing files in constrained/sandboxed environments:

### Preferred method (default)

- Use the native **Write** or **Edit** tool for all file creation and updates.
- Do NOT use Bash heredocs, shell redirects, or `cat > file <<'EOF'`.
- Do NOT use `tee`, `echo >`, or any shell redirection for file content writes.

### Disallowed patterns (default)

```bash
# DISALLOWED — do not use these for file creation:
cat > file <<'EOF'
tee file <<'EOF'
echo "content" > file
python -c "open('f','w').write(...)"  # unless Write tool is truly unavailable
```

### Allowed fallback (scoped only)

Use elevated/bypass mode (`mode: "bypassPermissions"`) only when:
- Write/Edit tool is confirmed unavailable in the agent's tool list
- Task is trusted, tightly scoped, and path-constrained
- Reason for elevation is documented in the task prompt

Must document in output:
- Why elevated mode was required
- Which file paths were written
- What mode was used

### Rationale

The Write tool bypasses shell sandbox restrictions. Bash heredoc writes fail silently or with permission errors in sandboxed agents. Write tool is always the correct primitive for file mutations.

---

## Completion evidence (required in agent output)

Every file-writing task MUST report:

```
FILES WRITTEN:
- <path>: <line count or section summary>
  Write method: Write/Edit tool | elevated Bash
```

---

## Examples

### Correct (Write tool)
```
Write tool → /path/to/file.md
Content: <full file content as string>
```

### Incorrect (Bash redirect — will fail in sandbox)
```bash
cat > /path/to/file.md <<'EOF'
# Content
EOF
```

---

## Taxonomy

- Kind: `constraint`
- External dependencies: none
- Applies to: all sub-agents spawned via Task tool
