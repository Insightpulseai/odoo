<!--
SSOT: Odoo-Fluent Design System
Source: https://raw.githubusercontent.com/Insightpulseai-net/.github/main/templates/odoo-fluent/AGENT_PROMPT.md
Policy: Do not edit downstream copies; update upstream template then re-sync.
-->
# CLAUDE.md — Odoo CE E-Commerce (Fluent Design System)

> **Repository:** `jgtolentino/odoo-ce`
> **Design System:** InsightPulse AI Fluent Theme (Microsoft Fluent UI v9)
> **Target:** Odoo 18/19 Website + eCommerce

---

## Design System Reference

The canonical Fluent UI theme template lives in the `.github` org-standards repo:

```
Insightpulseai-net/.github/templates/odoo-fluent/
├── __manifest__.py
├── static/src/scss/
│   ├── _fluent_tokens.scss    # Design tokens (SSOT)
│   └── fluent_website.scss    # Component styles
└── views/
    └── website_fluent_header.xml   # QWeb template overrides
```

**Always reference this as the source of truth for design decisions.**

---

## Design Tokens (Use These)

### Spacing (8px Grid)

| Token | Value | Use For |
|-------|-------|---------|
| `$fluent-spacing-xs` | 4px | Icon gaps, tight padding |
| `$fluent-spacing-s` | 8px | Button padding, card gaps |
| `$fluent-spacing-m` | 12px | Section padding |
| `$fluent-spacing-l` | 16px | Card body padding |
| `$fluent-spacing-xl` | 20px | Container gutters |
| `$fluent-spacing-xxl` | 24px | Hero sections |

### Border Radius

| Token | Value | Use For |
|-------|-------|---------|
| `$fluent-radius-s` | 4px | Badges, pills |
| `$fluent-radius-m` | 8px | Buttons, inputs |
| `$fluent-radius-l` | 12px | Cards, modals |
| `$fluent-radius-circular` | 9999px | Avatar, circular buttons |

### Colors (Brand)

```scss
// Primary brand (calm blue - NOT heavy saturated blue)
$fluent-brand-primary: #0052cc;
$fluent-brand-primary-hover: #0747a6;
$fluent-brand-background: #e6f0ff;  // Hover/selected states

// Surfaces
$fluent-neutral-background-1: #ffffff;  // Cards
$fluent-neutral-background-2: #fafafa;  // Page background
$fluent-neutral-stroke-1: rgba(0, 0, 0, 0.08);  // Borders
```

### Shadows (Elevation)

```scss
$fluent-shadow-2: 0 1px 2px rgba(0,0,0,0.06);   // Base cards
$fluent-shadow-8: 0 4px 8px rgba(0,0,0,0.10);   // Hover state
$fluent-shadow-16: 0 8px 16px rgba(0,0,0,0.12); // Modals
```

---

## CSS Custom Properties (Runtime)

Use these in any SCSS/CSS for runtime theming support:

```css
var(--ipai-bg)           /* Page background */
var(--ipai-surface)      /* Card/panel background */
var(--ipai-border)       /* Default border color */
var(--ipai-brand)        /* Primary brand color */
var(--ipai-shadow-1)     /* Base elevation */
var(--ipai-shadow-2)     /* Hover elevation */
var(--ipai-focus)        /* Focus ring */
var(--ipai-radius-m)     /* Standard border radius */
```

---

## Component Patterns

### Header → Command Surface

**DO:**
```xml
<header class="ipai-header">
  <!-- White background, subtle bottom border, minimal shadow -->
</header>
```

**DON'T:**
```xml
<header style="background: #0066cc;">
  <!-- Heavy colored backgrounds break Fluent pattern -->
</header>
```

### Buttons

| Class | When to Use |
|-------|-------------|
| `.ipai-btn-primary` | Primary actions: Add to Cart, Submit, Save |
| `.ipai-btn-secondary` | Secondary actions: Cancel, Back, Reset |
| `.ipai-btn-subtle` | Tertiary: Links, icon buttons, nav items |

```xml
<button class="ipai-btn-primary">Add to Cart</button>
<a href="/shop" class="ipai-btn-secondary">Continue Shopping</a>
<button class="ipai-btn-subtle"><i class="fa fa-heart"/></button>
```

### Cards (Products)

```xml
<div class="ipai-card">
  <div class="ipai-card-image-wrapper">
    <img t-att-src="product.image_url" class="ipai-card-image"/>
  </div>
  <div class="ipai-card-body">
    <h3 class="ipai-card-title" t-field="product.name"/>
    <span class="ipai-card-price" t-field="product.list_price"/>
  </div>
</div>
```

### Navigation Tabs

```xml
<nav class="ipai-tabs">
  <a class="ipai-tab active">All Products</a>
  <a class="ipai-tab">Categories</a>
  <a class="ipai-tab">On Sale</a>
</nav>
```

### Form Inputs

```xml
<input type="text" class="ipai-input" placeholder="Search products..."/>
<div class="ipai-search">
  <input type="text" placeholder="Search..."/>
  <button class="ipai-btn-subtle"><i class="fa fa-search"/></button>
</div>
```

---

## QWeb Template Inheritance

When modifying Odoo website templates, use XPath inheritance:

