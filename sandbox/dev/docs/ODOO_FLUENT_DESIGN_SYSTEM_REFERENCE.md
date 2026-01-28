# Odoo-Fluent Design System Reference

## Status: Pending Integration

**Source**: `Insightpulseai-net/.github` repository
**Branch**: `claude/pulser-hub-continue-parity-SU3bC`
**Commit**: `83c4735`
**Template**: `templates/odoo-fluent/AGENT_PROMPT.md`

## What This Contains

Comprehensive design system context for Claude agents working on Odoo 18 CE with Fluent UI-inspired styling.

### Sections Included

| Section | Purpose |
|---------|---------|
| **Design Tokens** | 8px spacing grid, border radius, colors, shadows |
| **CSS Variables** | `--ipai-*` custom properties for runtime theming |
| **Component Patterns** | Header, buttons, cards, tabs, inputs (with examples) |
| **QWeb Inheritance** | XPath patterns for Odoo template overrides |
| **Module Structure** | `ipai_*` prefix conventions, manifest assets config |
| **Forbidden Patterns** | Heavy blue backgrounds, Bootstrap defaults, inline styles |
| **Color Rules** | Brand vs background vs neutral usage guidelines |
| **Accessibility** | Focus rings, contrast requirements, touch targets (44×44px min) |
| **Testing Checklist** | Pre-commit validation items |

## Integration Methods

### Option 1: Fetch After PR Merge

Once the PR is merged to main:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
curl -o docs/ODOO_FLUENT_DESIGN_SYSTEM.md \
  https://raw.githubusercontent.com/Insightpulseai-net/.github/main/templates/odoo-fluent/AGENT_PROMPT.md
```

### Option 2: Reference in Claude Code MCP

Add to `.claude/mcp-servers.json` or agent config:

```json
{
  "context": [
    {
      "url": "https://github.com/Insightpulseai-net/.github/blob/main/templates/odoo-fluent/AGENT_PROMPT.md",
      "description": "Odoo-Fluent design system reference"
    }
  ]
}
```

### Option 3: Local Copy (Current Branch)

Fetch from feature branch before merge:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
curl -o docs/ODOO_FLUENT_DESIGN_SYSTEM.md \
  "https://raw.githubusercontent.com/Insightpulseai-net/.github/claude/pulser-hub-continue-parity-SU3bC/templates/odoo-fluent/AGENT_PROMPT.md"
```

## Design Token Overview (Summary)

### Spacing Scale (8px Grid)

```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
```

### Border Radius

```css
--radius-sm: 4px;   /* Buttons, inputs */
--radius-md: 8px;   /* Cards */
--radius-lg: 12px;  /* Modals */
--radius-pill: 999px; /* Pills */
```

### Color Palette (Fluent-Inspired)

```css
/* Brand */
--brand-primary: #0F6CBD;
--brand-hover: #115EA3;
--brand-pressed: #0F548C;

/* Backgrounds */
--bg-canvas: #FFFFFF;
--bg-surface: #F5F5F5;
--bg-overlay: #FFFFFF;

/* Neutrals */
--neutral-foreground-1: #242424;
--neutral-foreground-2: #424242;
--neutral-foreground-3: #616161;
```

### Shadows

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
--shadow-md: 0 2px 4px rgba(0,0,0,0.08);
--shadow-lg: 0 4px 8px rgba(0,0,0,0.12);
--shadow-xl: 0 8px 16px rgba(0,0,0,0.16);
```

## Component Patterns (QWeb Examples)

### Minimal Header (ipai_website_shell)

```xml
<template id="ipai_header" inherit_id="website.layout">
  <xpath expr="//header[@id='top']" position="replace">
    <header id="top" class="ipai-header">
      <div class="container">
        <nav class="navbar">
          <!-- Logo + Nav -->
        </nav>
      </div>
    </header>
  </xpath>
</template>
```

### Fluent-Style Button

```xml
<button class="ipai-btn ipai-btn--primary">
  <span class="ipai-btn__label">Submit</span>
