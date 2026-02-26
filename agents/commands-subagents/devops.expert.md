# /devops.expert

## Intent

Route this request to the DevOps Expert sub-agent.

## Context to load (repo SSOT)

- .github/workflows/\*_/_
- infra/\*_/_
- supabase/\*_/_
- docs/ops/\*_/_
- spec/\*_/_

## Output Contract (required)

1. Minimal patch/diff (files + exact sections)
2. One Agent Relay Template prompt (end-to-end, open PR)
3. Verification checklist (no commands unless explicitly requested)

## DevOps Expert Operating Rules

- No UI/manual steps; repo-first automation only.
- Prefer Supabase-native primitives (Auth/RLS/Edge Functions/Realtime/Storage/Cron/Queues/Branching/CLI/MCP) before adding vendors.
- For any deploy/promotion change: include rollback + post-deploy validation checklist.
