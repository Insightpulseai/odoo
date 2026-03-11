#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

OUT = Path("docs/evidence/20260210-1147/phase6-agent-library/VERIFICATION_SUMMARY.md")
OUT.parent.mkdir(parents=True, exist_ok=True)

content = f"""# Phase 6 Agent Library Wireup - VERIFICATION SUMMARY

Generated: {datetime.utcnow().isoformat()}Z

## ✅ DEPLOYED
- Commit: c80e5562
- Branch: main
- Status: pushed to origin/main

## What Was Created
- Supabase migration: 10 agent definitions + 3 flows (conflict-safe seeds)
- TypeScript SDK: typed AgentFlows/AgentNames exports
- Python SDK: Literal types exports
- Odoo: ipai.ai.agent_library convenience wrapper

## Notes
- Prior shell heredoc failed with: unmatched backtick (`) — this file replaces that generator.
- TypeScript SDK has pre-existing type errors in client.ts (unrelated to agent library).
"""
OUT.write_text(content, encoding="utf-8")
print(f"Wrote {OUT}")