</button>
```

```scss
.ipai-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-weight: 600;
  transition: background 0.1s ease;

  &--primary {
    background: var(--brand-primary);
    color: white;

    &:hover {
      background: var(--brand-hover);
    }
  }
}
```

### Card Component

```xml
<div class="ipai-card">
  <div class="ipai-card__header">
    <h3 class="ipai-card__title">Title</h3>
  </div>
  <div class="ipai-card__body">
    <p>Content</p>
  </div>
</div>
```

```scss
.ipai-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-md);
}
```

## Module Structure Convention

### Manifest Assets Declaration

```python
{
  "name": "IPAI Website Shell",
  "assets": {
    "web.assets_frontend": [
      "ipai_website_shell/static/src/scss/site_shell.scss",
      "ipai_website_shell/static/src/scss/_tokens.scss",
    ],
  },
}
```

### File Organization

```
addons/ipai_website_shell/
├── static/
│   ├── src/
│   │   ├── scss/
│   │   │   ├── _tokens.scss        # Design tokens
│   │   │   ├── _components.scss    # Component styles
│   │   │   └── site_shell.scss     # Main entry
│   │   └── img/
│   │       ├── logo.png
│   │       └── favicon.ico
│   └── description/
│       └── icon.png
└── views/
    └── layout.xml
```

## Forbidden Patterns

### ❌ Do NOT Use

```scss
/* Heavy blue backgrounds (Odoo default) */
.o_main_navbar {
  background: #00A09D; /* Too strong */
}

/* Bootstrap utility classes directly */
<div class="bg-primary text-white">

/* Inline styles */
<div style="margin: 20px; color: blue;">

/* Hardcoded colors */
background: #0000FF;
```

### ✅ Use Instead

```scss
/* Subtle, Fluent-inspired neutrals */
.ipai-header {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--neutral-stroke-1);
}

/* Component classes */
<div class="ipai-card ipai-card--primary">

/* CSS variables */
<div class="ipai-container">

/* Design tokens */
background: var(--brand-primary);
```

## Accessibility Requirements

### Focus Indicators

```scss
.ipai-btn:focus-visible {
  outline: 2px solid var(--brand-primary);
  outline-offset: 2px;
}
```

### Contrast Ratios

- **Normal text**: 4.5:1 minimum (WCAG AA)
- **Large text**: 3:1 minimum
- **UI components**: 3:1 minimum

### Touch Targets

- **Minimum size**: 44×44px (WCAG 2.1 AAA)
- **Recommended**: 48×48px for primary actions

## Testing Checklist

Before committing UI changes:

- [ ] Design tokens used (no hardcoded values)
- [ ] CSS variables defined for themeable properties
- [ ] Accessibility: focus indicators present
- [ ] Accessibility: contrast ratios meet WCAG AA
- [ ] Accessibility: touch targets ≥44×44px
- [ ] No Bootstrap default styles leaking
- [ ] No inline styles (use component classes)
- [ ] Responsive: mobile-first approach
- [ ] Browser tested: Chrome, Firefox, Safari
- [ ] Visual parity: SSIM ≥0.97 mobile, ≥0.98 desktop

## Integration with ipai-workspace

**Boundary rule**: Design tokens **defined in ipai-workspace** (`packages/tokens`), **consumed in odoo-ce** (as SCSS imports).

```bash
# Export tokens from ipai-workspace
cd ~/Documents/GitHub/ipai-workspace
node scripts/tokens-to-scss.js > tokens.scss

# Copy to Odoo module
cp tokens.scss ~/Documents/GitHub/odoo-ce/addons/ipai_website_shell/static/src/scss/_tokens.scss
```

## Next Steps

1. **Fetch canonical file** once PR merges to main
2. **Update CLAUDE.md** in odoo-ce to reference design system
3. **Create first Fluent-styled component** in ipai_website_shell
4. **Validate with brand assets validator** (scripts/brand/validate_brand_assets.sh)

---

**Source Branch**: https://github.com/Insightpulseai-net/.github/tree/claude/pulser-hub-continue-parity-SU3bC
**Commit**: `83c4735`
**Status**: Awaiting PR merge
**Last Updated**: 2026-01-28
