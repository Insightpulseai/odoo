# W9 Studio — Wix Site Design System Audit

> Extracted from PulseFit Studio template at `https://w9studio.wixstudio.com/my-site-2`
> Audit date: 2026-03-27
> Purpose: Design token extraction for Odoo Website rebuild

---

## Key Findings

The Wix site uses a **PulseFit gym template** with a tight black + white + orange (#FF5E1A) palette. The design system is template-grade but the color discipline and typography hierarchy are buildable foundations for the W9 Studio Odoo site.

**None of this is W9 Studio content** — it is template chrome only. The actual W9 Studio visual identity comes from the architect's deck (matte black interior, warehouse aesthetic).

---

## Color Palette (Canonical)

| Token | Value | Use |
|-------|-------|-----|
| `color.background.primary` | `#000000` | Page background, cards |
| `color.background.accent` | `#FF5E1A` | Orange accent surfaces |
| `color.text.primary` | `#FFFFFF` | Text on dark |
| `color.text.secondary` | `#EEEEEE` | Secondary text |
| `color.text.on-accent` | `#000000` | Text on orange (WCAG fix) |
| `color.action` | `#FF5E1A` | CTAs, hover states |
| `color.disabled` | `#949494` | Disabled elements |
| `color.border.subtle` | `rgba(255,255,255,0.2)` | Dividers |

### W9 Studio Adaptation

For the Odoo rebuild, the W9 Studio palette should shift to:

| Token | W9 Value | Rationale |
|-------|----------|-----------|
| `color.background.primary` | `#0F0F0F` | Matte black (warmer than pure black) |
| `color.accent.gold` | `#FFD700` | W9 Studio gold (established in React SPA) |
| `color.accent.cyan` | `#00FFFF` | Secondary accent |
| `color.accent.pink` | `#FF2E63` | Tertiary accent |

---

## Typography (Wix Template)

| Style | Font | Size (at 1280px) |
|-------|------|------------------|
| Display Hero | Impact | 120px |
| H2 Section | Sora | 85px |
| H3 Heading | Sora | 50px |
| Body | Arial | 16px |
| Nav | Arial | 15px |
| Caption | DIN Next Light | 12px |

### W9 Studio Adaptation

Odoo Website uses system fonts + Google Fonts. Recommended:
- **Display**: Keep mono/bold approach from React SPA
- **Headings**: Sora (available on Google Fonts)
- **Body**: System default (Arial/Helvetica)

---

## Button Variants

| Variant | Fill | Border | Text | Radius | Height |
|---------|------|--------|------|--------|--------|
| Primary | `#FF5E1A` | `#FF5E1A` | `#000` | 90px | 44px |
| Ghost White | transparent | `#FFF` | `#FFF` | 90px | 44px |
| Solid White | `#FFF` | none | `#000` | 90px | 44px |
| Jumbo Pill | `#FFF` | none | `#000` | 9999px | 76px |

All buttons hover → orange fill/border with 0.4s ease transition.

---

## Spacing

| Token | Value |
|-------|-------|
| Base unit | 8px |
| Section padding-y | 32px–80px |
| Site content width | 980px |
| Design reference width | 1280px |
| Header height | 63px |
| Card radius | 8px |
| Button radius (pill) | 90px |

---

## Component Inventory

1. **Header/Nav** — 63px, black, sticky with frosted overlay on scroll
2. **Hero** — Full-bleed video, Impact headline, dual pill CTAs
3. **News Slider** — 50/50 split panel with carousel arrows
4. **Service Rows** — Class name + price + "Book Now" button
5. **Trainer Cards** — Orange 274x395px cards, 3-column grid
6. **Feature Tiles** — 6 icon+label tiles, horizontal row
7. **Membership CTA** — Giant Impact watermark + centered orange card
8. **Newsletter Form** — Email input + checkbox + submit
9. **Footer** — 4-column info grid + social icons

---

## Accessibility Issues

- White on `#FF5E1A` fails WCAG AA for normal text (3.0:1, needs 4.5:1)
- No visible `:focus-visible` ring on interactive elements
- Service row dividers not rendering (border-width: 0px bug)
- Video hero has no captions/transcript
- Newsletter headline uses `<div>` not a heading element

---

## What Carries Forward to Odoo

| From Wix | W9 Studio Adaptation |
|----------|---------------------|
| Black + orange palette | Black + gold/cyan/pink palette |
| Impact display type | Bold mono display approach |
| Pill button shape (90px radius) | Keep pill buttons |
| Card-based service layout | 2x2 service card grid |
| 8px spacing rhythm | Keep 8px base unit |
| Sticky header pattern | Native Odoo sticky header |

| From Wix | Discarded |
|----------|-----------|
| PulseFit branding | Replace with W9 Studio |
| Gym/fitness content | Replace with recording studio |
| Orange `#FF5E1A` | Replace with gold `#FFD700` |
| Wix fluid `1cqw` scaling | Standard CSS clamp() |
| All stock photography | Replace with architect renderings |

---

*Audit date: 2026-03-27*
