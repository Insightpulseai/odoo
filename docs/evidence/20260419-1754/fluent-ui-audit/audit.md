---
stamp: 20260419-1754
scope: fluent-ui-audit
goal: Inventory current Microsoft Fluent UI v9 adoption across web/ workspace and identify consolidation gaps
---

# Fluent UI v9 Adoption Audit

## Outcome

Fluent UI v9 is **already adopted** in 5 packages across `web/`. The premise that we need to "install Fluent UI" was incorrect. Real gaps: version drift, missing canonical token export, no dark theme, undocumented decision (no ADR).

## Evidence — current adoption

| Package | `@fluentui/react-components` | `@fluentui/react-icons` | FluentProvider wired? |
|---|---|---|---|
| `web/control-room` | `9.72.9` | `2.0.316` | (check needed) |
| `web/apps/control-room` | `9.72.9` | `2.0.316` | (duplicate of above?) |
| `web/apps/designer-agent` | `^9.54.0` | `^2.0.0` | YES — `src/app/providers.tsx` |
| `web/packages/fluent-designer-theme` | `^9.54.0` | — | exports `designerTheme = {...webLightTheme}` (no-op spread) |
| `web/packages/platform-shell` | `9.73.3` | `2.0.321` | YES — `src/PreviewShellProvider.tsx` |
| `web/apps/diva-goals` | (check needed) | (check needed) | YES — `src/main.tsx` |

## Evidence — token state

| File | Purpose | Status |
|---|---|---|
| `design/tokens/tokens.json` | Generic IPAI tokens (Tailwind-style) | Exists — not Fluent-aligned |
| `design/tokens/fluent-docs-tokens.json` | Semantic mappings to Fluent token names (e.g. `colorNeutralBackground1`) | Exists — schema only, no values |
| `design/tokens/m365_planner.tokens.json` | M365 Planner-specific tokens | Exists |
| `design/tokens/w9studio.tokens.json` | W9 Studio brand tokens | Exists |
| `design/tokens/fluent-base.json` | Canonical Fluent v9 token export | **MISSING** |

## Evidence — `@fluentui/tokens` direct dependency

```
$ grep -l "@fluentui/tokens" web/**/package.json
(no results)
```

`@fluentui/tokens` is consumed transitively via `@fluentui/react-components` but never imported directly. No build-time token export pipeline exists.

## Gaps identified

| # | Gap | Risk |
|---|---|---|
| 1 | **Version drift**: `^9.54.0` / `9.72.9` / `9.73.3` across packages | Component API drift, type incompatibilities, duplicate bundles |
| 2 | **Icons drift**: `^2.0.0` / `2.0.316` / `2.0.321` | Same as above for icon API |
| 3 | **`fluent-base.json` missing** | Power BI custom visuals, Odoo CMS surfaces, marketing pages can't share Fluent tokens |
| 4 | **Dark theme not wired** anywhere | Cannot meet WCAG / user preference / Fluent 2 dark mode parity |
| 5 | **Duplicate `control-room`** (`web/control-room` and `web/apps/control-room`) | Unclear which is canonical |
| 6 | **No ADR** for Fluent adoption decision | Not codified in `docs/architecture/adr/` |
| 7 | **`fluent-designer-theme` is a no-op spread** | Brand overlay declared but not implemented |

## Verification commands

```bash
# Reproduce inventory:
for f in $(find web -maxdepth 4 -name "package.json" -not -path "*/node_modules/*"); do
  v=$(grep -oE '"@fluentui/react-components"[^"]*"[^"]*"' "$f")
  if [ -n "$v" ]; then
    echo "$(echo $f | sed 's|^web/||;s|/package.json||') -> $v"
  fi
done

# Find FluentProvider usage:
grep -rln "FluentProvider" web --include="*.tsx" --include="*.ts" | grep -v node_modules
```

## Next deterministic steps

1. Pin Fluent UI version target across all packages (`9.73.3` recommended — latest in repo)
2. Add `@fluentui/tokens` as direct devDependency in `web/packages/fluent-designer-theme`
3. Run `node scripts/design/extract_fluent_tokens.mjs` → produces `design/tokens/fluent-base.json`
4. Resolve `web/control-room` vs `web/apps/control-room` duplicate
5. Add `webDarkTheme` switch to `fluent-designer-theme` package
6. Land ADR `ADR_FLUENT_UI_CONSOLIDATION.md`
