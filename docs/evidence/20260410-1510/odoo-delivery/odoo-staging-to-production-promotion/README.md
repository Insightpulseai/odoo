# Evidence - Codex Advanced Config and Observability Prompt Update

Stamp: `20260410-1510`
Scope: `odoo-delivery/odoo-staging-to-production-promotion`
Branch: `main`

## Change Executed

Appended a `Codex advanced configuration and observability doctrine` block to the canonical prod-live deployment prompt at [prompt.md](/Users/tbwa/Documents/GitHub/Insightpulseai/agents/skills/odoo-staging-to-production-promotion/prompt.md#L376).

The new block adds explicit doctrine for:
- project-instructions discovery via `AGENTS.md`, skill directories, and fallback filenames
- customized `project_root_markers`
- provider/profile/override handling
- approval and sandbox hardening
- OTel/log/history/notification handling as release-evidence support only
- clickable citations and verbosity controls as operator convenience only

## Intent Preserved

- Repo-local project instructions remain authoritative for deployment doctrine.
- Advanced Codex config can shape execution behavior but cannot redefine MVP scope or release architecture.
- Telemetry, history, notifications, and clickable citations support evidence gathering and operator awareness only.
- Risky actions, rollback requirements, and release evidence requirements remain unchanged.
