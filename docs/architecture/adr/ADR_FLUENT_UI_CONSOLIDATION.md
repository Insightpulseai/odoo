# ADR: Fluent UI v9 Consolidation

- **Status**: Proposed
- **Date**: 2026-04-19
- **Authors**: Jake Tolentino
- **Supersedes**: —
- **Related**: `kasangkap-fluent` skill, `docs/skills/ios-native-wrapper.md` (iOS scope exclusion), Rule 19 (Apple Design Authority for iOS)

## Context

Microsoft Fluent UI v9 (`@fluentui/react-components`) is **already adopted** in 5 packages across the `web/` workspace (audit: `docs/evidence/20260419-1754/fluent-ui-audit/audit.md`). Adoption was incremental and uncoordinated:

- Versions diverge (`^9.54.0`, `9.72.9`, `9.73.3`)
- `@fluentui/tokens` is consumed transitively, never directly
- No canonical `design/tokens/fluent-base.json` exists for cross-surface parity (Power BI, Odoo CMS, marketing sites)
- `webDarkTheme` is wired nowhere
- `web/control-room` and `web/apps/control-room` appear to be duplicates
- `@repo/fluent-designer-theme` exists as a no-op spread (`{...webLightTheme}`) — declared but not implemented as the brand-overlay layer

There is no ADR documenting Fluent v9 as the canonical web component library, despite live usage.

## Decision

**Fluent UI v9 is the canonical web component library and design token source-of-truth for the IPAI platform on M365-adjacent and platform-internal web surfaces.**

Specifically:

1. **Component library**: `@fluentui/react-components` (v9, latest stable) is the default for all `web/apps/*` and shared `web/packages/*` surfaces.
2. **Icon library**: `@fluentui/react-icons` (v2, latest stable) is the default icon set for the same scope.
3. **Token authority**: `@fluentui/tokens` is the canonical token source. Brand overlays apply on top via `@repo/fluent-designer-theme`, never by forking Fluent.
4. **Theme provider**: Every Fluent-using app must wrap its root in `<FluentProvider theme={...}>`. Light theme default; dark theme available via app-level switch.
5. **Cross-surface tokens**: `design/tokens/fluent-base.json` is generated from `@fluentui/tokens` via `scripts/design/extract_fluent_tokens.mjs` and committed as the SSOT for non-React surfaces (Power BI custom visuals, Odoo CMS, marketing pages).

## Scope (in)

- All `web/apps/*` Next.js / React applications (control-room, designer-agent, diva-goals, copilot, billing-site, ipai-landing, etc.)
- All `web/packages/*` shared component libraries
- Power BI custom visuals (consume `fluent-base.json`)
- Odoo CMS templates (consume `fluent-base.json` color/type tokens via SCSS variables)

## Scope (out)

- **iOS wrapper** (`web/mobile/`) — Apple HIG / Liquid Glass per Rule 19/20/21
- **Odoo backend admin views** — owned by Odoo's own framework styling
- **Internal CLI / terminal tooling** — text-only, no UI

## Version target

| Package | Current pinned target |
|---|---|
| `@fluentui/react-components` | `9.73.3` (or latest stable) |
| `@fluentui/react-icons` | `2.0.321` (or latest stable) |
| `@fluentui/tokens` | matches `react-components` peer-dep range |

All packages MUST pin exact versions (no `^` range) to prevent drift. Updates are batched via a single PR that bumps all three across all consumers.

## Consequences

### Positive

- Single canonical UI vocabulary across IPAI web surfaces aligns with M365 Copilot, Teams, Outlook channel surfaces (per Rule: M365 Agents SDK is channel layer for enterprise delivery)
- Power BI / Odoo CMS / marketing pages can inherit Fluent token values without re-implementing
- `kasangkap-fluent` skill enforcement becomes meaningful (currently aspirational)
- Eliminates need to design/build a custom component library
- Dark mode support comes "for free" via `webDarkTheme`

### Negative

- Locks IPAI web stack to Microsoft's Fluent release cadence
- Requires version-bump PRs across all consumers
- iOS native wrapper continues to use Apple HIG — two design vocabularies to maintain (acceptable: enforced by platform conventions, not a design choice)
- `@fluentui/react-components` bundle size is non-trivial; tree-shaking discipline required for marketing/landing pages

### Mitigations

- Version updates gated behind a single ADR-amendment + sibling Azure Pipeline check
- Marketing pages use `@fluentui/tokens` (lightweight) not `@fluentui/react-components` (heavy) where component library isn't needed
- `kasangkap-fluent` skill includes bundle-size audit step

## Implementation plan

| Step | Owner | Status |
|---|---|---|
| 1. Land this ADR | Jake | This commit |
| 2. Land audit evidence | Jake | This commit |
| 3. Land `extract_fluent_tokens.mjs` script | Jake | This commit |
| 4. Resolve `web/control-room` vs `web/apps/control-room` duplicate | TBD | Open |
| 5. Pin `@fluentui/*` versions across all 5 consumers to `9.73.3` / `2.0.321` | TBD | Open |
| 6. Add `@fluentui/tokens` as devDep in `fluent-designer-theme`, run extractor, commit `fluent-base.json` | TBD | Open |
| 7. Wire `webDarkTheme` switch in `fluent-designer-theme` exports | TBD | Open |
| 8. Update `kasangkap-fluent` skill to enforce v9 + brand layer rules | TBD | Open |
| 9. Document Power BI custom visual token consumption pattern | TBD | Open |
| 10. Document Odoo CMS SCSS token consumption pattern | TBD | Open |

## Verification

- After step 5: `grep -E '"@fluentui/react-components": "[^9]'` returns no matches outside intended scope
- After step 6: `design/tokens/fluent-base.json` exists, contains both `webLightTheme` and `webDarkTheme` keys
- After step 7: `import { designerTheme, designerDarkTheme } from '@repo/fluent-designer-theme'` succeeds
- After step 8: `kasangkap-fluent` skill rejects use of v8 (`@fluentui/react`) or custom-built Fluent-lookalike components

## References

- [Fluent UI repository](https://github.com/microsoft/fluentui) (19.9K ★, MIT, last push 2026-04-18)
- [Fluent UI React docs](https://react.fluentui.dev)
- [Fluent UI Developer site](https://developer.microsoft.com/en-us/fluentui)
- [Microsoft Fluent 2 Web Figma Community file](https://www.figma.com/community/file/836828295772957889) — reference only; npm packages are the SSOT
- Audit evidence: `docs/evidence/20260419-1754/fluent-ui-audit/audit.md`
- Extractor script: `scripts/design/extract_fluent_tokens.mjs`
