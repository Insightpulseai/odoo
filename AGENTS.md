# AGENTS.md — Copilot Coding Agent Instructions

## Repo Topology

```
vendor/odoo/          Upstream Odoo 18 CE (read-only)
addons/ipai/          Custom IPAI modules
addons/oca/           OCA repos (read-only submodules)
addons/local/         Local-only addons
config/dev/           Dev odoo.conf
config/prod/          Prod odoo.conf
config/azure/         ACA odoo.conf
docker/               Dockerfiles, entrypoint, compose
docs/architecture/    Build specs, topology docs
```

## Canonical Addon Paths

- CE core: `vendor/odoo/addons/` (never modify)
- OCA: `addons/oca/<repo>/` (never modify, override via `ipai_*`)
- IPAI custom: `addons/ipai/ipai_<domain>_<feature>/`
- Local: `addons/local/` (dev-only, not in prod image)

## Build / Test / Update

```bash
# Install a module
odoo -d odoo_dev -i <module> --stop-after-init --no-http

# Update a module
odoo -d odoo_dev -u <module> --stop-after-init --no-http

# Run module tests
odoo -d test_<module> -i <module> --test-enable --stop-after-init --no-http

# Docker build (prod)
docker build -f docker/Dockerfile.prod -t ipai-odoo:18.0-rc .

# Docker local stack
docker --context colima-odoo compose -f docker-compose.odoo.local.yml up -d
```

## Decision Rules

### Before writing any code

1. Can CE configuration solve this? → Configure, do not code
2. Does an OCA 18.0 module exist? → Install it, do not rewrite
3. Does an existing `ipai_*` module handle this? → Extend it
4. Only then: create a new `ipai_<domain>_<feature>` addon

### Never do this

- Modify files in `vendor/odoo/` or `addons/oca/`
- Add Enterprise module dependencies
- Hardcode secrets, passwords, or API keys
- Replace upstream views (use xpath inheritance)
- Skip tests for behavior changes
- Use `sudo()` for user-facing actions
- Create fat custom modules (AI/RAG/OCR logic belongs outside Odoo)
- Reference deprecated items: Supabase, Vercel, Mailgun, DigitalOcean, `insightpulseai.net`

### When uncertain

- Read the module's `__manifest__.py` and existing models before proposing changes
- Check `docs/architecture/ODOO_IMAGE_BUILD_SPEC.md` for module classification
- Check if the OCA repo has the module at 18.0 branch before suggesting it
- State assumptions explicitly in PR description

## Skills

Invoke the matching skill by task domain:

| Domain | Skill |
|--------|-------|
| Module structure, manifests, scaffold | `.github/skills/odoo-module-architecture/SKILL.md` |
| Models, fields, ORM, compute, inheritance | `.github/skills/odoo-orm/SKILL.md` |
| Views, menus, actions, cron | `.github/skills/odoo-views-actions/SKILL.md` |
| ACLs, record rules, field access | `.github/skills/odoo-security/SKILL.md` |
| Python tests, JS tests, smoke tests | `.github/skills/odoo-testing/SKILL.md` |
| Controllers, assets, Owl, JS modules | `.github/skills/odoo-web-framework/SKILL.md` |
| Version migration, porting, deprecation | `.github/skills/odoo-upgrades/SKILL.md` |
| XML-RPC, JSON-RPC, external integrations | `.github/skills/odoo-external-api/SKILL.md` |

## Output Contract

Every code-changing task must produce:
1. Minimal targeted diff
2. Module install verification (`--stop-after-init` exits 0)
3. Test evidence (new or updated tests pass)
4. PR with summary identifying: which lane (CE/OCA/config/custom), what changed, why
