# Agent Instructions - SSOT Architecture

## Overview

This directory contains the **Single Source of Truth (SSOT)** for all AI agent instructions in this repository. Tool-specific files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) are **generated mirrors** and must never be edited directly.

## Architecture

```
docs/agent_instructions/
├── SSOT.md              # ← ONLY hand-edit this file
└── README.md            # This file

Generated mirrors (repo root):
├── CLAUDE.md            # Auto-read by Claude Code at session start
├── AGENTS.md            # For Codex CLI + agents.md ecosystem
└── GEMINI.md            # For Gemini Code Assist / CLI (manual injection)
```

## Workflow

### Updating Instructions

1. **Edit only** `docs/agent_instructions/SSOT.md`
2. **Regenerate mirrors**: `python scripts/agents/sync_agent_instructions.py`
3. **Verify sync**: `python scripts/agents/check_agent_instruction_drift.py`
4. **Commit all changes** if drift check passes

### Why This Pattern?

**Problem**: Claude Code, Codex CLI, and Gemini each have different instruction file conventions:
- **Claude Code**: Auto-reads `CLAUDE.md` at project root
- **Codex CLI**: Supports `AGENTS.md` / `agents.md` pattern
- **Gemini**: Requires manual injection via wrapper or CLI option

**Solution**: One SSOT → generated tool-specific mirrors with appropriate headers.

**Benefits**:
- ✅ Single source of truth - edit once, sync everywhere
- ✅ Consistency across all agent tools
- ✅ Drift detection prevents manual edits to generated files
- ✅ Tool-specific headers explain consumption model
- ✅ CI-enforceable via drift check

## Scripts

### `scripts/agents/sync_agent_instructions.py`

Reads `SSOT.md` and generates:
- `CLAUDE.md` (with Claude Code header)
- `AGENTS.md` (with agents.md header)
- `GEMINI.md` (with Gemini header + usage note)

Each generated file includes:
- Tool-specific header explaining its purpose
- `AUTO-GENERATED` warning
- Instructions to edit SSOT instead
- Full SSOT body content

### `scripts/agents/check_agent_instruction_drift.py`

Validates that generated files match SSOT:
- Regenerates mirrors to temp directory
- Compares with repo versions
- Fails (exit 1) if drift detected
- Shows diff for any drifted files

**Use in CI**:
```yaml
- name: Check agent instruction drift
  run: python scripts/agents/check_agent_instruction_drift.py
```

## Tool Consumption

### Claude Code
- **Auto-loads**: `CLAUDE.md` at session start
- **No action needed**: Just edit SSOT + sync

### Codex CLI / agents.md Ecosystem
- **File**: `AGENTS.md`
- **Usage**: Codex CLI auto-discovers `AGENTS.md` (depending on version)
- **Manual**: If not auto-discovered, inject via CLI option or wrapper

### Gemini Code Assist / CLI
- **File**: `GEMINI.md`
- **Usage**: Manual injection required (Gemini doesn't auto-discover)
- **Wrapper pattern**:
  ```bash
  gemini-cli --instructions "$(cat GEMINI.md)" <command>
  ```
- **Or**: Create `scripts/agents/print_gemini_instructions.sh` that outputs `GEMINI.md`

## Adding New Agent Tools

To add support for a new agent tool (e.g., `CURSOR.md`):

1. Update `scripts/agents/sync_agent_instructions.py`:
   ```python
   OUTPUTS["CURSOR.md"] = REPO_ROOT / "CURSOR.md"
   HEADERS["CURSOR.md"] = """# CURSOR.md — Cursor Agent Instructions
   > AUTO-GENERATED from `docs/agent_instructions/SSOT.md`
   ..."""
   ```

2. Run sync: `python scripts/agents/sync_agent_instructions.py`
3. Drift check will automatically include new file
4. Document consumption model in this README

## Maintenance

### If Drift Detected

```bash
# Option 1: SSOT is correct, regenerate mirrors
python scripts/agents/sync_agent_instructions.py

# Option 2: Generated file has improvements
# 1. Port improvements back to SSOT.md
# 2. Regenerate: python scripts/agents/sync_agent_instructions.py
# 3. Verify: python scripts/agents/check_agent_instruction_drift.py
```

### Before Committing

Always run drift check:
```bash
python scripts/agents/check_agent_instruction_drift.py
```

Should output:
```
✅ No drift detected. All mirrors match SSOT.
```

## References

- [Claude Code Documentation](https://code.claude.com/docs/en/overview)
- [OpenAI Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/)
- [agents.md Convention](https://github.com/topics/agents-md)
