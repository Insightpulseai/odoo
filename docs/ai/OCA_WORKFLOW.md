# OCA-Style Workflow (Canonical)
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Purpose

Keep this repo aligned with **OCA tooling + conventions** while preserving the existing layered architecture:
- **Odoo CE runtime**
- **OCA addons** (managed via `oca.lock.json`, not tracked)
- **IPAI addons** (tracked, ship-ready)

## Non-Negotiables

- **Do NOT run** `copier` in the repo root (it will overwrite structure).
- Use `/tmp/oca-template/` to generate templates and **selectively port** only the needed files.
- New custom modules live under: `addons/ipai/<module_name>/`
- OCA repos cloned under: `addons/oca/*/` are **NOT tracked** (only keep base marker files per `.gitignore`).
- Changes must remain deterministic and CI-friendly (no "works on my machine" steps).

## Standard Tooling (Must Stay Green)

### Pre-commit

Install + run:

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run -a
```

### Local verification (mirror CI)

Run:

```bash
./scripts/verify_local.sh
```

## Using OCA Template Safely (Selective Port Only)

### Generate OCA template in a temp directory

```bash
rm -rf /tmp/oca-template && mkdir -p /tmp/oca-template
cd /tmp/oca-template
pipx install copier || true
copier copy https://github.com/OCA/oca-addons-repo-template.git/ repo --trust
```

### Allowed files to port (only if beneficial)

* `.pre-commit-config.yaml` (rules/tools)
* `pyproject.toml` (lint/format defaults)
* targeted `.github/workflows/*` patterns (lint/test hygiene)

### Forbidden

* Overwriting repo layout
* Introducing a second "root" structure
* Moving existing directories to match the template

## Fast Module Scaffolding (mrbob)

### Install

```bash
pipx install mrbob
pipx inject mrbob bobtemplates.odoo
```

### Create addon (then move under addons/ipai/)

```bash
mrbob bobtemplates.odoo:addon
# move generated module into addons/ipai/<module_name>/
```

### Create model scaffolding inside addon

```bash
mrbob bobtemplates.odoo:model
```

## Commit Rules (OCA-style)

* Use conventional commits: `chore(oca): ...`, `feat(ipai_*): ...`, `fix(ci): ...`
* One feature = one commit whenever possible.
* Always include proof commands (logs/status) after changes that affect runtime or CI.
