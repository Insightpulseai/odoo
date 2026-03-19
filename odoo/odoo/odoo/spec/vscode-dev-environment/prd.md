# PRD — VS Code Local Dev Environment

## Objective

Create a deterministic, repo-scoped, high-signal local developer environment in VS Code optimized for: Odoo engineering, agent factory design, Foundry/Databricks/Azure integration, spec-driven implementation, and agentic DevOps.

## Target capabilities

### A. Python / Odoo developer experience
- Repo-local interpreter resolution
- Working IntelliSense across Odoo core + addons/oca + addons/ipai
- Ruff-based formatting/linting
- Test/debug readiness for Odoo CLI

### B. TypeScript / web developer experience
- Correct TypeScript SDK path
- ESLint/Prettier support
- Good frontend isolation for nested web workspaces

### C. Docker / runtime targeting
- Deterministic Docker context (colima-odoo)
- Alignment with devcontainer runtime
- No editor config that mutates global Docker context

### D. Agent factory workflows
- Strong YAML/JSON/Markdown/prompt template editing
- MCP-aware workspace ergonomics
- Support for personas, skills, judges, evals, templates, agent contracts

### E. Agentic SDLC / DevOps
- Easy editing of GitHub Actions, Azure Pipelines, Odoo manifests, Supabase config
- Task/debug scaffolding for preflight, tests, verify, Odoo run
- Clean spec-driven workflow support

### F. Performance
- Watcher/search excludes for large monorepo
- No duplicated/conflicting nested settings
- Fast IntelliSense on 80+ top-level dirs

## Files in scope
- `.vscode/settings.json` (root)
- `.vscode/extensions.json` (root)
- `odoo/.vscode/settings.json`
- `.devcontainer/devcontainer.json`

## Deliverables
1. Target capability matrix
2. Minimal patch set
3. Recommended workspace model
4. Validation checklist
