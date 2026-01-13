# Environment Model

## 1. Production Repo (Canonical Codebase)

- **Path:** `~/Documents/GitHub/odoo-ce`
- **Role:** Source-of-truth for all Odoo 18 CE + OCA + IPAI modules
- **Contains:**
  - Full git history
  - CI/CD workflows
  - All IPAI modules
  - Specs, docs, migrations
- **Rules:**
  - Only repo that pushes to GitHub
  - All code edits (Python, XML, manifests) happen here
  - Branching, PRs, and releases are managed here

## 2. Dev Sandbox (Runtime Only)

- **Path (inside repo):** `~/Documents/GitHub/odoo-ce/sandbox/dev`
- **Role:** Local Docker runtime for testing the `odoo-ce` codebase
- **Contains:**
  - `docker-compose.yml`
  - `config/odoo.conf`
  - Sandbox-specific README
- **Rules:**
  - No source code lives here (only mounts `../../addons`)
  - No git history (or kept out of main tree if needed)
  - Safe place to run migrations, test modules, validate UX

## Workflow Summary

- Edit code in `~/Documents/GitHub/odoo-ce`
- Run sandbox via Docker from `sandbox/dev`
- Once stable, commit + push from `odoo-ce` to GitHub
- Deploy production from GitHub (not from sandbox folders)

## Quick Commands

```bash
# Start sandbox
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose up -d

# Or use alias (after adding to ~/.zshrc)
odoo-sandbox

# View logs
docker compose logs -f odoo

# Stop sandbox
docker compose down
```

## Alias Setup

Add to `~/.zshrc`:

```bash
alias odoo-sandbox='cd ~/Documents/GitHub/odoo-ce/sandbox/dev && docker compose up -d && open http://localhost:8069/web/login'
```

Then reload:

```bash
source ~/.zshrc
```
