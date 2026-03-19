# CLI Skill Template

> Reusable contract for wrapping any CLI tool as a safe, non-interactive agent skill.

## Structure

```
skills/<tool-name>/
├── SKILL.md              # Skill contract (this template)
├── bin/<tool>-safe        # Safe wrapper script
├── policies/allowed-ops.md  # Operation classification
└── examples/              # Runnable examples
    ├── read.sh
    ├── write.sh
    └── verify.sh
```

## Contract sections (required)

### 1. Purpose

What system the skill talks to and what it is allowed to do.
One paragraph maximum.

### 2. Preconditions

What must already exist before the skill can run:
- Binary installed and on PATH
- Auth already configured (no interactive login)
- Required environment variables present
- Target endpoint reachable

### 3. Allowed operations

Categorized by risk:

| Class | Description | Examples |
|-------|-------------|----------|
| **Read-only** | No mutations | list, show, status, logs |
| **Controlled write** | Scoped mutations with verification | create, update, deploy |
| **Admin/bootstrap** | One-time setup (separate skill) | login, init, credential setup |

### 4. Disallowed operations

Hard blocks enforced by the wrapper:
- Interactive login or browser-based auth
- TTY-dependent commands (exec, ssh, console)
- Broad destructive operations (delete resource group, drop database)
- Writing secrets into repo files
- Wildcard/unscoped mutations

### 5. Output contract

- Prefer structured output: JSON, NDJSON, TSV
- Force output flags where possible (e.g., `--output json`)
- Machine-parseable over human-readable

### 6. Verification contract

What command proves the operation succeeded:
- Health check URL + expected status
- Resource state query + expected value
- Log inspection command

## Skill classes

### Runtime skills (used repeatedly)
- read, deploy, update, verify
- Non-interactive, idempotent, scriptable

### Bootstrap skills (used once)
- login, auth setup, credential init
- May require interaction — keep separate from runtime skills

## Wrapper behavior contract

Every `bin/<tool>-safe` wrapper must:
1. Fail fast if binary is not installed
2. Fail fast if auth is not configured
3. Deny destructive verbs by default
4. Deny interactive/TTY commands
5. Force structured output where possible
6. Pass through to the real CLI for allowed operations
