# Tasks — Agent-Ready CMS Implementation

## Completed ✅

### Phase 1: Agent-Ready Docs Scaffold
- [x] Create `docs/` directory structure (12 folders)
- [x] Create `docs/README.md` index
- [x] Create folder README.md stubs (11 files)
- [x] Create root `CLAUDE.md` agent contract
- [x] Create `scripts/scaffold_agent_docs.sh` (idempotent)
- [x] Create `.github/workflows/agent-docs-guard.yml` CI workflow

### Phase 2: Odoo CMS Theme Template
- [x] Create `templates/odoo-cms-copilot/` structure
- [x] Create `__manifest__.py` with tokens
- [x] Create `__init__.py`
- [x] Create `static/src/scss/theme.scss` (design tokens)
- [x] Create `static/src/scss/components.scss` (component styles)
- [x] Create `static/src/scss/animations.scss` (keyframes)
- [x] Create `static/src/js/motion.js` (IntersectionObserver)
- [x] Create `static/src/js/lottie_loader.js` (CDN loader)
- [x] Create `static/src/js/rive_loader.js` (CDN loader)
- [x] Create `views/assets.xml`
- [x] Create `views/snippets.xml` (5 CMS snippets)
- [x] Create `views/pages.xml` (page templates)
- [x] Create `README.md` usage guide

### Phase 3: Factory Integration
- [x] Create `scripts/new_odoo_cms_theme.sh` generator
- [x] Update `scripts/factory.sh` with new templates
- [x] Update `templates/catalog.yaml` with entries

### Phase 4: Org-Wide Rollout
- [x] Create `scripts/rollout_agent_docs.sh`

### Phase 5: Documentation
- [x] Create `odoo/specs/agent-ready-cms/constitution.md`
- [x] Create `odoo/specs/agent-ready-cms/prd.md`
- [x] Create `odoo/specs/agent-ready-cms/tasks.md`

## Pending 🔄

### Testing
- [ ] Test scaffold script (idempotent run)
- [ ] Test theme generator (create test module)
- [ ] Verify theme installs in Odoo 19
- [ ] Test snippets in Website Builder
- [ ] Validate animation behavior
- [ ] Test `prefers-reduced-motion`
- [ ] Run CI guard workflow

### Org Rollout (When Ready)
- [ ] Run dry-run: `./scripts/rollout_agent_docs.sh --dry-run`
- [ ] Review generated PRs
- [ ] Execute actual rollout
- [ ] Monitor PRs and merge compliant ones

---

## Verification Commands

```bash
# 1. Verify scaffold creates structure
./scripts/scaffold_agent_docs.sh
test -f CLAUDE.md && test -f docs/README.md && echo "✅ Scaffold OK"

# 2. Count docs folders
find docs -maxdepth 2 -name README.md | wc -l  # Should be 12+

# 3. Generate test theme
./scripts/new_odoo_cms_theme.sh --name "Test Theme" --dest /tmp/odoo-test

# 4. Verify theme structure
test -f /tmp/odoo-test/test_theme/__manifest__.py && echo "✅ Theme OK"

# 5. Factory list
./scripts/factory.sh list  # Should show odoo-cms-copilot

# 6. Rollout dry-run
./scripts/rollout_agent_docs.sh --dry-run
```

---

## Files Created

| File | Type | Purpose |
|------|------|---------|
| `/CLAUDE.md` | Markdown | Agent contract |
| `/docs/README.md` | Markdown | Docs index |
| `/docs/*/README.md` (11) | Markdown | Folder stubs |
| `/.github/workflows/agent-docs-guard.yml` | YAML | CI guard |
| `/scripts/scaffold_agent_docs.sh` | Shell | Scaffold generator |
| `/scripts/new_odoo_cms_theme.sh` | Shell | Theme generator |
| `/scripts/rollout_agent_docs.sh` | Shell | Org rollout |
| `/templates/odoo-cms-copilot/*` | Mixed | Theme template |
| `/templates/catalog.yaml` | YAML | Updated with entries |
| `/scripts/factory.sh` | Shell | Updated with routes |
| `/odoo/specs/agent-ready-cms/*` | Markdown | PRD bundle |

**Total new files**: ~35
**Total modified files**: 2
