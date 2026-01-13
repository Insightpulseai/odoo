# Prod Baseline Policy (Odoo 18 CE + OCA)

## Core Principles

- **Sandbox is the canonical baseline for prod**
- **Prefer inheritance + seed scripts over custom modules**
- Any existing custom modules should be downgraded to data/import/config assets when feasible
- **Truth source for "what to install" is deterministic repo scan**:
  - addon manifests (`__manifest__.py`)
  - seed scripts (`data/seed/*.py`, `data/finance_seed/*.py`)
  - compose config (`docker-compose.yml` / `compose.yaml`)
- **No narrative acceptance. Only CLI verifiable acceptance gates**

## Verification Process

All production deployments must pass deterministic verification:

```bash
# 1. Generate current baseline
python3 tools/generate_prod_canonical_requirements.py

# 2. Review generated artifacts
cat docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.md
cat docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.json

# 3. Verify Docker containers
docker ps | grep odoo

# 4. Test database connectivity
docker exec odoo-core odoo shell -d odoo_core --stop-after-init

# 5. Run seed scripts (if any)
# See PROD_CANONICAL_INSTALL_REQUIREMENTS.md for specific commands
```

## Container Architecture (Verified)

From actual docker ps scan:

- `odoo-core` → port 8069 (main instance, db: odoo_core)
- `odoo-dev` → port 9069 (development, db: odoo_dev)
- `odoo-marketing` → port 8070 (marketing edition, db: odoo_marketing)
- `odoo-accounting` → port 8071 (accounting edition, db: odoo_accounting)

## Module Installation Order

1. **Base Odoo CE 18.0** (from official image)
2. **OCA Foundation modules** (from dependencies scan)
3. **IPAI Custom modules** (321 modules detected from manifests)

## Acceptance Gates

Before marking any deployment as "production ready":

- ✅ All manifests parse without errors
- ✅ All dependencies resolve to existing modules
- ✅ Docker compose up succeeds
- ✅ All containers healthy
- ✅ Database migrations complete
- ✅ Seed scripts execute without errors
- ✅ No Enterprise-only modules detected (heuristic scan)
- ✅ Generated requirements.md + requirements.json committed to repo

## Regeneration Schedule

Run baseline generator:
- Before each production deployment
- After adding/removing custom modules
- After modifying seed scripts
- Weekly as part of CI/CD health check

## CI Integration

Add to `.github/workflows/`:

```yaml
- name: Generate Prod Baseline
  run: python3 tools/generate_prod_canonical_requirements.py

- name: Verify No Changes
  run: git diff --exit-code docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.*
```

Fails if generated files differ from committed versions (indicates undocumented changes).
