# Design Engineering Workflow

> **Contract for UI/UX contributions to `apps/ops-console` (and future apps).**
> This document defines the component lifecycle, token SSOT, and PR requirements
> for any change that touches the visual layer.

---

## 1. Component Lifecycle

```
Design token change?
  → Update token SSOT first (see §3)
  → Regenerate theme artifacts
  → Open "tokens:" PR before component PR

New component?
  shadcn/ui equivalent exists → use it (see §2)
  No equivalent → build from Radix UI primitive
  No Radix primitive → build from scratch with a11y checklist

Existing component change?
  → Read the component first (no blind edits)
  → Check for downstream usage (Grep for import)
  → Update snapshot / Playwright visual test if applicable
```

### States every interactive component must support

- Default
- Hover / focus (keyboard-navigable)
- Active / pressed
- Disabled
- Loading (skeleton or spinner)
- Error / invalid

---

## 2. Component Library Contract

`apps/ops-console` uses **shadcn/ui** (copied-in, not an npm dep) over Radix UI.

| Rule | Detail |
|------|--------|
| Source truth | `apps/ops-console/components/ui/` — never import from `@shadcn/ui` package |
| Adding a component | `npx shadcn@latest add <name>` from `apps/ops-console/` root |
| Customising | Edit the copied component; do not patch upstream |
| Icons | `lucide-react` only (already in deps); no additional icon libraries |
| Animation | `tailwindcss-animate` for entry/exit; `vaul` for drawer sheets |
| Toast / feedback | `sonner` only |

---

## 3. Token SSOT Contract

Design tokens flow in **one direction only**:

```
Source (Figma / manual JSON)
  → apps/ops-console/app/globals.css  (CSS custom properties)
  → apps/ops-console/tailwind.config.ts  (extend.colors, extend.spacing, etc.)
  → components/ui/*.tsx  (consume via Tailwind classes, never inline styles)
```

### Token naming convention

```css
/* Semantic tokens — always use these in components */
--background          /* page background */
--foreground          /* default text */
--primary             /* brand action color */
--primary-foreground  /* text on primary */
--muted               /* subdued backgrounds */
--muted-foreground    /* subdued text */
--border              /* dividers, outlines */
--ring                /* focus rings */
--radius              /* border-radius base */
```

**Rule**: components reference semantic tokens, not raw palette values.
Raw palette values (`slate-950`, `blue-500`) belong only in `globals.css` and
`tailwind.config.ts`, not in component JSX.

### Dark mode

- Implemented via `class="dark"` on `<html>` (not `prefers-color-scheme` media query).
- All semantic tokens must have a corresponding dark variant in `globals.css`.

---

## 4. PR Requirements for UI Changes

A PR that changes any file in `apps/ops-console/components/`,
`apps/ops-console/app/`, or `apps/ops-console/tailwind.config.ts` **must**:

### Mandatory

- [ ] **Preview URL**: include the Vercel Preview deployment URL in the PR description
- [ ] **Screenshot**: at least one before/after screenshot or screen recording
- [ ] **Keyboard navigation tested**: tab order is logical; no focus traps
- [ ] **Mobile viewport tested**: minimum 375 px width checked

### Required for new components

- [ ] **Accessible name**: all interactive elements have `aria-label` or associated `<label>`
- [ ] **Color contrast**: foreground/background pair passes WCAG AA (4.5:1 for body, 3:1 for large)
- [ ] **Loading/error states**: both are handled (no blank UI on async)

### Required for token changes

- [ ] **`globals.css` and `tailwind.config.ts` updated atomically** (same commit)
- [ ] **Dark mode variant confirmed** in globals.css for any new token
- [ ] **Diff labeled** in PR description: which semantic tokens changed and why

### Bundle budget

- [ ] Bundle size gate green (`ops-console-bundle-size.yml`)
- [ ] No new `!important` overrides
- [ ] No inline `style={{ }}` properties for values that belong in CSS tokens

---

## 5. Accessibility Baseline

All shipped UI must meet **WCAG 2.1 AA** minimum:

| Check | Tool |
|-------|------|
| Color contrast | Browser DevTools → Accessibility panel, or axe extension |
| Focus visibility | Tab through the feature in a browser; every interactive element must have a visible focus ring |
| Screen reader | At minimum, verify heading hierarchy with VoiceOver / NVDA |
| Motion | Respect `prefers-reduced-motion` — wrap animations in `@media (prefers-reduced-motion: no-preference)` |

The Playwright E2E workflow (`ops-console-playwright.yml`) runs chromium smoke tests.
Add accessibility assertions to `apps/ops-console/e2e/` when introducing complex interactive flows.

---

## 6. Review Surface

**Preview deployments are the primary review surface for UI changes.**

1. Push branch → Vercel auto-creates a Preview URL.
2. Include Preview URL in PR description.
3. Reviewers use the **Vercel Toolbar** to place inline comments directly on the UI.
4. Resolve all Preview comments before merge.

See `docs/ops/VERCEL_PREVIEWS.md` for how Previews work in this monorepo.

---

## 7. Design ↔ Code Handoff

| Phase | Output | Location |
|-------|--------|----------|
| Design exploration | Figma frames (optional) | Figma file linked in spec bundle |
| Token spec | CSS custom property names + values | `apps/ops-console/app/globals.css` |
| Component spec | Annotated screenshot or Storybook frame | Attached to PR or spec bundle |
| Implementation | Copied shadcn/ui or Radix component | `apps/ops-console/components/ui/` |
| Review | Vercel Preview URL + Toolbar comments | PR description |
| Sign-off | All Preview comments resolved | PR merged |

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `docs/platform/GOLDEN_PATH.md` | Overall monorepo contract, perf budgets, release lanes |
| `docs/ops/VERCEL_PREVIEWS.md` | Vercel Preview deployments, Toolbar comments |
| `docs/ops/VERCEL_MONOREPO.md` | Vercel workspace, skip-unaffected, env vars |
