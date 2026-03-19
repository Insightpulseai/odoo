#!/usr/bin/env python3
"""PreToolUse hook: block dangerous Bash commands."""
import json
import re
import sys


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = event.get("tool_name", "")
    if tool_name != "Bash":
        return

    tool_input = event.get("tool_input", {})
    command = tool_input.get("command", "")

    blocked_patterns = [
        (r"\brm\s+-rf\s+[/~]", "rm -rf targeting root or home"),
        (r"\bsudo\b", "sudo usage"),
        (r"\bgit\s+push\s+--force\b.*\b(main|master)\b", "force push to main/master"),
        (r"\bgit\s+push\s+-f\b.*\b(main|master)\b", "force push to main/master"),
        (r"\bdocker\s+system\s+prune\s+-a\b", "docker system prune -a"),
    ]

    for pattern, reason in blocked_patterns:
        if re.search(pattern, command):
            result = {
                "decision": "block",
                "reason": f"Blocked: {reason}",
            }
            print(json.dumps(result))
            return

    # Allow everything else
    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
