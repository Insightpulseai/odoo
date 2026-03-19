# Constitution — VS Code Local Dev Environment

## Non-negotiable rules

1. Repo-scoped settings override user-global drift
2. No hardcoded absolute user-specific paths (no `/Users/tbwa/...`)
3. No mixed addon path casing — only `addons/oca`, `addons/ipai`, `addons/local`
4. No explicit `python.languageServer` disablement without documented reason
5. Canonical Docker context is `colima-odoo`
6. Python 3.11+ for Odoo runtime
7. Ruff-based formatting/linting (not black+isort separately)
8. Root workspace provides safe baseline; odoo workspace provides Odoo-specific intelligence
9. Nested workspaces only override what they truly own
10. Agent factory workspaces are first-class for YAML/Markdown/template/eval editing
