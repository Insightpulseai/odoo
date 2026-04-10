# Evidence - Fully Merged Prod-Live Deployment Prompt

Stamp: `20260410-1503`
Scope: `odoo-delivery/odoo-staging-to-production-promotion`
Branch: `main`

## Change Executed

Replaced the prior short-form production promotion prompt with the fully merged prod-live deployment prompt at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md).

The canonical prompt now includes:
- Azure runtime reuse doctrine
- cloud-agent execution model
- Agent Skills discovery from `.github/skills/`, `.claude/skills/`, and `.agents/skills/`
- Foundry SDK / Azure AI Projects control-plane rules
- Codex config precedence, approvals, sandbox, environment forwarding, and MCP behavior
- Codex automations/worktree doctrine as secondary support tooling
- Azure reference-architecture doctrine constrained by repo SSOT and MVP scope

## Key Prompt Anchors

- Mission begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L5)
- Cloud-agent execution model begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L8)
- Foundry SDK control-plane rule begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L188)
- Codex runtime/config doctrine begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L233)
- Codex automations and worktree doctrine begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L295)
- Execution phases begin at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L429)
- Required final response format begins at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L574)

## Intent Preserved

- Odoo remains the sole business system of record.
- Foundry remains assistive and minimal.
- Existing Azure runtime surfaces are reused rather than replaced.
- Codex automations are explicitly secondary and cannot silently replace live release gates or human approvals.
- Azure reference architectures remain guidance, not scope-expansion authority.
