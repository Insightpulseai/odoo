#!/usr/bin/env python3
"""PostToolUse hook: log significant actions for evidence trail.

This hook does not block — it only logs.
Exit code 0 always (passthrough).
"""
import json
import os
import sys
from datetime import datetime

payload = json.load(sys.stdin)
tool_name = payload.get("tool_name", "")
tool_input = payload.get("tool_input", {})

# Only log significant mutations
LOGGED_TOOLS = {"Write", "Edit", "Bash"}

if tool_name not in LOGGED_TOOLS:
    sys.exit(0)

# Build log entry
entry = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "tool": tool_name,
}

if tool_name == "Bash":
    entry["command"] = tool_input.get("command", "")[:200]
elif tool_name in ("Write", "Edit"):
    entry["file"] = tool_input.get("file_path", "")

# Append to session log (best-effort, never block on failure)
log_dir = os.path.expanduser("~/.claude/logs")
try:
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"actions-{datetime.utcnow().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
except Exception:
    pass  # Never block on logging failure

sys.exit(0)
