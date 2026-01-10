# AGENTS.md - OdooForge Agent Rules

This file defines invariants and rules for AI agents (Codex, Claude Code, etc.) working in this repository.

---

## Odoo 18 / OCA Invariants

### View Syntax (Odoo 18+)
- List views use `<list>`, NOT `<tree>` (deprecated in Odoo 17+)
- Actions use `view_mode="list,form"`, NOT `view_mode="tree,form"`
- Kanban views remain `<kanban>`
- Form views remain `<form>`

### Smart Delta Principle
- **NEVER modify Odoo core** - extend only via `_inherit`
- **NEVER copy OCA modules** - declare them as dependencies
- Keep custom modules under `addons/ipai_*` namespace only
- Prefer configuration over code when possible

### OCA Compliance
- No brittle xpaths - use `position="attributes"` with care
- Version format: `<odoo_version>.<major>.<minor>.<patch>` (e.g., `18.0.1.0.0`)
- License: `LGPL-3` for all custom modules
- Manifest must include: `name`, `version`, `depends`, `license`
- Module names: `ipai_<domain>_<feature>` pattern

### Python Standards
- Python 3.10+ syntax only
- Use type hints for public methods
- No `print()` statements - use `_logger.info()` etc.
- Imports: stdlib → third-party → odoo → local (isort compatible)

---

## PR Gate Commands

Run these before any PR submission:

```bash
# Full PR gate (same as CI)
./scripts/codex_check.sh

# Individual checks
kit validate --strict      # Module structure + manifest
kit test                   # Run Odoo tests
pre-commit run -a          # Linting (if enabled)
python -m py_compile *.py  # Syntax check
```

---

## Output Expectations

### On CI Failure
1. Identify the root cause from logs
2. Fix the issue in the source file
3. Add a regression test if applicable
4. Run `./scripts/codex_check.sh` locally before pushing

### On Code Review
1. Check OCA compliance (no core modifications)
2. Verify manifest completeness
3. Ensure tests exist for new functionality
4. Validate view XML syntax for Odoo 18

### Security
- No secrets committed - `.env` is always gitignored
- Use `odoo.tools.config` for configuration
- Sanitize user inputs in controllers
- Use ORM methods, never raw SQL unless absolutely necessary

---

## Kit CLI Commands (Agent Reference)

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `kit init <name>` | Create module | Starting new feature |
| `kit validate` | Check structure | Before commit |
| `kit validate --strict` | Full compliance | Before PR |
| `kit test` | Run tests | After changes |
| `kit build <name>` | Package module | For deployment |
| `kit list` | Show modules | Discovery |
| `kit status` | Environment check | Debugging |

---

## Module Naming Convention

```
ipai_<domain>_<feature>

Domains:
- ai        : AI/ML features (ipai_ai_agents, ipai_ai_prompts)
- finance   : Financial modules (ipai_finance_ppm, ipai_finance_bir)
- platform  : Core platform (ipai_platform_workflow)
- workspace : Workspace features (ipai_workspace_core)
- web       : UI/UX modules (ipai_web_dashboard)
```

---

## File Structure (Expected)

```
addons/ipai_<module>/
├── __init__.py           # Required
├── __manifest__.py       # Required (OCA-compliant)
├── README.md             # Recommended
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── security/
│   └── ir.model.access.csv
├── data/                 # Optional
├── static/description/   # Optional (for icon)
└── tests/
    ├── __init__.py
    └── test_<module>.py
```

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ODOO_HOST` | `odoo` | Odoo service hostname |
| `ODOO_PORT` | `8069` | Odoo HTTP port |
| `DB_HOST` | `db` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `odoo` | Database user |
| `DB_PASSWORD` | `odoo` | Database password |
| `DB_NAME` | `odoo` | Database name |

---

## Agent Interaction Patterns

### For Codex / Claude Code Reviews
- Mention `@codex` or use `/review` for code review
- Expect OCA-compliant suggestions
- Auto-fix will respect Smart Delta principle

### For Module Generation
- Use `kit init ipai_<name>` to scaffold
- Provide spec in `specs/<module>/` directory
- Reference existing modules as patterns

### For Testing
- Run `kit test` after any model changes
- Add test cases for new business logic
- Use `TransactionCase` for most tests

---

*This file is read by AI agents before processing any task in this repository.*
