# Codebase Index — Insightpulseai/odoo

**Last Updated**: 2026-02-23 01:43 UTC
**Built by**: python-ast + find (macOS, BSD ctags not available)

## Index Statistics

- **Files indexed**:   128998 (excluding addons/oca, .pnpm-store, node_modules)
- **Symbols indexed**:     2002 (Python classes/functions in addons/ipai + scripts + agents)
- **Index location**: `.cache/`

## Index Files

### File Catalog
- **File**: `.cache/rg_catalog.txt`
- **Format**: one file path per line
- **Excludes**: addons/oca (git-aggregated, no-touch), .pnpm-store, node_modules, build artifacts

### Symbol Index
- **File**: `.cache/tags`
- **Format**: ctags-compatible (name TAB file TAB line)
- **Coverage**: Python classes + functions in addons/ipai, scripts/, agents/
- **Built with**: Python AST parser

## Key Paths

| Purpose | Path |
|---------|------|
| IPAI custom modules | `addons/ipai/` |
| Standalone IPAI modules | `addons/ipai_*/` |
| OCA modules (no-touch) | `addons/oca/` |
| CI workflows | `.github/workflows/` |
| Scripts | `scripts/` |
| Apps (Next.js etc) | `apps/` |
| Web | `web/` |
| Spec bundles | `spec/` |
| Agents | `agents/` |

## Refresh

```bash
# Rebuild file catalog
find /path/to/repo -not -path '*/.pnpm-store/*' -not -path '*/addons/oca/*' -not -path '*/.git/*' -type f > .cache/rg_catalog.txt

# Rebuild symbol index (Python AST)
python3 scripts/build_tags.py  # if script exists, else rerun sc-index
```
