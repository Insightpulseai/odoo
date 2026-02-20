# Root Allowlist

> **SSOT**: `.github/workflows/root-allowlist-guard.yml` is the enforcing source.
> This document explains *why* each entry is allowed.

## Policy

The repository root contains only files required by tooling conventions or GitHub.
All other files belong in canonical sub-directories (`docs/`, `config/`, `scripts/`, etc.).

The CI workflow `.github/workflows/root-allowlist-guard.yml` fails PRs that introduce
new root files outside this allowlist.

---

## Allowed Root Files

### GitHub / Community Health (GitHub convention)
| File | Reason |
|------|--------|
| `README.md` | GitHub convention |
| `CHANGELOG.md` | GitHub convention |
| `CONTRIBUTING.md` | GitHub `/.github/` or root convention |
| `SECURITY.md` | GitHub security policy |
| `AGENTS.md` | AI agent discovery standard |
| `CLAUDE.md` | Claude Code agent instructions |
| `GEMINI.md` | Gemini AI agent instructions |

### Node Tooling (required at root)
| File | Reason |
|------|--------|
| `package.json` | npm/pnpm workspace root |
| `pnpm-lock.yaml` | pnpm lockfile |
| `pnpm-workspace.yaml` | pnpm workspace config |
| `turbo.json` | Turborepo config |

### Python Tooling (required at root)
| File | Reason |
|------|--------|
| `pyproject.toml` | PEP 517/518 build config |
| `requirements.txt` | pip conventions |
| `requirements-dev.txt` | pip dev dependencies |
| `requirements-docs.txt` | docs build deps |
| `requirements-oca.txt` | OCA-specific deps |
| `.python-version` | pyenv/uv version pin |
| `.mypy-baseline.txt` | mypy suppression baseline |

### Linting / Quality
| File | Reason |
|------|--------|
| `.flake8` | flake8 expects root |
| `.markdownlint-cli2.jsonc` | markdownlint config |
| `.pre-commit-config.yaml` | pre-commit hooks |
| `.yamllint.yml` | yamllint config |
| `.cursorignore` | Cursor IDE ignore |
| `.agentignore` | AI agent ignore |

### Git
| File | Reason |
|------|--------|
| `.gitignore` | Git convention |
| `.gitmodules` | Git submodules |
| `.gitattributes` | Git attributes |

### Docker / Infrastructure
| File | Reason |
|------|--------|
| `Dockerfile` | Docker convention |
| `docker-compose.yml` | Docker Compose convention |
| `docker-compose.dev.yml` | Docker dev override |

### Build / Docs
| File | Reason |
|------|--------|
| `Makefile` | Make convention |
| `mkdocs.yml` | MkDocs expects root |
| `vercel.json` | Vercel deployment config |
| `odoo-bin` | Odoo entry point |
| `odoo.code-workspace` | VS Code workspace |

### OCA Tooling (hardcoded ROOT_DIR)
| File | Reason |
|------|--------|
| `oca-aggregate.yml` | `gitaggregate` expects root; `scripts/validate_oca_aggregate_output.py` hardcodes `ROOT_DIR / "oca-aggregate.yml"` |
| `oca.lock.json` | CI workflows (`build-odoo-ce19-ee-parity.yml`, `validate-addons-mounts.yml`) reference root |

### Odoo Manifest
| File | Reason |
|------|--------|
| `addons.manifest.json` | `.github/workflows/validate-addons-mounts.yml` and `scripts/verify-addons-mounts.sh` expect root |

### LLM Discovery
| File | Reason |
|------|--------|
| `llms.txt` | `llms.txt` standard; `.github/workflows/llms-txt-check.yml` checks root |
| `llms-full.txt` | Extended llms.txt; same CI check |

---

## Moved Files (root → canonical)

Moved as part of `chore(repo): root cleanup` — see `reports/repo_hygiene/root_file_moves_2026-02-17.json`.

| Old path | New path | Reason |
|----------|----------|--------|
| `COLIMA_SETUP_COMPLETE.md` | `docs/guides/COLIMA_SETUP_COMPLETE.md` | Setup guide, not a root convention |
| `branch_protection.json` | `docs/architecture/branch_protection.json` | Architecture doc, not tooling |
| `devserver.config.json` | `config/devserver.config.json` | Tool config, not a root convention |
| `superclaude_bridge.yaml` | `.claude/superclaude_bridge.yaml` | Claude tooling, belongs in `.claude/` |
| `aiux_ship_manifest.yml` | `config/aiux_ship_manifest.yml` | App config, not a root convention |
| `.env.production` | *(removed from git)* | Duplicate of `.env.prod`; contained hardcoded credentials |

---

## Requesting Allowlist Additions

1. Create PR with the new root file
2. Add justification (why it *must* be at root)
3. Update `ALLOWED` in `.github/workflows/root-allowlist-guard.yml`
4. Update this doc
5. PR reviewer must approve both the file and the allowlist change
