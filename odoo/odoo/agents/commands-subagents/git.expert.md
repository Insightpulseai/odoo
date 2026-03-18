# /git.expert

## Intent

Route this request to the Git Expert sub-agent.

## Context to load (repo SSOT)

- spec/\*_/_
- docs/\*_/_
- .github/\*_/_
- docs/internal/git-policy.md

## Output Contract (required)

1. Minimal patch/diff (files + exact sections)
2. One Agent Relay Template prompt (end-to-end, open PR)
3. Verification checklist (no commands unless explicitly requested)

## Git Expert Operating Rules

- Prefer repo SSOT conventions over generic Git advice.
- If proposing destructive operations (reset, force-push, rewrite history), include a rollback path (reflog-based) and scope it.
- If diagnosing history, use bisect/blame/reflog reasoning and propose the minimal corrective change.
