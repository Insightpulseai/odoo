# Relocation Map: Non-Odoo Directories

> **Purpose**: This document maps all directories in the `odoo` repo that do NOT belong
> to the canonical Odoo runtime boundary. These should eventually be relocated to
> dedicated repositories.
>
> **Status**: Documentation only — no moves executed. This map guides future repo splits.
>
> **Date**: 2026-03-10

---

## Canonical Odoo Repo Boundary

The following directories are **canonical** and remain in this repo:

| Directory | Purpose |
|-----------|---------|
| `addons/` | Custom modules (ipai/, local/, oca/) |
| `config/` | Odoo configuration files |
| `docker/` | Docker build files |
| `docs/` | Documentation (consolidated) |
| `scripts/` | Execution scripts |
| `spec/` | Spec bundles |
| `ssot/` | Runtime SSOT configs |
| `tests/` | Test infrastructure |
| `.claude/` | Claude Code agent config |
| `.devcontainer/` | Dev container config |
| `.github/` | CI/CD workflows |
| `.vscode/` | Editor config |

---

## Relocation Map

### Priority 0 — Delete (No Data Value)

| Current Path | Size | Tracked | Action | Reason |
|-------------|------|---------|--------|--------|
| `sandbox/` | 611M | 0 | DELETE | Local dev scratch (gitignored) |
| `odoo/` | 910M | 5 | CLEAN | Runtime artifacts, untracked content; 5 tracked files relocate to `docs/` or `spec/` |

### Priority 1 — High (Large, Active, Clear Target)

| Current Path | Target Repo | Size | Tracked | Notes |
|-------------|-------------|------|---------|-------|
| `web/` | `web` or `platform` | 3.6G | 1105 | Next.js public website, largest non-Odoo content |
| `templates/` | `templates` or delete | 938M | 4402 | Template projects (odooops-console, saas-landing, etc.) |
| `infra/` | `infra` | 1.4G | 500 | Infrastructure scripts, Terraform, Docker stacks |
| `ops-platform/` | `ops-platform` | 794M | 0 | Ops platform (untracked) |

### Priority 2 — Medium (Smaller, Active)

| Current Path | Target Repo | Size | Tracked | Notes |
|-------------|-------------|------|---------|-------|
| `agents/` | `agents` | 1.2M | 203 | Agent definitions, prompts, configs |
| `skills/` | `agents` | 80K | 172 | Agent skill definitions |
| `ops/` | `ops-platform` | 24K | 38 | Ops tooling (secrets, scripts) |
| `supabase/` | `supabase` or `platform` | 100K | 410 | Supabase edge functions, migrations |
| `automations/` | `automations` | 20K | 75 | n8n workflows, automation configs |
| `workflows/` | `automations` | 8K | 23 | Additional workflow definitions |
| `mcp/` | `mcp` or `platform` | 20K | 4 | MCP server configs |
| `lakehouse/` | `analytics` | 8.2M | 0 | Lakehouse/data platform (untracked) |

### Priority 3 — Low (Small, Infrequent)

| Current Path | Target Repo | Size | Tracked | Notes |
|-------------|-------------|------|---------|-------|
| `apps/` | `apps` | 12K | 374 | App manifests/metadata |
| `marketplace/` | `apps` | 88K | 21 | Marketplace listings |
| `data/` | Module data dirs or delete | 36K | 44 | Seed/reference data |
| `runtime/` | `platform` | 8K | 21 | Runtime config fragments |
| `vendor/` | Remove (use package mgr) | 12K | 7 | Vendored dependencies |
| `pipelines/` | `infra` or `ci` | 12K | 1 | Pipeline definitions |
| `compose/` | `docker/` (merge) | 4K | 0 | Docker compose fragments (untracked) |
| `archive/` | Delete after review | 4K | 563 | Historical artifacts |
| `evidence/` | `docs/evidence/` (merge) | 0B | 1 | Audit evidence (mostly empty) |

---

## Dependency Notes

- `web/` depends on `supabase/` edge functions for API calls
- `agents/` and `skills/` are tightly coupled — relocate together
- `automations/` and `workflows/` both contain n8n configs — merge before relocating
- `ops/` and `ops-platform/` overlap — consolidate into single `ops-platform` repo
- `infra/` contains Terraform state references — verify no hardcoded paths before moving
- `templates/` may reference `addons/` module structures — update template paths after split

## Execution Strategy

1. **Create target repos** on GitHub (empty, with CLAUDE.md)
2. **Extract with history**: Use `git filter-repo` or `git subtree split` to preserve commit history
3. **Update CI**: Add cross-repo references in GitHub Actions
4. **Update imports**: Search for inter-directory imports/references
5. **Remove from odoo repo**: Delete relocated directories, update `.gitignore`
6. **Verify**: Ensure Odoo runtime still functions without relocated content

---

## Post-Relocation Target Tree

After all relocations, the `odoo` repo should contain only:

```
odoo/
├── .claude/
├── .devcontainer/
├── .github/
├── .vscode/
├── addons/
│   ├── ipai/          # ~107 custom modules
│   ├── local/         # Local development modules
│   └── oca/           # OCA repos
├── config/            # Odoo configuration
├── docker/            # Docker files
├── docs/              # ~36 subdirs (consolidated)
├── scripts/           # Execution scripts
├── spec/              # Spec bundles
├── ssot/              # Runtime SSOT configs
├── tests/             # Test infrastructure
├── docker-compose.yml
├── requirements.txt
├── CLAUDE.md
└── README.md
```

---

*Generated: 2026-03-10 | Co-Authored-By: Claude Opus 4.6*
