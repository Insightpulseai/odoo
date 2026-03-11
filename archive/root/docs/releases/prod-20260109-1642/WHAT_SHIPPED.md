# What Shipped: prod-20260109-1642

**Release Date:** January 09, 2026 at 20:19 UTC
**Commit SHA:** `0b1e86b078b9a2c6562d437f9957577ac3246d04`
**Short SHA:** `0b1e86b`
**Previous Release:** (initial release)

---

## Summary

This release includes updates to the InsightPulse AI Odoo CE platform.

---

## Commits Included

```
0b1e86b fix(theme): deprecate ipai_theme_tbwa_backend modules causing SCSS errors
dbcad45 feat(theme): add ipai_theme_tbwa backend branding module
c285b67 fix(ipai_grid_view): correct XML data file loading order
cfc523e docs: auto-update SITEMAP.md and TREE.md [skip ci]
14dba47 Merge branch 'fix/tbwa-align-brand-tokens'
59bbac2 fix(tbwa): align brand tokens to official TBWA specifications
5037727 docs: auto-update SITEMAP.md and TREE.md [skip ci]
d6596bd Fix mode naming mismatch in PRD (#172)
934f300 Merge main into claude/fix-mode-naming-LdZMp
ac1e3a6 docs: auto-update SITEMAP.md and TREE.md [skip ci]
b8b5bdb fix(aiux): correct mode naming and add shipping bundle (#182)
772bded docs: auto-update SITEMAP.md and TREE.md [skip ci]
7676ffd Odoo 18 Community Edition core modules (#181)
2317ca3 docs: auto-update SITEMAP.md and TREE.md [skip ci]
7368e48 chore(auth): configure email + ai provider foundation
c36df68 fix(supabase): rename reserved column keyword to col_position in studio_schema
b196d54 docs: auto-update SITEMAP.md and TREE.md [skip ci]
5abff2b feat(stack): unified DO-managed compose (caddy+n8n+superset+ocr)
a6e35d8 docs: auto-update SITEMAP.md and TREE.md [skip ci]
95f6693 feat(vscode): add Odoo Language Server and ruff tooling (#179)
```

---

## Modules Changed

### Odoo Addons
- ipai/ipai_aiux_chat
- ipai/ipai_document_ai
- ipai/ipai_expense_ocr
- ipai/ipai_theme_aiux
- ipai/ipai_theme_tbwa_backend
- ipai/ipai_ui_brand_tokens
- ipai/ipai_web_theme_tbwa
- ipai_grid_view/__manifest__.py
- ipai_theme_tbwa/__init__.py
- ipai_theme_tbwa/__manifest__.py
- ipai_theme_tbwa/static
- ipai_theme_tbwa/views
- ipai_theme_tbwa_backend/__manifest__.py
- oca/oca.lock.json

### Supabase Edge Functions
- auth-bootstrap
- tenant-invite

### GitHub Workflows
- ai-naming-gate
- auth-email-ai-gate
- canonical-gate
- ci
- drive-sync
- drive-sync-verify
- ipai-doc-drift-gate

---

## Breaking Changes

- None identified

---

## Feature Flags / Config Changes

- None

---

## Known Issues / TODO Carryover

- See GitHub Issues for current backlog

---

## Rollback Instructions

```bash
# Rollback to previous release
git checkout main
docker compose down && docker compose up -d
```

---

## Related Links

- [GO_LIVE_MANIFEST.md](./GO_LIVE_MANIFEST.md)
- [DEPLOYMENT_PROOFS/](./DEPLOYMENT_PROOFS/)
- [GitHub Release](https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260109-1642)
