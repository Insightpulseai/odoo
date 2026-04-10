# Verification - Fully Merged Prod-Live Deployment Prompt

## Deterministic Checks

1. Replaced the canonical prompt file at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md).
2. Verified presence of the major merged sections with `rg`.
3. Verified exact line anchors with `nl -ba`.
4. Verified diff size and scope with `git diff --stat`.

## Section Presence Results

- `3:You are the cloud deployment agent for InsightPulseAI.`
- `8:Cloud-agent execution model`
- `188:Foundry SDK control-plane rule`
- `233:Codex runtime/config doctrine`
- `295:Codex automations and worktree doctrine`
- `429:Execution phases`
- `574:Required final response format`

## Diff Summary

- `agents/skills/odoo-staging-to-production-promotion/prompt.md | 581 insertions, 44 deletions`
- Full prompt replacement completed in the canonical production promotion skill prompt.

## Verification Verdict

PASS
