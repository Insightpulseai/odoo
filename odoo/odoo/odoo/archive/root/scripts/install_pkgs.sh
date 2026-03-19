#!/bin/bash
# SessionStart hook for Claude Code cloud sessions
# Installs project dependencies when running on Anthropic cloud VMs
# Ref: https://code.claude.com/docs/en/claude-code-on-the-web#dependency-management

# Only run in remote/cloud environments
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

# Python dependencies
if [ -f requirements.txt ]; then
  pip install -r requirements.txt 2>/dev/null || true
fi

# Node.js dependencies
if [ -f package.json ]; then
  npm install 2>/dev/null || true
fi

exit 0