```xml
<!-- Add Fluent class to existing element -->
<template id="fluent_product_card" inherit_id="website_sale.products_item">
    <xpath expr="//div[hasclass('o_wsale_product_card')]" position="attributes">
        <attribute name="class" add="ipai-card"/>
    </xpath>
</template>
```

**Never replace entire templates** - always use targeted XPath selectors.

---

## Module Structure (ipai_* Prefix)

Custom modules MUST follow this structure per RULE-ODOO-002:

```
ipai_website_shell/
├── __manifest__.py
├── __init__.py
├── static/
│   └── src/
│       └── scss/
│           ├── _variables.scss      # Import Fluent tokens
│           └── website_shell.scss   # Module-specific styles
├── views/
│   ├── templates.xml               # QWeb templates
│   └── snippets.xml                # Website builder snippets
├── security/
│   └── ir.model.access.csv
└── README.md
```

### __manifest__.py Assets

```python
'assets': {
    'web.assets_frontend': [
        # Fluent tokens first (import from theme or inline)
        'ipai_website_shell/static/src/scss/_variables.scss',
        'ipai_website_shell/static/src/scss/website_shell.scss',
    ],
},
```

---

## Forbidden Patterns

### DON'T: Heavy Blue Backgrounds
```scss
// BAD - breaks Fluent calm aesthetic
.header { background: #0066cc; }
.hero { background: linear-gradient(#003366, #0066cc); }
```

### DON'T: Bootstrap Default Styling
```xml
<!-- BAD - use ipai-* classes instead -->
<button class="btn btn-primary btn-lg">...</button>
```

### DON'T: Inline Styles
```xml
<!-- BAD - use design tokens -->
<div style="border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
```

### DON'T: Mixed Border Radii
```scss
// BAD - inconsistent corners
.card { border-radius: 6px; }
.button { border-radius: 4px; }
.input { border-radius: 8px; }

// GOOD - use tokens
.card { border-radius: $fluent-radius-l; }
.button { border-radius: $fluent-radius-m; }
.input { border-radius: $fluent-radius-m; }
```

---

## Color Usage Rules

### Primary Brand (#0052cc)
- Button backgrounds (primary only)
- Link hover states
- Active tab indicators
- Price displays
- **NOT for:** Backgrounds, headers, large areas

### Brand Background (#e6f0ff)
- Hover states on nav items
- Selected/active states
- Subtle highlights
- **Replaces:** Heavy blue backgrounds

### Neutrals
- Page background: `#fafafa`
- Cards/panels: `#ffffff`
- Borders: `rgba(0,0,0,0.08)`
- Text primary: `#242424`
- Text secondary: `#616161`

---

## Animation Guidelines

Use Fluent transitions:

```scss
// Standard transition
transition: all 150ms cubic-bezier(0.33, 0, 0.67, 1);

// Hover effects
&:hover {
  box-shadow: $fluent-shadow-8;
  transform: translateY(-2px);
}
```

**Timing:**
- Fast interactions: 150ms
- Normal transitions: 200ms
- Elaborate animations: 300ms

---

## Accessibility Requirements

### Focus States
All interactive elements MUST have visible focus:

```scss
&:focus-visible {
  outline: none;
  box-shadow: var(--ipai-focus); // 0 0 0 3px rgba(0,82,204,0.24)
}
```

### Color Contrast
- Text on white: minimum `#616161` (4.5:1 ratio)
- Text on brand: always white `#ffffff`
- Never use color alone to convey meaning

### Touch Targets
- Minimum 44x44px for mobile
- Buttons: min-height 36px desktop, 44px mobile

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| SCSS variables | `_*.scss` | `_fluent_tokens.scss` |
| SCSS components | `*.scss` | `product_cards.scss` |
| QWeb templates | `*.xml` | `website_header.xml` |
| Snippets | `s_*.xml` | `s_fluent_hero.xml` |

---

## Testing Checklist

Before committing any UI changes:

- [ ] Tokens used (no hardcoded values)
- [ ] Works on mobile (375px+)
- [ ] Focus states visible
- [ ] Hover states smooth (150ms)
- [ ] Cards have elevation on hover
- [ ] No heavy blue backgrounds
- [ ] Module installs without errors
- [ ] Lighthouse accessibility ≥90

---

## Quick Reference Card

```
SPACING:     8px grid (xs=4, s=8, m=12, l=16, xl=20, xxl=24)
RADIUS:      s=4px, m=8px, l=12px
BRAND:       #0052cc (accent only, NOT backgrounds)
SURFACE:     #ffffff cards, #fafafa page
BORDER:      rgba(0,0,0,0.08)
SHADOW:      2/8/16 levels
FOCUS:       3px brand ring at 24% opacity
TRANSITION:  150ms ease
```

---

## Related Documentation

- [Fluent UI v9](https://fluent2.microsoft.design/)
- [Odoo Website Docs](https://www.odoo.com/documentation/18.0/developer/tutorials/website.html)
- [ORG_RULES.md](https://github.com/Insightpulseai-net/.github/blob/main/docs/governance/ORG_RULES.md) - RULE-ODOO-*
- [Skills: odoo-oca-conventions](https://github.com/Insightpulseai-net/.github/blob/main/skills/odoo-oca-conventions/skill.yaml)
