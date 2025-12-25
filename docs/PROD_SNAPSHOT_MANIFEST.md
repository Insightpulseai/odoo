# Production Snapshot Manifest

> **Note**: Repo artifacts are generated locally. Runtime artifacts are **placeholders** that must be regenerated on the production server.

## Quick Start (On Production)

```bash
ssh deploy@erp.insightpulseai.net
cd /opt/odoo-ce
git pull origin claude/notion-clone-odoo-module-LSFan
./tools/audit/gen_prod_snapshot.sh
```

## Artifacts

### Repo Artifacts (Generated Locally)

| File | Description | Status |
|------|-------------|--------|
| `docs/repo/GIT_STATE.prod.txt` | Git SHA, branch, status | ✅ Generated |
| `docs/repo/REPO_TREE.prod.md` | Directory structure | ✅ Generated |
| `docs/repo/REPO_SNAPSHOT.prod.json` | File counts, module versions | ✅ Generated |

### Runtime Artifacts (Require Production)

| File | Description | Status |
|------|-------------|--------|
| `docs/runtime/ODOO_MENU_SITEMAP.prod.json` | Odoo UI menus and actions | ⏳ Placeholder |
| `docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json` | Installed models | ⏳ Placeholder |
| `docs/runtime/MODULE_STATES.prod.csv` | Module installation states | ⏳ Placeholder |
| `docs/runtime/ADDONS_PATH.prod.txt` | Odoo addons path config | ⏳ Placeholder |
| `docs/runtime/CONTAINER_PATH_CHECK.prod.txt` | Container path verification | ⏳ Placeholder |
| `docs/runtime/HTTP_SITEMAP.prod.json` | Public HTTP endpoints | ⏳ Placeholder |

## Tooling

| Script | Purpose |
|--------|---------|
| `tools/audit/gen_prod_snapshot.sh` | Master script - runs all generators |
| `tools/audit/gen_repo_tree_prod.sh` | Generates repo tree artifacts |
| `tools/audit/gen_runtime_sitemap.sh` | Extracts Odoo DB data |
| `tools/audit/http_crawler.py` | Crawls HTTP endpoints |

## Environment Variables

```bash
export COMPOSE_FILE=deploy/docker-compose.prod.yml
export COMPOSE_OVERRIDE=deploy/docker-compose.workos-deploy.yml
export DB_SERVICE=db
export DB_NAME=odoo
export DB_USER=odoo
export ODOO_SERVICE=odoo
export BASE_URL=https://erp.insightpulseai.net
```

## Verification Checklist

After running on production, verify:

- [ ] `docs/repo/GIT_STATE.prod.txt` shows correct SHA
- [ ] `docs/runtime/MODULE_STATES.prod.csv` shows `ipai_workos_*` as `installed`
- [ ] `docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json` contains `ipai.workos.*` models
- [ ] `docs/runtime/HTTP_SITEMAP.prod.json` shows `/web/login` with status 200

## Regeneration

```bash
# Full regeneration
./tools/audit/gen_prod_snapshot.sh

# Repo only
./tools/audit/gen_repo_tree_prod.sh

# Runtime only
./tools/audit/gen_runtime_sitemap.sh

# HTTP only
python3 tools/audit/http_crawler.py https://erp.insightpulseai.net docs/runtime/HTTP_SITEMAP.prod.json
```
