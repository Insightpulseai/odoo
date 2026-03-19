# Styles Catalog

## Purpose

Choose a visual style that matches product positioning, audience expectations, and platform constraints.

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

## Styles (Selection Guide)

- **Minimal / Editorial** — best for premium, clarity-first products
- **Glassmorphism** — best for modern, playful UIs; avoid for data-dense screens
- **Neumorphism** — use sparingly; accessibility risk (low contrast)
- **Brutalism** — niche; brand-forward; high risk for mainstream audiences
- **Corporate SaaS** — safe default; fastest to ship; widest audience
- **Claymorphism** — soft 3D aesthetic; suitable for playful products
- **Bento Grid** — grid-based cards; good for feature showcases and dashboards
- **Dark Mode** — reduce eye strain; test contrast carefully in both modes
- **Skeuomorphism** — realistic textures; rarely appropriate in modern web
- **Flat Design** — simple and clean; pairs well with strong typography

## Selection Heuristic

Pick based on:
1. **Trust requirement** (high → corporate/editorial)
2. **Information density** (high → minimal/corporate)
3. **Device primary** (mobile-first → minimal)
4. **Brand tone** (playful → glass/gradients; serious → editorial)

## Style-Specific Rules

| Rule | Do | Don't |
|------|----|----- |
| `style-match` | Match style to product type and audience | Pick trendy style without justification |
| `consistency` | Use the same style across all pages | Mix multiple visual languages |
| `no-emoji-icons` | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 as UI icons |
| `correct-brand-logos` | Research official SVG from Simple Icons | Guess or use incorrect logo paths |
| `consistent-icon-sizing` | Use fixed viewBox (24x24) with w-6 h-6 | Mix different icon sizes randomly |
