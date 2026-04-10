# Evidence — Codex Doctrine Prompt Update

Stamp: `20260410-1457`
Scope: `odoo-delivery/odoo-staging-to-production-promotion`
Branch: `main`

## Change Executed

Appended two Codex-specific doctrine sections to the production promotion prompt at [agents/skills/odoo-staging-to-production-promotion/prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md):

- `Codex runtime/config doctrine`
- `Codex automations and worktree doctrine`

The automation/worktree doctrine is explicitly framed as a secondary execution pattern. The prompt now keeps live production release steps human-accountable and forbids treating Codex automations as the default prod rollout driver.

## Affected Prompt Sections

- Runtime/config doctrine begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L46)
- Automations/worktree doctrine begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L119)
- Human-accountable final safety rule ends at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L207)

## Intent Preserved

- Repo SSOT and release doctrine remain authoritative for rollout scope.
- Codex config is treated as an execution constraint.
- Codex automations are limited to bounded support tasks such as evidence collection and non-destructive verification.
- Destructive, finance-sensitive, tax-sensitive, and approval-sensitive rollout actions remain gated by human approval and explicit release controls.
