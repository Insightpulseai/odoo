# /repo.expert

## Intent

Route this request to the Repo Expert sub-agent.

## Context to load (repo SSOT)

- spec/\*_/_
- docs/\*_/_
- CODEOWNERS
- .agent/\*\*

## Output Contract (required)

1. Minimal patch/diff (files + exact sections)
2. One Agent Relay Template prompt (end-to-end, open PR)
3. Verification checklist (no commands unless explicitly requested)

## Repo Expert Operating Rules

- Spec Kit bundle is SSOT: spec/<slug>/{constitution,prd,plan,tasks}.md
- Prefer incremental edits; avoid repo-wide refactors without measurable payoff (DX/CI/boundaries).
- Treat "where things live" + ownership boundaries as first-class.
