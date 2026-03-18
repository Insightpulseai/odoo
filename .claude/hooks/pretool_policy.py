#!/usr/bin/env python3
"""PreToolUse hook: enforce repo policy gates.

Exit codes:
  0 = allow
  2 = block (deny with reason)
"""
import json
import re
import sys

payload = json.load(sys.stdin)
tool_name = payload.get("tool_name", "")
tool_input = payload.get("tool_input", {})

# --- Bash command policy ---
if tool_name == "Bash":
    command = tool_input.get("command", "")

    # Block destructive commands
    blocked_patterns = [
        r"\brm\s+-rf\s+/",           # rm -rf with absolute path
        r"\bsudo\b",                   # sudo
        r"\bgit\s+push\s+--force\b",  # force push
        r"\bgit\s+reset\s+--hard\b",  # hard reset
        r"\bdrop\s+database\b",        # drop database
        r"\bdrop\s+table\b",           # drop table
    ]
    for pattern in blocked_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked by repo policy: matches dangerous pattern '{pattern}'"
                }
            }))
            sys.exit(0)

    # Block deprecated provider commands
    deprecated = [
        r"\bdoctl\b",                  # DigitalOcean CLI
        r"\bvercel\b",                 # Vercel CLI
        r"\bmailgun\b",               # Mailgun references
    ]
    for pattern in deprecated:
        if re.search(pattern, command, re.IGNORECASE):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked: deprecated provider tool '{pattern}'. Use Azure-native equivalent."
                }
            }))
            sys.exit(0)

# --- Write/Edit policy ---
if tool_name in ("Write", "Edit"):
    file_path = tool_input.get("file_path", "")

    # Block writing secrets files
    secret_patterns = [
        r"\.env$", r"\.env\.", r"credentials\.json", r"secrets/",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, file_path):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked: cannot write to secrets file '{file_path}'"
                }
            }))
            sys.exit(0)

    # Block modifying OCA source
    if "/addons/oca/" in file_path and "/ipai_" not in file_path:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Blocked: never modify OCA source directly. Create an ipai_* override module instead."
            }
        }))
        sys.exit(0)

# Allow by default
sys.exit(0)
