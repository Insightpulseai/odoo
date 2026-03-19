# AI-first development

InsightPulse AI uses AI agents as first-class development participants. Every code change, deployment, and migration follows the agent workflow:

```
explore → plan → implement → verify → commit
```

Agents operate under strict contracts defined in `CLAUDE.md` and `.claude/rules/`. They execute deterministically, produce evidence, and never ship unverified work.

## What this means in practice

- **No manual guides** — agents execute changes directly
- **Evidence-based** — every action produces verifiable proof
- **Spec-driven** — significant features require spec bundles before implementation
- **Quality-gated** — verification scripts run before every commit

## In this section

| Page | Description |
|------|-------------|
| [Agent workflow](agent-workflow.md) | The mandatory explore→plan→implement→verify→commit cycle |
| [Spec-kit methodology](spec-kit.md) | How spec bundles govern feature development |
| [Claude Code integration](claude-code.md) | Agent instructions, rules, and operating contracts |
| [MCP servers](mcp-servers.md) | Model Context Protocol server architecture |
| [AI modules](ai-modules.md) | Odoo modules for AI/agent capabilities |
